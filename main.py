from conf import conf_token
import telebot

TOKEN = conf_token

bot = telebot.TeleBot(TOKEN)

class Form:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.age = None
        self.sex = None
        self.disc = None

new_forms = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    main_menu(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton('Смотреть анкеты', callback_data='view_form')
    button2 = telebot.types.InlineKeyboardButton('Редактировать анкету', callback_data='edit_form')
    button3 = telebot.types.InlineKeyboardButton('Заполнить анкету заново', callback_data='create_form')
    markup.row(button1)
    markup.row(button2, button3)
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=markup)

@bot.callback_query_handler(lambda query: query.data == 'create_form')
def create_form(query):
    id = str(query.message.chat.id)
    form = Form(id)
    new_forms[id] = form
    bot_message = bot.send_message(query.message.chat.id, "Сколько тебе лет?")
    bot.register_next_step_handler(bot_message, process_age_step)

def process_age_step(message):
    id = str(message.chat.id)
    age = message.text
    new_forms[id].age = age
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton('Мужчина', callback_data='man')
    button2 = telebot.types.InlineKeyboardButton('Женщина', callback_data='woman')
    button3 = telebot.types.InlineKeyboardButton('Не указывать', callback_data='undefined')
    markup.row(button1, button2)
    markup.row(button3)
    bot.send_message(message.chat.id, 'Теперь укажи свой пол', reply_markup=markup)   

@bot.callback_query_handler(lambda query: query.data in ['man', 'woman', 'undefined'])
def callback_sex(query : telebot.types.CallbackQuery):
    id = str(query.message.chat.id)
    if query.data == 'man':
        new_forms[id].sex = 'Мужской'
    elif query.data == 'woman':
        new_forms[id].sex = 'Женский'
    else:
        new_forms[id].sex = 'Не указано'
    bot_message = bot.send_message(query.message.chat.id, "Теперь напиши своё имя, которое будет отображаться в твоей анкете")
    bot.register_next_step_handler(bot_message, process_name_step)

def process_name_step(message):
    id = str(message.chat.id)
    name = message.text
    new_forms[id].name = name
    bot_message = bot.send_message(message.chat.id, 'Расскажи о себе')
    bot.register_next_step_handler(bot_message, process_description_step)

def process_description_step(message):
    id = str(message.chat.id)
    disc = message.text
    new_forms[id].disc = disc
    confirm_form(message)

def confirm_form(message):
    bot.send_message(message.chat.id, 'Вот так выглядит твоя анкета:')
    show_my_form(message)
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton('Да', callback_data='save_form')
    button2 = telebot.types.InlineKeyboardButton('Нет', callback_data='cancel_save_form')
    markup.row(button1, button2)
    bot.send_message(message.chat.id, 'Сохранить?', reply_markup=markup)

def show_my_form(message):
    id = str(message.chat.id)
    text = new_forms[id].name + ', ' + new_forms[id].age + ' лет.\n' + 'Пол: ' + new_forms[id].sex + '\n\nОбо мне:\n' + new_forms[id].disc
    bot.send_message(message.chat.id, text)
    
    
bot.infinity_polling()
