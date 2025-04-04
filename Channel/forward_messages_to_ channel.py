import asyncio
import os
from dotenv import load_dotenv
from random import randrange
from telethon import TelegramClient, events

load_dotenv()

api_id = os.getenv('API_ID_2')
api_hash = os.getenv('API_HASH_2')

# Список исходных каналов и целевой канал
source_channels = []
target_channel = 'news_fresh_vl'

client = TelegramClient('forward',
                        api_id,
                        api_hash,
                        system_version='4.16.31-vxCUSTOM',
                        device_model='1.0.97'
                                     'osint',
                        )

async def main():
    await client.start()
    print("Бот запущен! Ожидаем сообщения...")


    @client.on(events.NewMessage(chats=source_channels))
    async def handler(event):
        try:
            await client.forward_messages(target_channel, event.message)
            print(f"Переслано сообщение из {event.chat.title} | ID: {event.message.id}")

            await asyncio.sleep(randrange(1, 7))

        except Exception as e:
            print(f"Ошибка: {str(e)}")


    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Работа бота остановлена")
