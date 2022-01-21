#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response
from dateutil.relativedelta import *
from uuid import uuid4
from random import randint
from time import sleep
import datetime, json, os, codecs, requests

pwd = '/root/TimeBox/' if os.name == 'posix' else ''
sysTokens = {}
lib = {
    "mon": "понедельник",
    "tue": "вторник",
    "wed": "среда",
    "thu": "четверг",
    "fri": "пятница",
    "sat": "суббота",
    "sun": "воскресенье",
}


def addStorage(set, name):
    f = open(pwd + name, mode='a', encoding="utf-8")
    f.write(set)
    f.close()


def writeStorage(set, name):
    f = open(pwd + name, mode='w', encoding="utf-8")
    f.write(set)
    f.close()


def readStorage(name):
    try:
        with codecs.open(pwd + name, 'r', encoding='utf-8',
                         errors='ignore') as f:
            # f = open(pwd + name, 'r')
            set = f.read()
            f.close()
    except:
        set = None
    return set


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return (next_month - datetime.timedelta(days=next_month.day)).day


def prefixWeek(deadline): return lib[deadline.strftime(
    "%a").lower()] + f" ({'не чётная' if bool(deadline.isocalendar()[1] % 2) else 'чётная'})"


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

    date = {
        "day": str(deadline.strftime("%d.%m.%Y")),
        "name": prefixWeek(deadline),
        "les": [
            {
                "name": "Расписание",
                "link": url_for('now'),
            },
            {
                "name": "Календарь",
                "link": url_for('calendar'),
            },
            {
                "name": "Личный Кабинет",
                "link": url_for('signin'),
            },
            {
                "name": "О проекте",
                "link": url_for('aboutus'),
            },

        ]
    }
    ''''"l_box": url_for('now', time=timecode),
    #"l_list": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('list', time=timecode)
    "l_sindin": url_for('signin'), # url_for('sindin', time=timecode)
    "l_about": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # url_for('sindin', time=timecode)
    '''
    return render_template('index.html', data=date)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try:
        auth = json.loads(readStorage('auth.json'))
    except Exception as e:
        print(e)
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
        "name": 'Вход',
        "way": url_for('check'),
        "error": ""
    }
    # res = make_response("Setting a cookie")
    # res.set_cookie('token', '', max_age=30)

    if request.args.get('error', ''):
        if request.args.get('error', '') == 'LoginWrong': date['error'] = 'Неверный пароль или логин'

    return render_template('signin.html', data=date)

@app.route('/check', methods=['GET', 'POST'])
def check():
    try:
        auth = json.loads(readStorage('auth.json'))
    except Exception as e:
        print(e)
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
        return redirect(url_for('signin', error='LoginWrong'))

    else:
        response = requests.get(request.args.get('photo', ''))
        if response.status_code == 200:
            with open(pwd + "photos/time.png", 'wb') as f:
                f.write(response.content)
        return redirect(url_for('signup', hash=request.args.get('hash', ''), uid=request.args.get('uid', ''),
                                name=request.args.get('first_name', ''),
                                surname=request.args.get('last_name', ''),
                                photo=str(request.args.get('photo', ''))))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        auth = json.loads(readStorage('auth.json'))
    except Exception as e:
        print(e)
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.method == 'POST':
        idl = str(uuid4())
        while (idl in auth['accounts']): idl = str(uuid4())
        auth['vkHash'][request.args.get('hash', '')] = idl
        auth['accounts'][idl] = {
            "img": request.args.get('photo', '').replace('amp;', '&'),
            "name": request.args.get('name', ''),
            "surname": request.args.get('surname', ''),
            "hash": request.args.get('hash', ''),
            "uid": request.args.get('uid', ''),
            "login": request.form['login'],
            "password": request.form['password']
        }

        writeStorage(json.dumps(auth, ensure_ascii=False), 'auth.json')
        res = make_response(redirect(url_for('dashboard')))
        res.set_cookie('log', idl, max_age=60 * 60 * 24 * 7)
        return res

    elif request.cookies.get('log') in auth['accounts']:
        return redirect(url_for('check'))

    else:
        data = {
            "img": request.args.get('photo', ''),
            "name": request.args.get('name', ''),
            "surname": request.args.get('surname', ''),
            "hash": request.args.get('hash', ''),
            "uid": request.args.get('uid', '')
        }
        return render_template('signup.html', data=data)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        auth = json.loads(readStorage('auth.json'))
    except Exception as e:
        print(e)
        return '<h1>Error UNDEFINED</h1><hr>\
    <p>Пиши Alph-е, т.к. это значит доступа к данным акков не возможно получить!</p>'

    if request.cookies.get('log') in auth['accounts']:
        data = auth['accounts'][request.cookies.get('log')]
        return render_template('room.html', data=data)
    else:
        res = make_response(redirect(url_for('signin')))
        res.set_cookie('log', '', max_age=0)
        return res

