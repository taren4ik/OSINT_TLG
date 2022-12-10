import time, os
import json
import pandas as pd
import matplotlib.pyplot as plt
from telethon import TelegramClient
from telethon import functions
from dotenv import load_dotenv

load_dotenv()


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
channel = 't.me/pr_russia'
client = TelegramClient('osint', api_id, api_hash)


async def get_comment(channel, offset_msg, offset):
    result = await client(functions.messages.GetRepliesRequest(
        peer=channel,
        msg_id=offset_msg,
        offset_id=0,
        offset_date=0,
        add_offset=offset,
        limit=100,
        max_id=0,
        min_id=0,
        hash=0
    ))
    return result


async def main():
    user_ids = []
    first_names = []
    last_names = []
    usernames = []
    phones = []
    bots = []
    ids_comment = []
    messages_comment = []
    dates_comment = []
    post_id = []
    post_message = []
    post_date = []
    users_data = {}

    client_msg = await client.get_messages(channel)
    if client_msg[0].id:
        messages_total = client_msg[0].id
        offset_msg = messages_total
    else:
        print('нет поста!!!')
        offset_msg = ''

    while offset_msg > 41140:  # глубина сканирования
        client_msg = await client.get_messages(channel, ids=offset_msg)
        if client_msg is not None:
            post = client_msg
            if post.message == '':
                offset_msg = offset_msg - 1
                continue
            else:
                post_message.append(post.message)

            post_id.append(str(post.id))
            post_date.append(str(post.date.day) + '.' +
                             str(post.date.month) + '.' +
                             str(post.date.year))

        else:
            offset_msg = offset_msg - 1

        df_post = pd.DataFrame(
            {'Id': post_id, 'Date': post_date,
             'Message': post_message})

        df_post.to_csv(f'{channel.split("/")[1]}.csv', mode='a',
                       sep=':',
                       header=True,
                       index=False,
                       encoding='utf-16')

        try:
            part_of_division = client_msg.replies.replies // 100

            while part_of_division >= 0:
                result = await get_comment(channel, offset_msg,
                                           part_of_division * 100)

                for user in result.users:
                    user_ids.append(str(user.id))
                    first_names.append(str(user.first_name))
                    last_names.append(str(user.last_name))
                    usernames.append('@' + str(user.username))
                    phones.append(str(user.phone))
                    bots.append(str(user.bot))

                    if f'{user.id}' in users_data:
                        count = users_data[f'{user.id}'] + 1
                        users_data[f'{user.id}'] = count
                    else:
                        users_data[f'{user.id}'] = 1

                for msg in result.messages:
                    ids_comment.append(str(msg.sender_id))
                    messages_comment.append(str(msg.message))
                    dates_comment.append(str(msg.date.day) + '.' +
                                         str(msg.date.month) + '.' +
                                         str(msg.date.year))

                df_users = pd.DataFrame(
                    {'Id': user_ids,
                     'Username': usernames,
                     'First_name': first_names,
                     'Last_names': last_names,
                     'Phone': phones,
                     'isBot': bots})

                df_messages = pd.DataFrame(
                    {'Id': ids_comment,
                     'Date': dates_comment,
                     'Message': messages_comment})

                # sorted_df_messages = df_messages.sort_values(by='Id')

                df_comments = df_messages.merge(df_users, on='Id',
                                                how='left')
                df_comments = df_comments.drop_duplicates(subset='Id')
                part_of_division -= 1

            if df_comments.size != 0:
                df_comments.to_csv(f'{channel.split("/")[1]}.csv',
                                   mode='a',
                                   sep=';',
                                   header=True,
                                   index=False,
                                   encoding='utf-16')
                df_users = df_users[0:0]
                df_messages = df_messages[0:0]

        except:
            print(f'Нет информации по посту!!!!ID: {str(post.id)}')

        offset_msg = offset_msg - 1
        ids_comment = []
        messages_comment = []
        dates_comment = []

        post_id = []
        post_message = []
        post_date = []
        df_post = df_post[0:0]
        df_comments = df_comments[0:0]
        time.sleep(0.5)
    sorted_tuple = sorted(users_data.items(), key=lambda x: x[1],reverse=True)
    users_data = dict(sorted_tuple)

    with open("users.json", "w") as json_file:
        json.dump(users_data, json_file)

    fig, ax = plt.subplots()
    ax.pie(users_data.items(), labels=users_data.keys())
    ax.axis("equal")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())