import asyncio
import logging
import os
from dotenv import load_dotenv
from random import randrange
from telethon.errors import FloodWaitError
from telethon import TelegramClient, events

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)


api_id = os.getenv('API_ID_2')
api_hash = os.getenv('API_HASH_2')

# Список исходных каналов и целевой канал
# source_channels = ['svodka25', 'vlnews25', 'newsvlc', 'newsvlru', 'jobbber123']
source_channels = ['news_kremlin']
target_channel = 'news_kremlin_reserve'

client = TelegramClient('forward',
                        api_id,
                        api_hash,
                        device_model="iPhone 13 Pro Max",
                        system_version="14.8.1",
                        app_version="8.4",
                        lang_code="en",
                        system_lang_code="en-US"
                        )


async def check_channels():
    for channel in source_channels:
        try:
            entity = await client.get_entity(channel)
            logging.info(f"Канал {channel} доступен: {entity.id}")
        except Exception as e:
            logging.error(f"Ошибка доступа к {channel}: {str(e)}")


async def main():
    await client.start()
    logging.info("Бот запущен!")
    print("Бот запущен! Ожидаем сообщения...")

    await check_channels()
    @client.on(events.NewMessage(chats=source_channels))
    async def handler(event):
        try:
            #await client.forward_messages(target_channel, event.message)
            await client.send_message(target_channel, event.message)
            logging.info(f"Переслано из {event.chat.title} | ID: {event.message.id}")
            await asyncio.sleep(randrange(1, 3))
        except FloodWaitError as e:
            logging.warning(f"FloodWait: ожидаем {e.seconds} сек.")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            print(f"Ошибка: {str(e)}")

    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Работа бота остановлена")
        print("Работа бота остановлена")
