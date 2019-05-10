#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import mysql.connector
import datetime
import html
import uuid
import config as cfg
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
try:
    cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'], host='127.0.0.1', database=cfg.mysql['db'])
except mysql.connector.Error as err:
    print(err)
cursor = cnx.cursor()
def photofunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
        if update.message.caption != None:
            update.message.reply_text(update.message.caption)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_id = update.message.photo[-1].file_id
        photo = bot.getFile(file_id)
        imgfilename = uuid.uuid4().hex
        photo.download(cfg.imgsavepath+imgfilename)
        eintrag = "INSERT INTO `instatgbot` (`title`, `text`, `link`, `imgfile`, `user`, `timestamp`) VALUES (%s, %s, %s, %s, %s, %s)"
        eintrag_data = (html.escape(update.message.caption), '', '', imgfilename, update.message.from_user.id, now)
        cursor.execute(eintrag, eintrag_data)
        cnx.commit()
    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))

def startfunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
    	update.message.reply_text('Huhu, hier kannst du Instaposts quasi erstellen \n\nWenn du diesem Bot ein Bild schickst wird die Bild Unterschrift / Beschreibung als Instagrampost verwendet')
    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))

bot_key = cfg.bot_key
updater = Updater(bot_key)

updater.dispatcher.add_handler(CommandHandler('start', startfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photofunc))

updater.start_polling()
updater.idle()
