import asyncio
import os
import pandas as pd

from dotenv import load_dotenv
from telethon import TelegramClient
from random import randrange

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
choice = ()  # Список id.
client = TelegramClient('osint', api_id, api_hash)

channel = ''  # Бот для отправки.


async def main():
    """ Send messsage."""
    sequence = {}
    df_buffer = pd.DataFrame()
    for value in choice:
        now = randrange(1, 7)
        delay = (randrange(5, 25) + now)
        await client.send_message(channel, f'{value}')
        await asyncio.sleep(randrange(1, 5))
        message = await client.get_messages(channel)
        message = message[0]
        await message.click(0, 0)
        messag = await client.get_messages(channel, limit=10)
        for msg in messag:
            # if msg.media is not None:
            #     await client.download_media(message=msg)
            if '##############' and '######' in msg.message:
                report = msg.message.split('\n')
                for value in report:
                    if '####' in value:
                        tg = value[5:]
                    elif '######' in value:
                        phone = value[10:]

                sequence[tg] = phone
                df_buffer = pd.DataFrame.from_dict(sequence,
                                                   orient='index',
                                                   columns=[
                                                       "COUNT"]).reset_index()

        await asyncio.sleep(delay)
        df_buffer.to_csv('PHONE_users.csv',
                         mode='a',
                         sep=';',
                         header=False,
                         index=False,
                         encoding='utf-16')


with client:
    client.loop.run_until_complete(main())
