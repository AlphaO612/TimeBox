import PySimpleGUI as sg
import json, datetime, calendar, traceback

def writeStorage(set, name):
    f = open(name, mode='w', encoding="utf-8")
    f.write(set)
    f.close()

def readStorage(name):
    import codecs
    with codecs.open(name, 'r', encoding='utf-8',
                     errors='ignore') as f:
        # f = open(pwd + name, 'r')
        set = f.read()
        f.close()
    return set

lib = {
	"mon": "понедельник",
	"tue": "вторник",
	"wed": "среда",
	"thu": "четверг",
	"fri": "пятница",
	"sat": "суббота",
	"sun": "воскресенье",
}

times = [['9:00', '10:30'],
         ['10:40','12:10'],
         ['12:40','14:10'],
         ['14:20','15:50']
         ]

namesT = ['Маренич Е.Е.',
          'Шилин И.А.',
          'Быкова О.Н.',
          'Федотенко М.А.',
          'Кашпарова В.С.',
          'Иванова Н.Ю.',
          'Тисовский А.Г',
          'Пожилов Д.М.',
          'Шаповалов М.И',
          'Кашпарова В.С.',
          'Курбангалеева М.Р.',
          'Маняхина В.Г.',
          'Марченкова Н.П.'
]

types = ['Лекция', 'Сессия', 'Практика']

data = {
    'week':{
        "mon":[],
        "tue":[],
        "wed":[],
        "thu":[],
        "fri":[],
        "sat":[],
        "sun":[],
    },
    'other':{},
    'lessons':[],
    'teachers':[*namesT],
}

### Data для хранения в ежедневном расписание
#{
#    'name': 'test',
#    'time': {
#        "mon": ['9:00','12:00'],
#        #Если неn его в этот день - не пиши этот день
#        "wed": ['9:00','12:00'],
#        "thu": ['9:00','12:00'],
#        "fri": ['9:00','12:00'],
#        "sat": ['9:00','12:00'],
#        "sun": ['9:00','12:00'],
#    },
#    'teacher': 'Маренич Е. Е.',
#    'info': 'https://nbb.mpgu.su' # Если что вместо ссылки можно писать доп инфу или Аудиторию! хы
#}
### Data для хранения в индивидуальных днях
#'04.09.2021': [{
#    'name': 'test',
#    'time': ['9:00','12:00'],
#    'teacher': 'Маренич Е. Е.',
#    'info': 'https://nbb.mpgu.su' # Если что вместо ссылки можно писать доп инфу или Аудиторию! хы
#},]
#

layout1 = [[sg.Listbox([f'00.00.0000 {lib[i]}' for i in list(data['week'])], size=(22, 28), auto_size_text=True,
                       select_mode=sg.SELECT_MODE_SINGLE, enable_events=True, key='-L-')],
           [sg.Button('Copy', key='-copyDay-'),sg.Button('Paste', key='-pasteDay-'),sg.Button('X', key='-deleteDay-')]]

tabs = [[
        [sg.Text('Название:*')],
        [sg.Input(default_text="Тест", size=(22,None), enable_events=True, key='-nameLes-')],

        [sg.Text('Начало:*')],
        [sg.Spin(values=list(range(0, 23+1)), initial_value=9, size=(2, None),
                 enable_events=True, key='-hSt-'),
         sg.Text(':'),
         sg.Spin(values=list(range(0, 59 + 1)), initial_value=0, size=(2, None),
                 enable_events=True, key='-mSt-')],

        [sg.Text('Конец:*')],
        [sg.Spin(values=list(range(0, 23+1)), initial_value=12, size=(2, None),
                 enable_events=True, key='-hEn-'),
         sg.Text(':'),
         sg.Spin(values=list(range(0, 59 + 1)), initial_value=40, size=(2, None),
                 enable_events=True, key='-mEn-')],

        [sg.Text('Преподаватель:*')],
        [sg.Combo(namesT, size=(20, None), default_value=namesT[0], key='-teacher-')],
        [sg.Button('Добавить в виде паттерна', key='-like-')],
        [sg.Button('Добавить', key='-addLes-'), sg.Button('Изменить', key='-editLes-')]
    ],
    [[sg.Text('Название пары:')],
     [sg.Combo(['---' , *[i['name'] for i in data['lessons']]], default_value='---',
               size=(22,None), enable_events=True, key='-lesLIST-')],
     [sg.Text('Временной промежуток:')],
     [sg.Combo([f"{i[0]}-{i[1]}" for i in times], default_value=[f"{i[0]}-{i[1]}" for i in times][0],
               size=(22, None), enable_events=True, key='-timeLIST-')],
     [sg.Text('Преподаватели:')],
     [sg.Combo(namesT, size=(20, None), enable_events=True, default_value=namesT[0], key='-teacherLIST-'),
      sg.Button('+', key='-addTeacher-')],
     [sg.Listbox([], size=(20, 4), enable_events=True, select_mode=sg.SELECT_MODE_SINGLE, key='-teacherText-'),
      sg.Button('-', key='-delTeacher-')],
     [sg.Button('Добавить', key='-addLes1-')]

]]

