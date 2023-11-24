from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from datetime import datetime as dt
from datetime import timedelta as td
from configparser import ConfigParser


#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####


configur = ConfigParser()
config_file_obj = configur.read('config.ini')
user_upload_pdf_path = configur.get(enivronment,'user_upload_pdf')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def read_mail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    file_list = []
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gmail_token.json'):
        creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gmail_token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages')

        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            datetime = int(message['internalDate'])//1000
            if dt.fromtimestamp(datetime).strftime('%Y-%m-%d') >= ((dt.now() + td(days=-3)).strftime('%Y-%m-%d')) :
                try:
                    # print(msg['id'])
                    for parts in message['payload']['parts'] :
                        if parts['filename'].find(".pdf") != -1:
                            if 'data' in parts['body']:
                                data = parts['body']['data']
                            else:
                                att_id = parts['body']['attachmentId']
                                att = service.users().messages().attachments().get(userId='me', messageId=message['id'],id=att_id).execute()
                                data = att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            filename = parts['filename']
                            try :
                                path = user_upload_pdf_path+filename
                                file_list.append(filename)
                                if(parts['filename'].find(".pdf") != -1): 
                                    with open(path, 'xb') as f:
                                        f.write(file_data)
                                        f.close()
                            except Exception as e:
                                # print(e)
                                continue
                        
                except Exception as e:
                    # print(e)
                    continue
        
        return list(set(file_list))
            
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
        return []


if __name__ == '__main__':
    read_mail()