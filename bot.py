#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response
from random import randint
from time import sleep
import datetime, json, os, codecs, requests, asyncio

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


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return (next_month - datetime.timedelta(days=next_month.day)).day


def prefixWeek(deadline): return lib[deadline.strftime(
    "%a").lower()] + f" ({'не чётная' if bool(deadline.isocalendar()[1] % 2) else 'чётная'})"


class vkApi:
    def __init__(self, access_token: str, group_id: str, wait: int):
        self.token = access_token
        self.id = group_id
        self.wait = wait
        self.info = {}
        self.server = {"server": "",
                       "key": "",
                       "ts": ""}

    def upgrade(self):
        try:
            self.server = requests.get("https://api.vk.com/method/groups.getLongPollServer",
                                       params={
                                           "group_id": self.id,
                                           "access_token": self.token,
                                           "v": 5.131
                                       }).json()['response']
        except Exception as e:
            raise SyntaxError(f"Check your data(token, id, wait), maybe which one isn\'t available now: {e}")

    def update(self, tsUpd: bool):
        try:
            self.info = requests.get(f"{self.server['server']}",
                                     params={
                                         "act": "a_check",
                                         "key": self.server['key'],
                                         "ts": self.server['ts'],
                                         "wait": self.wait
                                     }).json()
            if tsUpd:
                self.server['ts'] = self.info['ts']
        except Exception as e:
            raise SyntaxError(f"Check your data(token, id, wait), maybe which one isn\'t available now: {e}")
        else:
            return True

    def readTypeEvents(self, typeEvent: str):
        result = []
        for i in self.info['updates']:
            if i['type'] == typeEvent:
                result.append(i['object'])
        return result

    def send(self, text: str, user_ids: list, **param):
        # try:
        info = requests.get(f"https://api.vk.com/method/messages.send",
                            params={**{
                                "access_token": self.token,
                                "user_ids": user_ids,
                                "message": text,
                                "random_id": 0,
                                "v": 5.131
                            }, **param}).json()
        return info
        # except Exception as e:
        #    raise SyntaxError(f"Check your data(token, id, wait), maybe which one isn\'t available now: {e}")


auth = json.loads(readStorage("auth.json"))['settings']['integration']['vk']
main = vkApi(access_token=auth['access_token'], group_id=auth['group_id'], wait=1)

main.upgrade()

buttons = {
    "помощь": {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Помощь"
                    },
                    "color":"primary"
                },
                {
                    "action": {
                        "type": "open_link",
                        "link": "http://tibox.tk",
                        "label": "Зайти на сайт Tibox.tk"
                    }
                },

            ]
        ]
    },
    "подтвердить": {
        "inline": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "open_link",
                        "link": "http://tibox.tk/dashboard",
                        "label": "Зайти в личный кабинет"
                    }
                },

            ]
        ]
    },

}


async def checkMsgs():
    for i in main.readTypeEvents("message_new"):
        command = i['message']['text'].lower().split()
        content = {
            "text": "",
            "buttons": (command[0] if command[0] in buttons else "помощь")
        }
        if command[0] == "помощь":
            content['text'] = "Проверяй мои кнопки!"

        elif command[0] == "подтвердить" and len(command) > 1:
            auth = json.loads(readStorage("auth.json"))
            trigger = None
            for a in auth["timeToken"]:
                if a['uid'] == str(i['message']['from_id']):
                    trigger = a
                    account = auth['accounts'][auth["vkHash"][trigger["hash"]]]
                    if trigger in account["api"]["timeToken"]:
                        if i['message']['date'] - trigger['time'] <= 3600\
                                and trigger['type'] in account and trigger['type'] not in ["hash", "uid", "surname"]:
                            account[trigger['type']] = trigger[trigger['type']]
                            content['text'] = f"Всё прошло успешно, изменения приняты!\n Теперь ваш {trigger['type']} - {trigger[trigger['type']]}"
                        else:
                            content['text'] = "Время ожидания истекло или вы неправильно ввели код!( \nПопытайтесь ещё раз провести процедуру заново!"
                if trigger in auth['timeToken']:
                    auth['timeToken'].remove(trigger)
                if trigger in account["api"]["timeToken"]:
                    account["api"]["timeToken"].remove(trigger)
                writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")
                if trigger != None: break

            if trigger == None:
                content['text'] = "Время ожидания истекло или вы неправильно ввели код!( \nПопытайтесь ещё раз провести процедуру заново!"
        else:
            content['text'] = "Прости, но видно команда не правильно написана!"


        print(main.send(content['text'],
                  [i['message']['from_id']],
                  reply_to=i['message']['id'],
                  keyboard=json.dumps(buttons[content['buttons']], ensure_ascii=False)))

async def meetingFirst():
    for i in main.readTypeEvents("message_allow"):
        main.send("Привет!\n Я - бот TimeBox, созданный для помощи в работе с сайтом!", [i['user_id']],
                  keyboard=json.dumps(buttons['help'], ensure_ascii=False))

async def body():
    while main.update(True):
        print(main.info)
        task1 = asyncio.create_task(
            checkMsgs())
        task2 = asyncio.create_task(
            meetingFirst())
        await task1
        await task2
        sleep(1)


asyncio.run(body())
