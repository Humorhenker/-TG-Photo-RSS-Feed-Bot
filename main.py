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
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image
logging.basicConfig(filename=cfg.logpath, level=logging.INFO, filemode='w', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
def registermsg(msgid, postid, chatid):
    try:
        cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'], host='127.0.0.1', database=cfg.mysql['db'])
    except mysql.connector.Error as err:
        logging.error('MYSQL '+str(err))
    cursor = cnx.cursor(buffered=True)
    eintrag = "INSERT INTO `msg2post` (`postid`, `chatid`, `msgid`) VALUES (%s, %s, %s)"
    eintrag_data = (postid, chatid, msgid)
    cursor.execute(eintrag, eintrag_data)
    cnx.commit()
    cursor.close()
    cnx.close()

def dellastpost(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
        update.message.delete()
        try:
            cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'], host='127.0.0.1', database=cfg.mysql['db'])
        except mysql.connector.Error as err:
            logging.error('MYSQL '+str(err))
        cursor = cnx.cursor(buffered=True)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            abfrage = "SELECT `id`, `imgfile`, `timestamp`, TIME_TO_SEC(TIMEDIFF(%s, `timestamp`)) from `instatgbot` WHERE `user` LIKE %s AND TIME_TO_SEC(TIMEDIFF(%s, `timestamp`)) < %s ORDER BY `timestamp` DESC LIMIT 1;"
            userid = update.message.from_user.id
            abfrage_data = (now, userid, now, cfg.postingtreshhold)
            cursor.execute(abfrage, abfrage_data)
            if cursor.rowcount == 1:
                lastpostdata = cursor.fetchone()
            else:
                if (cfg.debuglog):
                    abfrage = "SELECT `timestamp`, TIME_TO_SEC(TIMEDIFF(%s, `timestamp`)) from `instatgbot` WHERE `user` LIKE %s ORDER BY `timestamp` DESC LIMIT 1;"
                    userid = update.message.from_user.id
                    abfrage_data = (now, userid)
                    cursor.execute(abfrage, abfrage_data)
                    lastpostdata = cursor.fetchone()
                    logging.error('Post versucht zu löschen '+str(update.message.from_user.id)+' '+str(update.message.chat.id)+' '+str(lastpostdata[1]))

                update.message.reply_text('Dein letzter Post ist schon zu alt und wurde bereits gepostet. Nix zu machen')
                return
        except mysql.connector.Error as err:
            logging.error('MYSQL '+str(err))
        try:
            abfrage = "SELECT `chatid`, `msgid` from `msg2post` WHERE `postid` LIKE %s"
            abfrage_data = (lastpostdata[0],)
            cursor.execute(abfrage, abfrage_data)
        except mysql.connector.Error as err:
            logging.error('MYSQL '+str(err))
        for (chatid, msgid) in cursor:
            bot.delete_message(chatid,msgid)
        try:
            eintrag = "DELETE FROM `msg2post` WHERE `postid` LIKE %s;"
            eintrag_data = (lastpostdata[0],)
            cursor.execute(eintrag, eintrag_data)
        except mysql.connector.Error as err:
            logging.error('MYSQL '+str(err))
        logging.error(lastpostdata)
        filepath = cfg.imgsavepath+lastpostdata[1]
        logging.error(lastpostdata[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        try:
            eintrag = "DELETE FROM `instatgbot` WHERE `id` LIKE %s;"
            eintrag_data = (lastpostdata[0],)
            cursor.execute(eintrag, eintrag_data)
        except mysql.connector.Error as err:
            logging.error('MYSQL '+str(err))
        if (cfg.debuglog):
            logging.error('Post gelöscht '+str(update.message.from_user.id)+' '+str(update.message.chat.id)+' '+str(lastpostdata[2])+' '+str(lastpostdata[3]))
        cnx.commit()
        cursor.close()
        cnx.close()

def getqcolor(image):
    qcolor = [0,0,0]
    imdata = image.getdata()
    for data in imdata:
        qcolor[0] = qcolor[0]+data[0]
        qcolor[1] = qcolor[1]+data[1]
        qcolor[2] = qcolor[2]+data[2]
    qcolor[0] = int(qcolor[0]/len(imdata))
    qcolor[1] = int(qcolor[1]/len(imdata))
    qcolor[2] = int(qcolor[2]/len(imdata))
    return qcolor
        
def photofunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
        if update.message.caption != None:
            captioneintrag = html.escape(update.message.caption)
            try:
                cnx = mysql.connector.connect(user=cfg.mysql['user'], password=cfg.mysql['password'], host='127.0.0.1', database=cfg.mysql['db'])
            except mysql.connector.Error as err:
                logging.error('MYSQL '+str(err))
            cursor = cnx.cursor(buffered=True)
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_id = update.message.photo[-1].file_id
            photo = bot.getFile(file_id)
            imgfilename = uuid.uuid4().hex
            savepath = cfg.imgsavepath+imgfilename
            photo.download(savepath)
            limratio = (0.8,1.9)
            ratio = (0.9,1.5)
            im = Image.open(savepath)
            imsize = im.size
            oldratio = imsize[0]/imsize[1]
            pfusch = 0
            if (oldratio<limratio[0]):
                pfusch = 1
                if (cfg.debuglog):
                    logging.error("Ratio ist nicht fine, wird gepfuscht")
                newbreite = int(ratio[0]*imsize[1])
                if (cfg.debuglog):
                    logging.error("altes Ratio (gerundet):")
                    logging.error(round(oldratio,4))
                    logging.error("neues Ratio (gerundet):")
                    logging.error(round(newbreite/imsize[1],4))
                bg = Image.new('RGB',(newbreite,imsize[1]),tuple(getqcolor(im)))
                box = (int(((newbreite-imsize[0])/2)),0,int((((newbreite-imsize[0])/2)+imsize[0])),imsize[1])
                bg.paste(im,box)
                bg.save(savepath, "PNG")
            elif (oldratio>limratio[1]):
                pfusch = 1
                if (cfg.debuglog):
                    logging.error("Ratio ist nicht fine, wird gepfuscht")
                newhoehe = int((1/ratio[1])*imsize[0]) # 1 / wird hier verwendet um das gleiche Ratioformat wie sonst auch verwenden zu können
                if (cfg.debuglog):
                    logging.error("altes Ratio (gerundet):")
                    logging.error(round(oldratio,4))
                    logging.error("neues Ratio (gerundet):")
                    logging.error(round(imsize[0]/newhoehe,4))
                bg = Image.new('RGB',(imsize[0],newhoehe),tuple(getqcolor(im)))
                box = (0,int(((newhoehe-imsize[1])/2)),imsize[0],int((((newhoehe-imsize[1])/2)+imsize[1])))
                bg.paste(im,box)
                bg.save(savepath, "PNG")
            else:
                if (cfg.debuglog):
                    logging.error("Ratio ist fine:")
                    logging.error(round(oldratio,4))
                im.save(savepath, "PNG")
            try:
                eintrag = "INSERT INTO `instatgbot` (`title`, `text`, `link`, `imgfile`, `user`, `timestamp`, `publish`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                eintrag_data = (captioneintrag, '', '', imgfilename, update.message.from_user.id, now, cfg.publish)
                cursor.execute(eintrag, eintrag_data)
                postid = cursor.lastrowid
            except mysql.connector.Error as err:
                logging.error('MYSQL '+str(err))
            try:
                abfrage = "SELECT `id`, `imgfile` from `instatgbot` WHERE DATEDIFF(%s, `timestamp`) > %s"
                abfrage_data = (now, cfg.deletedaydiff)
                cursor.execute(abfrage, abfrage_data)
            except mysql.connector.Error as err:
                logging.error('MYSQL '+str(err))
            for (id, imgfile) in cursor:
                filepath = cfg.imgsavepath+imgfile
                if os.path.exists(filepath):
                    os.remove(filepath)
                try:
                    eintrag = " DELETE FROM `msg2post` WHERE `postid` LIKE %s; DELETE FROM `instatgbot` WHERE `id` LIKE %s;"
                    eintrag_data = (id, id)
                    cursor.execute(eintrag, eintrag_data)
                except mysql.connector.Error as err:
                    logging.error('MYSQL '+str(err))
            if (cfg.debuglog):
                logging.error('Post gepostet '+str(update.message.from_user.id)+' '+str(update.message.chat.id))
            registermsg(update.message.message_id,postid,update.message.chat_id)
            if (pfusch):
                registermsg(update.message.reply_text('Okidoki, aber ich musste etwas an dem Seitenverhältnis rumpfuschen... Der Post sieht jetzt so aus:').message_id,postid,update.message.chat_id)
                image = open(savepath, 'rb')
                registermsg(update.message.reply_photo(image).message_id,postid,update.message.chat_id)
                image.close()
                registermsg(update.message.reply_text('falls er dir nicht gefällt kannst du ihn für ' +str(cfg.postingtreshhold/60) +' Minuten mit /dellastpost löschen').message_id,postid,update.message.chat_id)
            else:
                registermsg(update.message.reply_text('Okidoki').message_id,postid,update.message.chat_id)
            cnx.commit()
            cursor.close()
            cnx.close()
        else:
            registermsg(update.message.reply_text('Wird nicht gepostet').message_id,postid,update.message.chat_id)
            if (cfg.debuglog):
                logging.error('Post wie gefordert nicht gepostet '+str(update.message.from_user.id)+' '+str(update.message.chat.id))

    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))

def startfunc(bot, update):
    if str(update.message.chat.id) == cfg.tgallowedgroup:
    	update.message.reply_text('Huhu, mit diesem Bot kannst du Instaposts erstellen \n\nWenn du diesem Bot ein Bild schickst wird die Bild Unterschrift / Beschreibung als Instagrampost verwendet.')
    else:
        update.message.reply_text('Sorry, Falsche Gruppe '+str(update.message.chat.id))
    bot.send_message(chat_id=update.message.chat.id, text='TG Photo RSS-Feed Bot  Copyright (C) 2019  Paul \nThis program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome to redistribute it under certain conditions; for details see https://gitlab.roteserver.de/Humorhenker/tg-photo-rss-feed-bot/blob/master/LICENSE', disable_web_page_preview=True)
    if (cfg.debuglog):
        logging.error('Start aufgerufen '+str(update.message.from_user.id)+' '+str(update.message.chat.id))


bot_key = cfg.bot_key
updater = Updater(bot_key)

updater.dispatcher.add_handler(CommandHandler('start', startfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photofunc))
updater.dispatcher.add_handler(CommandHandler('dellastpost', dellastpost))

updater.start_polling()
updater.idle()
