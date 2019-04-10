from telegram.ext import MessageHandler, Filters, Updater, CommandHandler, ConversationHandler

def echo(bot, update):
	print('a')
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)  

def skip_photo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text='next') 
	return 1

def stop(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text='stop')
	return -1 


def hello(bot, update):
	print("hi")
	bot.send_message(chat_id=update.message.chat_id, text='Hi') 
	return 0

updater = Updater(token='773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')
#updater.idle()

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('hello', hello)],

        states={
            0: [MessageHandler(Filters.text, echo),
                    CommandHandler('skip', skip_photo)],

            1: [MessageHandler(Filters.text, stop)]
        },

        fallbacks=[CommandHandler('cancel', stop)]
    )
updater.dispatcher.add_handler(conv_handler)

updater.start_polling()

