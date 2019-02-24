import sys
import json
import time
from datetime import date
from datetime import datetime
from story_generator import generator
import random

import requests
from flask import Flask, request
import google_sheets

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

questions = [
    "notable experience",
    "reason to be thankful",
    "small victory"
]
responses_to_positive_start = [
    "Thank you for sharing that with me!",
    "That's great!",
    "Nice!",
	"Awesome!",
	"That's cool!"
]
responses_to_positive_end = [
    "I'd love to hear more about it!",
    "Do you have more positive memories for today?",
    "How's school?",
	"Anything else you want to share?"
]
responses_to_thanks = [
    "Don't mention it!",
    "You're welcome!",
    "Welcome!",
	"Anytime!",
    "I'll always be here whenever you wanna share. :)"
]

responses_to_bye = [
	"Alright. I hope to hear more from you soon!",
	"I see. Talk to you again soon!",
	"Thanks for sharing with me. I hope we can talk again tomorrow!",
	"I'll still be here tomorrow when you have something you want to share!"
]

responses_neutral_negative = [
	"I see. Can you think of something that made you even a little bit happy today?",
	"Oh, okay. Maybe there's more you can share with me!"
]

# active_users = set()

spreadsheet = '1HRSiXLFFe3fYqGKCYSRYsYYgHpWQDKegpDJ1M4--mTQ'

users_data = {}
def prepare_user_data(sheet):
    for i in range(1, len(sheet)):
        users_data[sheet[i][0]] = [[], [], []]

    for i in range(1, len(sheet)):
        temp = (sheet[i][1], sheet[i][3])
        if sheet[i][2] == "positive":
            users_data[sheet[i][0]][0].append(temp)
        elif sheet[i][2] == "unsure":
            users_data[sheet[i][0]][1].append(temp)
        else:
            users_data[sheet[i][0]][2].append(temp)

@app.route('/', methods=['POST'])
def webhook():
    global users_data
    users_data = {}

    sheet = google_sheets.get_values(spreadsheet, 'messages')
    prepare_user_data(sheet)

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

                    bye = False
                    if (nlp_entities.get("bye")):
                        if (float(nlp_entities["bye"][0]["confidence"]) > 0.8):
                            bye = True

                    thanks = False
                    if (nlp_entities.get("thanks")):
                        if (float(nlp_entities["thanks"][0]["confidence"]) > 0.8):
                            thanks = True

                    datetime_body = None
                    datetime_type = None
                    if nlp_entities.get("datetime"):
                        if float(nlp_entities["datetime"][0]["confidence"]) > 0.8:
                            datetime_body = nlp_entities["datetime"][0]["_body"]
                            datetime_type = nlp_entities["datetime"][0]["type"]

                    if sender_id not in users_data:
                        q = "Hi! Can you share a " + random.choice(questions) + " for today?"
                        send_message(sender_id, q)
                    else:
                        if thanks:
                            r = random.choice(responses_to_thanks)
                            send_message(sender_id, r)
                        elif bye:
                            send_message(sender_id, random.choice(responses_to_bye))
                        elif sentiment == "positive":
                            r_start = random.choice(responses_to_positive_start)
                            r_end = random.choice(responses_to_positive_end)
                            if datetime_body:
                                if datetime_type == "interval":
                                    r_end = "What else happened " + datetime_body + "?"
                                else:
                                    r_end = "What else happened around " + datetime_body + "?"
                            if (len(users_data[sender_id][0]) + 1) % 10 == 0:
                                robot_message = "I'm really thankful that you've shared your positive experiences with me. In return, let me write an imaginary continuation of your last message:"
                                imaginary_story = generator(message_text)
                                send_message(sender_id, robot_message + "\n\n" + imaginary_story)
                            else:
                                send_message(sender_id, r_start + " " + r_end)
                        elif random.random() < 0.20 and len(users_data[sender_id][0]) > 0:
                            message, date_dati = random.choice(users_data[sender_id][0])
                            send_message(sender_id, "On " + date_dati + ", this memory lifted your spirits up. :)")
                            send_message(sender_id, message)
                        else: # if unsure or negative
                            send_message(sender_id, random.choice(responses_neutral_negative))

                    values = [
                        [sender_id,
                        message_text,
                        sentiment,
                        str(date.today())
                        ]
                    ]
                    google_sheets.append_values(spreadsheet, 'messages', 'RAW', values)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    payload = messaging_event["postback"]["payload"]
                    print(payload)
                    send_message(sender_id, payload)

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
        "get_started": {
            "payload": "get_started"
        },
        "greeting": [{
            "locale":"default",
            "text":"Hello, {{user_first_name}}!"
        }]
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile", params=params, headers=headers, data=data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8081)
