import os
import asyncio
import socks
import random
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, RPCError

load_dotenv()

API_ID = int(os.getenv("API_ID_3"))
API_HASH = os.getenv("API_HASH_3")
SOURCE = os.getenv("SOURCE").split(",")
TARGET = os.getenv("TARGET")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

client = TelegramClient(
    'tgch_session',
    API_ID,
    API_HASH,
    proxy=(
        socks.SOCKS5,
        os.getenv("PROXY_HOST"),
        int(os.getenv("PROXY_PORT")),
    ),
    system_version="4.16.31-vxCUSTOM",
    device_model="1.0.99",
)



@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    if not event.chat or not event.chat.username:
        return
    if not event.message:
        return
    text = (event.message.raw_text or "").lower()
    if "реклама" in text:
        return

    try:
        await client.forward_messages(TARGET, event.message)
        logging.info(f"➡️ @{event.chat.username}: {event.message.id}")
        await asyncio.sleep(random.uniform(3, 9))

    except FloodWaitError as e:
        logging.warning(f"⏳ FloodWait {e.seconds}")
        await asyncio.sleep(e.seconds + 1)

    except RPCError:
        if event.message.text:
            await client.send_message(TARGET, event.message.text)

    except Exception:
        logging.exception("❌ Ошибка")


with client:
    logging.info("🚀 Форвардер запущен")
    client.run_until_disconnected()
