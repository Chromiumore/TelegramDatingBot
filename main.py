from conf import conf_token
import telebot

TOKEN = conf_token

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в лучший чат для знакомств.")
    main_menu(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Редактировать анкету', callback_data='edit_form'))
    markup.add(telebot.types.InlineKeyboardButton('Смотреть анкеты', callback_data='view_form'))
    markup.add(telebot.types.InlineKeyboardButton('Настройки поиска', callback_data='search_settings'))
    bot.send_message(message.chat.id, 'Выбери действие:  ', reply_markup=markup)

bot.infinity_polling()
