import os
from slack_sdk import WebClient

# tests slacktoken and api connection
def test_connection():
    client = WebClient(token=os.environ['SLACKTOKEN'])

    response = client.api_test()

    assert response['ok'] == True
