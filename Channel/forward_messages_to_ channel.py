import asyncio
import logging
import os
from dotenv import load_dotenv
from random import uniform
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

api_id = int(os.getenv("API_ID_2"))
api_hash = os.getenv("API_HASH_2")

source_channels = ['news_kremlin']
target_channel = 'news_kremlin_reserve'

client = TelegramClient(
    'forward',
    api_id,
    api_hash,
    device_model="iPhone 13 Pro Max",
    system_version="14.8.1",
    app_version="8.4",
    lang_code="en"
)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        await client.forward_messages(
            target_channel,
            event.message
        )
        logging.info(f"Переслано {event.message.id}")
        await asyncio.sleep(uniform(0.5, 1.5))

    except FloodWaitError as e:
        logging.warning(f"FloodWait {e.seconds}s")
        await asyncio.sleep(e.seconds + 5)

    except Exception as e:
        logging.exception(e)

async def main():
    await client.start()
    logging.info("Бот запущен")
    print("Бот запущен")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
