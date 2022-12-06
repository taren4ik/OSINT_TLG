import time
import pandas as pd
from telethon import TelegramClient
from telethon import functions

api_id = 5323380
api_hash = '4f155364624eec73220ef19877b2d60'
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

    client_msg = await client.get_messages(channel)
    if client_msg[0].id:
        messages_total = client_msg[0].id
        offset_msg = 41153
    else:
        print('нет поста!!!!')
        offset_msg = ''

    while True:
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
                       sep=';',
                       header=True,
                       index=False,
                       encoding='utf-8')

        try:
            part_of_division = client_msg.replies.replies // 100
            header_comment = True

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
                                             how='inner')

                df_comments.to_csv(f'{channel.split("/")[1]}.csv',
                                   mode='a',
                                   sep=';',
                                   header=header_comment,
                                   index=False,
                                   encoding='utf-8')

                part_of_division -= 1
                header_comment = False

        except:
            print(f'Нет информации по посту!!!! {str(post.id)}')

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


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
