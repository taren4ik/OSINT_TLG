# TODO ограничение на крличество бесплатных запросов
# TODO проверка подписки на канал
# TODO обработка всех пользователей чата
# TODO обработка всех пользователей чата
# TODO обработка всех сообщений пользователей чата


import logging
import os
from datetime import time

import pandas as pd
from telethon import functions
from asyncio import set_event_loop, new_event_loop
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.sync import TelegramClient


load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

bot = Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

BUTTONS = ['chat_users', 'chat_messages', 'chanel_users']
app = TelegramClient('osint', api_id, api_hash)
app.start()


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
    # app.start()
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

    app = TelegramClient('osint', api_id, api_hash)
    app.start()
    # print(app.get_participants.total)
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



async def get_comment(channel, offset_msg, offset):
    result = await app(functions.messages.GetRepliesRequest(
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
    return result

async def get_chanel(channel):
    """Парсинг сообщений."""
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
    # client = TelegramClient('osint', api_id, api_hash)
    # client.start()

    client_msg = await app.get_messages(channel)
    if client_msg[0].id:
        messages_total = client_msg[0].id
        offset_msg = messages_total
    else:
        print('нет поста!!!')
    # offset_msg = 0

    while offset_msg > 0:  # глубина сканирования сообщений в канале
        client_msg = await app.get_messages(channel, ids=offset_msg)
        if client_msg is not None:
            post = client_msg

            if post.message == '':
                offset_msg = offset_msg - 1
                continue
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

        df_post.to_csv(f'{channel.split("/")[1]}.csv', mode='a',
                       sep=':',
                       header=True,
                       index=False,
                       encoding='utf-16')

        try:
            part_of_division = client_msg.replies.replies // 100

            while part_of_division >= 0:
                result = await get_comment(channel, offset_msg,
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

                # sorted_df_messages = df_messages.sort_values(by='Id')

                df_comments = df_messages.merge(df_users, on='Id',
                                                how='left')

                df_comments = df_comments.drop_duplicates(subset='Message')
                part_of_division -= 1

            if df_comments.size != 0:
                df_comments.to_csv(f'{channel.split("/")[1]}.csv',
                                   mode='a',
                                   sep=';',
                                   header=True,
                                   index=False,
                                   encoding='utf-16')

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
    sorted_tuple = sorted(users_data.items(), key=lambda x: x[1], reverse=True)
    users_data = dict(sorted_tuple)

    return users_data


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
    get_users(user_chat, chat)  # логирование пользователей.
    set_event_loop(new_event_loop())

    if type_report == 'chat_users':
        df_list = get_chat(chat)
    elif type_report == 'chat_messages':
        df_list = get_message(chat)
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
    """БД пользователей ."""
    df_users = pd.DataFrame(
        {'ID': user_chat.id, 'USERNAME': user_chat.username, 'FIRSTNAME':
            user_chat.first_name,
         'REQUEST': chat}, index=[0])
    df_users.to_csv(f'users.csv', sep=';', header=True, index=False)


def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))

    updater.dispatcher.add_handler(MessageHandler(Filters.text(BUTTONS),
                                                  get_report))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, choice_report))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
