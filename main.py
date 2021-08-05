import os, sys, csv
from time import sleep
from datetime import datetime
from pprint import pprint
from slack_sdk import WebClient
import slack_sdk.errors


# slack object, basically info related to a slack workspace
class Workspace:
    def __init__(self, token):
        # slack api token
        self.token = token

        # create client
        self.client = WebClient(self.token)

        # get all channels
        try:
            channel_response = self.client.conversations_list(
                types="public_channel")

            if channel_response['ok'] == True:
                self.channel_dict = {}

                for channel in channel_response['channels']:
                    self.channel_dict[channel['id']] = channel['name']
            
        except slack_sdk.errors.SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            print('Api failed: {}'.format(e.response["error"]))

        # gets all users for a workspace
        # try api call
        try:
            user_response = self.client.users_list()
        except slack_sdk.errors.SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]
            print('Api failed: {}'.format(e.response["error"]))

        # associates users ids and names
        if user_response['ok'] == True:
            self.users = {}
            for user in user_response['members']:
                self.users[user['id']] = user['name']

    # gets all messages from the channel name provided
    def get_messages(self, channel, **kwargs):

        # gets channel id and messages
        try:
            c = list(self.channel_dict.keys())[
                list(self.channel_dict.values()).index(channel)]

            results = self.client.conversations_history(
                token=self.token,
                channel=c,
                limit=1000,
                latest=kwargs.get('latest', None)  # defaults to now
            )

            # lazy way of getting around the rate limit
            print("zzz + channel: {0} timestamp: {1}".format(channel, datetime.now()))
            sleep(2)


        except ValueError as e:
            print("Channel {0} not in workspace: {1}".format(channel, e))

        except slack_sdk.errors.SlackApiError as e:
            print("Slack API error: {0}".format(e))
            return None

        messages = []

        for message in results['messages']:
            if message['type'] == "message":

                # empty try because I'm lazy, only want user messages
                try:
                    ts = datetime.utcfromtimestamp(
                        int(float(message['ts']))).strftime('%Y-%m-%d %H:%M:%S')
                    msg = {
                        'ts': message['ts'],
                        'utc_time': ts,
                        'user': self.users[message['user']],
                        'channel': channel,
                        'text': message['text']
                    }
                    messages.append(msg)
                except Exception as e:
                    pass

        return messages

    # returns all messages and outputs to csv, gets around the 1k limit
    def get_all_messages(self, channel = None):
        
        # gets all channels
        channels = self.get_channels()

        # if a channel argument was given, ensure it's valid
        if channel:
            if (channel in channels):

                # clear the current list and only add the provided channel
                channels.clear()
                channels.append(channel)


        for channel in channels:
            
            # empty vars to get our loop started
            ts = ''
            messages = True 

            while messages:
                messages = self.get_messages(channel, latest=ts)
                
                # if there's any messages in the channel, save to csv
                if messages:
                    filename = 'src/' + str(channel) + '.csv'
                    self.output_msgs_to_csv(filename, messages)

                    ts = messages[-1]['ts']
                    


    # outputs messages to csv
    def output_msgs_to_csv(self, file, messages):

        # if file doesn't exist, create one and insert headers
        if os.path.isfile(file) == False:
            headers = []
            for key in messages[0]:
                headers.append(key)

            with open(file, mode='w') as outputfile:
                output_writer = csv.writer(outputfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                output_writer.writerow(headers)

        # open csv in append mode and insert data
        with open(file, mode='a') as outputfile:
            output_writer = csv.writer(outputfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            reader = csv.reader(outputfile)

            # loops through messages and writes to csv
            for message in messages:
                row = []
                
                for key in message:
                    row.append(message[key])

                output_writer.writerow(row)


    # outputs info about a workplace
    def print_info(self):
        pprint(self.channel_dict)
        pprint(self.users)

    # lists all channels by name
    def get_channels(self):
        channels = []
        
        for key in self.channel_dict:
            channels.append(self.channel_dict[key])

        return channels
    

# gets token info
def slacktoken():
    return os.environ.get('SLACKTOKEN')


# runs everything
if __name__ == "__main__":
    
    # check if a channel is provided
    if 'CHANNEL' in os.environ:
        channel = os.environ.get('CHANNEL')
    else:
        channel = None

    # creates workspace instance
    workspace = Workspace(slacktoken())

    # checks for info flags
    if any(x in sys.argv for x in ['-i', '--info']):
        workspace.print_info()

    else:
        workspace.get_all_messages(channel=channel)
