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
    if update.message.caption != None:
        update.message.reply_text(update.message.caption)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_id = update.message.photo[-1].file_id
    photo = bot.getFile(file_id)
    imgpath = "J:\Documents\Geek\Python\projects\insta-bot\img.jpg"
    photo.download(imgpath)
    with open(imgpath, "rb") as imageFile:
        photoB = imageFile.read()
    eintrag = "INSERT INTO `instatgbot` (`title`, `text`, `image`, `link`, `user`, `timestamp`) VALUES (%s, %s, %s, %s, %s, %s)"
    eintrag_data = (html.escape(update.message.caption), '', photoB, '', update.message.from_user.id, now)
    cursor.execute(eintrag, eintrag_data)
    cnx.commit()

def startfunc(bot, update):
    update.message.reply_text('Huhu, hier kannst du Instaposts quasi erstellen \n\nWenn du diesem Bot ein Bild schickst wird die Bild Unterschrift / Beschreibung als Instagrampost verwendet')


bot_key = sys.argv[1]
updater = Updater(bot_key)

updater.dispatcher.add_handler(CommandHandler('start', startfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, testfunc))

updater.start_polling()
updater.idle()