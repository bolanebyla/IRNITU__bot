import telebot
import os
import json 
import openpyxl
import config 
from openpyxl import load_workbook
from telebot.types import Message
from telebot import types



bot = telebot.TeleBot(config.TOKEN)

global BUFFER
BUFFER = {}


# /start
@bot.message_handler(commands=['start'])
def start_message(message:Message):
    bot.send_message(message.chat.id,'Привет, я IRNITU_bot!\n' + 'Проидите регистрацию')

    keyboard = types.InlineKeyboardMarkup()
    button_student = 'Студент'
    button_visitor = 'Посетитель'

    keyboard.add(types.InlineKeyboardButton(text = button_student, callback_data = 'student'))
    keyboard.add(types.InlineKeyboardButton(text = button_visitor, callback_data = 'visitor'))

    bot.send_message(message.chat.id,'Зарегистрировться как:', reply_markup = keyboard)



# Обработка ответов от чат-клавиатуры
@bot.callback_query_handler(func=lambda message:True)
def ans(message:Message):
    chat_id = message.message.chat.id

    # регистрация студента
    if message.data == 'student':
        if str(chat_id) in read():
            bot.send_message(chat_id,'Вы уже зарегистрированы!')
            return
        
        msg = bot.send_message(chat_id,'Введите ФИО (через пробел)')
        bot.register_next_step_handler(msg, ask_name)

    # Регистрация посетителя
    if message.data == 'visitor':
        if str(chat_id) in read():
            bot.send_message(chat_id,'Вы уже зарегистрированы!')
            return
        msg = bot.send_message(chat_id, 'Введите номер договора')
        bot.register_next_step_handler(msg, ask_contract)

    # Описание оборудования
    if message.data[:7] == 'info_eq':
        name =  message.data[7:-1]
        keyboard = types.InlineKeyboardMarkup()
        button = 'Свернуть описание'
        keyboard.add(types.InlineKeyboardButton(text = button, callback_data = 'close_info_eq' + name))

        bot.edit_message_text(name + info_equipment(name, 'Оборудование'), 
                              chat_id, message.message.message_id, reply_markup = keyboard)

    # Свернуть описание обоудования
    if message.data[:13] == 'close_info_eq':
        name = message.data[13:]   

        keyboard = types.InlineKeyboardMarkup()
        button = 'Описание'
        keyboard.add(types.InlineKeyboardButton(text = button, callback_data = 'info_eq' + name + '\n'))
                                                   
        bot.edit_message_text(name, chat_id, message.message.message_id, reply_markup = keyboard)
    # Кнопка израсходовать
    if message.data[:13] == 'spend_exp_mat':
        name = message.data[13:]
        global BUFFER
        if (chat_id) in BUFFER:
            bot.send_message(chat_id, 'Вы уже нажали на кнопку Израсходовать ( ' + name + ')'
                            '\nВведите количество, либо нажмите кнопку Отмена')
        else:
            
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
            btn = types.KeyboardButton('Отмена')
            markup.add(btn)
            msg = bot.send_message(chat_id, name +'\nВведите количество', reply_markup = markup)
            BUFFER[chat_id] = name
            bot.register_next_step_handler(msg, spend_kol)



# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text(message:Message):
    chat_id = message.chat.id
    # Присвоение статуса пользователю
    user_data = read()[str(chat_id)]
    if isinstance(user_data, dict):
        user_status = 'student'
    elif user_data == 'admin':
        user_status = 'admin'
    else:
        user_status = 'visitor'



       
    # Вывод списка оборудования
    if message.text == 'Оборудование':
        eq = change_BD('Оборудование')
        bot.send_message(message.chat.id, 'Список оборудования:')
        for i in range(len(eq)):
            button = 'Описание'
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text = button, callback_data = 'info_eq' + 
                                                    change_BD('Оборудование')[i]))
            bot.send_message(message.chat.id, change_BD('Оборудование')[i], reply_markup = keyboard)    
    # Вывод списка инструментов
    if message.text == 'Инструмент':
        tools = change_BD('Инструмент')
        tools_str =''
        bot.send_message(message.chat.id, 'Доступный инструмент:')
        for i in tools:
            tools_str = tools_str + i
        bot.send_message(message.chat.id, tools_str)

    # Вывод списка расходных материалов
    if message.text == 'Расходные материалы':
        eq = change_BD('Расходные материалы')

        bot.send_message(message.chat.id, 'Расходные материалы:')
        for i in range(len(eq)):
            name = change_BD('Расходные материалы')[i][:-1]
            button1 = 'Израсходовать'
            button2 = 'Отменить расходование'
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text = button1, callback_data = 'spend_exp_mat' + name))
            keyboard.add(types.InlineKeyboardButton(text = button2, callback_data = 'cancel_spend_exp_mat' + name))
            bot.send_message(message.chat.id, name + ' ' + '(доступно: ' +
                             str(exp_mat_kol(name, 'Расходные материалы')) + ' ' +
                            exp_mat_ed_izm(name, 'Расходные материалы') + ')', 
                             reply_markup = keyboard)    

    # Вывод расписания кабинета
    if message.text == 'Расписание кабинета':
        pass
    # Кнопка отмена для студентов
    if message.text == 'Отмена' and user_status == 'student':
        bot.send_message(chat_id, 'Отменено', reply_markup = keyboard_main_menu_student())
        


