from conf import conf_token
import telebot

TOKEN = conf_token

bot = telebot.TeleBot(TOKEN)

@bot.message_handler()
def echo(message):
    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()
