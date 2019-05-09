#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import mysql.connector
import datetime
import html
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
try:
    cnx = mysql.connector.connect(user=sys.argv[2], password=sys.argv[3], host='127.0.0.1', database=sys.argv[4])
except mysql.connector.Error as err:
    print(err)
cursor = cnx.cursor()
def testfunc(bot, update):
    update.message.reply_text(
    update.message.text)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    eintrag = "INSERT INTO `instatgbot` (`title`, `text`, `link`, `user`, `timestamp`) VALUES (%s, %s, %s, %s, %s)"
    eintrag_data = (html.escape(update.message.text.split('\n', 1)[0]), html.escape(update.message.text.split('\n', 1)[1]), '', update.message.from_user.id, now)
    cursor.execute(eintrag, eintrag_data)
    cnx.commit()

def startfunc(bot, update):
    update.message.reply_text('Huhu, hier kannst du Instaposts quasi erstellen \n\nBitte so vorhegehen: \nTitle\nText')

bot_key = sys.argv[1]
updater = Updater(bot_key)

updater.dispatcher.add_handler(CommandHandler('start', startfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.text, testfunc))

updater.start_polling()
updater.idle()
