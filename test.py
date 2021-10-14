#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response 
from uuid import uuid4
from random import randint
from time import sleep
import datetime, json, os, codecs, requests

pwd = '/root/TimeBox/' if os.name == 'posix' else ''
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

def addStorage(set, name):
    f = open(pwd+name, mode='a', encoding="utf-8")
    f.write(set)
    f.close()

def writeStorage(set, name):
    f = open(pwd+name, mode='w', encoding="utf-8")
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
            "name":lib[deadline.strftime("%a").lower()]+\
                   f"({'не чётная' if bool(deadline.isocalendar()[1]%2) else 'чётная'})",
            "l_box": url_for('hello', time=timecode),
            #"l_list": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('list', time=timecode)
            "l_sindin": url_for('signin'), # url_for('sindin', time=timecode)
            "l_about": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('sindin', time=timecode)
    }
    return render_template('index.html', data=date)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try:
        auth = json.loads(readStorage('auth.json'))
    except:
        auth = {
            "vkHash": {},
            "accounts": {}
        }
        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.cookies.get('log') in auth['accounts']:
        return redirect(url_for('check'))

    date = {
        "name":'Вход',
        "way":url_for('check'),
        "error":""
    }
    #res = make_response("Setting a cookie")
    #res.set_cookie('token', '', max_age=30)

    if request.args.get('error', ''):
        if request.args.get('error', '') == 'LoginWrong': date['error'] = 'Неверный пароль или логин'

    return render_template('signin.html', data=date)

@app.route('/check', methods=['GET', 'POST'])
def check():
    try:
        auth = json.loads(readStorage('auth.json'))
    except:
        auth = {
            "vkHash": {},
            "accounts": {}
        }
        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.args.get('hash', '') and request.args.get('hash', '') in auth['vkHash']:
        res = make_response(redirect(url_for('dashboard')))
        res.set_cookie('log', auth['vkHash'][request.args.get('hash', '')], max_age=60 * 60 * 24 * 7)
        return res


    elif request.args.get('loseLog', '') == '1':
        res = make_response(redirect(url_for('signin')))
        res.set_cookie('log', '', max_age=0)
        return res

    elif request.cookies.get('log') and request.cookies.get('log') not in auth['accounts']:
        res = make_response(redirect(url_for('signin')))
        res.set_cookie('log', '', max_age=0)
        return res

    elif request.cookies.get('log') in auth['accounts']:
        return redirect(url_for('dashboard'))

    elif request.method == 'POST':
        login, password = request.form['login'], request.form['password']
        for i in list(auth['accounts']):
            if login == auth['accounts'][i]['login'] and password == auth['accounts'][i]['password']:
                res = make_response(redirect(url_for('dashboard')))
                res.set_cookie('log', i, max_age=60 * 60 * 24 * 7)
                return res
        return redirect(url_for('signin',error='LoginWrong'))

    else:
        response = requests.get(request.args.get('photo',''))
        if response.status_code == 200:
            with open(pwd+"photos/time.png", 'wb') as f:
                f.write(response.content)
        return redirect(url_for('signup', hash=request.args.get('hash', ''), uid=request.args.get('uid', ''),
                                name=request.args.get('first_name', ''),
                                surname=request.args.get('last_name', ''),
                                photo=str(request.args.get('photo', ''))))

@app.route('/signup', methods=['GET','POST'])
def signup():
    try:
        auth = json.loads(readStorage('auth.json'))
    except:
        auth = {
            "vkHash": {},
            "accounts": {}
        }
        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.method == 'POST':
        idl = str(uuid4())
        while (idl in auth['accounts']): idl = str(uuid4())
        auth['vkHash'][request.args.get('hash', '')] = idl
        auth['accounts'][idl] = {
            "img": request.args.get('photo', '').replace('amp;','&'),
            "name": request.args.get('name', ''),
            "surname": request.args.get('surname', ''),
            "hash": request.args.get('hash', ''),
            "uid": request.args.get('uid', ''),
            "login":request.form['login'],
            "password":request.form['password']
        }

        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return redirect(url_for('dashboard'))
    elif request.cookies.get('log') in auth['accounts']:
        return redirect(url_for('check'))

    else:
        data = {
            "img": request.args.get('photo',''),
            "name": request.args.get('name',''),
            "surname": request.args.get('surname',''),
            "hash": request.args.get('hash',''),
            "uid": request.args.get('uid','')
        }
        return render_template('signup.html', data=data)


@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    try:
        auth = json.loads(readStorage('auth.json'))
    except:
        auth = {
            "vkHash": {},
            "accounts": {}
        }
        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.cookies.get('log') in auth['accounts']:
        data = auth['accounts'][request.cookies.get('log')]
        return render_template('room.html',data=data)
    else:
        res = make_response(redirect(url_for('signin')))
        res.set_cookie('log', '', max_age=0)
        return res

@app.route('/dashboard/file', methods=['GET','POST'])
def file():
    try:
        auth = json.loads(readStorage('auth.json'))
    except:
        auth = {
            "vkHash": {},
            "accounts": {}
        }
        addStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.cookies.get('log') in auth['accounts'] and False:
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
                return f'<h3>Upload file(s) at server</h3><form enctype="multipart/form-data" method="POST">\
<p><input type="file" name="file" required title="Upload..."></p><p><a href="{url_for("index")}">Back</a>\
 <input type="submit" value="Load"></p> </form>'
    else: return redirect(url_for('index'))


@app.route('/box', methods=['GET'])
def hello():
    if request.args.get('time', ''):
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))
        date={
            "day": str(deadline.strftime("%d.%m.%Y")),
            "name":lib[deadline.strftime("%a").lower()] +\
                   f"({'не чётная' if bool(deadline.isocalendar()[1]%2) else 'чётная'})",
            "-": url_for('hello', time=int((deadline + datetime.timedelta(days = -1)).timestamp())),
            "+": url_for('hello', time=int((deadline + datetime.timedelta(days = 1)).timestamp())),
            "way": "?time=" + str(int((deadline + datetime.timedelta(days = 1)).timestamp())),
            'les':[],
            'textTime': (f"Сегодня" if deadline.date()==datetime.datetime.today().date() else (f"В будущем\
 на {abs((deadline.date()-datetime.datetime.today().date()).days)} дней" if deadline > datetime.datetime\
                                                                                           .today() else f"В прошлом\
 на {abs((deadline.date()-datetime.datetime.today().date()).days)} дней"))
        }

        page = json.loads(readStorage(f'solo.json'))
        ids = []
        for i in page['week'][deadline.strftime("%a").lower()]:
            idL = None
            while (idL in ids or idL == None): idL = randint(0,10000)
            ids.append(idL)

            d = {
                'id': idL,
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
                idL = None
                while (idL in ids or idL == None): idL = randint(0,10000)
                ids.append(idL)
                date['les'].append({
                    'id': idL,
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
