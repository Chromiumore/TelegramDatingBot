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

@bot.message_handler(commands=['start'])
def start_message(message):
    clear_temp_data(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    if db.check_field_exists(message.chat.id):
        main_menu(message)
    else:
        bot.send_message(message.chat.id, 'Чтобы начать, тебе нужно заполнить свою анкету')
        create_form(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    clear_temp_data(message.from_user.id, message.chat.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('Смотреть анкеты')
    button2 = telebot.types.KeyboardButton('Редактировать анкету')
    button3 = telebot.types.KeyboardButton('Заполнить анкету заново')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Смотреть анкеты', 'Редактировать анкету', 'Заполнить анкету заново'])
def menu_action(message):
    if message.text == 'Смотреть анкеты':
        pass
    elif message.text == 'Редактировать анкету':
        edit_form(message)
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
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('Парень')
    button2 = telebot.types.KeyboardButton('Девушка')
    button3 = telebot.types.KeyboardButton('Не указывать')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Теперь укажи свой пол', reply_markup=markup)   

@bot.message_handler(state=FormState.sex)
def get_sex(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text == 'Парень':
            data['sex'] = 'Мужской'
        elif message.text == 'Девушка':
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
    form = generate_form(message.from_user.id, message.chat.id)
    text = form.show_data()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('Да')
    button2 = telebot.types.KeyboardButton('Нет')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=markup)
    bot.set_state(message.from_user.id, FormState.save, message.chat.id)

def edit_form(message):
    if not db.check_field_exists(message.chat.id):
        bot.send_message(message.chat.id, 'У тебя ещё нет анкеты. Давай создадим её!')
        create_form(message)
    else:
        bot.set_state(message.from_user.id, FormState.edit_menu, message.chat.id)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = telebot.types.KeyboardButton('Возраст')
        button2 = telebot.types.KeyboardButton('Пол')
        button3 = telebot.types.KeyboardButton('Имя')
        button4 = telebot.types.KeyboardButton('Описание')
        button5 = telebot.types.KeyboardButton('Отмена')
        button6 = telebot.types.KeyboardButton('Сохранить')
        markup.row(button1, button2, button3, button4)
        markup.row(button5, button6)
        bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
        form = db.download_form(message.from_user.id)
        set_temp_data(message.from_user.id, message.chat.id, form)
        text = form.show_data()
        bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, 'Что ты хочешь изменить?', reply_markup=markup)

@bot.message_handler(state=FormState.edit_menu)
def edit_action(message):
    if message.text == 'Возраст':
        pass
    elif message.text == 'Пол':
        pass
    elif message.text == 'Имя':
        pass
    elif message.text == 'Описание':
        pass
    elif message.text == 'Отмена':
        clear_temp_data(message.from_user.id, message.chat.id)
    elif message.text == 'Сохранить':
        pass

@bot.message_handler(func=lambda message: message.text in ('Да', 'Нет'), state=FormState.save)
def save_form_decision(message):
    if message.text == 'Нет':
        main_menu(message)
    else:
        id = message.chat.id
        db.upload_form(generate_form(message.from_user.id, message.chat.id))
        bot.send_message(message.chat.id, 'Данные успешно сохранены')
    bot.delete_state(message.from_user.id, message.chat.id)

def generate_form(user_id, chat_id):
    with bot.retrieve_data(user_id, chat_id) as data:
        form = Form(user_id, data['name'], data['age'], data['sex'], data['desc'])
    return form

def clear_temp_data(user_id, chat_id):
    bot.delete_state(user_id, chat_id)
    bot.reset_data(user_id, chat_id)

def set_temp_data(user_id, chat_id, form : Form):
    with bot.retrieve_data(user_id, chat_id) as data:
        _, data['name'], data['age'], data['sex'], data['desc'] = form.get_data()

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
