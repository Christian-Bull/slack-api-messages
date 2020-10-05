import os
import sqlite3
import json
from datetime import datetime
from slack import WebClient
import slack.errors


# slack object, basically info related to a slack workspace
class Workspace:
    def __init__(self, token):
        # slack api token
        self.token = token

    # gets all channels for a workspace
        self.client = WebClient(self.token)

        # try api call
        try:
            channel_response = self.client.conversations_list(
                types="public_channel")
        except slack.errors.SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            print('Api failed: {}'.format(e.response["error"]))

        if channel_response['ok'] == True:
            self.channel_dict = {}
            for channel in channel_response['channels']:
                self.channel_dict[channel['id']] = channel['name']

    # gets all users for a workspace
        # try api call
        try:
            user_response = self.client.users_list()
        except slack.errors.SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            print('Api failed: {}'.format(e.response["error"]))

        # associates users ids and names
        if user_response['ok'] == True:
            self.users = {}
            for user in user_response['members']:
                self.users[user['id']] = user['name']

    # gets all messages from the channel names provided
    def get_messages(self, channels):
        client = WebClient(self.token)

        for channel in channels:
            # gets channel id
            c = list(self.channel_dict.keys())[
                list(self.channel_dict.values()).index(channel)]
            results = client.conversations_history(
                token=self.token,
                channel=c,
                limit=1000
            )
            for message in results['messages']:
                if message['type'] == "message":
                    # empty try because I'm lazy, only want user messages
                    ts = datetime.utcfromtimestamp(int(float(message['ts']))).strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        ts = datetime.utcfromtimestamp(int(float(message['ts']))).strftime('%Y-%m-%d %H:%M:%S')
                        msg = {
                            'user': self.users[message['user']],
                            'channel': channel,
                            'text': message['text'],
                            'timestamp': message['ts'],
                            'utc_time': ts
                        }
                        insert_data(msg)
                    
                    except Exception as e:
                        pass


    # outputs info about a workplace
    def print_info(self):
        print(self.channel_dict)
        print(self.users)


# gets token info
def slacktoken():
    return os.environ.get('SLACKTOKEN')


# creates table it it's not already created
def create_db():
    conn = sqlite3.connect('src/slack')
    c = conn.cursor()

    # this might be sql injection idk it doesn't matter
    c.execute('''CREATE TABLE IF NOT EXISTS slack
                            (user text,
                             channel text,
                             timestamp text,
                             utc_time text,
                             msg text)''')

    conn.commit()
    conn.close()


# takes dict and makes insert statement
def insert_data(msg):
    conn = sqlite3.connect('src/slack')
    c = conn.cursor()

    # users sqlite3 concatination insated of python
    c.execute('INSERT INTO slack VALUES (?, ?, ?, ?, ?)',
              (msg['user'],
               msg['channel'],
               msg['timestamp'],
               msg['utc_time'],
               msg['text']))
    conn.commit()
    conn.close()


def main():
    # creates workspace instance
    workspace = Workspace(slacktoken())

    # creates db
    create_db()

    # inserts messages into db
    # just gets one channel right now for testing
    workspace.get_messages([
        os.environ.get('CHANNEL')
    ])

# runs everything
main()
