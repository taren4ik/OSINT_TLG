import asyncio
import os
from dotenv import load_dotenv
from random import randrange
from telethon import TelegramClient, events

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Список исходных каналов и целевой канал
source_channels = ['make_dobro']
target_channel = 'news_fresh_vl'

client = TelegramClient(
    'osint_session', api_id, api_hash,
    device_model="iPhone 13 Pro Max",
    system_version="14.8.1",
    app_version="8.4",
    lang_code="en",
    system_lang_code="en-US"
)


async def main():
    await client.start()
    print("Клиент запущен!")

    sources = [await client.get_entity(username) for username in SOURCE_USERNAMES]
    target = await client.get_entity(TARGET_USERNAME)

    @client.on(events.NewMessage(chats=sources))
    async def handler(event):
        message_id = (event.chat_id, event.message.id)

        if message_id in forwarded_messages:
            return

        try:
            try:
                await client.forward_messages(target, event.message)
            except errors.RPCError:
                text = event.message.text or ""
                if text:
                    await client.send_message(target, text)
            forwarded_messages.add(message_id)

            print(f"Переслано: {event.chat.title} | ID: {event.message.id}")

            await asyncio.sleep(randint(2, 6))

        except errors.FloodWait as e:
            print(f"FloodWait {e.seconds} сек. Ожидаем...")
            await asyncio.sleep(e.seconds + 1)

        except Exception as e:
            print("Ошибка:", e)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
