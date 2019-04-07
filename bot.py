import logging
import os
from urllib.parse import urlparse

import youtube_dl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import downloader
from db import DBManager

token = "723941396:AAHLfhiXueI3o5WCvVhH6UReBW2c0Z2GuUs"
owner_chat_id = 237735014
TELEGRAM_LOG = "@{} requested for\n{}"
TELEGRAM_ERROR = "User @{} caused error:\n{}"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
from lepl.apps.rfc3696 import HttpUrl

validator = HttpUrl()


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! This is yputube downloader bot. Enter a link to download video.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def download_video(update, context):
    db = DBManager()
    url = update.message.text
    username = str(update.message.from_user.username)
    if is_url(url) is False:
        update.message.reply_text('Enter Url please')
        return

    file_id = db.get_url_file_id(url)
    if file_id:
        update.message.reply_audio(file_id)
        db.insert_user_request(url, username)
        context.bot.send_message(chat_id=owner_chat_id,
                                 text=TELEGRAM_LOG.format(username, url))
        return
    try:
        meta = downloader.download_video(url)
    except youtube_dl.utils.DownloadError as e:
        update.message.reply_text(str(e))
        return
    audio_file = open(meta.file_name, 'rb')
    cover = open(meta.cover, 'rb')
    response = update.message.reply_audio(audio_file,
                                          title=meta.meta.get('title', None),
                                          performer=meta.meta.get('uploader', None),
                                          duration=meta.meta.get('duration', None),
                                          caption=meta.meta.get('title', None),
                                          thumb=cover)
    context.bot.send_message(chat_id=owner_chat_id,
                             text=TELEGRAM_LOG.format(username, url))

    db.insert_file_id(url, response['audio']['file_id'])
    db.insert_user_request(url, username)

    os.remove(meta.file_name)
    os.remove(meta.cover)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    context.bot.send_message(chat_id=owner_chat_id,
                             text=TELEGRAM_ERROR.format(update.message.from_user.username, context.error))


def main():
    db = DBManager()
    db.create_tables()
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, download_video))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
