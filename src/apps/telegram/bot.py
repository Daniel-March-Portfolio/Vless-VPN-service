from django.conf import settings
from telebot import TeleBot

bot = TeleBot(token=settings.BOT_TOKEN)
