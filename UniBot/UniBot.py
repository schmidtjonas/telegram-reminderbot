from telegram.ext import Updater, CommandHandler, MessageHandler
from datetime import datetime


class Entry:
	def __init__(self, fach, ersteller, subscribers = []):
		print("create Entry")
		self.fach = fach
		self.ersteller = ersteller
		self.datum = datetime.now().strftime('%Y-%m-%d')
		self.subscribers = subscribers
		#self.save()
		print(self)


	def save(self):
		print("save",self.fach)
		with open(file, "a") as f:
			
				f.write(str(self) + "\n")

		return

	def __str__(self):
		return self.fach + "|" + str(self.ersteller) + "|" + str(self.datum) + "|" + str(self.subscribers)

	def __repr__(self):
		return self.fach




class UniBot:
	def __init__(self):

		
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

		args = " ".join(args)

		if args in self.entries:
			self.errorHandler(update, "Fach existiert bereits!")
			return

		print(args, update.message.from_user.id)

		e = Entry(args, str(update.message.from_user.id))
		self.entries.append(e)

		e.save()

		self.sendMessage(update, str(args) + ' wurde hinzugefügt. ')

	def errorHandler(self, update, error):
		self.sendMessage(update, "Fehler: " + error)

	def deleteFach(self, bot, update, args):
		print('del')
		fach = " ".join(args)
		entry = self.findEntry(fach)
		if entry == None:
			return
		if str(update.message.from_user.id) != entry.ersteller:
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")
			return
		self.entries.remove(entry)
		self.saveEntries()
		self.sendMessage(update, fach + " wurde gelöscht!")

	def saveEntries(self):
		with open(file, "w") as f:
			for entry in self.entries:
				f.write(str(entry) + "\n")

		return


	def loadEntries(self):
		with open(file, "r") as f:
			fileinhalt = f.readlines()


		entries = []
		for entry in fileinhalt:
			e = entry.split("|")
			entries.append(Entry(e[0],e[1]))

		print(entries)
		return entries


####################
file = "faecher.txt"
b = UniBot()
updater = Updater('773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k')

updater.dispatcher.add_handler(CommandHandler('hello', b.hello))
updater.dispatcher.add_handler(CommandHandler('start', b.start))
updater.dispatcher.add_handler(CommandHandler('add', b.add, pass_args = True))
updater.dispatcher.add_handler(CommandHandler('delete', b.deleteFach, pass_args = True))

updater.start_polling()
updater.idle()