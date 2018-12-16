from telegram.ext import Updater, CommandHandler, MessageHandler

class UniBot:
	def __init__(self):
		file = "faecher.txt"

	def start(self, bot, update):
		update.message.reply_text("""
	        Willkommen {}
	Befehle:
	/add FACH um ein neues Fach hinzuzufügen

	        """.format(update.message.from_user.first_name))

	def hello(self, bot, update):
	    update.message.reply_text(
	        'Hello {}'.format(update.message.from_user.first_name))

	def add(self, bot, update, args):
		if len(args) != 1:
			errorHandler(update, "Gib bitte genau ein Fach an!")
			return
		update.message.reply_text(str(args) + 'Wurde hinzugefügt. ')

	def errorHandler(self, update, error):
		update.message.reply_text("Fehler: " + error)

	def saveEntries(self):
		

		return


b = UniBot()
updater = Updater('773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')

updater.dispatcher.add_handler(CommandHandler('hello', b.hello))
updater.dispatcher.add_handler(CommandHandler('start', b.start))
updater.dispatcher.add_handler(CommandHandler('add', b.add, pass_args = True))

updater.start_polling()
updater.idle()