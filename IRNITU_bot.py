import telebot
import config 
import os
import json 
from telebot.types import Message
from telebot import types



bot = telebot.TeleBot(config.TOKEN)




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
        add_user(chat_id,'student')
        msg = bot.send_message(chat_id,'Введите ФИО (через пробел)')
        bot.register_next_step_handler(msg, ask_name)

    # регистрация посетителя
    if message.data == 'visitor':
        msg = bot.send_message(chat_id, 'Введите номер договора')
        bot.register_next_step_handler(msg, ask_contract)




# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text(message:Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Вижу, что написал')
    print(message.data)





# Ввод номера договора (для посетителей)
def ask_contract(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Номер договора должен состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_contract)
        return
    add_user(chat_id, text)


# Ввод ФИО (для студентов)
def ask_name(message):
    chat_id = message.chat.id
    text = message.text
    if text.replace(' ', '').isdigit():
        msg = bot.send_message(chat_id, 'ФИО не может состоять из цифр, введите ещё раз.')
        bot.register_next_step_handler(msg, ask_name)
        return
    msg = bot.send_message(chat_id, 'Введите группу (в формате XXX-16-1)')
    bot.register_next_step_handler(msg, ask_group)

# Ввод группы (для студентов)
def ask_group(message):
    chat_id = message.chat.id
    text = message.text
    print(text)


# Добавляем пользователя
def add_user(chat_id, data): 
    content = read()   
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



print('Бот запущен')
bot.polling()