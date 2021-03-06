#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import os

import telegram
from telegram.ext import (CommandHandler, ConversationHandler, Filters, Job,
						  MessageHandler, RegexHandler, Updater)

from bot_base import base
from bot_interface import interface
from bot_logging import logger, scheduler
from bot_usersettings import users
from bot_sender import sender


def subscribe(bot, update):
	user_id = update.message.chat_id
	logger.info('Subscribe user %s' % user_id)
	users.change(modify=[user_id, ['send_5_min_before_launch_alert', True]])
	update.message.reply_text(interface.subscribe_message)
	# TODO add user setting to send in time

def unsubscribe(bot, update):
	user_id = update.message.chat_id
	logger.info('Unsubscribe user %s' % user_id)
	users.change(modify=[user_id, ['send_5_min_before_launch_alert', False]])
	update.message.reply_text(interface.unsubscribe_message)

def send_uncertain_launches(bot, update):
	user_id = update.message.chat_id
	users.change(modify=[user_id, ['send_uncertain_launches', True]])

def SendNext(bot, update, args):
	count = 1
	if args:
		count = int(args[0])

	user_id = update.message.chat_id
	logger.info("Sending user %s next %d events" % (user_id, count))
	sender.SendNext(user_id, count)

def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"' % (update, error))

def start(bot, update):
	user_id = update.message.chat_id
	logger.info('Starting with user %s' % user_id)
	update.message.reply_text(interface.welcome_message)
	user = update.message.from_user
	logger.info('new user %s' % user.first_name)
	users.add_user(user_id)
	help(bot, update)

def help(bot, update):
	update.message.reply_text(interface.help_message)
	
def main():
	# TODO show notif of the ongoing launch mission if one is happening while your chat 
	# TODO probability coefs
	# TODO if no vid, send pic 
	# TODO add user setting chat with 15 min update and 'only last change matters'
	# TODO user settings: if to send msgs without videos
	# 					  if to send uncertain launches
	# 					  if to send pictures in what resolution is preferable
	# TODO make available more info about the launch
	#	   maybe send launch id and make a func '/more_info id 1234'
	# TODO make a full python lib for the source site ;;launchlibrary;;

	# TODO last week till now base of launches

	token = ''
	if os.path.isfile('_token.token'):
		with open('_token.token', 'r') as tokenFile:
			token = tokenFile.read().replace('\n', '')

	updater = Updater(token)
	# Get the dispatcher to register handlers
	dp = updater.dispatcher
	sender.set_bot(dp.bot)

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler('next', SendNext, 
								pass_args=True))

	dp.add_handler(CommandHandler('subscribe', subscribe))
	dp.add_handler(CommandHandler('unsubscribe', unsubscribe))
	dp.add_handler(CommandHandler('send_uncertain_launches', send_uncertain_launches))
	# dp.add_handler(CommandHandler('send_non_video_launches', send_non_video_launches,
	# 							pass_chat_data=True, pass_args=True))
	# log all errors
	dp.add_error_handler(error)

	base.update()
	scheduler.add_job(base.update, 'interval', hours=5)
	
	users.get_from_file()
	scheduler.add_job(users._change, 'interval', minutes=15)
	
	scheduler.start()

	# Start the Bot
	updater.start_polling()

	# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
	# SIGABRT. This should be used most of the time, since start_polling() is
	# non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()