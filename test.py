import os
from slack_sdk import WebClient

client = WebClient(token=os.environ['SLACKTOKEN'])

print(client.api_test())
