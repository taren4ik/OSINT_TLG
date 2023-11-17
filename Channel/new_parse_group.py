from xmlrpc.client import DateTime
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, ChannelParticipantsAdmins
from telethon.tl.functions.messages import GetHistoryRequest

import csv


load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

client = TelegramClient('osint',
                        api_id,
                        api_hash,
                        system_version='4.16.33-vxCUSTOM',
                        device_model='1.0.97'
)
client.start()

chats = []
last_date = None
chunk_size = 200
groups = []
result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)
for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue
print("Выберите группу для парсинга сообщений и членов группы:")
i = 0
for g in groups:
    print(str(i) + "- " + g.title)
    i += 1
g_index = input("Введите нужную цифру: ")
target_group = groups[int(g_index)]
print("Узнаём пользователей...")
all_participants = []
all_participants = client.get_participants(target_group)
admin_user = []
for user in client.iter_participants(
        target_group, filter=ChannelParticipantsAdmins):
    admin_user.append(user.id)


print("Сохраняем данные в файл...")
with open("members.csv", "w", encoding="UTF-8") as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(["id", "username", "first_name", "last_name", "phone",
                     "is_bot", "is_admin",
                     "group"])

    for user in all_participants:
        if user.id:
            id = user.id
        else:
            id = "null"
        if user.username:
            username = user.username
        else:
            username = "null"
        if user.first_name:
            first_name = user.first_name
        else:
            first_name = "null"
        if user.last_name:
            last_name = user.last_name
        else:
            last_name = "null"
        if user.phone:
            phone = user.phone
        else:
            phone = "null"
        if user.bot:
            is_bot = user.bot
        else:
            is_bot = "null"

        if user.id in admin_user:
            is_admin = 'True'
        else:
            is_admin = 'False'

        writer.writerow([id, username, first_name, last_name, phone, is_bot,
                         is_admin, target_group.title])
print("Парсинг участников группы успешно выполнен.")

offset_id = 0
limit = 100
all_messages = []
total_messages = 0
total_count_limit = 0

while True:
    history = client(GetHistoryRequest(
        peer=target_group,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))
    if not history.messages:
        break
    messages = history.messages
    for message in messages:
        all_messages.append(message.message)
    offset_id = messages[len(messages) - 1].id
    if total_count_limit != 0 and total_messages >= total_count_limit:
        break

print("Сохраняем данные в файл...")
with open("chats.csv", "w", encoding="UTF-8") as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    for message in all_messages:
        writer.writerow([message])
print('Парсинг сообщений группы успешно выполнен.')