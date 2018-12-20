import pickle
from datetime import datetime, timedelta

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from entry import *
from task import *


def sendOperationtoAdmins(message):
	print(message)
	bot.send_message(chat_id=group, text=message)


class FachFilter(BaseFilter):
	def filter(self, message):
		for i in b.entries:
			if i.fach == message.text:
				return True
		return False


class ZeitFilter(BaseFilter):
	def filter(self, message):
		try:
			zeit = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
			return zeit > datetime.now()
		except:
			return False

class NotZeitFilter(BaseFilter):
	def filter(self, message):
		try:
			zeit = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
			return zeit < datetime.now()
		except:
			return True


# erlaube operation nur für admins: @restricted vor Function

def restricted(func):
	def wrapped(self, bot, update, *args, **kwargs):
		user_id = str(update.effective_user.id)
		if user_id not in admins and str(update.message.chat_id) != group:
			print("Unauthorized access denied for {}.".format(user_id))
			self.errorHandler(update, "Du bist nicht berechtigt dies zu tun!")
			return
		return func(self, bot, update, *args, **kwargs)

	return wrapped


# suche den passenden Entry oder liefere einen Error

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
	def __init__(self, createNewFile=False):
		self.lukas = '507305205'
		self.entries = []
		self.newtasks = {}
		if not createNewFile:
			self.loadEntriesPkl()
			print(self.entries)
		else:
			self.saveEntriesPkl()

		self.updater = Updater(token)

		# self.spamLukas()

		self.handler = [CommandHandler('hello', self.hello),
						CommandHandler('add', self.add, pass_args=True),
						CommandHandler('delete', self.deleteFach, pass_args=True),
						CommandHandler('faecher', self.faecher),
						CommandHandler('subscribe', self.subscribe, pass_args=True),
						CommandHandler('unsubscribe', self.unsubscribe, pass_args=True),
						CommandHandler('status', self.status),
						CommandHandler('newtask', self.newtask),

						CommandHandler('start', self.start),
						CommandHandler('vorschlag', self.vorschlag, pass_args=True),
						CommandHandler('report', self.report, pass_args=True),
						CommandHandler('help', self.help)]

		fachfilter = FachFilter()
		zeitfilter = ZeitFilter()
		notzeitfilter = NotZeitFilter()


		self.conv_handler = ConversationHandler(
			entry_points=[CommandHandler('start', self.start)],
			states={
				0: self.handler,

				1: [CommandHandler('c', self.cancel),
				    MessageHandler(fachfilter, self.inputTaskTitle),
				    CallbackQueryHandler(self.button)],

				2: [CommandHandler('c', self.cancel),
				    MessageHandler(Filters.text, self.inputTaskTime)],

				3: [CommandHandler('c', self.cancel),
				    MessageHandler(zeitfilter, self.taskCreated, pass_job_queue=True, pass_chat_data=True),
				    MessageHandler(notzeitfilter, self.error)]
			},

			fallbacks=[MessageHandler(Filters.command, self.help)])

		# self.addCmdHandler()

		self.updater.dispatcher.add_handler(self.conv_handler)
		self.updater.dispatcher.add_handler(CommandHandler('report', self.report, pass_args=True))
		self.updater.dispatcher.add_handler(CommandHandler('vorschlag', self.vorschlag, pass_args=True))
		self.updater.dispatcher.add_handler(MessageHandler(Filters.command, self.help))
		self.updater.dispatcher.add_handler(CommandHandler('help', self.help))
		self.updater.dispatcher.add_handler(CommandHandler('start', self.start))



		self.updater.start_polling()
		# self.updater.idle() #keine Ahnung was das macht aber es geht auch (nur) ohne ^^

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

	def inputTaskTitle(self, bot, update):
		self.sendMessage(update.callback_query, "Bitte gib ein Titel an!\n/c zum abbrechen")
		return 2

	def inputTaskTime(self, bot, update):
		self.newtasks[str(update.message.from_user.id)].append(update.message.text)

		self.sendMessage(update, "Bitte gib Datum und Uhrzeit des Termins an! Du wirst gleich gefragt wann die Abonennten erinnert werden sollen.\nFormat: dd.mm.yyyy HH:MM\n/c zum abbrechen")

		return 3

	def inputTaskRemindTime(self, bot, update):
		zeit = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
		self.newtasks[str(update.message.from_user.id)].append(zeit)

		keyboard = [[InlineKeyboardButton("am Termin", callback_data=0)]]

		# wenn die Termine in der Zukunft liegen
		if zeit - timedelta(hours= 3) > datetime.now():
					keyboard.append([InlineKeyboardButton("3 Stunden vorher", callback_data=1)])
		if (zeit - timedelta(day=1)).replace(hour = 20) > datetime.now():
					keyboard.append([InlineKeyboardButton("am Abend vorher", callback_data=2)])
					
		reply_markup = InlineKeyboardMarkup(keyboard)

		update.message.reply_text('Wann soll die Erinnerung gesendet werden?', reply_markup=reply_markup)
		return 4

	def buttonremind(self, bot, update, job_queue, chat_data):
		query = update.callback_query
		print(query.data)
		bot.delete_message(chat_id=query.message.chat_id,
		message_id=query.message.message_id)

		self.newtasks[str(query.message.chat_id)].append(query.data)

		return self.inputTaskTitle(bot, update, job_queue, chat_data)


	def taskCreated(self, bot, update, job_queue, chat_data):
		data = self.newtasks[str(update.message.from_user.id)]

		zeit = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
		t = Task(str(update.message.from_user.id), data[0], data[1], zeit)

		entry = self.findEntry(data[0])

		job = job_queue.run_once(entry.remind, zeit, context=data[1])
		chat_data['job'] = job

		self.sendMessage(update, 'Du hast die Task "' + data[1] + '" in "' + data[0] + '" hinzugefügt!')
		sendOperationtoAdmins(
			'addtask: ' + data[1] + ' in ' + data[0] + ', ' + str(update.message.from_user.first_name) + ' in ' + str(
				zeit))

		return 0

	def newtask(self, bot, update):
		keyboard = []
		# man sieht nur die Entries zu denen man subscribt ist
		subed = [i for i in self.entries if str(update.message.from_user.id) in i.subscribers]

		if not subed: # subed == []
			self.errorHandler(update, "Du hast kein Fach abonniert! Nutze /subscribe FACH zum abonnieren")
			return 0


		for entry in subed:
			keyboard.append([InlineKeyboardButton(entry.fach, callback_data=entry.fach)])

		reply_markup = InlineKeyboardMarkup(keyboard)

		update.message.reply_text('Bitte wähle ein Fach:', reply_markup=reply_markup)

		return 1

	def button(self, bot, update):
		query = update.callback_query
		print(query.data)
		bot.edit_message_text(text="Du hast das Fach *{}* gewählt".format(query.data),
		                      chat_id=query.message.chat_id,
		                      message_id=query.message.message_id,
		                      parse_mode=ParseMode.MARKDOWN)

		self.newtasks[str(query.message.chat_id)] = [query.data]

		return self.inputTaskTitle(bot, update)

	def sendMessage(self, update, message):
		update.message.reply_text(message)

	def errorHandler(self, update, error):
		self.sendMessage(update, "Fehler: " + error)

	def error(self, bot, update):
		self.errorHandler(update, "Bitte gib eine Nachricht ein, die ich verstehe!")

	def start(self, bot, update):
		self.sendMessage(update, """
			Willkommen {}, \nich soll in Zukunft an Übungsabgaben und Veranstaltungen erinnern. 
Du kannst neue Fächer anlegen und andere Fächer abonnieren um Reminder zu erhalten. Außerdem kannst du Tasks erstellen. Alle Abonennten des Fachs werden dann an den Termin erinnert.
Bei Fehlern oder Verbesserungsvorschlägen nutze gerne die entsprechenden Befehle!
			\n---- Befehle: ----
			/add FACH um ein neues Fach erstellen
			/delete FACH um ein Fach zu löschen
			/faecher um eine Übersicht der Fächer zu erhalten
			/subscribe FACH um ein Fach zu abonnieren
			/unsubscribe FACH um ein Fach zu deabonnieren
			/newtask um eine neue Task anzulegen
			/report BUG um einen Fehler zu melden
			/vorschlag TEXT für einen Verbesserungsvorschlag

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

		sendOperationtoAdmins('add: ' + fach + ', ' + str(update.message.from_user.first_name))
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
		sendOperationtoAdmins('del: ' + entry.fach + ', ' + str(update.message.from_user.first_name))

	###subscribe und unsubscribe

	@lookUpEntry
	def subscribe(self, bot, update, entry):
		print("sub")

		if entry.addSubcriber(str(update.message.from_user.id)):
			self.saveEntriesPkl()
			self.sendMessage(update, "Du hast " + entry.fach + " abonniert!")
			sendOperationtoAdmins('sub: ' + entry.fach + ', ' + str(update.message.from_user.first_name))
		else:
			self.errorHandler(update, "Du hast dieses Fach bereits abonniert!")

	@lookUpEntry
	def unsubscribe(self, bot, update, entry):
		print("unsub")

		if entry.delSubscriber(str(update.message.from_user.id)):
			self.saveEntriesPkl()
			self.sendMessage(update, "Du hast " + entry.fach + " deabonniert!")
			sendOperationtoAdmins('desub: ' + entry.fach + ', ' + str(update.message.from_user.first_name))

		else:
			self.errorHandler(update, "Du hast dieses Fach nicht abonniert!")

	def findEntry(self, fach):  # find Entryobj by fach
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
					self.entries.append(e)
				except:
					break

	@restricted
	def status(self, bot, update):  # Outputs all Entries to telegram
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
			bot.sendMessage(chat_id=self.lukas, text="Hier ist CT. Du hast 5,0 in Mathe.")

	def report(self, bot, update, args):
		if not args:
			self.errorHandler(update, "Bitte schreib eine kurze Nachricht!")
			return
		with open(reportfile, "a") as file:
			txt = " ".join(args) + "\n"
			file.write(txt)
			self.sendMessage(update, "Vielen Danke für deine Hilfe!")
			sendOperationtoAdmins("report: " + txt)

	def vorschlag(self, bot, update, args):
		if not args:
			self.errorHandler(update, "Bitte schreib eine kurze Nachricht!")
			return
		with open(vorschlagfile, "a") as file:
			txt = " ".join(args) + "\n"
			file.write(txt)
			self.sendMessage(update, "Vielen Danke für deine Hilfe!")
			sendOperationtoAdmins("vorschlag: " + txt)

	def help(self, bot, update):
		self.sendMessage(update, """---- Befehle: ----
			/add FACH um ein neues Fach erstellen
			/delete FACH um ein Fach zu löschen
			/faecher um eine Übersicht der Fächer zu erhalten
			/subscribe FACH um ein Fach zu abonnieren
			/unsubscribe FACH um ein Fach zu deabonnieren
			/newtask um einen neuen Task anzulegen
			/report BUG um einen Fehler zu melden
			/vorschlag TEXT für einen Verbesserungsvorschlag
			/c falls du /newtask abbrechen möchtest
			/help für Befehlsliste
			/start falls gar nichts funktioniert""")
		return 0



###########################################################################

token = '734149613:AAE5mrKSu_FIaVaZJFPpn0TUYowJSabs-uI'
token2 = '773918644:AAHnwfrZFkwXJIW0QuU6ibAOyOZ3NyGcL0k'
group = '-385326743'
admins = ['691400978', '636733660', '672114483']  # jonas, rohan, robert

reportfile = "report.txt"
vorschlagfile = "vorschlag.txt"

###########################################################################

bot = Bot(token)

testbot = Bot(token2)

chat = Chat(group, 'group')

b = UniBot()  # True als Parameter erstellt ein komplett neues File
