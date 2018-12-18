import pickle

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from entry import *
from task import *


def sendOperationtoAdmins(message):
	print(message)

	bot.send_message(chat_id=group, text=message)




class UniBot:
	def __init__(self, createNewFile = False):

		self.lukas = '507305205'
		self.admin = ['691400978', '636733660', '672114483'] #jonas, rohan, robert
		self.entries = []
		if not createNewFile:
			self.loadEntriesPkl()
			print(self.entries)
		else:
			self.saveEntriesPkl()

		self.updater = Updater(token)

		#self.spamLukas()

		self.handler = [CommandHandler('hello', self.hello),
						CommandHandler('start', self.start),
						CommandHandler('add', self.add, pass_args = True),
						CommandHandler('delete', self.deleteFach, pass_args = True),
						CommandHandler('faecher', self.faecher),
						CommandHandler('subscribe', self.subscribe, pass_args = True),
						CommandHandler('unsubscribe', self.unsubscribe, pass_args = True),
						CommandHandler('status', self.status),
						CommandHandler('input', self.input)]


		self.addCmdHandler()
		self.updater.start_polling()
		#self.updater.idle() #keine Ahnung was das macht aber es geht auch ohne ^^


		return

		
	def addCmdHandler(self):
		for h in self.handler:
			self.updater.dispatcher.add_handler(h)

	def rmCmdHandler(self):
		for h in self.handler:
			self.updater.dispatcher.remove_handler(h)


	def sendMessage(self, update, message):
		update.message.reply_text(message)


	def errorHandler(self, update, error):
		self.sendMessage(update, "Fehler: " + error)

	def error(self, bot, update, telegramError):
		print(update.message.text, telegramError)



	def start(self, bot, update):
		self.sendMessage(update, """
	        Willkommen {}
	**Befehle:**
	/add FACH um ein neues Fach erstellen
	/delete FACH um ein Fach zu löschen
	/faecher um eine Übersicht der verfügbaren Fächer zu erhalten
	/subscribe um ein bestehendes Fach zu abbonieren
	/newtask um einen neuen Task anzulegen

	        """.format(update.message.from_user.first_name))



	def hello(self, bot, update):
	    self.sendMessage(update,
	        'Hello {}'.format(update.message.from_user.first_name))


#### add und delete Fach


	def add(self, bot, update, args):
		print('add', args)

		fach = " ".join(args)
		print(fach)

		if args == []:
			self.errorHandler(update, "Bitte gib ein gültiges Fach ein. Das Fach darf kein Leerzeichen am Anfang oder Ende enthalten")
			return

		if self.findEntry(fach) != None:
			self.errorHandler(update, "Fach existiert bereits!")
			return

		sendOperationtoAdmins('add: '+fach+ ', ' + str(update.message.from_user.first_name))

		e = Entry(fach, str(update.message.from_user.id))
		self.entries.append(e)
		self.saveEntriesPkl()

		#e.save()

		self.sendMessage(update, str(fach) + ' wurde hinzugefügt. ')




	def deleteFach(self, bot, update, args):
		print('del')
		fach = " ".join(args)
		entry = self.findEntry(fach)


		if entry == None:
			print('error')
			self.errorHandler(update, "Verschrieben? Dieses Fach existiert nicht!")
			return

		if str(update.message.from_user.id) != entry.ersteller and str(update.message.from_user.id) not in self.admin:
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")
			return


		self.entries.remove(entry)
		self.saveEntriesPkl()
		self.sendMessage(update, fach + " wurde gelöscht!")
		sendOperationtoAdmins('del: '+fach+ ', '+ str(update.message.from_user.first_name))



###subscribe und unsubscribe


	def subscribe(self, bot, update, args):
		print("sub")
		fach = " ".join(args)

		print(fach)
		entry = self.findEntry(fach)

		if entry == None:
			print('error')
			self.errorHandler(update, "Verschrieben? Dieses Fach existiert nicht!")
			return

		if entry.addSubcriber(str(update.message.from_user.id)):
			self.saveEntriesPkl()
			self.sendMessage(update, "Du hast "+ fach + " abonniert!")
			sendOperationtoAdmins('sub: '+fach+ ', '+ str(update.message.from_user.first_name))
		else:
			self.errorHandler(update, "Du hast dieses Fach bereits abonniert!")

	def unsubscribe(self, bot, update, args):
		print("unsub")
		fach = " ".join(args)

		print(fach)
		entry = self.findEntry(fach)

		if entry == None:
			print('error')
			self.errorHandler(update, "Verschrieben? Dieses Fach existiert nicht!")
			return
		if entry.delSubscriber(str(update.message.from_user.id)):
			self.saveEntriesPkl()
			self.sendMessage(update, "Du hast "+ fach + " deabonniert!")
			sendOperationtoAdmins('desub: '+fach+ ', '+ str(update.message.from_user.first_name))

		else:
			self.errorHandler(update, "Du hast dieses Fach nicht abonniert!")





	def addtask(self, bot, update, args, job_queue, chat_data):

		fach = " ".join(args[2:])
		print("addtask", args[0], args[1], fach)

		entry = self.findEntry(fach)

		job = job_queue.run_once(entry.remind, int(args[0]), context=args[1])
		chat_data['job'] = job

		self.sendMessage(update, "Du hast die Task "+ args[1] + " in " + fach + " hinzugefügt!")
		sendOperationtoAdmins('addtask: '+args[1] +' in ' +fach+ ', '+ str(update.message.from_user.first_name) + ' in ' + args[0])




	def input(self, bot, update):
		self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))


	def echo(self, bot, update):
		update.message.reply_text(update.message.text)


	def findEntry(self, fach):  #find Entryobj by fach
		print('find')
		for i in self.entries:
			if i.fach == fach:
				return i
		
		return None

###save und load

	def saveEntriesPkl(self):
		with open('data.pkl', 'wb') as output:
			for entry in self.entries:
				pickle.dump(entry, output, pickle.HIGHEST_PROTOCOL)

	def loadEntriesPkl(self):
		with open('data.pkl', 'rb') as input:
			while True:
				try:
					e = pickle.load(input)
					print(e.fach)
					self.entries.append(e)
				except:
					break



	def status(self, bot, update): #Outputs all Entries to telegram
		print("status")
		if str(update.message.chat_id) == group:
			string = ''
			for entry in self.entries:
				string += str(entry) + '\n\n'
			sendOperationtoAdmins(string)
			return

		elif str(update.message.from_user.id) in self.admin:
			string = ''
			for entry in self.entries:
				string += str(entry) + '\n\n'
			self.sendMessage(update, string)
			return

		else:
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")




	def faecher(self, bot, update):
		text = "**Übersicht aller verfügbaren Fächer: ** \n ----------------------------------------------------------- \n"

		for entry in self.entries:
			text += entry.fach + "\n" 

		self.sendMessage(update, text)





	def spamLukas(self):
		time.sleep(3)
		while True:
			print("spam")
			time.sleep(0.1)
			#print("Hallo"+ self.lukas)
			bot.sendMessage(chat_id=self.lukas, text="Hier ist CT. Du hast 5,0 in Mathe.")



####################
token = '734149613:AAE5mrKSu_FIaVaZJFPpn0TUYowJSabs-uI'

token2 = '773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k'

bot = Bot(token)


testbot = Bot(token2)

group = '-385326743'
chat = Chat(group, 'group')


b = UniBot() # True als Parameter erstellt ein komplett neues File




