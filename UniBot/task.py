from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot, Chat
from datetime import datetime
import pickle
import time


class Task:
	def __init__(self, ersteller, titel, datum , uhrzeit, fach, reminder = None):
		self.ersteller = ersteller

		self.titel = titel
		self.datum = datum
		self.uhrzeit = uhrzeit
		self.fach = fach

		if reminder == none:
			self.reminder = int(datetime.datetime.strptime(self.datum +' ' +self.uhrzeit, '%Y-%m-%d %H:%M'))
		else:
			self.reminder = reminder


	def __str__(self):
		return self. fach * "|" + self.titel + "|" + str(self.ersteller) + "|" + str(self.datum) + "|" + str(self.uhrzeit) +"|" + str(self.reminder)