@app.route('/dashboard/file', methods=['GET', 'POST'])
def file():
    try:
        auth = json.loads(readStorage('auth.json'))
    except Exception as e:
        print(e)
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
                    except Exception as e:
                        return f'<p><h1 style="color:red;">Check your file</h1></p><p>{e} - {str(e)}</p><p><a href="{request.url}">Back</a></p>'
                    else:
                        writeStorage(json.dumps(data, ensure_ascii=False), 'solo.json')
                        return f'<p><h1>fine! you loaded it!</h1></p<p><a href="{url_for("index")}">Back</a></p>'
                return redirect(url_for('index'))
        else:
            return f'<h3>Upload file(s) at server</h3><form enctype="multipart/form-data" method="POST">\
<p><input type="file" name="file" required title="Upload..."></p><p><a href="{url_for("index")}">Back</a>\
 <input type="submit" value="Load"></p> </form>'
    else:
        return redirect(url_for('index'))

@app.route('/now', methods=['GET'])
def now():
    deadline = datetime.datetime.combine(datetime.date.today(), datetime.datetime.now().time())
    date = {
        "day": str(deadline.strftime("%d.%m.%Y")),
        "name": prefixWeek(deadline),
        "-": url_for('hello', time=int((deadline + datetime.timedelta(days=-1)).timestamp())),
        "+": url_for('hello', time=int((deadline + datetime.timedelta(days=1)).timestamp())),
        "way": "?time=" + str(int((deadline).timestamp())),
        'les': [],
        'textTime': (f"Сегодня" if deadline.date() == datetime.datetime.today().date() else (f"В буд\
ущем на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней" if deadline > datetime.datetime \
                                                                                             .today() else f"В прошлом \
на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней"))
    }

    page = json.loads(readStorage(f'solo.json'))
    ids = []
    for i in page['week'][deadline.strftime("%a").lower()]:
        idL = None
        while (idL in ids or idL == None): idL = randint(0, 10000)
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
            if i['weekType'] == 0 or (i['weekType'] == 1 and bool(deadline.isocalendar()[1] % 2)) or \
                    (i['weekType'] == 2 and not bool(deadline.isocalendar()[1] % 2)):
                date['les'].append(d)
        else:
            date['les'].append(d)

    if deadline.strftime("%d.%m.%Y") in page['other']:
        for i in page['other'][deadline.strftime("%d.%m.%Y")]:
            idL = None
            while (idL in ids or idL == None): idL = randint(0, 10000)
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

@app.route('/aboutus', methods=['GET'])
def aboutus():
    deadline = datetime.datetime.today()
    date = {
        "day": str(deadline.strftime("%d.%m.%Y")),
        "name": "О проекте",
        "way": "?time=" + str(int((deadline).timestamp())),
    }
    args = list(request.args)
    date['img'] = (url_for('static', filename='smile.png') if 'author' not in args else url_for(\
        'static', filename='author.jpg'))
    date['title'] = ({"author":"AlphaSTE","commits":"Commits"}[args[0]] if len(args) else "TimeBox")
    date['subname'] = ({"author":"О авторе","commits":"Commits"}[args[0]] if len(args) else "Добро пожаловать!")
    date['links'] = [
        {"name":"Github","link":"https://github.com/AlphaO612"},
        {"name":"Vk.com","link":"https://vk.com/aao2014"},
        {"name":"Commits","link":url_for('aboutus', commits=0)},
        {"name":"О проекте","link":url_for('aboutus')},
        {"name":"О создателе","link":url_for('aboutus', author=0)},]
    date['links'].remove(date['links'][{"author":4,"commits":2}[args[0]] if len(args) else 3])
    if 'commits' in args:
        date['commits'] = []
        info = requests.get("https://api.github.com/repos/alphao612/TimeBox/commits").json()
        for i in info: date['commits'].append({
            "author":i['commit']['author']['name'],
            "date": i['commit']['author']['date'],
            "name": i['commit']['message'].replace("\n","</div><div>"),
        })
    if 'author' in args: date["text"] = \
"""Создал сие проект - я, Иванов Андрей!
Человек, который говорит, что умеет программировать, но у него всегда всё с проблемами)))
Учусь сейчас в МПГУ на прикладную информатику, также параллельно работаю над двумя активными проектами: TimeBox и ApiAlpha. 
Также обожаю аниме и мангу... и Komi-san!
Для вопросов, предложений и багов мой вк всегда открыт!
Удачки!"""
    else: date["text"] =\
"""TimeBox - проект, который был создан ещё мною во время конце карантина у меня в 10 классом в качестве единой альтернативной неофициальной площадки для получения расписания, оценок. Она должна была заменить edu.tatar.ru, но проект лишь увидел свет во время поступления в МПГУ!
Причиной его появления для меня стало ужастное лично для меня отображения расписания, по сраавнению с другими университетами моих друзей.
Пока проектом занимаюсь лишь я, но надеюсь данный проект станет чуть больше, чем любительский... 
Ага, конечно!)))))))"""

    return render_template('aboutus.html', data=date)

