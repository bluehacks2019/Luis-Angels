import sys
import json
import time
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

PAT = 'EAAFkcN1DoJ0BAPwiRqGRN3AdvLjoNLOiWoXZCWa2uUyVtuJAdO57CBZC2gYSbMv73beNxLVTa9Sgn1ej4HqoicsXqOmU9LdyaY4juKxS9BIiCH7r8llffRraDS8WroJTg0UNWsBZAZB6q8fUGIJZAA7n142KFWGfJ4t55tRZBEZCQZDZD'
VERIFY_TOKEN = 'luis_angels'

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()

    display_greeting()

    if data["object"] == "page":
        for entry in data["entry"]:
            print(entry)
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                display_action(sender_id, "mark_seen")
                display_action(sender_id, "typing_on")
                time.sleep(0.5)

                if messaging_event.get("message"):  # someone sent us a message

                    message_text = messaging_event["message"]["text"]  # the message's text

                    nlp_entities = messaging_event["message"]["nlp"]["entities"]
                    sentiment = "unsure"
                    if (nlp_entities.get("sentiment")):
                        if (float(nlp_entities["sentiment"][0]["confidence"]) > 0.6):
                            sentiment = nlp_entities["sentiment"][0]["value"]

                    send_message(sender_id, message_text + ", sentiment: " + sentiment)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

                display_action(sender_id, "typing_off")

    return "ok", 200


def send_message(recipient_id, message_text):
    params = {
        "access_token": PAT
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)

def display_action(recipient_id, action):
    params = {
        "access_token": PAT
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action": action
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)

def display_greeting():
    params = {
        "access_token": PAT
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "greeting": [{
            "locale":"default",
            "text":"Hello {{user_first_name}}!!"
        }]
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile", params=params, headers=headers, data=data)


if __name__ == '__main__':
    app.run(debug=True)
