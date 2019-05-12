#!/usr/bin/python
# -*- coding: UTF-8 -*-
#    TG Photo RSS-Feed Bot
#    Copyright (C) 2019  Paul
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mysql.connector
import datetime
import html
import uuid
import os
import config as cfg
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
try:
    cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'], host='127.0.0.1', database=cfg.mysql['db'])
except mysql.connector.Error as err:
    print(err)
cursor = cnx.cursor()
def photofunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
        update.message.reply_text('Okidoki')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_id = update.message.photo[-1].file_id
        photo = bot.getFile(file_id)
        imgfilename = uuid.uuid4().hex
        photo.download(cfg.imgsavepath+imgfilename)
        if update.message.caption != None:
            captioneintrag = html.escape(update.message.caption)
        else:
            captioneintrag = ''
        eintrag = "INSERT INTO `instatgbot` (`title`, `text`, `link`, `imgfile`, `user`, `timestamp`) VALUES (%s, %s, %s, %s, %s, %s)"
        eintrag_data = (captioneintrag, '', '', imgfilename, update.message.from_user.id, now)
        cursor.execute(eintrag, eintrag_data)
        abfrage = "SELECT `id`, `imgfile` from `instatgbot` WHERE DATEDIFF(`timestamp`, %s) > %s"
        abfrage_data = (now, cfg.deletedaydiff)
        cursor.execute(abfrage, abfrage_data)
        for (id, imgfile) in cursor:
            filepath = cfg.imgsavepath+imgfile
            if os.path.exists(filepath):
                os.remove(filepath)
            eintrag = "DELETE FROM `instatgbot` WHERE `id` LIKE %s;"
            eintrag_data = (id)
            cursor.execute(eintrag, eintrag_data)
        cnx.commit()
    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))

def startfunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
    	update.message.reply_text('Huhu, mit diesem Bot kannst du Instaposts erstellen \n\nWenn du diesem Bot ein Bild schickst wird die Bild Unterschrift / Beschreibung als Instagrampost verwendet.')
    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))
    bot.send_message(chat_id=update.message.chat.id, text='TG Photo RSS-Feed Bot  Copyright (C) 2019  Paul \nThis program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome to redistribute it under certain conditions; for details see https://gitlab.roteserver.de/Humorhenker/tg-photo-rss-feed-bot/blob/master/LICENSE', disable_web_page_preview=True)

bot_key = cfg.bot_key
updater = Updater(bot_key)

updater.dispatcher.add_handler(CommandHandler('start', startfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photofunc))

updater.start_polling()
updater.idle()
