# TODO ограничение на крличество бесплатных запросов
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
    """Выбор типа парсинга."""
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
    # Использую контекст context.user_data
    context.user_data['chat_name'] = update.message.text
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберете тип отчета ',
        reply_markup=buttons,
    )


def get_message(chat):
    """Парсинг сообщений."""
    msg_id = []
    msg_dt = []
    msg_txt = []
    url = f'https://t.me/{chat}'

    app = TelegramClient('osint', api_id, api_hash)
    app.start()
    messages = app.get_messages(url, 5000)
    for msg in messages:
        msg_txt.append(str(msg.message))
        msg_id.append(str(msg.sender_id))
        msg_dt.append(str(msg.date))
    df_list = pd.DataFrame(
        {'Id': msg_id, 'DateTime': msg_dt, 'Message': msg_txt})
    app.disconnect()
    return df_list


def msg_parse(update, context):
    """Парсинг сообщений."""
    user_chat = update.effective_chat
    context_user = context.user_data['chat_name']
    if context_user.find(r'https://t.me/') != -1:
        chat = context.user_data['chat_name'].split(r'/')[3]
    else:
        chat = context.user_data['chat_name']
    get_users(user_chat, chat)  # логирование пользователей.
    set_event_loop(new_event_loop())
    df_list = get_message(chat)
    df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False,
                   encoding='utf-8')
    path = os.path.abspath(f'{chat}.csv')
    context.bot.send_document(
        chat_id=user_chat.id,
        document=open(f'{path}', 'rb')
    )
    os.remove(path)


def get_people(chat):
    """Формирование таблицы с информацией о пользователях."""
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    bots = []
    standart_phones = []
    url = f'https://t.me/{chat}'

    app = TelegramClient('osint', api_id, api_hash)
    app.start()
    # print(app.get_participants.total)
    participants = app.get_participants(url, aggressive=False, limit=5000)

    for user in participants:
        user_ids.append(str(user.id))
        first_names.append(str(user.first_name))
        last_names.append(str(user.last_name))
        usernames.append('@' + str(user.username))
        standart_phones.append(str(user.phone))
        bots.append(str(user.bot))

    df_list = pd.DataFrame(
        {'Id': user_ids, 'Usernames': usernames, 'First_name': first_names,
         'Last_names': last_names, 'standart_phones': standart_phones,
         'Bots': bots})
    app.disconnect()
    return df_list


def people_parse(update, context):
    """Парсинг пользователей чата."""
    user_chat = update.effective_chat
    context_user = context.user_data['chat_name']
    if context_user.find(r'https://t.me/') != -1:
        chat = context.user_data['chat_name'].split(r'/')[3]
    else:
        chat = context.user_data['chat_name']
    get_users(user_chat, chat)  # логирование пользователей.
    set_event_loop(new_event_loop())
    df_list = get_people(chat)  # получаем данные
    df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False,
                   encoding='utf-8')
    path = os.path.abspath(f'{chat}.csv')
    context.bot.send_document(
        chat_id=user_chat.id,
        document=open(f'{path}', 'rb')
    )
    os.remove(path)


def get_users(user_chat, chat):
    """БД пользователей ."""
    df_users = pd.DataFrame(
        {'ID': user_chat.id, 'USERNAME': user_chat.username, 'FIRSTNAME':
            user_chat.first_name,
         'REQUEST': chat}, index=[0])
    df_users.to_csv(f'users.csv', sep=';', header=True, index=False)


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
