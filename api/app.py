import os
import logging
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi
from onboarding_tutorial import OnboardingTutorial

import json
import random
import time
import pandas as pd, numpy as np
import csv

import sys
from io import StringIO
import contextlib


# Initialize a Flask app to host the events adapter
app = Flask(__name__)
#CORS(app)

slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

code_calls = 1
# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])




def code_blocks(code):
    blocks = []

    IN_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*In* *["+str(code_calls)+"]: * " + str(code["input"])
            ),
        },
    }
    DIVIDER_BLOCK = {"type": "divider"}

    output_text = ""

    if code["output"]:
        output_text = code["output"]
    else:
        output_text = code["eval"]



    OUT_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "*Out* *["+str(code_calls)+"]: * "+ str(output_text)
            ),
        },
    }
    blocks.append(IN_BLOCK)
    blocks.append(DIVIDER_BLOCK)
    blocks.append(OUT_BLOCK)
    return blocks

def start_onboarding(user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = slack_web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


@app.route("/health")
def health():
    return jsonify({"healthy": "true"})


def run_code(code):
    jsonResp = {}

    print("Got this as code " + str(code))
    jsonResp["input"] = code

    with stdoutIO() as s:
        try:
            exec(code,globals())
            jsonResp["status"] = "success"
            jsonResp["output"] = s.getvalue()
            try:
                jsonResp["eval"] = eval(code)
            except:
                jsonResp["eval"] = ""
        except Exception as e:
            print(e)
            print("Something wrong with the code")
            jsonResp["status"] = "error"
            jsonResp["output"] = str(e)

    return jsonResp

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("app_mention")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    print("got message")
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "help":
        return start_onboarding(user_id, channel_id)
    else:
        print(user_id)
        print(text)
        code_snippet = text.split(" ",1)[1]
        code = run_code(code_snippet)
        slack_web_client.chat_postMessage(
            channel=channel_id,
            blocks = code_blocks(code)
            )



if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    #ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(host="0.0.0.0", port=5035)