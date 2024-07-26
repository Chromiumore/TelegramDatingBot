import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from conf import conf_token
from form import Form, FormState
from database import Database

TOKEN = conf_token
DB_FILE = 'src/database.db'

db = Database(DB_FILE)

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

new_forms = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    if db.check_field_exists(message.chat.id):
        main_menu(message)
    else:
        bot.send_message(message.chat.id, 'Чтобы начать, тебе нужно заполнить свою анкету')
        create_form(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('Смотреть анкеты')
    button2 = telebot.types.KeyboardButton('Редактировать анкету')
    button3 = telebot.types.KeyboardButton('Заполнить анкету заново')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Смотреть анкеты', 'Редактировать анкету', 'Заполнить анкету заново'])
def callback_menu(message):
    if message.text == 'Смотреть анкеты':
        pass
    elif message.text == 'Редактировать анкету':
        pass
    else:
        create_form(message)

def create_form(message):
    bot.send_message(message.chat.id, "Сколько тебе лет?")
    bot.set_state(message.from_user.id, FormState.age, message.chat.id)

@bot.message_handler(state=FormState.age)
def get_age(message):
    age = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = age
    bot.set_state(message.from_user.id, FormState.sex, message.chat.id)
    markup = telebot.types.ReplyKeyboardMarkup()
    button1 = telebot.types.KeyboardButton('Мужчина')
    button2 = telebot.types.KeyboardButton('Женщина')
    button3 = telebot.types.KeyboardButton('Не указывать')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Теперь укажи свой пол', reply_markup=markup)   

@bot.message_handler(state=FormState.sex)
def get_sex(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text == 'Мужчина':
            data['sex'] = 'Мужской'
        elif message.text == 'Женский':
            data['sex'] = 'Женский'
        else:
            data['sex'] = 'Не указано'
    bot.set_state(message.from_user.id, FormState.name, message.chat.id)
    bot.send_message(message.chat.id, "Напиши своё имя, оно будет отображаться в твоей анкете")

@bot.message_handler(state=FormState.name)
def get_name(message):
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name
    bot.send_message(message.chat.id, 'Расскажи о себе')
    bot.set_state(message.from_user.id, FormState.desc, message.chat.id)

@bot.message_handler(state=FormState.desc)
def process_description_step(message):
    desc = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['desc'] = desc
    confirm_form(message)

def confirm_form(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        form = Form(message.from_user.id, data['name'], data['age'], data['sex'], data['desc'])
    text = form.show_data()
    new_forms[message.from_user.id] = form
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('Да')
    button2 = telebot.types.KeyboardButton('Нет')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=markup)
    bot.set_state(message.from_user.id, FormState.save, message.chat.id)

# def edit_form(message):
#     if not db.check_field_exists(message.chat.id):
#         bot.send_message(message.chat.id, 'У тебя ещё нет анкеты. Давай создадим её!')
#         create_form(message)
#     else:
#         markup = telebot.types.InlineKeyboardMarkup()
#         button1 = telebot.types.InlineKeyboardButton('Возраст', callback_data='edit_age')
#         button2 = telebot.types.InlineKeyboardButton('Пол', callback_data='edit_sex')
#         button3 = telebot.types.InlineKeyboardButton('Имя', callback_data='edit_name')
#         button4 = telebot.types.InlineKeyboardButton('Описание', callback_data='edit_desc')
#         button5 = telebot.types.InlineKeyboardButton('Отмена', callback_data='cancel_edit')
#         button6 = telebot.types.InlineKeyboardButton('Сохранить', callback_data='save_edit')
#         markup.row(button1, button2, button3, button4)
#         markup.row(button5, button6)
#         bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
#         send_form(message, get_form(message.chat.id)) 
#         bot.send_message(message.chat.id, 'Что ты хочешь изменить?', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ('Да', 'Нет'),)
def save_form_decision(message):
    if message.text == 'Нет':
        main_menu(message)
    else:
        id = message.chat.id
        db.upload_form(new_forms[id])
        new_forms.pop(id)
        bot.send_message(message.chat.id, 'Данные успешно сохранены')
    bot.delete_state(message.from_user.id, message.chat.id)

def get_form(id):
    data = db.download_form(id)
    form = Form(*data)
    return form

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
