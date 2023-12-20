import pandas as pd
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class FetchFromGsheetClass():
    
    def __init__(self,sheet_id,range_name) :
        self.gsheet_id = sheet_id
        self.grange_name = range_name
    
    def get_values(self):
        gsheet_df = pd.DataFrame()
        creds = None
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("gsheet_token.json"):
            creds = Credentials.from_authorized_user_file("gsheet_token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "gsheet_credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("gsheet_token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("sheets", "v4", credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.gsheet_id, range=self.grange_name)
                .execute()
            )
            values = result.get("values", [])

            for row in values:
                temp_gsheet_df = pd.DataFrame()
                temp_gsheet_df['DESCRIPTION'] = [row[0]]
                try :
                    temp_gsheet_df['L'] = [row[1]]
                except :
                    temp_gsheet_df['L'] = ''
                try :
                    temp_gsheet_df['ML'] = [row[2]]
                except :
                    temp_gsheet_df['ML'] = ''
                try :
                    temp_gsheet_df['KG'] = [row[3]]
                except :
                    temp_gsheet_df['KG'] = ''
                try :
                    temp_gsheet_df['GM'] = [row[4]]
                except :
                    temp_gsheet_df['GM'] = ''
                try :
                    temp_gsheet_df['PC'] = [row[5]]
                except :
                    temp_gsheet_df['PC'] = ''
                try :
                    temp_gsheet_df['PRODUCT_GROUP'] = [row[6]]
                except :
                    temp_gsheet_df['PRODUCT_GROUP'] = ''
                
                gsheet_df = pd.concat([gsheet_df,temp_gsheet_df],axis=0,ignore_index=True)
            return gsheet_df
        
        except HttpError as err:
            print(err)

