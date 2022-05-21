import os
import logging
from telethon.sync import TelegramClient
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Bot
from multiprocessing import Process
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
from asyncio import set_event_loop, new_event_loop

load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

bot = Bot(token=token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введите название чата '.format(name),

    )
    logging.DEBUG('wake_up отработала')


def parsing(update, context):
    """ Парсинг пользователей чата."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['/people'], ['/message']],
                                  resize_keyboard=True)
    context.user_data['chat_name'] = update.message.text
    # Используя контекст context.user_data
    context.bot.send_message(
        chat_id=chat.id,
        text='Выберете тип отчета ',
        reply_markup=buttons,
    )
    # print(context.user_data.get('chat_name', 'Not found'))
    # procs = []
    # proc = Process(target=msg_parse, args=(context.user_data['chat_name']), )
    # procs.append(proc)
    # proc.start()
    # for proc in procs:
    #     proc.join()


def msg_parse(update, context):
    # Получаем информацию о чате, из которого пришло сообщение,
    # и сохраняем в переменную chat
    user_chat = update.effective_chat
    #context.user_data['chat_name'] = update.message.text
    chat = context.user_data['chat_name']
    # proc = Process(target=client, args=(chat, user_chat), )
    # proc.start()
    # print('Start')
    # proc.join()

    set_event_loop(new_event_loop())
    client(chat, user_chat)


def client(chat, url):
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    standart_phones = []
    url = f'https://t.me/{chat}'
    app = TelegramClient('osint', api_id, api_hash)
    app.start()
    participants = app.get_participants(url)  # получаем список участников
    # считывание основных параметров участников
    for user in participants:
        user_ids.append(str(user.id))
        first_names.append(str(user.first_name))
        last_names.append(str(user.last_name))
        usernames.append('@' + str(user.username))
        standart_phones.append(str(user.phone))
        # if len(user_ids) == 10:
        # break
    # df_list = pd.DataFrame({'Id': user_ids,'Usernames': usernames,'First_name': first_names, 'Last_names': last_names,'standart_phones': standart_phones})
    # df_list.to_csv('D:\HHHH.csv', sep=';', header=True, index=False)
    print(user_ids)
    app.run_until_disconnected()


def people_parse(update, context):
    pass


def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('message', msg_parse))

    updater.dispatcher.add_handler(
        CommandHandler('people', people_parse))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parsing))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
