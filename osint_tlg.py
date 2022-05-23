import os

import pandas as pd
import logging
from telethon.sync import TelegramClient
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
from asyncio import set_event_loop, new_event_loop

load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

bot = Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введите название чата '.format(name),

    )
    logging.DEBUG('wake_up отработала')


def parsing(update, context):
    """Выбор типа парсинга."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['/people'], ['/message']],
                                  resize_keyboard=True)
    # Используtv контекст context.user_data
    context.user_data['chat_name'] = update.message.text
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберете тип отчета ',
        reply_markup=buttons,
    )


def msg_parse(update, context):
    """Прасинг сооющений."""
    pass


def client(chat):
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    standart_phones = []
    url = f'https://t.me/{chat}'

    app = TelegramClient('osint', api_id, api_hash)
    app.start()
    participants = app.get_participants(url)  # получаем список участников
    # считывание основных параметров участников
    for user in participants:
        user_ids.append(str(user.id))
        first_names.append(str(user.first_name))
        last_names.append(str(user.last_name))
        usernames.append('@' + str(user.username))
        standart_phones.append(str(user.phone))
        # if len(user_ids) == 10:
        # break
    df_list = pd.DataFrame(
        {'Id': user_ids, 'Usernames': usernames, 'First_name': first_names,
         'Last_names': last_names, 'standart_phones': standart_phones})
    # df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False)
    print(df_list)
    app.disconnect()
    # app.run_until_disconnected()
    return df_list


def people_parse(update, context):
    """Парсинг пользователей чата."""
    # Получаем информацию о чате, из которого получено сообщение,
    # и сохраняем в переменную chat
    user_chat = update.effective_chat
    chat = context.user_data['chat_name']
    set_event_loop(new_event_loop())
    df_list = client(chat)
    df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False)
    # context.bot.send_message(
    #     chat_id=user_chat.id,
    #     text=''
    # )
    path = os.path.abspath(f'{chat}.csv')
    context.bot.send_document(
        chat_id=user_chat.id,
        document= open(f'{path}', 'rb')
    )


def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('message', msg_parse))

    updater.dispatcher.add_handler(
        CommandHandler('people', people_parse))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parsing))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