@app.route('/box', methods=['GET'])
def hello():
    if request.args.get('time', ''):
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))
        minus = (deadline + datetime.timedelta(days=-1)).date() != datetime.datetime.today().date()
        plus = (deadline + datetime.timedelta(days=1)).date() != datetime.datetime.today().date()

        print(deadline.day)
        print(deadline.month)
        print(deadline.year)

        date = {
            "day": str(deadline.strftime("%d.%m.%Y")),
            "now": deadline.date() != datetime.datetime.today().date(),
            "name": prefixWeek(deadline),
            "-": (url_for('hello', time=int((deadline + datetime.timedelta(days=-1)) \
                                            .timestamp())) if minus else url_for('now')),
            "+": (url_for('hello', time=int((deadline + datetime.timedelta(days=1)) \
                                            .timestamp())) if plus else url_for('now')),
            "way": "?time=" + request.args.get('time', ''),
            'les': [],
            'textTime': (f"Сегодня" if deadline.date() == datetime.datetime.today().date() else (f"В буд\
ущем на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней" if deadline > datetime.datetime \
                                                                                            .today() else f"В прошлом \
на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней"))
        }

        page = json.loads(readStorage(f'solo.json'))
        ids = []
        for i in page['week'][deadline.strftime("%a").lower()]:
            idL = None
            while (idL in ids or idL == None): idL = randint(0, 10000)
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
                if i['weekType'] == 0 or (i['weekType'] == 1 and bool(deadline.isocalendar()[1] % 2)) or \
                        (i['weekType'] == 2 and not bool(deadline.isocalendar()[1] % 2)):
                    date['les'].append(d)
            else:
                date['les'].append(d)

        if deadline.strftime("%d.%m.%Y") in page['other']:
            for i in page['other'][deadline.strftime("%d.%m.%Y")]:
                idL = None
                while (idL in ids or idL == None): idL = randint(0, 10000)
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
        deadline = now
        print(deadline)
        deadline = int(deadline.timestamp())
        return redirect(url_for('hello', time=deadline))

@app.route('/calendar', methods=['GET'])
def calendar():
    if request.args.get('time', ''):
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))
        minus = (deadline + relativedelta(months=-1)).date() != datetime.datetime.today().date()
        plus = (deadline + relativedelta(months=1)).date() != datetime.datetime.today().date()
        nowDate = datetime.datetime.today()
        date = {
            "day": str(deadline.strftime("%m.%Y")),
            "now": deadline.date() != datetime.datetime.today().date(),
            "name": "Календарь",
            "title": deadline.strftime("%B"),
            "-": (url_for('calendar', time=int((deadline + relativedelta(months=-1)) \
                                               .timestamp())) if minus else url_for('calendar')),
            "+": (url_for('calendar', time=int((deadline + relativedelta(months=1)) \
                                               .timestamp())) if plus else url_for('calendar')),
            "way": "?time=" + request.args.get('time', ''),
            'month': [],
            'textTime': (f"Сегодня" if deadline.date() == datetime.datetime.today().date() else (f"В буд\
ущем на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней" if deadline > datetime.datetime \
                                                                                        .today() else f"В прошлом \
на {abs((deadline.date() - datetime.datetime.today().date()).days)} дней"))
        }

        day = 0
        for a in range(6):
            date['month'].append([])
            for i in range(7):
                mainDate = datetime.date(deadline.year, deadline.month, 1)
                if list(lib).index(mainDate.strftime("%a").lower()) > i + (a * 7) or day >= last_day_of_month(deadline):
                    date['month'][a].append({"on": False})
                else:
                    day += 1
                    date['month'][a].append({
                        "on": True,
                        "name": day,
                        "color": (
                            "background: rgb(201 112 227);color: #fff;" if day == nowDate.day and deadline.month == datetime.datetime.today().month and deadline.year == datetime.datetime.today().year else ""),
                        "link": url_for('hello', time=int(datetime.datetime(mainDate.year, mainDate.month, day) \
                                                          .timestamp()))})

        return render_template('calendar.html', data=date)
    else:
        today = datetime.date.today()
        moment = datetime.datetime.now().time()
        deadline = int(datetime.datetime.combine(today, moment).timestamp())
        return redirect(url_for('calendar', time=deadline))

@app.route('/lesson/<name>', methods=['GET'])
def les(name=None):
    if request.args.get('time', '') and name:
        deadline = datetime.datetime.fromtimestamp(int(request.args.get('time', '')))

        date = {
            "day": str(deadline.strftime("%d.%m.%Y")),
            "name": lib[deadline.strftime("%a").lower()],
            "-": url_for('les', time=int((deadline + datetime.timedelta(days=-1)).timestamp()), name=name),
            "+": url_for('les', time=int((deadline + datetime.timedelta(days=1)).timestamp()), name=name)
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
        info = {
            "lesson": name,
            "text": text,
            "files": files,
        }

        return render_template('lesson.html', data=date, info=info)
    else:
        today = datetime.date.today()
        moment = datetime.datetime.now().time()
        now = datetime.datetime.combine(today, moment)
        deadline = now + datetime.timedelta(days=1)
        print(deadline)
        deadline = int(deadline.timestamp())
        return redirect(url_for('les', name=name, time=deadline))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
