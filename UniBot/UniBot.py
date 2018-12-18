from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot, Chat
from datetime import datetime
import pickle
import time


def sendOperationtoAdmins(message):
	print(message)

	bot.send_message(chat_id=group, text=message)



class Entry:
	def __init__(self, fach, ersteller, datum = None,  subscribers = []):
		print("create Entry")
		self.fach = fach
		self.ersteller = ersteller

		if datum == None:
			self.datum = datetime.now().strftime('%Y-%m-%d')
		else:
			self.datum = datum

		self.subscribers = subscribers
		#self.save()
		print(self)

	def addSubcriber(self, sub):
		if sub not in self.subscribers:
			self.subscribers.append(sub)
			return True
		return False

	def delSubscriber(self, sub):
		if sub in self.subscribers:
			self.subscribers.remove(sub)
			return True
		return False

	def __str__(self):
		return self.fach + " | " + str(self.ersteller) + " | " + str(self.datum) + " | " + str(self.subscribers)[1:-1]

	def __repr__(self):
		return self.fach


	def remind(self, bot, job):
		print('remind')
		for user in self.subscribers:
			bot.sendMessage(chat_id=user, text="Reminder " + self.fach + ": " + job.context)

class Task:
	def __init__(self, ersteller, titel, datum , uhrzeit, reminder = None):
		self.ersteller = ersteller

		self.titel = titel
		self.datum = datum
		self.uhrzeit = uhrzeit

		if reminder == none:
			self.reminder = int(datetime.datetime.strptime(self.datum +' ' +self.uhrzeit, '%Y-%m-%d %H:%M'))
		else:
			self.reminder = reminder

		


	def __str__(self):
		return self.titel + "|" + str(self.ersteller) + "|" + str(self.datum) + "|" + str(self.uhrzeit) +"|" + str(self.reminder)

class UniBot:
	def __init__(self, createNewFile = False):

		self.lukas = '507305205'
		self.robert = '672114483'
		self.admin = ['691400978', '636733660'] #jonas, rohan
		self.entries = []
		if not createNewFile:
			self.loadEntriesPkl()
			print(self.entries)
		else:
			self.saveEntriesPkl()

		updater = Updater(token)

		#self.spamLukas()


		updater.dispatcher.add_handler(CommandHandler('hello', self.hello))
		updater.dispatcher.add_handler(CommandHandler('start', self.start))
		updater.dispatcher.add_handler(CommandHandler('add', self.add, pass_args = True))
		updater.dispatcher.add_handler(CommandHandler('delete', self.deleteFach, pass_args = True))
		updater.dispatcher.add_handler(CommandHandler('faecher', self.faecher))
		updater.dispatcher.add_handler(CommandHandler('subscribe', self.subscribe, pass_args = True))
		updater.dispatcher.add_handler(CommandHandler('unsubscribe', self.unsubscribe, pass_args = True))

		updater.dispatcher.add_handler(CommandHandler('newtask', self.newTask))
		updater.dispatcher.add_handler(CommandHandler('newtask-title', self.taskTitle))
		updater.dispatcher.add_handler(CallbackQueryHandler(self.button))
		updater.dispatcher.add_handler(CommandHandler('addtask', self.addtask, pass_args = True, pass_job_queue=True, pass_chat_data=True))


		updater.dispatcher.add_handler(CommandHandler('status', self.status))




		updater.start_polling()
		updater.idle()

		

	def sendMessage(self, update, message):
		update.message.reply_text(message)

	def start(self, bot, update):
		self.sendMessage(update, """
	        Willkommen {}
	**Befehle:**
	/add FACH um ein neues Fach erstellen
	/delete FACH um ein Fach zu löschen
	/subscribe um ein bestehendes Fach zu abbonieren
	/newtask um einen neuen Task anzulegen

	        """.format(update.message.from_user.first_name))

	def hello(self, bot, update):
	    self.sendMessage(update,
	        'Hello {}'.format(update.message.from_user.first_name))

	def add(self, bot, update, args):
		print('add')

		fach = " ".join(args)

		if self.findEntry(fach) != None:
			self.errorHandler(update, "Fach existiert bereits!")
			return

		sendOperationtoAdmins('add: '+fach+ ', ' + str(update.message.from_user.first_name))

		e = Entry(fach, str(update.message.from_user.id))
		self.entries.append(e)
		self.saveEntriesPkl()

		#e.save()

		self.sendMessage(update, str(fach) + ' wurde hinzugefügt. ')

	def errorHandler(self, update, error):
		self.sendMessage(update, "Fehler: " + error)

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

	def faecher(self, bot, update):
		text = "**Übersicht aller verfügbaren Fächer: **\n \n"

		for entry in self.entries:
			text += "\n" + entry.fach

		self.sendMessage(update, text)


	def addtask(self, bot, update, args, job_queue, chat_data):

		fach = " ".join(args[2:])
		print("addtask", args[0], args[1], fach)

		entry = self.findEntry(fach)

		job = job_queue.run_once(entry.remind, int(args[0]), context=args[1])
		chat_data['job'] = job

		self.sendMessage(update, "Du hast die Task "+ args[1] + " in " + fach + " hinzugefügt!")
		sendOperationtoAdmins('addtask: '+args[1] +' in ' +fach+ ', '+ str(update.message.from_user.first_name) + ' in ' + args[0])




	def findEntry(self, fach):
		print('find')
		for i in self.entries:
			if i.fach == fach:
				return i
		
		return None

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

	def newTask(self, bot, update):
		print("Hi")
		keyboard = [
			[InlineKeyboardButton("Titel", callback_data='1')],
			[InlineKeyboardButton("Datum", callback_data='2'),InlineKeyboardButton("Uhrzeit", callback_data='3')]]

		reply_markup = InlineKeyboardMarkup(keyboard)


		update.message.reply_text('NEUEN TASK ERSTELLEN \n '+
			'---------------------------------------------------\n' +
			'1.Gib zuerst den Titel des Tasks an \n' +
			'2. Gib dann Datum und Uhrzeit des Abgabedatums an \n' +
			'Anschließend wirst du gefragt werden, ob du noch ein seperates Reminder-Datum angeben möchstest', reply_markup=reply_markup)

	def button(self, bot, update):

		query = update.callback_query

		if int(query.data) == 1:
			self.taskTitle
			return
		elif int(query.data) == 2:
			self.sendMessage(update, "Datum ändern: ")
			return
		elif int(query.data) == 3:
			self.sendMessage(update, "Uhrzeit ändern: ")
			return
		else:
			self.errorHandler(update, "Ein unerwarteter Fehler ist aufgetreten!")


	def taskTitle(self, bot, update):
		return

	def status(self, bot , update):
		print(1)
		print(str(update.message.chat_id) , str(update.message.from_user.id), group)
		if str(update.message.chat_id) == group:
			print(1)
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

	def spamLukas(self):
		time.sleep(3)
		while True:
			print("spam")
			time.sleep(0.1)
			#print("Hallo"+ self.lukas)
			bot.sendMessage(chat_id=self.robert, text="Hier ist CT. Du hast 5,0 in Mathe.")






####################
token = '734149613:AAE5mrKSu_FIaVaZJFPpn0TUYowJSabs-uI'

token2 = '773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k'

bot = Bot(token)


testbot = Bot(token2)

group = '-385326743'
chat = Chat(group, 'group')


b = UniBot() # True als Parameter erstellt ein komplett neues File




