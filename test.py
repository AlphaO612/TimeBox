#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response
from dateutil.relativedelta import *
from uuid import uuid4
from random import randint
from time import sleep
import datetime, json, os, codecs, requests

pwd = '/root/TimeBox/' if os.name == 'posix' else ''

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


mainData = json.loads(readStorage("auth.json"))


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return (next_month - datetime.timedelta(days=next_month.day)).day


def prefixWeek(deadline): return lib[deadline.strftime(
    "%a").lower()] + f" ({'не чётная' if bool(deadline.isocalendar()[1] % 2) else 'чётная'})"


def genTimeToken(typeInput: str, userData: dict, params: dict):
    auth = json.loads(readStorage("auth.json"))

    if "timeToken" not in auth: auth["timeToken"] = []
    token = {
        "type": typeInput,
        "uid": userData['uid'],
        "time": int(datetime.datetime.today().timestamp()),  # на час отличается - минусуй!
        "hash": userData['hash'],
        "token": randint(100000, 1000000)
    }

    token = {**params, **token}

    for i in auth["timeToken"]:
        if i['uid'] == auth['accounts'][request.cookies.get('log')]['uid'] and i['type'] == typeInput:
            auth["timeToken"].remove(i)
    for i in auth['accounts'][request.cookies.get('log')]['timeToken']:
        if typeInput in i:
            auth['accounts'][request.cookies.get('log')]['timeToken'].remove(i)

    auth["timeToken"].append(token)
    auth['accounts'][request.cookies.get('log')]['timeToken'].append(token)

    writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")
    return token['token']


def extractInfo(data):
    if 'content' in data['pattern'][data['id']]:
        items = data['pattern'][data['id']]['content']['items']
        for item in items:
            for line in list(item['content']):
                if line != "name":
                    try:
                        if type(item['content'][line]) == dict:
                            array = item['content'][line]['value']
                        else:
                            array = item['content']['value']
                    except:
                        pass
                    else:
                        array = array.split("<#>")
                        if "-@" in array[0] and len(array) > 1:
                            array[0] = array[0].replace("-@", "")
                            path = array[0].split("|")
                            lastElement = path[len(path) - 1].split("->")
                            try:
                                info = data
                                for i in range(len(path) - 1): info = info[path[i]]
                            except:
                                raise RuntimeError(f'Неправильно указали путь, либо его не существует - {str(path)}')
                            else:
                                part = (
                                    item['content'][line] if type(item['content'][line]) == dict else item['content'])
                                if len(lastElement) > 1:
                                    element = lastElement[1].split("/")
                                    part['value'] = str(element[0] if info[lastElement[0]] else element[1])
                                else:
                                    part['value'] = str(info[lastElement[0]]) + array[1]
    return data


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = pwd + "downloadFiles"


@app.route('/favicon.ico', methods=['GET'])
def icons():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route("/upload/<path:name>")
def download_file(name):
    auth = json.loads(readStorage('auth.json'))
    if request.cookies.get('log') in auth['accounts']:
        if auth['accounts'][request.cookies.get('log')]['statusTimeBox']:
            if "solo.json" in name:
                way = pwd
            else:
                way = app.config['UPLOAD_FOLDER']
            print(way)
            return send_from_directory(way, name, as_attachment=True)
    return redirect(url_for("index"))


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    return render_template('wait.html')

@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(403)
def page_error(e):
    return render_template('gen.html', data={"pattern": json.loads(readStorage("templates/dashboard.json")),
                                             "list": [],
                                             "profile": False,
                                             "textMsg": "",
                                             'id': "error"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
