import httplib2
from googleapiclient.discovery import build
from oauth2client import file, client, tools
import os, json
from datetime import datetime
import google_auth_oauthlib.flow
import google.oauth2.credentials
import requests
from oauthlib.oauth2.rfc6749.errors import MissingCodeError
from google.auth.exceptions import RefreshError
from google.oauth2 import service_account

CLIENT_SECRETS_FILE = 'peep-secrets.json'
SCOPES = ['https://www.googleapis.com/auth/drive',
	'https://www.googleapis.com/auth/drive.file',
	'https://www.googleapis.com/auth/spreadsheets'
]

spreadsheet = '1HRSiXLFFe3fYqGKCYSRYsYYgHpWQDKegpDJ1M4--mTQ'

# ------------------ REMOVE IN PRODUCTION ----------------------
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def append_values(spreadsheet_id, range_name, value_input_option, values):
	# Load credentials from the session.
	# print(info)
	credentials = service_account.Credentials.from_service_account_file(
		CLIENT_SECRETS_FILE, scopes=SCOPES)

	service = build('sheets', 'v4', credentials=credentials)

    # [START sheets_append_values]
	# values = [
	#     [
	#         # Cell values ...
	#     ],
	#     # Additional rows ...
	# ]
	# # [START_EXCLUDE silent]
	# values = _values
	# [END_EXCLUDE]
	body = {
		'values': values
	}
	result = service.spreadsheets().values().append(
	    spreadsheetId=spreadsheet_id, range=range_name,
	    valueInputOption=value_input_option, body=body).execute()
	# print('{0} cells appended.'.format(result \
	#    .get('updates') \
    #    .get('updatedCells')))
    # [END sheets_append_values]
	return result

append_values(spreadsheet, 'messages', 'RAW', [[5, 'askldfjas', 'I hate life!']])