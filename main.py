import os

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from huggingface_hub import InferenceClient

from config import *
from google_services import *

os.environ['HF_TOKEN'] = "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"


def query_llm(prompt, model="deepseek-r1:1.5b"):
    client = InferenceClient("HuggingFaceTB/SmolLM2-135M-Instruct")
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    response = client.chat_completion(messages)
    return response.choices[0].message


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

        prompt = (f'You are a helpful AI Agent in report reading. You are tasked with reading a report that often '
                  f'contains references to other papers and extract all paper titles. References are often bounded '
                  f'inside a pair of parenthesis and follow the (author - paper title) format. Do not duplicate the '
                  f'paper of the report. Output a list of paper titles seperated by a comma. \n\nHere is the report: '
                  f'{text_content}\n\n Output:')

        # paper_titles = query_llm(prompt)

        # update_google_sheet(creds, SPREADSHEET_ID, RANGE, paper_titles)

        API_URL = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-cased-distilled-squad"
        headers = {
            "Authorization": f"Bearer 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",
        }
        payload = {
            "inputs": {
                "question": 'What are the paper mentioned?',
                "context": f'{text_content}'
            },
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        print(response.json())

    except HttpError as err:
        print(err)
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
