import pandas as pd
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class UpdateDataInGsheetClass():
    def __init__(self,sheet_id,range_name) :
        self.gsheet_id = sheet_id
        self.grange_name = range_name
    
    def update_values(self,product_df):
        gsheet_df = product_df
        values = []
        # print(product_df)
        for data in gsheet_df.itertuples():
            values.append([data[1],data[2],data[3],data[4],data[5],data[6],data[7]])
        data = [
            {"range": self.grange_name, "values": values}
        ]
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": data
        }
        creds = None
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
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
            result = (
                service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=self.gsheet_id,body=body)
                .execute()
            )
            
            
        except HttpError as err:
            print(err)