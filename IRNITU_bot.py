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

def registration(message):
    BUFFER = {}
    keyboard = types.InlineKeyboardMarkup()
    button_student = 'Студент'
    button_visitor = 'Посетитель'

    keyboard.add(types.InlineKeyboardButton(text = button_student, callback_data = 'student'))
    keyboard.add(types.InlineKeyboardButton(text = button_visitor, callback_data = 'visitor'))

    bot.send_message(message.chat.id,'Зарегистрировться как:', reply_markup = keyboard)

# /start
@bot.message_handler(commands=['start'])
def start_message(message:Message):
    bot.send_message(message.chat.id,'Привет, я IRNITU_bot!\n' + 'Проидите регистрацию')
    registration(message)





# Обработка ответов от чат-клавиатуры
@bot.callback_query_handler(func=lambda message:True)
def ans(message:Message):
    chat_id = message.message.chat.id
    global BUFFER
    # регистрация студента
    if message.data == 'student':
        if str(chat_id) in read() and not check_start_reg(chat_id):
            bot.send_message(chat_id,'Вы уже зарегистрированы!')
            return

        if not check_start_reg(chat_id, True):
            BUFFER[chat_id] = 'студент'
            msg = bot.send_message(chat_id,'Введите ФИО (через пробел)')
            bot.register_next_step_handler(msg, ask_name)

    # Регистрация посетителя
    if message.data == 'visitor':
        if str(chat_id) in read() and not check_start_reg(chat_id):
            bot.send_message(chat_id,'Вы уже зарегистрированы!')
            return

        if not check_start_reg(chat_id, True):
            BUFFER[chat_id] = 'посетитель'
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
        if str(chat_id) in BUFFER and BUFFER[str(chat_id)][-1] == 's' :
            
            bot.send_message(chat_id, f'Вы уже нажали на кнопку Израсходовать  ({BUFFER[str(chat_id)]})'+
                            '\nВведите количество, либо нажмите кнопку Отмена')
        else:
            
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
            btn = types.KeyboardButton('Отмена')
            markup.add(btn)
            msg = bot.send_message(chat_id, name +'\nВведите количество', reply_markup = markup)
            BUFFER[str(chat_id)] = name + 's' # Записываем в буфер название материала который выбрал пользователь и действие (s-spend)
            BUFFER['m_id' + str(chat_id)] = message.message.message_id #записываем в буфер id сообщения для дальнейшего редактирования
            bot.register_next_step_handler(msg, change_kol)

    # Кнопка отменить расходование
    if message.data[:20] == 'cancel_spend_exp_mat':
        name = message.data[20:]
        if str(chat_id) in BUFFER and BUFFER[str(chat_id)][-1] == 'b':
            
            bot.send_message(chat_id, f'Вы уже нажали на кнопку Отменить расходование ({BUFFER[str(chat_id)]})'+
                            '\nВведите количество, либо нажмите кнопку Отмена')
        else:
            
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
            btn = types.KeyboardButton('Отмена')
            markup.add(btn)
            msg = bot.send_message(chat_id, name +'\nВведите количество', reply_markup = markup)
            BUFFER[str(chat_id)] = name + 'b' # Записываем в буфер название материала который выбрал пользователь и действие (b-back)
            BUFFER['m_id' + str(chat_id)] = message.message.message_id #записываем в буфер id сообщения для дальнейшего редактирования
            bot.register_next_step_handler(msg, change_kol)



# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text(message:Message):
    chat_id = message.chat.id


    # Присваивание статуса пользователю
    user_status = read()[str(chat_id)]['status']


  
    # Вывод списка оборудования
    if message.text == 'Оборудование' and user_status == 'student':
        eq = change_BD('Оборудование')
        bot.send_message(message.chat.id, 'Список оборудования:')
        for i in range(len(eq)):
            button = 'Описание'
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text = button, callback_data = 'info_eq' + 
                                                    change_BD('Оборудование')[i]))
            bot.send_message(message.chat.id, change_BD('Оборудование')[i], reply_markup = keyboard)    
    # Вывод списка инструментов
    if message.text == 'Инструмент' and user_status == 'student':
        tools = change_BD('Инструмент')
        tools_str =''
        bot.send_message(message.chat.id, 'Доступный инструмент:')
        for i in tools:
            tools_str = tools_str + i
        bot.send_message(message.chat.id, tools_str)

    # Вывод списка расходных материалов
    if message.text == 'Расходные материалы' and user_status == 'student':
        eq = change_BD('Расходные материалы')

        bot.send_message(message.chat.id, 'Расходные материалы:')
        for i in range(len(eq)):
            name = change_BD('Расходные материалы')[i][:-1]
            button1 = ('Израсходовать ' + 
                       f'(доступно: {str(exp_mat_kol(name, "Расходные материалы"))} {exp_mat_ed_izm(name, "Расходные материалы")})')
            button2 = 'Отменить расходование'
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text = button1, callback_data = 'spend_exp_mat' + name))
            keyboard.add(types.InlineKeyboardButton(text = button2, callback_data = 'cancel_spend_exp_mat' + name))
            bot.send_message(message.chat.id, name, 
                             reply_markup = keyboard)    

    # Вывод расписания кабинета
    if message.text == 'Расписание кабинета' and user_status == 'student':
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

 # Изменить кол-во рас мат в базе данных 
