from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot, Chat
from datetime import datetime
import pickle
import time

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
