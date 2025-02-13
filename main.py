import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from ollama import chat, ChatResponse

from config import *
from google_services import *


def query_llm(prompt, model="deepseek-r1:1.5b"):
    response: ChatResponse = chat(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': prompt,
            }
        ]
    )

    return response.message.content


def main():
    """
        Shows basic usage of the Docs API.
        Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        text_content = read_google_docs(creds, DOCUMENT_ID)

        prompt = f'Extract all papers from this text: {text_content}'

        paper_titles = query_llm(prompt)

        update_google_sheet(creds, SPREADSHEET_ID, RANGE, paper_titles)

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
