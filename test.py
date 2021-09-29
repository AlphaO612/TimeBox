#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response 
from uuid import uuid4
from random import randint
from time import sleep
import datetime, json, os, codecs

pwd = '/root/TimeBox/'
sysTokens = {}
lib = {
    "mon":"понедельник",
    "tue":"вторник",
    "wed":"среда",
    "thu":"четверг",
    "fri":"пятница",
    "sat":"суббота",
    "sun":"воскресенье",
}

def writeStorage(set, name):
    f = open(name, mode='w', encoding="utf-8")
    f.write(set)
    f.close()

def readStorage(name):
    try:
        with codecs.open(pwd + name, 'r', encoding='utf-8',
                     errors='ignore') as f:
        #f = open(pwd + name, 'r')
            set = f.read()
            f.close()
    except:
        set=None
    return set

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    today = datetime.date.today()
    moment = datetime.datetime.now().time()
    deadline = datetime.datetime.combine(today, moment)
    print(deadline)
    timecode = int(deadline.timestamp())
    
    date={
            "day": str(deadline.strftime("%d.%m.%Y")),
            "name":lib[deadline.strftime("%a").lower()],
            "l_box": url_for('hello', time=timecode),
            #"l_list": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('list', time=timecode)
            "l_sindin": url_for('sighin'), # url_for('sindin', time=timecode)
            "l_about": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('sindin', time=timecode)

        }
    return render_template('index.html', data=date)

@app.route('/sighin', methods=['GET', 'POST'])
def sighin():
    if request.cookies.get('log') == readStorage('set'): return redirect(url_for('admin'))
    else:
        date = {
            "name":'Вход',
            "way":url_for('check'),
        }
        #res = make_response("Setting a cookie")
        #res.set_cookie('token', '', max_age=30)

        return render_template('signin.html', data=date)

@app.route('/check', methods=['GET', 'POST'])
def check():
    print([request.form['login'],request.form['password']])
    if [request.form['login'],request.form['password']] == ['alphaste', 'AzureNotHere']:
        res = make_response(redirect(url_for('admin')))
        writeStorage('set',str(uuid4()))
        res.set_cookie('log', readStorage('set'), max_age=60 * 60 * 24)
        return res
    else:
        return redirect(url_for('sighin'))

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return redirect(url_for('file'))

@app.route('/dashboard/file', methods=['GET','POST'])
def file():
    if request.cookies.get('log') == readStorage('set'):
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and file.filename:
                    for file in request.files.getlist('file'):
                        file.save(os.path.join(pwd, 'test.json'))
                        try:
                            data = json.loads(readStorage('test.json'))
                            if list(lib) != list(data['week']): raise TypeError()
                        except Exception as e: return f'<p><h1 style="color:red;">Check your file</h1></p><p>{e} - {str(e)}</p><p><a href="{request.url}">Back</a></p>'
                        else:
                            writeStorage(json.dumps(data, ensure_ascii=False), 'solo.json')
                            return f'<p><h1>fine! you loaded it!</h1></p<p><a href="{url_for("index")}">Back</a></p>'
                    return redirect(url_for('index'))
            else:
                return f'<h3>Upload file(s) at server</h3><form enctype="multipart/form-data" method="POST"><p><input type="file" name="file" required title="Upload..."></p><p><a href="{url_for("index")}">Back</a> <input type="submit" value="Load"></p> </form>'
    else: redirect(url_for('index'))


@app.route('/box', methods=['GET'])
def hello():
    if request.args.get('time', ''):
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))
        date={
            "day": str(deadline.strftime("%d.%m.%Y")),
            "name":lib[deadline.strftime("%a").lower()],
            "-": url_for('hello', time=int((deadline + datetime.timedelta(days = -1)).timestamp())),
            "+": url_for('hello', time=int((deadline + datetime.timedelta(days = 1)).timestamp())),
            "way": "?time=" + str(int((deadline + datetime.timedelta(days = 1)).timestamp())),
            'les':[]
        }

        page = json.loads(readStorage(f'solo.json'))
        ids = []
        id = None
        for i in page['week'][deadline.strftime("%a").lower()]:
            while (id in ids or id == None): id = randint(0,10000000000)

            d = {
                'id': id,
                'st': i['time'][0],
                'en': i['time'][1],
                'name': i['name'],
                'teacher': 'Профессор ' + i['teacher'],
                'infoSh': i['info'][0:10] + '...',
                'info': i['info']
            }
            if 'weekType' in i:
                if i['weekType'] == 0 or (i['weekType'] == 1 and bool(deadline.isocalendar()[1]%2)) or\
                        (i['weekType'] == 2 and not bool(deadline.isocalendar()[1]%2)):
                    date['les'].append(d)
            else:
                date['les'].append(d)

        if deadline.strftime("%d.%m.%Y") in page['other']:
            for i in page['other'][deadline.strftime("%d.%m.%Y")]:
                while (id in ids or id == None): id = randint(0, 10000000000)
                date['les'].append({
                    'id': id,
                    'st': i['time'][0],
                    'en': i['time'][1],
                    'name': i['name'],
                    'teacher': 'Профессор ' + i['teacher'],
                    'infoSh': i['info'][0:20] + '...',
                    'info': i['info']
                })

        return render_template('data.html', data=date)
    else:
        today = datetime.date.today()
        moment = datetime.datetime.now().time()
        now = datetime.datetime.combine(today, moment)
        deadline = now + datetime.timedelta(days = 1)
        print(deadline)
        deadline = int(deadline.timestamp())
        return redirect(url_for('hello', time=deadline))

@app.route('/lesson/<name>', methods=['GET'])
def les(name=None):
    if request.args.get('time', '') and name:
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))

        date={
            "day": str(deadline.strftime("%d.%m.%Y")),
            "name":lib[deadline.strftime("%a").lower()],
            "-": url_for('les', time=int((deadline + datetime.timedelta(days = -1)).timestamp()), name=name),
            "+": url_for('les', time=int((deadline + datetime.timedelta(days = 1)).timestamp()), name=name)
        }

        try:
            page = json.loads(readStorage(f'10/lessons/{name}.json'))
        except Exception as e:
            print(f"error - {e}")
            name = "Неизвестный урок"
            text = ""
            files = []
        else:
            name = page['name']
            if page.get('info'):
                print(deadline.strftime("%d.%m.%Y"))
                gun = list(page['info'].keys())
                gun.sort()
                gun.reverse()
                print(gun)
                i = 0
                ray = None
                for i in range(len(gun)):
                    print(i)
                    point = datetime.datetime.strptime(gun[0], "%d.%m.%Y")
                    if point < deadline:
                        ray = gun[0]
                        break
                    else:
                        gun.remove(gun[0])
                print(ray)
                if ray:
                    text = page['info'][ray]['text']
                    files = page['info'][ray]['files']
                else:
                    text, files = '', []
            else:
                text = ""
                files = []
        info={
            "lesson": name,
            "text": text,
            "files": files,
        }

        return render_template('lesson.html', data=date, info=info)
    else:
        today = datetime.date.today()
        moment = datetime.datetime.now().time()
        now = datetime.datetime.combine(today, moment)
        deadline = now + datetime.timedelta(days = 1)
        print(deadline)
        deadline = int(deadline.timestamp())
        return redirect(url_for('les', name=name, time=deadline))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