layout2 = [[sg.Frame('Пара', [
                         [sg.TabGroup([[sg.Tab('Главная', tabs[0],
                                               tooltip='Место, где вы можете настраивать каждую мелочь'),
                                        sg.Tab('Помощь', tabs[1])]], tooltip='Место, где добавить пару легко')],
                         [sg.Text('Тип пары:')],
                         [sg.Combo(types, default_value=types[0],
                                   size=(22, None), enable_events=True, key='-lesType-')],
                         [sg.Text('Дополнительная инфа:')],
                         [sg.Input(default_text="https://nbb.mpgu.su", size=(22, None), enable_events=True, key='-info-')],
                     ])],
           # При нажатии любой кнопки спрашивать в недельное или разовое повторение
           [sg.Frame('День', [
               [sg.Text('Дата:*')],
               [sg.Spin(values=list(range(1, calendar.mdays[datetime.date.today().month]+1)),
                        initial_value=datetime.date.today().day,
                        size=(3, None), enable_events=True, key='day'),
                sg.Spin(values=list(range(datetime.date.today().month, 12 + 1)),
                        initial_value=datetime.date.today().month,
                        size=(3, None), enable_events=True, key='month'),
                sg.Spin(values=list(range(datetime.date.today().year, datetime.date.today().year + 12)),
                        initial_value=datetime.date.today().year,
                        size=(5, None), enable_events=True, key='year'),],
               [sg.Button('Добавить', key='-addDay-'),sg.Button('Изменить', key='-editDay-')]])],]

layout3 = [[sg.Text(f' --.--.---- -/-',
                    font='Arial 19 bold', key='-datatable-')],
           [sg.Listbox([], size=(50, 27), auto_size_text=True,
                       select_mode=sg.SELECT_MODE_SINGLE, enable_events=True, key='-R-')],
           [sg.Button('Copy', key='-copyLes-'),
            sg.Button('Paste', key='-pasteLes-'),
            sg.Button('X', key='-deleteLes-'), sg.Text('---', key='type')]]

menus = [['&File', ['&New file', '&Open', '&Save', 'Save &As']]]

layout = [[sg.Menu(menus, tearoff=True, pad=(200, 1))],
          [sg.Column(layout1, key='-COL1-'),
           sg.Column(layout2, key='-COL2-'),
           sg.Column(layout3, key='-COL3-',)]]


window = sg.Window('Генератор расписания', layout, size=(758, 570), use_default_focus=False, finalize=True)

unchange = False
datSel = None

def DayList():
    gg = []
    for i in list(data['other']):
        gg.append(f"""{datetime.datetime.strptime(i, '%d.%m.%Y').strftime('%d.%m.%Y')} \
{lib[datetime.datetime.strptime(i, '%d.%m.%Y').strftime('%a').lower()]}""")
    gg.sort()
    return [*[f'00.00.0000 {lib[i]}' for i in list(lib)], *gg]

def dialog():
    window = sg.Window('Укажите тип', [
        [sg.T('Какого типа пара')],
        [sg.Radio('В любой неделе', 'type', default=True)],
        [sg.Radio('На чётной неделе', 'type')],
        [sg.Radio('На нечётной неделе', 'type')],
        [sg.Button('Подтвердить', key='accept')],
    ], size=(300, 150), use_default_focus=False, finalize=True)
    while True:
        try:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                return None
            if event == 'accept':
                for i in list(values):
                    if values[i]:
                        return i
        except Exception as e:
            sg.PopupScrolled(
                "Пожалуйста, проверьте корректность заполнения полей!\n" +
                f"-------------------------------\n{e}\n****************\n{traceback.format_exc()}"
            )

    window.close()

