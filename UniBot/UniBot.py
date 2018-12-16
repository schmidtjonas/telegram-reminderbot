from telegram.ext import Updater, CommandHandler, MessageHandler



def start(bot, update):
	update.message.reply_text("""
        Willkommen {}
Befehle:
/add FACH um ein neues Fach hinzuzufügen

        """.format(update.message.from_user.first_name))

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def add(bot, update, args):
	if len(args) != 1:
		errorHandler(update, "Gib bitte genau ein Fach an!")
		return
	update.message.reply_text(str(args) + 'Wurde hinzugefügt. ')

def errorHandler(update, error):
	update.message.reply_text(error)

def saveEntries():
	return



updater = Updater('773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('add', add, pass_args = True))

updater.start_polling()
updater.idle()