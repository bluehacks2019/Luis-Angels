# Peep-Chatbot

- Team Name and Members
- Application Description
- Installation Guide
- App Guidelines (guidelines include the languages, frameworks, libraries, etc. that were used in making the app)

Luis' Angels
- Franz Louis T. Cesista
- Daniel Raymond D. Del Rio
- Luis Rainier T. Ligunas
- Riana Mary Claire G. Lim

Peep Chatbot
Peep is a chatbot that serves as a simple journal for anyone. It focuses on the everyday joys and achievements and helps the users recall good memories when they need to. Anyone can message the chatbot and share their stories and memories to it, and Peep will engage in simple conversations with them to encourage them to reflect on good experiences no matter how insignificant they may seem. Peep reminds you that you are more than your negative thoughts and experiences.

## Install

You'll need to have Python 3.7.0 installed on your computer.
You'll need to install all the dependencies found in requirements.txt:
```python
pip3 install -r requirements.txt
```

In order to install Flask on Google App Engine and get the chatbot working, please check out the instructions [here](https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env).

To set up the connection between Flask and Messenger, please check out this link:
https://developers.facebook.com/docs/messenger-platform/getting-started/
Please note that the user token from https://developers.facebook.com/tools/accesstoken should be inputted into the code as well.

## App Guidelines
We used Flask and Google App Engine to run the chatbot through Facebook Messenger. For the database of the messages, we fetched from and wrote the data to a spreadsheet using Google Developer API.
