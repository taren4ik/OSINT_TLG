import configparser
import json
import asyncio
import time
import pandas as pd
from telethon.sync import TelegramClient
from telethon import connection
from telegram import TelegramError
from datetime import date, datetime
from asyncio import set_event_loop, new_event_loop

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon import functions, types
# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

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

api_id = ''
api_hash = ''
channel = 't.me/pr_russia'

with TelegramClient('osint', api_id, api_hash) as client:
    if client.get_messages(channel)[0].id:
        messages_total = client.get_messages(channel)[0].id  # последний пост
        offset_msg = messages_total
    else:
        print("нет поста!!!!")

    while True:
        if client.get_messages(channel, ids=offset_msg) is not None:
            post = client.get_messages(channel, ids=offset_msg)  # пост
            post_id.append(str(post.id))
            post_message.append(post.message)
            post_date.append(str(post.date.day) + '.' +
                             str(post.date.month) + '.' +
                             str(post.date.year))

        df_post = pd.DataFrame(
            {'Id': post_id, 'Date': post_date,
             'Message': post_message})
        result = client(functions.messages.GetRepliesRequest(
            peer=channel,
            msg_id=offset_msg,
            offset_id=0,
            offset_date=0,
            add_offset=0,
            limit=100,
            max_id=0,
            min_id=0,
            hash=0
        ))

        for user in result.users:
            user_ids.append(str(user.id))
            first_names.append(str(user.first_name))
            last_names.append(str(user.last_name))
            usernames.append('@' + str(user.username))
            phones.append(str(user.phone))
            bots.append(str(user.bot))

        for msg in result.messages:
            ids_comment.append(str(msg.sender_id))
            messages_comment.append(str(msg.message))
            dates_comment.append(str(msg.date.day) + '.' +
                                 str(msg.date.month) + '.' +
                                 str(msg.date.year))

        df_users = pd.DataFrame(
            {'Id': user_ids, 'Username': usernames, 'First_name': first_names,
             'Last_names': last_names, 'Phone': phones, 'isBot': bots})

        df_messages = pd.DataFrame(
            {'Id': ids_comment, 'Date': dates_comment,
             'Message': messages_comment})
        sorted_df_messages = df_messages.sort_values(by='Id')

        df_comments = df_users.merge(sorted_df_messages, on='Id',
                                      how='inner')

        df_post.to_csv(f'{channel.split("/")[1]}.csv', mode='a', sep=';',
                       header=True,
                       index=False,
                       encoding='utf-8')
        df_comments.to_csv(f'{channel.split("/")[1]}.csv', mode='a', sep=';',
                           header=True,
                           index=False,
                           encoding='utf-8')

        offset_msg = offset_msg - 1
        ids_comment = []
        messages_comment = []
        dates_comment = []

        post_id = []
        post_message = []
        post_date = []
        df_post = df_post[0:0]
        df_comments = df_comments[0:0]
        time.sleep(3)

    else:
        offset_msg = offset_msg - 1



client.disconnect()

# async def dump_all_messages(channel):
# 	"""Записывает json-файл с информацией о всех сообщениях канала/чата"""
# 	offset_msg = 0    # номер записи, с которой начинается считывание
# 	limit_msg = 100   # максимальное число записей, передаваемых за один раз
#
# 	all_messages = []   # список всех сообщений
# 	total_messages = 0
# 	total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения
#
# 	class DateTimeEncoder(json.JSONEncoder):
# 		'''Класс для сериализации записи дат в JSON'''
# 		def default(self, o):
# 			if isinstance(o, datetime):
# 				return o.isoformat()
# 			if isinstance(o, bytes):
# 				return list(o)
# 			return json.JSONEncoder.default(self, o)
#
# 	while True:
# 		history = await client(GetHistoryRequest(
# 			peer=channel,
# 			offset_id=offset_msg,
# 			offset_date=None, add_offset=0,
# 			limit=limit_msg, max_id=0, min_id=0,
# 			hash=0))
# 		if not history.messages:
# 			break
# 		messages = history.messages
# 		for message in messages:
# 			all_messages.append(message.to_dict())
# 		offset_msg = messages[len(messages) - 1].id
# 		total_messages = len(all_messages)
# 		if total_count_limit != 0 and total_messages >= total_count_limit:
# 			break
#
# 	with open('channel_messages.json', 'w', encoding='utf8') as outfile:
# 		 json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)
