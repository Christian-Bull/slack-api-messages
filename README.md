# slack-messages

Quick wip script for exporting slack messages to csv

Creates a csv file for each channel in `./src`  

<br>

# Quickstart

Use a venv if you want

    $ python3 -m venv venv
    $ source venv/bin/activate

Install pytest and slack-sdk

    $ python3 -m pip install -r requirements.txt

Add the following env vars:
    
    export SLACKTOKEN=<yourbotsslacktoken>  

    * Optional, if not supplied it will return all channels
    export CHANNEL=<channeltogetmessagesfrom>  

run it :)

    $ python3 main.py

<br>

# Tests

Loops through valid tests in the `/tests` folder

    $ pytest

Not particulary useful but ensures your token and slack connection are valid