def change_kol(message): 
    chat_id = message.chat.id
    text = message.text
    global BUFFER
    action = BUFFER[str(chat_id)][-1] # Действие которое нужно выполнить(s-spend, b-back)

    if text == 'Отмена':
        bot.send_message(chat_id, 'Отменено', reply_markup = keyboard_main_menu_student())
        del BUFFER[str(chat_id)]
        del BUFFER['m_id' + str(chat_id)]
        return 

    try:
        data = float(text.replace(',', '.'))
    except:
        msg = bot.send_message(chat_id, 'Введите число!')
        return bot.register_next_step_handler(msg, change_kol)

    if data <= 0: # Если пользователь ввел значение меньше нуля
        msg = bot.send_message(chat_id, 'Значение должно быть больше нуля!')
        return bot.register_next_step_handler(msg, change_kol)

    name = BUFFER[str(chat_id)][:-1] # Название материала
    message_id = BUFFER['m_id' + str(chat_id)] # id сообщения для редактирования количества

    wb = load_workbook('BD.xlsx')
    sheet = wb['Расходные материалы']
    value = float(exp_mat_kol(name, 'Расходные материалы'))
    last_value = value

    if int(last_value) == float(last_value):
        last_value = int(last_value)


    if action == 's':
        value -= data
        if value < 0: # Если пользователь расходует больше чем доступно
            msg = bot.send_message(chat_id, f'Такого количества расходного материала нет (доступно: {last_value})')
            return bot.register_next_step_handler(msg, change_kol)
    elif action == 'b':
        value += data

   # записывем новое значение в БД
    i=2
    while(True):
       val = sheet.cell(row = i, column = 1).value
       if str(name) == str(val):
           sheet.cell(row = i, column = 2).value = value
           wb.save('BD.xlsx')
           break
       i+=1


    # Меняем текст сообщения (количество)
    button1 = ('Израсходовать ' + 
               f'(доступно: {str(exp_mat_kol(name, "Расходные материалы"))} {exp_mat_ed_izm(name, "Расходные материалы")})')
    button2 = 'Отменить расходование'
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text = button1, callback_data = 'spend_exp_mat' + name))
    keyboard.add(types.InlineKeyboardButton(text = button2, callback_data = 'cancel_spend_exp_mat' + name))
    bot.edit_message_text(name, chat_id, message_id, reply_markup = keyboard)

    if action == 's': 
        bot.send_message(chat_id, f'Израсходовано {message.text} {exp_mat_ed_izm(name, "Расходные материалы")}',
                         reply_markup = keyboard_main_menu_student())
    if action == 'b': 
        bot.send_message(chat_id, f'Возвращено {message.text} {exp_mat_ed_izm(name, "Расходные материалы")}', 
                         reply_markup = keyboard_main_menu_student())
    del BUFFER[str(chat_id)]
    del BUFFER['m_id' + str(chat_id)]
    return

#=========================================#

#==========Оборудование============#

# Возвращает описание оборудования
def info_equipment(name, kategory): 
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

# Открываем BD (возвращаем страницу)
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

# Проверка начал ли пользователь регистрацию
def check_start_reg(chat_id, send_msg=False):
    if chat_id in BUFFER:
        if BUFFER[chat_id] == 'студент' or BUFFER[chat_id] == 'посетитель':
            data = BUFFER[chat_id]
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            btn = types.KeyboardButton('Начать регистрацию с начала') 
            markup.add(btn)
            if send_msg:
                msg = bot.send_message(chat_id, 'Вы уже начали регистрацию как ' + data + 
                            '\nЕсли хотите начать регистрацию с начала, нажмите на кнопку Начать регистрацию с начала\n'+
                           'Если хотите продолжить регистрацию как ' + data +
                          ', продолжайте вводить данные', reply_markup = markup)

            return True 
    return False
           
# Удаляем данные из буффера и бд для пользователей, если пользователь нажал Начать регистрацию с начала             
def repeat_reg(message):
    if message.text == 'Начать регистрацию с начала':
        data = read()
        if str(message.chat.id) in read():
            del data[str(message.chat.id)]
            save(data)
        global BUFFER

        if message.chat.id in BUFFER:
            del BUFFER[message.chat.id]
        return True
    return False

# Ввод номера договора (для посетителей)
def ask_contract(message):

    if repeat_reg(message):
        return registration(message)

    chat_id = message.chat.id
    text = message.text

    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Номер договора должен состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_contract)
        return
    add_user(chat_id, text)
    bot.send_message(chat_id, 'Вы успешно зарегистрировались!')
    del BUFFER[chat_id]


# Ввод ФИО (для студентов)
def ask_name(message):

    if repeat_reg(message):
        return registration(message)

    chat_id = message.chat.id
    text = message.text

    if text == 'Начать регистрацию с начала':
       return registration(message)

    if text.replace(' ', '').isdigit():
        msg = bot.send_message(chat_id, 'ФИО не может состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_name)
        return

    add_user(chat_id, text, 'name')
    msg = bot.send_message(chat_id, 'Введите группу (в формате XXX-16-1)')
    bot.register_next_step_handler(msg, ask_group)

# Ввод группы (для студентов)
def ask_group(message):

    if repeat_reg(message):
        return registration(message)

    chat_id = message.chat.id
    text = message.text

    add_user(chat_id, text, 'group')
    
    bot.send_message(chat_id, 'Вы успешно зарегистрировались!', reply_markup = keyboard_main_menu_student())
    del BUFFER[chat_id]

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
    #s = {}
    
    content = read()
    if key == 'admin':
        s = {'status': 'admin'}
        content[chat_id] = s

    elif key:

        if key == 'group':
            content[chat_id]['group'] = data
        else:
            s = {'status': 'student'}
            s[key] = data
            content[chat_id] = s
    
    else:
        s = {'status': 'visitor'}
        content[chat_id] = s
        content[chat_id]['number'] = data
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

print('Бот запущен...')
bot.polling()

