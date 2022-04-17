import logging
import os
from dotenv import load_dotenv
from pyrogram import Client
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters

load_dotenv()

token = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
app = Client('new_account', api_id, api_hash)

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


def parsing(update, context):
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


def msg_parse(update, context):
    pass


def people_parse(update, context):
    print(context.user_data.get('chat_name', 'Not found'))
    url = f'https://t.me/{ context.user_data.get("chat_name", "Not found")}'
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    standart_phones = []
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


def main():
    while True:
        updater = Updater(token)
        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(CommandHandler('people', people_parse))
        updater.dispatcher.add_handler(CommandHandler('message', msg_parse))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, parsing))
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
