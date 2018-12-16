from telegram.ext import Updater, CommandHandler, MessageHandler

class UniBot:
	def __init__(self):
		self.file = "faecher.txt"
		self.entries = []

	def start(self, bot, update):
		update.message.reply_text("""
	        Willkommen {}
	Befehle:
	/add FACH um ein neues Fach erstellen

	        """.format(update.message.from_user.first_name))

	def hello(self, bot, update):
	    update.message.reply_text(
	        'Hello {}'.format(update.message.from_user.first_name))

	def add(self, bot, update, args):
		if len(args) != 1:
			errorHandler(update, "Gib bitte genau ein Fach an!")
			return
		elif args[0] == " ":
			errorHandler(update, "Gib bitte genau ein Fach an!")
			return
		if args[0] not in self.entries:
			self.entries.append(args[0])
		else:
			errorHandler(update, "Fach existiert bereits!")

		self.saveEntry(args[0])

		update.message.reply_text(str(args[0]) + 'Wurde hinzugefügt. ')

	def errorHandler(self, update, error):
		update.message.reply_text("Fehler: " + error)

	def deleteFach(self, fach, update):
		if fach not in self.entries:
			errorHandler("Verschrieben? Dieses Fach existiert nicht!")
		else:
			self.entries.remove(fach)

	def saveEntries(self):
		with open(self.file, "a") as file:
			file.write("")

		return

	def saveEntry(self, entry):
		with open(self.file, "a") as file:
			file.write("\n" + entry)


b = UniBot()
updater = Updater('773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')

updater.dispatcher.add_handler(CommandHandler('hello', b.hello))
updater.dispatcher.add_handler(CommandHandler('start', b.start))
updater.dispatcher.add_handler(CommandHandler('add', b.add, pass_args = True))
updater.dispatcher.add_handler(CommandHandler('delete', b.deleteFach, pass_args = True))

updater.start_polling()
updater.idle()