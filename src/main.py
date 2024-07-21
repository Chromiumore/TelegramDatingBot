from conf import conf_token
import telebot
from form import Form
from database import Database

TOKEN = conf_token

db_file = 'src/database.db'
db = Database(db_file)

bot = telebot.TeleBot(TOKEN)

new_forms = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    main_menu(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton('Смотреть анкеты', callback_data='view_forms')
    button2 = telebot.types.InlineKeyboardButton('Редактировать анкету', callback_data='edit_form')
    button3 = telebot.types.InlineKeyboardButton('Заполнить анкету заново', callback_data='create_form')
    markup.row(button1)
    markup.row(button2, button3)
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=markup)

@bot.callback_query_handler(lambda query: query.data == 'create_form')
def create_form(query):
    id = query.message.chat.id
    form = Form(id)
    new_forms[id] = form
    bot_message = bot.send_message(query.message.chat.id, "Сколько тебе лет?")
    bot.register_next_step_handler(bot_message, process_age_step)

def process_age_step(message):
    id = message.chat.id
    age = message.text
    new_forms[id].age = age
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton('Мужчина', callback_data='man')
    button2 = telebot.types.InlineKeyboardButton('Женщина', callback_data='woman')
    button3 = telebot.types.InlineKeyboardButton('Не указывать', callback_data='undefined')
    markup.row(button1, button2)
    markup.row(button3)
    bot.send_message(message.chat.id, 'Теперь укажи свой пол', reply_markup=markup)   

@bot.callback_query_handler(lambda query: query.data in ('man', 'woman', 'undefined'))
def callback_sex(query : telebot.types.CallbackQuery):
    id = query.message.chat.id
    if query.data == 'man':
        new_forms[id].sex = 'Мужской'
    elif query.data == 'woman':
        new_forms[id].sex = 'Женский'
    else:
        new_forms[id].sex = 'Не указано'
    bot_message = bot.send_message(query.message.chat.id, "Напиши своё имя, оно будет отображаться в твоей анкете")
    bot.register_next_step_handler(bot_message, process_name_step)

def process_name_step(message):
    id = message.chat.id
    name = message.text
    new_forms[id].name = name
    bot_message = bot.send_message(message.chat.id, 'Расскажи о себе')
    bot.register_next_step_handler(bot_message, process_description_step)

def process_description_step(message):
    id = message.chat.id
    desc = message.text
    new_forms[id].desc = desc
    confirm_form(message)

def confirm_form(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton('Да', callback_data='save_form')
    button2 = telebot.types.InlineKeyboardButton('Нет', callback_data='cancel_save_form')
    markup.row(button1, button2)
    bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
    send_my_form(message, new_forms[message.chat.id])
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=markup)

def send_my_form(message, form : Form):
    text = form.show_data()
    bot.send_message(message.chat.id, text)

@bot.callback_query_handler(lambda query: query.data == 'edit_form')
def edit_form(query : telebot.types.CallbackQuery):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton('Возраст', callback_data='edit_age')
    button2 = telebot.types.InlineKeyboardButton('Пол', callback_data='edit_sex')
    button3 = telebot.types.InlineKeyboardButton('Имя', callback_data='edit_name')
    button4 = telebot.types.InlineKeyboardButton('Описание', callback_data='edit_desc')
    button5 = telebot.types.InlineKeyboardButton('Отмена', callback_data='cancel_edit')
    button6 = telebot.types.InlineKeyboardButton('Сохранить', callback_data='save_edit')
    markup.row(button1, button2, button3, button4)
    markup.row(button5, button6)
    bot.send_message(query.message.chat.id, 'Вот так выглядит твоя анкета:')
    send_my_form(query.message, new_forms[query.message.chat.id])
    bot.send_message(query.message.chat.id, 'Что ты хочешь изменить?', reply_markup=markup)

@bot.callback_query_handler(lambda query: query.data in ('save_form', 'cancel_save_form'))
def save_form_decision(query : telebot.types.CallbackQuery):
    if query.data == 'cancel_save_form':
        main_menu(query.message)
    else:
        id = query.message.chat.id
        db.upload_form(new_forms[id])
        new_forms.pop(id)
        bot.send_message(query.message.chat.id, 'Данные успешно сохранены')

bot.infinity_polling()
