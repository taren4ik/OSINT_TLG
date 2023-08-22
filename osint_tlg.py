# TODO реализовать запуск клиента единажды (DRY)
# TODO проверка подписки на канал
# TODO обработка всех пользователей чата
# TODO обработка соединить функциональность для групп и каналов
# TODO обработка всех сообщений пользователей чата
# TODO переписать на асинронный код работу бота



import logging
import os
import sqlite3

import pandas as pd
from asyncio import set_event_loop, new_event_loop
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.sync import TelegramClient, functions

from sqlalchemy import create_engine, select, MetaData, Table, Column, \
    Integer, String
from sqlalchemy.orm import sessionmaker


load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')


bot = Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


BUTTONS = ['chat_users', 'chat_messages', 'chanel_users']


def wake_up(update, context):
    """Запрос ссылки на канал/чат."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введите название чата '.format(name),

    )
    logging.DEBUG('wake_up отработала')


def choice_report(update, context):
    """Выбор типа отчета."""
    chat = update.effective_chat
    markup = ReplyKeyboardMarkup.from_column(BUTTONS, resize_keyboard=True)
    # Использую контекст context.user_data
    context.user_data['chat_name'] = update.message.text
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберете тип отчета ',
        reply_markup=markup,
    )


def get_message(chat):
    """Извлечение  сообщений из чата."""
    msg_id = []
    msg_dt = []
    msg_txt = []
    url = f'https://t.me/{chat}'

    # app = TelegramClient('osint', api_id, api_hash)
    app = TelegramClient(
        'osint',
        api_id,
        api_hash,
        system_version='4.16.30-vxCUSTOM',
        device_model='1.py.0.97'
    )

    app.start()
    messages = app.get_messages(url, 5000)
    for msg in messages:
        msg_txt.append(str(msg.message))
        msg_id.append(str(msg.sender_id))
        msg_dt.append(str(msg.date))
    df_list = pd.DataFrame(
        {'Id_user': msg_id, 'DateTime': msg_dt, 'Message': msg_txt})
    df_list.sort_values(by='Id_user', ascending=False)
    app.disconnect()
    return df_list


def get_chat(chat):
    """Извлечение участников чата."""
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    bots = []
    standart_phones = []
    admins = []
    admin_user = []

    url = f'https://t.me/{chat}'

    app = TelegramClient(
        'osint',
        api_id,
        api_hash,
        system_version='4.16.31-vxCUSTOM',
        device_model='1.0.97'
    )

    app.start()

    participants = app.get_participants(url, aggressive=False, limit=5000)
    for user in app.iter_participants(
            chat, filter=ChannelParticipantsAdmins):
        admin_user.append(user.id)
    for user in participants:
        user_ids.append(str(user.id))
        first_names.append(str(user.first_name))
        last_names.append(str(user.last_name))
        usernames.append('@' + str(user.username))
        standart_phones.append(str(user.phone))
        bots.append(str(user.bot))
        if user.id in admin_user:
            admins.append('True')
        else:
            admins.append('None')

    df_list = pd.DataFrame(
        {'Id': user_ids, 'Usernames': usernames, 'First_name': first_names,
         'Last_names': last_names, 'standart_phones': standart_phones,
         'Bots': bots, 'Admin': admins})
    app.disconnect()
    return df_list


def get_chanel(channel):
    """Парсинг сообщений."""
    post_id = []
    post_message = []
    post_date = []

    url = f'https://t.me/{channel}'
    return ()


def get_report(update, context):
    """Подготовка отчета."""
    user_chat = update.effective_chat
    context_user = context.user_data['chat_name']
    context.user_data['button_type'] = update.message.text
    type_report = update.message.text
    if context_user.find(r'https://t.me/') != -1:
        chat = context.user_data['chat_name'].split(r'/')[3]
    else:
        chat = context.user_data['chat_name']
    #get_users(user_chat, chat)  # логирование пользователей.
    set_event_loop(new_event_loop())

    if type_report == 'chat_users':
        df_list = get_chat(chat)
    elif type_report == 'chat_messages':
        df_list = get_message(chat)
        chat += '_messages'
    else:
        df_list = get_chanel(chat)
    df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False,
                   encoding='utf-16')
    path = os.path.abspath(f'{chat}.csv')
    context.bot.send_document(
        chat_id=user_chat.id,
        document=open(f'{path}', 'rb')
    )
    os.remove(path)


def get_users(user_chat, chat):
    """Запись в БД SQlite пользователей бота."""
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY,
                    id_group INTEGER,
                    username TEXT,
                    firstname TEXT,
                    request TEXT);""")
    connect.commit()
    user = (user_chat.id, user_chat.username, user_chat.first_name, chat)
    cursor.execute("""INSERT INTO users (id_group, firstname,
                   username,request) VALUES (?, ?, ?, ?);""", user)
    connect.commit()

    dbpath = 'dafile2.db'
    engine = create_engine(f'sqlite:///{dbpath}')
    metadata = MetaData()
    people = Table('people', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('id_group', Integer),
                   Column('firstname', String),
                   Column('username', String),
                   Column('request', String), )

    Session = sessionmaker(bind=engine)
    session = Session()
    metadata.create_all(engine)  # создание таблицы

    people_ins = people.insert().values(id_group=user_chat.id,
                                        username=user_chat.username,
                                        firstname=user_chat.first_name,
                                        request=chat
                                        )
    session.execute(people_ins)
    session.commit()


def main():

    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text(BUTTONS),
        get_report)
    )
    updater.dispatcher.add_handler(MessageHandler(Filters.text, choice_report))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()