#--------ФУНКЦИИ---------#    

#==========Расходные материалы============#

# Возвращает количество расходного материала
def exp_mat_kol(name, kategory):
      sheet = read_BD(kategory)
      i=2
      while(True):
        
        val = sheet.cell(row = i, column = 1).value

        if str(name) == str(val):
            if sheet.cell(row = i, column = 2).value == None :
                return '0'
            else:
                return (sheet.cell(row = i, column = 2).value)
        i+=1

# Возвращает eдeницы измерения расходного материала
def exp_mat_ed_izm(name, kategory):
      sheet = read_BD(kategory)
      i=2
      while(True):
        
        val = sheet.cell(row = i, column = 1).value
        if str(name) == str(val):
            if sheet.cell(row = i, column = 2).value == None :
                return ''
            else:
                return (sheet.cell(row = i, column = 3).value)
        i+=1
 # Уменьшает кол-во рас мат
def spend_kol(message): 
    chat_id = message.chat.id
    text = message.text
    global BUFFER
    name = BUFFER[chat_id]
    print('зашло в функцию')
    print(message)

    #print(message)
    if text == 'Отмена':
        bot.send_message(chat_id, 'Отменено', reply_markup = keyboard_main_menu_student())
        del BUFFER[chat_id]
        return
    text = int(text)
    wb = load_workbook('BD.xlsx')
    sheet = wb['Расходные материалы']
    value = int(exp_mat_kol(name, 'Расходные материалы'))
    value -= text

   #(вынести в отдельную функцию)
    i=2
    while(True):
      
       val = sheet.cell(row = i, column = 1).value
       if str(name) == str(val):
           sheet.cell(row = i, column = 2).value = value
           wb.save('BD.xlsx')
           break
       i+=1
    bot.send_message(chat_id, 'Израсходовано ' + message.text, reply_markup = keyboard_main_menu_student())
    del BUFFER[chat_id]
    return

#=========================================#

#==========Оборудование============#


def info_equipment(name, kategory): # Возвращает описание оборудования
      sheet = read_BD(kategory)
      i=2
      while(True):
        
        val = sheet.cell(row = i, column = 1).value

        if str(name) == str(val):
            if sheet.cell(row = i, column = 2).value == None :
                return '\n\nОписание не найдено'
            else:
                return '\n\nОписание:\n' + sheet.cell(row = i, column = 2).value
        i+=1

#==================================#

#==========Считывание данных из базы данных============#

# Открываем BD
def read_BD(kategory):
    #wb = load_workbook(config.BD)
    wb = load_workbook('BD.xlsx')
    sheet = wb[kategory]
    return sheet 

 # Вывод списка элементов категории (возвращает список)
def change_BD(kategory):
    sheet = read_BD(kategory)
    #data = {}
    #data[kategory] = ''
    data = []
    i=2
    val = ''
    while(True):
        val = sheet.cell(row = i, column = 1).value
        if val == None:
            break
        #data[kategory] = data[kategory] + val + '\n'
        data.append(val + '\n')
        i+=1
    return data
#==================================#


#==========Регистрация пользователей============#

# Ввод номера договора (для посетителей)
def ask_contract(message):
    chat_id = message.chat.id
    text = message.text

    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Номер договора должен состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_contract)
        return
    add_user(chat_id, text)
    bot.send_message(chat_id, 'Вы успешно зарегистрировались!')


# Ввод ФИО (для студентов)
def ask_name(message):
    chat_id = message.chat.id
    text = message.text
    if text.replace(' ', '').isdigit():
        msg = bot.send_message(chat_id, 'ФИО не может состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_name)
        return
    add_user(chat_id, text, 'name')
    msg = bot.send_message(chat_id, 'Введите группу (в формате XXX-16-1)')
    bot.register_next_step_handler(msg, ask_group)

# Ввод группы (для студентов)
def ask_group(message):
    chat_id = message.chat.id
    text = message.text

    add_user(chat_id, text, 'group')
    
    bot.send_message(chat_id, 'Вы успешно зарегистрировались!', reply_markup = keyboard_main_menu_student())

# Основное меню студентов 
def keyboard_main_menu_student():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Оборудование')
    btn2 = types.KeyboardButton('Инструмент')
    btn3 = types.KeyboardButton('Расходные материалы')
    btn4 = types.KeyboardButton('Расписание кабинета')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

    # Добавляем пользователя
def add_user(chat_id, data, key=''): 
    chat_id = str(chat_id)
    s = {}
    content = read()
    if key:
        s[key] = data
        if key == 'group':
            content[chat_id]['group'] = data
        else:
            content[chat_id] = s
    else:   
        content[chat_id] = data
    save(content) 
    return 


# Считываем список пользователей
def read(): 
    if os.path.isfile('users.json'): 
        file=open('users.json').read() 
        if file: 
            content=json.loads(file) 
            return content 
    return {} 

# Сохраняем список пользователей
def save(content): 
    file=open('users.json', 'wt') 
    file.write(json.dumps(content))

#==================================#

print('Бот запущен')
bot.polling()

