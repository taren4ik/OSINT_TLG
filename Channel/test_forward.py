import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

api_id = int(os.getenv("API_ID_3"))
api_hash = os.getenv("API_HASH_3")

client = TelegramClient(
    'session_tests',
    api_id,
    api_hash,
    device_model="iPhone 14 Pro Max",
    system_version="14.8.1",
    app_version="10.2",
    lang_code="ru"
)

SOURCE = {

}

TARGET = 'news_fresh_vl'


@client.on(events.NewMessage)
async def handler(event):
    if not event.chat or not event.chat.username:
        return

    if event.chat.username not in SOURCE:
        return

    await client.forward_messages(TARGET, event.message)


client.start()
print("✅ Запущено")
client.run_until_disconnected()
