import os
import time

import pandas as pd
from datetime import datetime
from asyncio import set_event_loop, new_event_loop
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
from telethon.sync import TelegramClient, functions
from sqlalchemy import create_engine, select, MetaData, Table, Column, \
    Integer, String
from sqlalchemy.orm import sessionmaker

load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

bot = Bot(token=token)

BUTTONS = ['channel']


def get_comment(channel, offset_msg, offset):
    """Извлекает комментарии поста."""
    client = TelegramClient(
        'osint',
        api_id,
        api_hash,
        system_version='4.16.31-vxCUSTOM',
        device_model='1.0.97'
    )
    client.start()
    result = client(functions.messages.GetRepliesRequest(
        peer=channel,
        msg_id=offset_msg,
        offset_id=0,
        offset_date=0,
        add_offset=offset,
        limit=100,
        max_id=0,
        min_id=0,
        hash=0
    ))
    client.disconnect()
    return result


def wake_up(update, context):
    """Запрос ссылки на канал/чат."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введите название канала'.format(name),
    )


def choice_date(update, context):
    """Запрашивает дату(глубину) парсинга."""
    chat = update.effective_chat
    context.user_data['chat_name'] = update.message.text
    context.bot.send_message(
        chat_id=chat.id,
        text='Введите глубину(дата) сканирования в формате дд.мм.гггг',
    )


def choice_report(update, context):
    """Выбор типа отчета."""
    chat = update.effective_chat
    markup = ReplyKeyboardMarkup.from_column(BUTTONS, resize_keyboard=True)
    date = update.message.text.split('.')
    if int(date[0][0]) == 0:
        date[0] = date[0][1]
    if int(date[1][0]) == 0:
        date[1] = date[1][1]

    if (int(date[0]) not in range(1, 32)) or (
            int(date[1]) not in range(1, 13)) or (int(date[2]) not in
                                                   range(2010, 2100)):
        context.bot.send_message(
            chat_id=chat.id,
            text='Введите глубину(дата) сканирования в формате дд.мм.гггг',
        )
    else:

        context.user_data['date_to'] = update.message.text
        context.bot.send_message(
            chat_id=chat.id,
            text='Выберете тип отчета ',
            reply_markup=markup,
        )


def get_channel(chat, date_to):
    """Извлечение участников и сообщений из канала."""
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    phones = []
    bots = []
    ids_comment = []
    messages_comment = []
    dates_comment = []
    post_id = []
    post_message = []
    post_date = []
    users_data = {}
    date = date_to.split('.')



    df_result = pd.DataFrame(columns=['ID', 'COUNT'])
    url = f'https://t.me/{chat}'

    client = TelegramClient(
        'osint',
        api_id,
        api_hash,
        system_version='4.16.31-vxCUSTOM',
        device_model='1.0.97'
    )
    client.start()

    client_msg = client.get_messages(url)
    if client_msg[0].id:
        messages_total = client_msg[0].id
        offset_msg = messages_total
    else:
        print('нет поста!!!')
    # offset_msg = 0

    while offset_msg > 0:
        client_msg = client.get_messages(url, ids=offset_msg)

        if client_msg is not None:
            if client_msg.date.date() < datetime.date(
                    date[2], date[1], date[0]):
                break
            else:
                post = client_msg

                if post.message == '':
                    offset_msg = offset_msg - 1
                    continue
                else:
                    if post.message:
                        post_message.append(post.message.replace(r'\n', ''))
                    else:
                        post_message.append(post.message)

                post_id.append(str(post.id))
                post_date.append(str(post.date.day) + '.' +
                                 str(post.date.month) + '.' +
                                 str(post.date.year))

        else:
            offset_msg = offset_msg - 1

        df_post = pd.DataFrame(
            {'Id': post_id, 'Date': post_date,
             'Message': post_message})

        df_post.to_csv(f'{url.split("/")[1]}.csv', mode='a',
                       sep=':',
                       header=True,
                       index=False,
                       encoding='utf-16')

        try:
            part_of_division = client_msg.replies.replies // 100

            while part_of_division >= 0:
                result = get_comment(url, offset_msg,
                                     part_of_division * 100)

                for user in result.users:
                    user_ids.append(str(user.id))
                    first_names.append(str(user.first_name))
                    last_names.append(str(user.last_name))
                    usernames.append('@' + str(user.username))
                    phones.append(str(user.phone))
                    bots.append(str(user.bot))

                    if f'{user.id}' in users_data:
                        count = users_data[f'{user.id}'] + 1
                        users_data[f'{user.id}'] = count
                    else:
                        users_data[f'{user.id}'] = 1

                for msg in result.messages:
                    ids_comment.append(str(msg.sender_id))
                    if msg.message:
                        messages_comment.append(
                            str(msg.message.replace(r'\n', '')))
                    else:
                        messages_comment.append(str(msg.message))
                    dates_comment.append(str(msg.date.day) + '.' +
                                         str(msg.date.month) + '.' +
                                         str(msg.date.year))

                df_users = pd.DataFrame(
                    {'Id': user_ids,
                     'Username': usernames,
                     'First_name': first_names,
                     'Last_names': last_names,
                     'Phone': phones,
                     'isBot': bots})

                df_messages = pd.DataFrame(
                    {'Id': ids_comment,
                     'Date': dates_comment,
                     'Message': messages_comment})

                df_comments = df_messages.merge(df_users, on='Id',
                                                how='left')

                df_comments = df_comments.drop_duplicates(subset='Message')
                part_of_division -= 1

            if df_comments.size != 0:
                df_comments.to_csv(f'{url.split("/")[1]}.csv',
                                   mode='a',
                                   sep=';',
                                   header=True,
                                   index=False,
                                   encoding='utf-16')
                users_data = dict(df_comments.iloc[:, 0].value_counts())
                df_buffer = pd.DataFrame.from_dict(users_data,
                                                   orient='index',
                                                   columns=[
                                                       "COUNT"]).reset_index()

                df_buffer.rename(columns={'Index': 'ID'}, inplace=True)
                df_buffer.columns = ['ID', 'COUNT']
                df_result = df_result.append(df_buffer)
                df_buffer = df_buffer[0:0]

        except:
            print(f'Нет информации по посту!!!!ID: {str(post.id)}')

        offset_msg = offset_msg - 1
        ids_comment = []
        messages_comment = []
        dates_comment = []

        post_id = []
        post_message = []
        post_date = []
        df_messages = df_messages[0:0]
        df_users = df_users[0:0]
        df_comments = df_comments[0:0]
        time.sleep(0.5)

    df_result = df_result.groupby(['ID'])[['COUNT']].sum().reset_index()
    df_result = df_result.sort_values(by=['COUNT'], ascending=[False])
    df_result.to_csv(f'{url.split("/")[1]}_users.csv',
                     mode='a',
                     sep=';',
                     header=True,
                     index=False,
                     encoding='utf-16')

    client.disconnect()
    return df_result


def get_report(update, context):
    """Подготовка отчета в формате *.CSV."""
    user_chat = update.effective_chat
    context_user = context.user_data['chat_name']
    context.user_data['button_type'] = update.message.text
    type_report = update.message.text
    if context_user.find(r'https://t.me/') != -1:
        chat = context.user_data['chat_name'].split(r'/')[3]
    else:
        chat = context.user_data['chat_name']
    date_to = context.user_data['date_to']
    set_event_loop(new_event_loop())
    if type_report == 'channel':
        df_list = get_channel(chat, date_to)

    df_list.to_csv(f'{chat}.csv', sep=';', header=True, index=False,
                   encoding='utf-16')
    path = os.path.abspath(f'{chat}.csv')
    context.bot.send_document(
        chat_id=user_chat.id,
        document=open(f'{path}', 'rb')
    )
    os.remove(path)


# def get_users(user_chat, chat):
#     """Запись в БД SQlite пользователей бота."""
#     connect = sqlite3.connect('users.db')
#     cursor = connect.cursor()
#     cursor.execute("""CREATE TABLE IF NOT EXISTS users(
#                     id INTEGER PRIMARY KEY,
#                     id_group INTEGER,
#                     username TEXT,
#                     firstname TEXT,
#                     request TEXT);""")
#     connect.commit()
#     user = (user_chat.id, user_chat.username, user_chat.first_name, chat)
#     cursor.execute("""INSERT INTO users (id_group, firstname,
#                    username,request) VALUES (?, ?, ?, ?);""", user)
#     connect.commit()

def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text(BUTTONS),
        get_report)
    )

    updater.dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^\d{2}\.\d{2}\.\d{4}'), choice_report))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text, choice_date))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
