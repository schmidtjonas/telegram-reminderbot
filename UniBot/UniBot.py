import pickle

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, ConversationHandler

from entry import *
from task import *


def sendOperationtoAdmins(message):
	print(message)

	bot.send_message(chat_id=group, text=message)


class FachFilter(BaseFilter):
	def filter(self, message):
		print('filter')
		for i in b.entries:
			if i.fach == message.text:
				return True
		return False

#erlaube operation nur für admins: @restricted vor Function

def restricted(func):
	def wrapped(self, bot, update, *args, **kwargs):
		user_id = str(update.effective_user.id)
		if user_id not in admins or str(update.message.chat_id) != group:
			print("Unauthorized access denied for {}.".format(user_id))
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")
			return
		return func(self, bot, update, *args, **kwargs)
	return wrapped

#suche den passenden Entry oder liefere einen Error

def lookUpEntry(func):
	def wrapped(self, bot, update, args, *moreargs, **kwargs):
		fach = " ".join(args)
		entry = self.findEntry(fach)
		if entry is None:
			self.errorHandler(update, "Verschrieben? Dieses Fach existiert nicht!")
			return
		return func(self, bot, update, entry)
	return wrapped


#############


class UniBot:
	def __init__(self, createNewFile = False):

		self.lukas = '507305205'
		self.entries = []
		if not createNewFile:
			self.loadEntriesPkl()
			print(self.entries)
		else:
			self.saveEntriesPkl()

		self.updater = Updater(token)

		#self.spamLukas()

		self.handler = [CommandHandler('hello', self.hello),
						
						CommandHandler('add', self.add, pass_args = True),
						CommandHandler('delete', self.deleteFach, pass_args = True),
						CommandHandler('faecher', self.faecher),
						CommandHandler('subscribe', self.subscribe, pass_args = True),
						CommandHandler('unsubscribe', self.unsubscribe, pass_args = True),
						CommandHandler('status', self.status),
						CommandHandler('input', self.input)
						]

		fachfilter = FachFilter()

		self.conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', self.start)],

		states={
			0: self.handler,

			1: [CommandHandler('c', self.cancel),
				MessageHandler(fachfilter, self.inputTaskTitle), 
				CommandHandler('faecher', self.faecher)],

			2: [CommandHandler('c', self.cancel)
				]
		},

		fallbacks=[CommandHandler('stop', self.stop)])


		#self.addCmdHandler()

		self.updater.dispatcher.add_handler(self.conv_handler)

		self.updater.start_polling()
		#self.updater.idle() #keine Ahnung was das macht aber es geht auch (nur) ohne ^^

		return

		
	def addCmdHandler(self):
		for h in self.handler:
			self.updater.dispatcher.add_handler(h)

	def stop(self, bot, update):
		self.errorHandler(update, 'Abbruch')
		return 0

	def cancel(self, bot, update):
		self.sendMessage(update, 'Die Task wurde nicht erstellt.')
		return 0

	def input(self, bot, update):
		self.sendMessage(update, "Bitte gib ein Fach an!\n/faecher um alle Fächer zu sehen\n/c zum abbrechen")
		print(0)
		return 1

	def inputTaskTitle(self, bot, update):
		self.sendMessage(update, "Bitte gib ein Titel an!\n/c zum abbrechen")
		print(update.message.text)
		print(1)
		return 2

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
		return 0




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


		e = Entry(fach, str(update.message.from_user.id))
		self.entries.append(e)
		self.saveEntriesPkl()

		#e.save()
		sendOperationtoAdmins('add: '+fach+ ', ' + str(update.message.from_user.first_name))
		self.sendMessage(update, str(fach) + ' wurde hinzugefügt. ')



	@lookUpEntry
	def deleteFach(self, bot, update, entry):
		print('del')
		
		if str(update.message.from_user.id) != entry.ersteller and str(update.message.from_user.id) not in admins:
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")
			return

		self.entries.remove(entry)
		self.saveEntriesPkl()
		self.sendMessage(update, entry.fach + " wurde gelöscht!")
		sendOperationtoAdmins('del: '+entry.fach+ ', '+ str(update.message.from_user.first_name))



###subscribe und unsubscribe

	@lookUpEntry
	def subscribe(self, bot, update, entry):
		print("sub")

		if entry.addSubcriber(str(update.message.from_user.id)):
			self.saveEntriesPkl()
			self.sendMessage(update, "Du hast "+ entry.fach + " abonniert!")
			sendOperationtoAdmins('sub: '+entry.fach+ ', '+ str(update.message.from_user.first_name))
		else:
			self.errorHandler(update, "Du hast dieses Fach bereits abonniert!")

	@lookUpEntry
	def unsubscribe(self, bot, update, entry):
		print("unsub")

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



	def findEntry(self, fach):  #find Entryobj by fach
		print('find')
		for i in self.entries:
			if i.fach == fach:
				return i
		
		return None

	def existsEntry(self, bot, update):
		print('exists')
		message = update.message.text
		for i in self.entries:
			if i.fach == message:
				return True
		
		return False

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


	@restricted
	def status(self, bot, update): #Outputs all Entries to telegram
		print("status")
		string = ''
		for entry in self.entries:
			string += str(entry) + '\n\n'
		self.sendMessage(update, string)


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





###########################################################################

token = '734149613:AAE5mrKSu_FIaVaZJFPpn0TUYowJSabs-uI'
token2 = '773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k'
group = '-385326743'
admins = ['691400978', '636733660', '672114483'] #jonas, rohan, robert

###########################################################################

bot = Bot(token)

testbot = Bot(token2)

chat = Chat(group, 'group')



b = UniBot() # True als Parameter erstellt ein komplett neues File




