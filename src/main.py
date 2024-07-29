import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from conf import conf_token
from form import Form, FormState
from database import Database
from telebot.handler_backends import State

TOKEN = conf_token
DB_FILE = 'src/database.db'

db = Database(DB_FILE)

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

cancel_text = 'Отменить❌'
save_text = 'Сохранить✔️'
cancel_button = telebot.types.KeyboardButton(cancel_text)
save_button = telebot.types.KeyboardButton(save_text)
cancel_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_markup.add(cancel_button)

@bot.message_handler(commands=['start'])
def start_message(message):
    clear_temp_data(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    if db.check_field_exists(message.from_user.id):
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

@bot.message_handler(func=lambda message: message.text == cancel_text, state = '*')
def cancel(message: telebot.types.Message):
    if not (bot.get_state(message.from_user.id, message.chat.id) in ['FormState:edit_age', 'FormState:edit_name', 'FormState:edit_sex', 'FormState:edit_desc', 'FormState:edit_save']):
        bot.delete_state(message.from_user.id, message.chat.id)
        main_menu(message)
    else:
        edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(func=lambda message: message.text in ['Смотреть анкеты', 'Редактировать анкету', 'Заполнить анкету заново'])
def menu_action(message):
    if message.text == 'Смотреть анкеты':
        pass
    elif message.text == 'Редактировать анкету':
        if not db.check_field_exists(message.chat.id):
            bot.send_message(message.chat.id, 'У тебя ещё нет анкеты. Давай создадим её!')
            create_form(message)
        else:
            form = db.download_form(message.from_user.id)
            edit_form(message, form)
    else:
        create_form(message)

def create_form(message):
    bot.send_message(message.chat.id, "Сколько тебе лет?", reply_markup=cancel_markup)
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
    markup.add(button1, button2, button3, cancel_button)
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
    bot.send_message(message.chat.id, "Напиши своё имя, оно будет отображаться в твоей анкете", reply_markup=cancel_markup)

@bot.message_handler(state=FormState.name)
def get_name(message):
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name
    bot.send_message(message.chat.id, 'Расскажи о себе', reply_markup=cancel_markup)
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
    markup.add(save_button, cancel_button)
    bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=markup)
    bot.set_state(message.from_user.id, FormState.save, message.chat.id)

def edit_form(message, form):
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
        markup.row(button1, button2, button3, button4)
        markup.row(save_button, cancel_button)
        bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
        set_temp_data(message.from_user.id, message.chat.id, form)
        text = form.show_data()
        bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, 'Что ты хочешь изменить?', reply_markup=markup)

@bot.message_handler(state=FormState.edit_menu)
def edit_action(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.text == 'Возраст':
        bot.send_message(chat_id, 'Напиши новый возраст', reply_markup=cancel_markup)
        bot.set_state(user_id, FormState.edit_age, chat_id)
    elif message.text == 'Пол':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = telebot.types.KeyboardButton('Парень')
        button2 = telebot.types.KeyboardButton('Девушка')
        button3 = telebot.types.KeyboardButton('Не указывать')
        markup.row(button1, button2, button3)
        markup.row(cancel_button)
        bot.send_message(chat_id, 'Укажи свой пол', reply_markup=markup)
        bot.set_state(user_id, FormState.edit_sex, chat_id)
    elif message.text == 'Имя':
        bot.send_message(chat_id, 'Напиши новое имя', reply_markup=cancel_markup)
        bot.set_state(user_id, FormState.edit_name, chat_id)
    elif message.text == 'Описание':
        bot.send_message(chat_id, 'Расскажи о себе:', reply_markup=cancel_markup)
        bot.set_state(user_id, FormState.edit_desc, chat_id)
    # elif message.text == 'Отменить':
    #     clear_temp_data(message.from_user.id, message.chat.id)
    #     main_menu(message)
    elif message.text == save_text:
        save_form(message)
        bot.send_message(message.chat.id, 'Вы успешно измнили свою анкету')
        bot.delete_state(user_id, chat_id)
        main_menu(message)

@bot.message_handler(state=FormState.edit_age)
def edit_age(message):
    age = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = age
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_sex)
def edit_sex(message):
    sex = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if sex == 'Парень':
            data['sex'] = 'Мужской'
        elif sex == 'Девушка':
            data['sex'] = 'Женский'
        else:
            data['sex'] = 'Не указано'
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_name)
def edit_name(message):
    name = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_desc)
def edit_desc(message):
    desc = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['desc'] = desc
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(func=lambda message: message.text in (save_text, cancel_text), state=FormState.save)
def save_form_decision(message):
    if message.text == save_text:
        save_form(message)
        bot.send_message(message.chat.id, 'Данные успешно сохранены')
    main_menu(message)

def save_form(message):
    id = message.chat.id
    db.upload_form(generate_form(message.from_user.id, message.chat.id))

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
