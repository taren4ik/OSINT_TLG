import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events, errors
from random import randint

load_dotenv()

api_id = int(os.getenv("API_ID_3"))
api_hash = os.getenv("API_HASH_3")

client = TelegramClient('forward_session', api_id, api_hash)

# SOURCE_USERNAMES = [
#     'vlnews25', 'newsvlc', 'svodka25', 'newsvlru',
#     'dpskontrol_125rus', 'primamedia', 'make_dobro'
# ]
SOURCE_USERNAMES = [
'make_dobro'
]


TARGET= 'news_fresh_vl'

forwarded_messages = set()
sources = []
target = None


@client.on(events.NewMessage)
async def handler(event):
    if event.chat_id not in [s.id for s in sources]:
        return

    print("📩 Новое сообщение")

    message_id = (event.chat_id, event.message.id)
    if message_id in forwarded_messages:
        return

    try:
        try:
            await client.forward_messages(target, event.message)
        except errors.RPCError:
            if event.message.text:
                await client.send_message(target, event.message.text)

        forwarded_messages.add(message_id)
        print(f"➡️ Переслано из {event.chat.title}")
        await asyncio.sleep(randint(2, 5))

    except errors.FloodWait as e:
        print(f"⏳ FloodWait {e.seconds} сек")
        await asyncio.sleep(e.seconds + 1)

    except Exception as e:
        print("❌ Ошибка при пересылке:", e)


async def main():
    global sources, target

    await client.start()
    print("✅ Клиент запущен")

    for username in SOURCE_USERNAMES:
        try:
            entity = await client.get_entity(username)
            sources.append(entity)
            print(f"✅ Источник: {username}")
        except Exception as e:
            print(f"❌ {username}: {e}")

    target = await client.get_entity(TARGET)
    print(f"✅ Цель: {TARGET}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
