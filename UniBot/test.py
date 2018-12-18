from telegram.ext import MessageHandler, Filters, Updater, CommandHandler

def echo(bot, update):
	print('a')
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)  

def hello(bot, update):
	print("hi")

updater = Updater(token='773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')
updater.start_polling()
#updater.idle()

updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
updater.dispatcher.add_handler(CommandHandler('hello', hello))


