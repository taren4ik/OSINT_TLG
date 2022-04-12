from telegram.ext import CommandHandler, Updater
from telegram import ReplyKeyboardMarkup
import requests
from dotenv import load_dotenv
import os, logging
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters

load_dotenv()

token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def get_new_image():
    try:
        url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(url)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    chat = update.effective_chat
    # context.bot.send_photo(chat.id, get_new_image())
    context.bot.send_photo(chat.id, get_new_image())


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введите название чата '.format(name),

    )


def parsing(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['/people'], ['/message']],
                                  resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберете тип отчета ',
        reply_markup=buttons,
    )


def msg_parse(update, context):
    pass


def people_parse(update, context):
    pass


def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('people', people_parse))
    updater.dispatcher.add_handler(CommandHandler('message', msg_parse))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parsing))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
