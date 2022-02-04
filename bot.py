#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Flask, redirect, url_for, request, send_from_directory, flash, make_response
from random import randint
from uuid import uuid4
from time import sleep
import datetime, json, os, codecs, requests, asyncio, traceback

pwd = '/root/TimeBox/' if os.name == 'posix' else ''
author_id = 204987435

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
        print(json.dumps({**{
                                "access_token": self.token,
                                "user_ids": user_ids,
                                "message": text,
                                "random_id": 0,
                                "v": 5.131
                            }, **param}, ensure_ascii=False))
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
                    "color": "primary"
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
    "принять": {
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


async def checkCalls():
    content = {
        "text": "",
        "users": []
    }

    auth = json.loads(readStorage("auth.json"))
    for block in auth["timeToken"]:
        if block['type'].split("#")[0] == "@call" and "checkBot" not in block:
            content['users'] = [author_id]
            content['text'] = "Сообщение вызова\n" + "_" * 10
            for i in list(block):
                content['text'] += f"\n{i} - {block[i] if i != 'date' else datetime.datetime.fromtimestamp(block[i]).strftime('%A, %d. %B %Y %I:%M%p')}"
            print(main.send(content['text'],
                            content['users']))
            block['checkBot'] = int(datetime.datetime.today().timestamp())
            writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")


async def checkMsgs():
    for i in main.readTypeEvents("message_new"):
        auth = json.loads(readStorage("auth.json"))
        command = i['message']['text'].lower().split()
        content = {}
        if command[0] == "помощь":
            content['text'] = "Проверяй мои кнопки!"

        elif command[0] == "подтвердить" and len(command) > 1:
            trigger = None
            content['text'] = "Время ожидания истекло или вы неправильно ввели код!( \nПопытайтесь ещё раз провести процедуру заново!"
            for a in auth["timeToken"]:
                if a['uid'] == str(i['message']['from_id']):
                    trigger = a
                    account = auth['accounts'][auth["vkHash"][trigger["hash"]]]
                    if trigger in account["timeToken"]:
                        if i['message']['date'] - trigger['time'] <= 3600:
                            if trigger['type'] in account and trigger['type'] not in ["hash", "uid", "surname"]:
                                account[trigger['type']] = trigger[trigger['type']]
                                content['text'] = f"Всё прошло успешно, изменения приняты!\n Теперь ваш {trigger['type']} - {trigger[trigger['type']]}"
                        else:
                            content['text'] = "Время ожидания истекло или вы неправильно ввели код!( \nПопытайтесь ещё раз провести процедуру заново!"

                    if trigger in auth['timeToken']:
                        auth['timeToken'].remove(trigger)

                    if trigger in account["timeToken"]:
                        account["timeToken"].remove(trigger)

                writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")

        else:
            content['text'] = "Прости, но видно команда не правильно написана!"

        if i['message']['from_id'] == author_id:
            if command[0] == "список" and len(command) > 1:
                count = 0
                content['text'] = ""
                for block in auth["timeToken"]:
                    if command[1] in block['type']:
                        account = auth['accounts'][auth['vkHash'][block['hash']]]
                        content['text'] += f"\n{count + 1}. {account['name']} {account['surname']}({block['uid']})" \
                                           + "=" * 5
                        content['text'] += f"\n- Группа: {block['groupNum']} в {block['institute']} " \
                                           f"(https://vk.com/id{block['lvl']} курс)"
                        content['text'] += f"\n- Система: {block['system']}({block['systemName']})"
                        content['text'] += "\n" + "=" * 5
                        count += 1
                content['text'] = f"Список {count} человек с типом запросом \"{command[1]}\":" + content['text']
            elif command[0] == "принять" and len(command) > 3:
                for block in auth["timeToken"]:
                    block['type'] = block['type'].lower()
                    print(f"{block['type'].split('#')[1]}")
                    if command[1] == str(block['uid']) and command[2] == block['type']:
                        account = auth['accounts'][auth['vkHash'][block['hash']]]
                        main.send(f"Ваш запрос был одобрен!\nКомментарий модератора: {command[3]}", [block['uid']])
                        if block['type'].split("#")[1] == "requestmod":
                            auth['accounts'][auth['vkHash'][block['hash']]]['statusTimeBox'] = True

                            if block in auth['timeToken']:
                                auth['timeToken'].remove(block)
                            for a in auth['accounts'][auth['vkHash'][block['hash']]]["timeToken"]:
                                if block["type"] == a['type'].lower():
                                    auth['accounts'][auth['vkHash'][block['hash']]]["timeToken"].remove(a)
                            writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")

                            content['text'] = f"Отправлен и принят запрос!"

            elif command[0] == "отклонить" and len(command) > 3:
                for block in auth["timeToken"]:
                    block['type'] = block['type'].lower()
                    print(f"{block['type'].split('#')[1]}")
                    if command[1] == str(block['uid']) and command[2] == block['type']:
                        account = auth['accounts'][auth['vkHash'][block['hash']]]
                        main.send(f"Ваш запрос был отклонён!\nКомментарий модератора: {command[3]}", [block['uid']])
                        if block['type'].split("#")[1] == "requestmod":
                            auth['accounts'][auth['vkHash'][block['hash']]]['statusTimeBox'] = False
                            if block in auth['timeToken']:
                                auth['timeToken'].remove(block)
                            for a in auth['accounts'][auth['vkHash'][block['hash']]]["timeToken"]:
                                if block["type"] == a['type'].lower():
                                    auth['accounts'][auth['vkHash'][block['hash']]]["timeToken"].remove(a)
                            writeStorage(json.dumps(auth, ensure_ascii=False), "auth.json")

                            content['text'] = f"Отправлен и принят запрос!"

            elif command[0] == "пользователь" and len(command) > 2:
                for user in auth['accounts']:
                    if auth['accounts'][user]['hash'] == command[1] or auth['accounts'][user]['uid'] == command[1]:
                        content['text'] = f"Информация о {command[1]}:\n"
                        for a in auth['accounts'][user]:
                            content['text'] += f"{a} - {str(auth['accounts'][user][a])}\n"

        content['buttons'] = (command[0] if command[0] in buttons else "помощь")
        content['reply_id'] = i['message']['id']
        content['users'] = [i['message']['from_id']]

        print(main.send(content['text'],
                        content['users'],
                        reply_to=content['reply_id'],
                        keyboard=json.dumps(buttons[content['buttons']], ensure_ascii=False)))


async def meetingFirst():
    for i in main.readTypeEvents("message_allow"):
        main.send("Привет!\nЯ - бот TimeBox, созданный для помощи в работе с сайтом!", [i['user_id']],
                  keyboard=json.dumps(buttons['помощь'], ensure_ascii=False))


async def body():
    while main.update(True):
        try:
            print(main.info)
            task1 = asyncio.create_task(
                checkMsgs())
            task2 = asyncio.create_task(
                meetingFirst())
            task3 = asyncio.create_task(
                checkCalls())
            await task3
            await task1
            await task2
        except Exception as e:
            try:
                main.send(
                    f"Ошибка в боте\n-------------------------------\n{e}\n**************\n{traceback.format_exc()}",
                    [author_id])
            except:
                pass
        sleep(1)


asyncio.run(body())
