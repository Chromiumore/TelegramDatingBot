import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from conf import conf_token
from form import Form, FormState
from database import Database
from custom import *

TOKEN = conf_token # Unique telegram bot token
DB_FILE = 'src/database.db' # Path of database file

db = Database(DB_FILE) # Creating database for storing all information about the users

state_storage = StateMemoryStorage() # Bot's internal storage to keep states

bot = telebot.TeleBot(TOKEN, state_storage=state_storage) # Creating bot

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
    bot.set_state(message.from_user.id, FormState.main_menu, message.chat.id)
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=Markups.MAIN_MENU.value)

@bot.message_handler(func=lambda message: message.text == Texts.CANCEL.value, state = '*')
def cancel(message: telebot.types.Message):
    if not (bot.get_state(message.from_user.id, message.chat.id) in ['FormState:edit_age', 'FormState:edit_name', 'FormState:edit_sex', 'FormState:edit_desc', 'FormState:edit_save', 'FormState:edit_photos', 'FormState:edit_numbered_photo']):
        bot.delete_state(message.from_user.id, message.chat.id)
        main_menu(message)
    else:
        edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.main_menu)
def menu_action(message : telebot.types.Message):
    if message.text == Texts.SEARCH.value:
        pass
    elif message.text == Texts.EDIT.value:
        if not db.check_field_exists(message.chat.id):
            bot.send_message(message.chat.id, 'У тебя ещё нет анкеты. Давай создадим её!')
            create_form(message)
        else:
            form = db.download_form(message.from_user.id)
            edit_form(message, form)
    elif message.text == Texts.CREATE.value:
        create_form(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта ответа')

# Function to start creating form sequence
def create_form(message):
    bot.send_message(message.chat.id, "Сколько тебе лет?", reply_markup=Markups.CANCEL.value)
    bot.set_state(message.from_user.id, FormState.age, message.chat.id)

@bot.message_handler(state=FormState.age)
def get_age(message : telebot.types.Message):
    age = str(message.text)
    if not age.isdigit():
        bot.send_message(message.chat.id, 'Ты указал неправильный возраст, используй только цифры!')
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = age
    bot.set_state(message.from_user.id, FormState.sex, message.chat.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    button1 = telebot.types.KeyboardButton('Парень')
    button2 = telebot.types.KeyboardButton('Девушка')
    button3 = telebot.types.KeyboardButton('Не указывать')
    bot.send_message(message.chat.id, 'Теперь укажи свой пол', reply_markup=Markups.SEX.value)   

@bot.message_handler(state=FormState.sex)
def get_sex(message):
    sex = str(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if sex == Texts.MALE.value:
            data['sex'] = 'Мужской'
        elif sex == Texts.FEMALE.value:
            data['sex'] = 'Женский'
        elif sex == Texts.NO_SEX.value:
            data['sex'] = 'Не указано'
        else:
            bot.send_message(message.chat.id, 'Нет такого варианта ответа')
            return
    bot.set_state(message.from_user.id, FormState.name, message.chat.id)
    bot.send_message(message.chat.id, "Напиши своё имя, оно будет отображаться в твоей анкете", reply_markup=Markups.CANCEL.value)

@bot.message_handler(state=FormState.name)
def get_name(message : telebot.types.Message):
    name = str(message.text)
    print(name)
    if not check_name_correct(name):
        bot.send_message(message.chat.id, 'Ты использовал запрещённые символы, твоё имя должно содержать только буквы')
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name
    bot.send_message(message.chat.id, 'Расскажи о себе', reply_markup=Markups.CANCEL.value)
    bot.set_state(message.from_user.id, FormState.desc, message.chat.id)

@bot.message_handler(state=FormState.desc)
def get_desc(message : telebot.types.Message):
    desc = str(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['desc'] = desc
        data['photos'] = []
    bot.send_message(message.chat.id, 'Отправь свою фотографию. Ты можешь сохранить в своей анкете от 1 до 4 фотографий.\nОтправляй по одной!', reply_markup=Markups.DEFAULT.value)
    bot.set_state(message.from_user.id, FormState.photos, message.chat.id)
    print(f'State of {message.from_user.id} changed to', bot.get_state(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.photos, content_types=['photo', 'text'])
def get_photos(message : telebot.types.Message):
    if add_photo_from_message(message):
        confirm_form(message)

def confirm_form(message):
    form = generate_form(message.from_user.id, message.chat.id)
    print(message.from_user.id, 'is thinking about saving his new form: ', form.get_data())
    show_form(form, message.chat.id)
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=Markups.SAVE.value)
    bot.set_state(message.from_user.id, FormState.save, message.chat.id)

def edit_form(message, form):
    if not db.check_field_exists(message.chat.id):
        bot.send_message(message.chat.id, 'У тебя ещё нет анкеты. Давай создадим её!')
        create_form(message)
    else:
        bot.set_state(message.from_user.id, FormState.edit_menu, message.chat.id)
        set_temp_data(message.from_user.id, message.chat.id, form)
        show_form(form, message.chat.id)
        bot.send_message(message.chat.id, 'Что ты хочешь изменить?', reply_markup=Markups.EDIT_MENU.value)

@bot.message_handler(state=FormState.edit_menu)
def edit_action(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.text == Texts.AGE.value:
        bot.send_message(chat_id, 'Напиши новый возраст', reply_markup=Markups.CANCEL.value)
        bot.set_state(user_id, FormState.edit_age, chat_id)
    elif message.text == Texts.SEX.value:
        bot.send_message(chat_id, 'Укажи свой пол', reply_markup=Markups.SEX.value)
        bot.set_state(user_id, FormState.edit_sex, chat_id)
    elif message.text == Texts.NAME.value:
        bot.send_message(chat_id, 'Напиши новое имя', reply_markup=Markups.CANCEL.value)
        bot.set_state(user_id, FormState.edit_name, chat_id)
    elif message.text == Texts.DESCRIPTION.value:
        bot.send_message(chat_id, 'Расскажи о себе:', reply_markup=Markups.CANCEL.value)
        bot.set_state(user_id, FormState.edit_desc, chat_id)
    elif message.text == Texts.PHOTOS.value:
        start_edit_photos(user_id, chat_id)
    elif message.text == Texts.SAVE.value:
        save_form(message)
        bot.send_message(message.chat.id, 'Вы успешно измнили свою анкету')
        bot.delete_state(user_id, chat_id)
        main_menu(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта ответа')
        return

@bot.message_handler(state=FormState.edit_age)
def edit_age(message):
    age = str(message.text)
    if not age.isdigit():
        bot.send_message(message.chat.id, 'Ты указал неправильный возраст, используй только цифры!')
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = age
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_sex)
def edit_sex(message):
    sex = str(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if sex == Texts.MALE.value:
            data['sex'] = 'Мужской'
        elif sex == Texts.FEMALE.value:
            data['sex'] = 'Женский'
        elif sex == Texts.NO_SEX.value:
            data['sex'] = 'Не указано'
        else:
            bot.send_message(message.chat.id, 'Нет такого варианта ответа')
            return
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_name)
def edit_name(message):
    name = str(message.text)
    print(name)
    if not check_name_correct(name):
        bot.send_message(message.chat.id, 'Ты использовал запрещённые символы, твоё имя должно содержать только буквы')
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = name
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(state=FormState.edit_desc)
def edit_desc(message):
    desc = str(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['desc'] = desc
    edit_form(message, generate_form(message.from_user.id, message.chat.id))

def start_edit_photos(user_id, chat_id):
    markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    with bot.retrieve_data(user_id, chat_id) as data:
        photo_buttons = []
        amount = len(data['photos'])
        for i in range(amount):
            photo_buttons.append(telebot.types.KeyboardButton(str(i + 1)))
        if amount < 4:
            photo_buttons.append(Buttons.ADD_PHOTO.value)
    markup.row(*photo_buttons)
    markup.row(Buttons.PHOTOS_AGAIN.value)
    markup.row(Buttons.CONFIRM.value, Buttons.CANCEL.value)
    show_form(generate_form(user_id, chat_id), chat_id, False)
    bot.send_message(chat_id, 'Какую фотографию ты хочешь изменить?', reply_markup=markup)
    bot.set_state(user_id, FormState.edit_photos, chat_id)

@bot.message_handler(state=FormState.edit_photos)
def edit_photos(message):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 4:
            bot.set_state(message.from_user.id, FormState.edit_numbered_photo, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_num'] = int(message.text)
            bot.send_message(message.chat.id, 'Отправь новую фотографию', reply_markup=Markups.PHOTO_EDIT.value)
        else:
            bot.send_message(message.chat.id, 'Нет фотографии с таким номером')
    else:
        if message.text == Texts.CONFIRM.value:
            edit_form(message, generate_form(message.from_user.id, message.chat.id))
        elif message.text == Texts.ADD_PHOTO.value:
            bot.send_message(message.chat.id, 'Отправь новую фотографию', reply_markup=Markups.CANCEL.value)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photo_num'] = len(data['photos']) + 1 # Position of new photo (not index)
            bot.set_state(message.from_user.id, FormState.edit_numbered_photo, message.chat.id)
        elif message.text == Texts.PHOTOS_AGAIN.value:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photos'].clear()
            bot.send_message(message.chat.id, 'Отправь свою фотографию. Ты можешь сохранить в своей анкете от 1 до 4 фотографий.\nОтправляй по одной!', reply_markup=Markups.DEFAULT.value)
            bot.set_state(message.from_user.id, FormState.edit_photos_again, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Нет такого варианта ответа')

@bot.message_handler(state=FormState.edit_numbered_photo, content_types=['photo', 'text', 'video'])
def edit_photo(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        num = data['photo_num']
    if message.content_type != 'photo':
        if message.text == Texts.DELETE.value:
            if len(data['photos']) == 1:
                bot.send_message(message.chat.id, 'У тебя дожна быть как минимум 1 фотография')
            else:
                data['photos'].pop(num - 1)
                start_edit_photos(message.from_user.id, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Это не подойдёт, мне нужны только твои фотографии')
    else:
        photo_id = message.photo[-1].file_id
        if len(data['photos']) >= num:
            data['photos'][num - 1] = photo_id
        else:
            data['photos'].append(photo_id)
        start_edit_photos(message.from_user.id, message.chat.id)

@bot.message_handler(state=FormState.edit_photos_again, content_types=['photo', 'text', 'video'])
def edit_photos_again(message : telebot.types.Message):
    if add_photo_from_message(message):
        edit_form(message, generate_form(message.from_user.id, message.chat.id))

@bot.message_handler(func=lambda message: message.text in (Texts.SAVE.value, Texts.CANCEL.value), state=FormState.save)
def save_form_decision(message):
    if message.text == Texts.SAVE.value:
        save_form(message)
        bot.send_message(message.chat.id, 'Данные успешно сохранены')
        main_menu(message)
    elif message.text == Texts.CANCEL.value:
        main_menu(message)
    else:
        bot.send_message(message.chat.id, 'Нет такого варианта ответа')
        return

def save_form(message):
    id = message.chat.id
    db.upload_form(generate_form(message.from_user.id, message.chat.id))

# This function gaenerates form based on data about the user from the bot's context manager 
def generate_form(user_id, chat_id):
    with bot.retrieve_data(user_id, chat_id) as data:
        form = Form(user_id, data['name'], data['age'], data['sex'], data['desc'], data['photos'])
        print(f'Generated form {form.get_data()}')
    return form

# Deletes current state and data for a user in chat
def clear_temp_data(user_id, chat_id):
    bot.delete_state(user_id, chat_id)
    bot.reset_data(user_id, chat_id)

# Sets current state and data for a user in chat
def set_temp_data(user_id, chat_id, form : Form):
    with bot.retrieve_data(user_id, chat_id) as data:
        _, data['name'], data['age'], data['sex'], data['desc'], data['photos'] = form.get_data()

def check_name_correct(name : str):
    for i in range(len(name)):
        num = ord(name[i].lower())
        if not ( ((ord('а') <= num) and (num <= ord('я'))) or (ord('a') <= num) and (num <= ord('z')) or (num == ' ') ):
            return False
    return True

def show_form(form, chat_id, has_text=True):
    photos_to_send = []
    for i in range(len(form.photos)):
        if i == 0 and has_text:
            photos_to_send.append(telebot.types.InputMediaPhoto(form.photos[i], form.show_data()))
        else:
            photos_to_send.append(telebot.types.InputMediaPhoto(form.photos[i]))
    bot.send_message(chat_id, 'Вот так выглядит твоя анкета:')
    bot.send_media_group(chat_id, photos_to_send)

def add_photo_from_message(message : telebot.types.Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        stop_add_photos = False
        if message.content_type == 'text':
            if message.text == 'Далее' and len(data['photos']) > 0:
                stop_add_photos = True
            else:
                bot.send_message(message.chat.id, 'У тебя должна быть как минимум 1 фотография')
        else:
            print('Getting a photo from user: ', message.from_user.id)
            photo_id = message.photo[-1].file_id
            data['photos'].append(photo_id)
            print(f'User {message.from_user.id} has next photos: ', data['photos'])
            bot.send_message(message.chat.id, f'{len(data['photos'])}/2 фотографий добавлено')
            if len(data['photos']) >= 2:
                stop_add_photos = True
    return stop_add_photos

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)
