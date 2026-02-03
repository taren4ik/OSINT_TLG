import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("API_ID_3"))
API_HASH = os.getenv("API_HASH_3")
SOURCE = os.getenv("SOURCE")
TARGET = os.getenv("TARGET")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

client = TelegramClient(
    'session_tests',
    API_ID,
    API_HASH,
    device_model="iPhone 14 Pro Max",
    system_version="14.8.1",
    app_version="10.2",
    lang_code="ru"
)



@client.on(events.NewMessage)
async def handler(event):
    if not event.chat or not event.chat.username:
        return

    if event.chat.username not in SOURCE:
        return

    await client.forward_messages(TARGET, event.message)


client.start()
logging.info(f"Приложение запущено ✅")
client.run_until_disconnected()
