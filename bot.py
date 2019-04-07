import logging
import os
import sqlite3
from urllib.parse import urlparse

import youtube_dl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import downloader

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
    conn = sqlite3.connect('video_stats.db')

    conn.execute("""CREATE TABLE IF NOT EXISTS requests (
                     id integer PRIMARY KEY,
                     date DATETIME DEFAULT (datetime('now','localtime')),
                     url text,
                     user text);
                    """
                 )
    conn.execute("""CREATE TABLE IF NOT EXISTS uploaded_files (
                         id integer PRIMARY KEY,
                         url text,
                         file_id text);
                        """
                 )
    url = update.message.text
    if is_url(url) is False:
        update.message.reply_text('Enter Url please')
        return
    cur = conn.cursor()
    file_ids = cur.execute("""SELECT file_id FROM uploaded_files WHERE url=?""", (url,)).fetchall()
    print(file_ids)
    if file_ids:
        update.message.reply_audio(file_ids[0][0])
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
    file_id = response['audio']['file_id']
    cur = conn.cursor()
    sql = """INSERT INTO uploaded_files(url, file_id) VALUES(?,?)"""
    cur.execute(sql, (url, file_id))

    sql = """INSERT INTO requests(url,user)
                  VALUES(?,?);"""
    cur.execute(sql, (url, str(update.message.from_user.username)))
    conn.commit()
    os.remove(meta.file_name)
    os.remove(meta.cover)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("723941396:AAHLfhiXueI3o5WCvVhH6UReBW2c0Z2GuUs", use_context=True)

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
