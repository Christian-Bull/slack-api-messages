import os
from slack import WebClient

client = WebClient(token=os.environ['SLACKTOKEN'])

api_response = client.api_test()

print(api_response)
