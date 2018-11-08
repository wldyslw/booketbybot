import os
import sys
import logging
import requests
from dotenv import load_dotenv
from models import init_session, Subscriber

from telegram import ParseMode
from telegram.ext import (
    Updater,
    CommandHandler
)

logging.basicConfig(filename="./log/production.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

load_dotenv()

TOKEN = os.getenv("TOKEN")

class BooketbyBot:
    def __init__(self, token):
        self.session = init_session('sqlite', os.path.join(os.getcwd(), "db/db.sqlite3"))()
        self.updater = Updater(token=token)
        self.intervalJob = self.updater.job_queue.run_repeating(
            self.intervalJobCallback,
            interval=60,
            first=0
        )
        self.status = 200
        self.notifierStatus = False

        handlers = self.initHandlers()
        for handler in handlers:
            self.updater.dispatcher.add_handler(handler)

    def getBooketStatus(self):
        response = requests.get('https://booket.by')
        self.status = response.status_code
        if self.status == 200:
            if self.notifierStatus:
                self.notifierStatus = False
            logging.log(logging.INFO, "booket.by status checked, no problems were found")
        else:
            logging.log(logging.WARNING, f"Something went wrong, status code: {self.status}")
        return self.status

    def intervalJobCallback(self, bot, job):
        self.getBooketStatus()
        if self.status != 200 and not self.notifierStatus:
            for user in self.session.query(Subscriber):
                if user.subs_type == 'default':
                    pass
                elif user.subs_type == 'silent':
                    bot.send_message(user.id, f"Something went wrong, status code: `{self.status}`", parse_mode=ParseMode.MARKDOWN)
            self.notifierStatus = True

    def statusCallback(self, bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text="Checking booket.by status...")
        message = "Ok." if self.status == 200 else f"Something went wrong, status code: `{self.status}`"
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)

    def subscribeCallback(self, bot, update):
        chat_id = update.message.chat_id
        try:
            if self.session.query(Subscriber.id).filter_by(id=chat_id).scalar() is not None:
                for user in self.session.query(Subscriber).filter(Subscriber.id == chat_id):
                    user.subs_type = 'silent'
                    self.session.commit()
            else:
                self.session.add(Subscriber(id=chat_id, subs_type='silent'))
                self.session.commit()
            bot.send_message(chat_id=chat_id, text="Successfully subscribed on status updates")
        except:
            logging.log(logging.ERROR, f"Error during subscriber adding: {sys.exc_info()[0]}")
            raise

    def unsubscribeCallback(self, bot, update):
        chat_id = update.message.chat_id
        try:
            for user in self.session.query(Subscriber).filter(Subscriber.id == chat_id):
                user.subs_type = 'disabled'
                self.session.commit()
            bot.send_message(chat_id=chat_id, text="Successfully unsubscribed from status updates")
        except:
            logging.log(logging.ERROR, f"Error during subscriber deleting: {sys.exc_info()[0]}")
            raise

    def getAllSubscribersCallback(self, bot, update):
        subs = []
        for user in self.session.query(Subscriber).filter(Subscriber.subs_type != 'disabled'):
            subs.append(str(user))
        message = ',\n'.join(subs)
        bot.send_message(update.message.chat_id, message or "No subscribers yet.")

    def subscribeModeCallback(self, bot, update):
        self.missingFunctionCallback(bot, update)

    def pingCallback(self, bot, update):
        bot.send_message(update.message.chat_id, "Pingback", reply_to_message_id=update.message.message_id)

    def missingFunctionCallback(self, bot, update):
        bot.send_message(update.message.chat_id, "This function is not avaliable now.")

    def initHandlers(self):
        return [
            CommandHandler('status', self.statusCallback),
            CommandHandler('subscribe', self.subscribeCallback),
            CommandHandler('unsubscribe', self.unsubscribeCallback),
            CommandHandler('getallsubs', self.getAllSubscribersCallback),
            CommandHandler('subscribemode', self.subscribeModeCallback),
            CommandHandler('ping', self.pingCallback)
        ]

    def run(self):
        self.updater.start_polling()

def main():
    if TOKEN != None:
        bot = BooketbyBot(TOKEN)
        bot.run()
        print('Bot is running...\nPress Ctrl + C to exit')
    else:
        print("TOKEN has not been provided!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()