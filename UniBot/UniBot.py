from telegram.ext import Updater, CommandHandler, MessageHandler

class UniBot:
	def __init__(self):

		self.file = "faecher.txt"

		
		self.entries = self.loadEntries()

	def sendMessage(self, update, message):
		update.message.reply_text(message)

	def start(self, bot, update):
		self.sendMessage(update, """
	        Willkommen {}
	Befehle:
	/add FACH um ein neues Fach erstellen

	        """.format(update.message.from_user.first_name))

	def hello(self, bot, update):
	    self.sendMessage(update,
	        'Hello {}'.format(update.message.from_user.first_name))

	def add(self, bot, update, args):
		print('add')
		if len(args) != 1:
			self.errorHandler(update, "Gib bitte genau ein Fach an!")
			return
		elif args[0] == " ":
			self.errorHandler(update, "Gib bitte genau ein Fach an!")
			return
		if args[0] not in self.entries:
			self.entries.append(args[0])
		else:
			self.errorHandler(update, "Fach existiert bereits!")
			return

		self.saveEntry(args[0])

		self.sendMessage(update, str(args[0]) + ' wurde hinzugefügt. ')

	def errorHandler(self, update, error):
		self.sendMessage(update, "Fehler: " + error)

	def deleteFach(self, bot, update, args):
		print('del')
		fach = args[0]
		if fach not in self.entries:
			self.errorHandler(update, "Verschrieben? Dieses Fach existiert nicht!")
		else:
			self.entries.remove(fach)
			self.saveEntries()
			self.sendMessage(update, fach + "wurde gelöscht!")

	def saveEntries(self):
		with open(self.file, "a") as file:
			file.write("")

		return

	def saveEntry(self, entry):
		with open(self.file, "w") as file:
			for entry in self.entries:
				file.write(entry + "\n")

	def loadEntries(self):
		with open(self.file, "r") as file:
			entries = file.readlines()
		entries = [i[:-1] for i in entries]
		print(entries)
		return entries


b = UniBot()
updater = Updater('773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')

updater.dispatcher.add_handler(CommandHandler('hello', b.hello))
updater.dispatcher.add_handler(CommandHandler('start', b.start))
updater.dispatcher.add_handler(CommandHandler('add', b.add, pass_args = True))
updater.dispatcher.add_handler(CommandHandler('delete', b.deleteFach, pass_args = True))

updater.start_polling()
updater.idle()