from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot, Chat
from datetime import datetime
import time


class Task:
	def __init__(self, ersteller, fach, titel, zeit, reminder):
		self.ersteller = ersteller

		self.titel = titel
		self.zeit = zeit
		self.fach = fach

		self.reminder = reminder



	def __str__(self):
		return self.fach * " | " + self.titel + " | " + str(self.ersteller) + " | " + str(self.zeit) + str(self.reminder)