def UpdR():
    l = []
    for i in datSel:
        if 'weekType' in i:
            if i['weekType'] == 0: g = '*'
            elif i['weekType'] == 1: g = 'чёт'
            elif i['weekType'] == 2: g = 'нечёт'
        else: g = '*'
        l.append(f"{i['time'][0]} - {i['time'][1]} | {i['name']} | {g}")
    window['-R-'].Update(l)

def UpdL():
    value = DayList()
    window['-L-'].Update(value)

last = []
value = None
filename=None

window.bind('<Control-n>', 'New file')
window.bind('<Control-o>', 'Open')
window.bind('<Control-s>', 'Save')
window.bind('<Control-f>', 'Save As')

while True:
    try:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break

        if event == '-lesLIST-':
            for i in data['lessons']:
                if i['name'] in window['-lesLIST-'].get():
                    window['-teacherText-'].Update(values=i['teacher'])
                    window['-info-'].Update(i['info'])

        if event == '-addTeacher-':
            if window['-teacherLIST-'].get() not in window['-teacherText-'].get_list_values():
                window['-teacherText-'].Update(
                    values=window['-teacherText-'].get_list_values()+[window['-teacherLIST-'].get()])

        if event == '-delTeacher-':
            if values['-teacherText-'] != []:
                g = window['-teacherText-'].get_list_values()
                g.remove(values['-teacherText-'][0])
                window['-teacherText-'].Update(values=g)
            else:
                sg.popup_error('Выбери препода на удаление!')

        if event == '-like-':
            if sg.popup_yes_no('Ты уверен, что хочешь сохранить, как предмет повторяющийся?') == "Yes":
                if 'lessons' not in data: data['lessons']=[]
                inde = None
                for i in data['lessons']:
                    if window['-nameLes-'].get() in i['name'] or i['name'] in window['-nameLes-'].get():
                        inde = i
                        break
                if inde:
                    if sg.popup_yes_no('Такой предмет уже есть в реестре! Его изменить?') == "Yes":
                        data['lessons'].remove(inde)
                        data['lessons'].append({"name": window['-nameLes-'].get(),
                                                "teacher": window['-teacher-'].get().split('/'),
                                                "info": window['-info-'].get()})
                else:
                    data['lessons'].append({"name": window['-nameLes-'].get(),
                                            "teacher": window['-teacher-'].get().split('/'),
                                            "info": window['-info-'].get()})
                for i in window['-teacher-'].get().split('/'):
                    if i not in data['teachers']: data['teachers'] += [i]

                for a in window['-teacher-'].get().split('/'):
                    tex = False
                    for i in data['teachers']:
                        if a.split()[0] in i:
                            tex = True
                            break
                    if not tex:
                        data['teachers'] += [i]

                window['-lesLIST-'].Update(values=[i['name'] for i in data['lessons']])
                window['-teacherLIST-'].Update(values=[i for i in data['teachers']],
                                               value=window['-teacherLIST-'].get())
                window['-teacher-'].Update(values=[i for i in data['teachers']],
                                           value=window['-teacher-'].get())

        if event == '-addDay-':
            name = datetime.datetime.strptime(f"{window['day'].get()}.{window['month'].get()}.{window['year'].get()}",
                                              '%d.%m.%Y').strftime('%d.%m.%Y')
            data['other'][name] = []
            UpdL()

        if event == '-deleteDay-':
            g = values['-L-']
            for i in ['00.00.0000 понедельник', '00.00.0000 вторник', '00.00.0000 среда', '00.00.0000 четверг',
                      '00.00.0000 пятница', '00.00.0000 суббота', '00.00.0000 воскресенье']:
                if i in g: g.remove(i);
            if g:
                for i in g:
                    print(i.split()[0])
                    data['other'].pop(i.split()[0])
                UpdL()

        if event == '-editDay-':
            g = values['-L-']
            for i in ['00.00.0000 понедельник', '00.00.0000 вторник', '00.00.0000 среда', '00.00.0000 четверг',
                      '00.00.0000 пятница', '00.00.0000 суббота', '00.00.0000 воскресенье']:
                if i in g: g.remove(i);
            if len(g) >1 or len(g) < 1: sg.popup_error('Нужно выбрать лишь один День!')
            else:
                name = datetime.datetime.strptime(f"{window['day'].get()}.{window['month'].get()}.{window['year'].get()}",
                                                  '%d.%m.%Y').strftime('%d.%m.%Y')
                data['other'][name] = data['other'][g[0].split()[0]]
                data['other'].pop(g[0].split()[0])
                UpdL()

        if '-addLes' in event:
            if len(window['-L-'].get()) == 1:
                typ = dialog()
                if typ != None:
                    if '1' in event:
                        g = window['-teacherText-'].get_list_values()[0]
                        for i in window['-teacherText-'].get_list_values():
                            if i not in g: g = g + f'/{i}'
                        datSel.append({
                            'name': window['-lesLIST-'].get() + f' ({window["-lesType-"].get()})',
                            'time': window['-timeLIST-'].get().split('-'),
                            'teacher': g,
                            'info': window['-info-'].get(),
                            'weekType': typ
                        })
                    else:
                        datSel.append({
                            'name': window['-nameLes-'].get(),
                            'time': [f"{window['-hSt-'].get()}:{window['-mSt-'].get()}",
                                     f"{window['-hEn-'].get()}:{window['-mEn-'].get()}"],
                            'teacher': window['-teacher-'].get(),
                            'info': window['-info-'].get(),
                            'weekType': typ
                        })
                    UpdR()
                    last = window['-R-'].get()
            else:
                sg.popup_error('Нужно выбрать лишь один День!')

        if event == '-editLes-':
            value = DayList()

            typ = dialog()
            if typ != None:
                for i in datSel:
                    if i['time'] == last[0].split(' | ')[0].split(' - ') and i['name'] == last[0].split(' | ')[1]:
                        datSel[datSel.index(i)] = {
                            'name': window['-nameLes-'].get(),
                            'time': [f"{window['-hSt-'].get()}:{window['-mSt-'].get()}",
                                     f"{window['-hEn-'].get()}:{window['-mEn-'].get()}"],
                            'teacher': window['-teacher-'].get(),
                            'info': window['-info-'].get(),
                            'weekType': typ
                        }
                        break
            UpdR()

        if event == '-deleteLes-':
            if last != []:
                for i in datSel:
                    if i['time'] == last[0].split(' | ')[0].split(' - ') and i['name'] == last[0].split(' | ')[1]:
                        datSel.remove(i)
                        break
            UpdR()

        if event == 'Open':
            if filename or filename=='':
                if sg.popup_yes_no('А вам тот файл нафиг не нужен?') == "Yes":
                    filename = sg.popup_get_file('file to open', file_types = (('Json', '*.json'),), no_window=True)
                    data = json.loads(readStorage(filename))
                    UpdL()
            else:
                filename = sg.popup_get_file('file to open', file_types=(('Json', '*.json'),), no_window=True)
                data = json.loads(readStorage(filename))
                UpdL()
            if 'lessons' not in data: data['lessons'] = []
            if 'teachers' not in data: data['teachers'] = namesT

            window['-lesLIST-'].Update(values=[i['name'] for i in data['lessons']])
            window['-teacherLIST-'].Update(values=[i for i in data['teachers']],
                                       value=window['-teacherLIST-'].get())
            window['-teacher-'].Update(values=[i for i in data['teachers']],
                                       value=window['-teacher-'].get())

        if event == 'Save':
            if not filename or filename == '':
                filename = sg.popup_get_file('file to save', save_as=True, file_types = (('Json', '*.json'),), no_window=True)
            writeStorage(json.dumps(data, ensure_ascii=False),filename)
            #sg.PopupScrolled(json.dumps(data, ensure_ascii=False))

        if event == 'Save As':
            filename = sg.popup_get_file('file to save', save_as=True,
                                         file_types=(('Json', '*.json'),), no_window=True)
            writeStorage(json.dumps(data, ensure_ascii=False), filename)
            #sg.PopupScrolled(json.dumps(data, ensure_ascii=False))

        if event == 'New file':
            if filename or filename == '':
                if sg.popup_yes_no('А вам тот файл нафиг не нужен?') == "Yes":
                    data = {
                        'week': {
                            "mon": [],
                            "tue": [],
                            "wed": [],
                            "thu": [],
                            "fri": [],
                            "sat": [],
                            "sun": [],
                        },
                        'other':{},
                        'lessons':[],
                        'teachers':[*namesT],
                    }
                    window['-R-'].Update(values=[])
                    UpdL()
                    filename=None
            else:
                data = {
                    'week': {
                        "mon": [],
                        "tue": [],
                        "wed": [],
                        "thu": [],
                        "fri": [],
                        "sat": [],
                        "sun": [],
                    },
                    'other':{},
                    'lessons':[],
                    'teachers':[*namesT],
                }
                window['-R-'].Update(values=[])
                UpdL()
                filename = None

        if event == '-copyDay-' and value:
                if unchange: sg.PopupScrolled(json.dumps({
                    list(lib)[list(window.Element('-L-').Widget.curselection())[0]]: data['week'][list(lib)[
                        list(window.Element('-L-').Widget.curselection())[0]]]}, ensure_ascii=False))
                else: sg.PopupScrolled(json.dumps({
                    value[list(window.Element('-L-').Widget.curselection())[0]].split()[0]: data['other'][
                        value[list(window.Element('-L-').Widget.curselection())[0]].split()[0]]},
                    ensure_ascii=False))

        if event == '-copyLes-' and last:
            for i in datSel:
                if i['time'] == last[0].split(' | ')[0].split(' - ') and i['name'] == last[0].split(' | ')[1]:
                    sg.PopupScrolled(json.dumps(i, ensure_ascii=False))
                    break

        if event == '-pasteDay-':
            try:
                js = json.loads(sg.PopupGetText(message='Paste here JSON code'))
                if list(js)[0][0].isdigit() and list(js)[0] in data['other']:
                    data['other'][list(js)[0]] = data['other'][list(js)[0]] + js[list(js)[0]]
                elif list(js)[0][0].isdigit() and not list(js)[0] in data['other']:
                    data['other'][list(js)[0]] = js[list(js)[0]]
                else: data['week'][list(js)[0]] = data['week'][list(js)[0]] + js[list(js)[0]]
                UpdL()
            except: sg.PopupError('Wrong code')

        if event == '-pasteLes-' and datSel != None:
            try:
                js = json.loads(sg.PopupGetText(message='Paste here JSON code'))
                datSel.append(js)
            except: sg.PopupError('Wrong code')

        if len(list(window.Element('-L-').Widget.curselection())) == 1:
            value = DayList()
            if list(window.Element('-L-').Widget.curselection())[0] <= 6:
                datSel, unchange = data['week'][list(lib)[list(window.Element('-L-').Widget.curselection())[0]]], True
            else:
                datSel, unchange = data['other'][value[list(
                    window.Element('-L-').Widget.curselection())[0]].split()[0]], False
            UpdR()
            name = value[list(window.Element('-L-').Widget.curselection())[0]]
            window['-datatable-'].Update(value=f" {name}")

        if last != values['-R-'] and values['-R-'] != []:
            value = DayList()
            for i in datSel:
                if i['time'] == values['-R-'][0].split(
                        ' | ')[0].split(' - ') and i['name'] == values['-R-'][0].split(' | ')[1]:
                    window['-nameLes-'].Update(value=i['name'])
                    window['-hSt-'].Update(value=i['time'][0].split(':')[0])
                    window['-mSt-'].Update(value=i['time'][0].split(':')[1])
                    window['-hEn-'].Update(value=i['time'][1].split(':')[0])
                    window['-mEn-'].Update(value=i['time'][1].split(':')[1])
                    window['-teacher-'].Update(value=i['teacher'])
                    window['-info-'].Update(value=i['info'])
                    if 'weekType' in i:
                        if i['weekType'] == 0: g = '*'
                        elif i['weekType'] == 1: g = 'чёт'
                        elif i['weekType'] == 2: g = 'нечёт'
                        window['type'].Update(value=g)
                    else: window['type'].Update(value='*')
                    break
            if values['-R-'] != []: last = values['-R-']
    except Exception as e:
        sg.PopupScrolled(
            "Пожалуйста, проверьте корректность заполнения полей!\n" +
            f"-------------------------------\n{e}\n****************\n{traceback.format_exc()}"
        )

window.close()
