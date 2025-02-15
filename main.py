import os

from langchain_core.output_parsers.json import JsonOutputParser

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from groq import Groq

from config import *
from services.google_services import *

load_dotenv()


def query_llm(prompt, model="llama3-8b-8192"):
    client = Groq()
    messages = [
        {"role": "system", "content": "You are a helpful AI Agent in report reading. You are tasked with reading a "
                                      "report that often contains references to other papers and extract all paper "
                                      "titles. References are often bounded inside a pair of parenthesis and follow "
                                      "the (author - paper title) format. Do not duplicate the paper of the report. "},
        {"role": "user", "content": prompt}
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
    )

    json_parser = JsonOutputParser()
    output = json_parser.parse(completion.choices[0].message.content)
    return output


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
        prompt = (f'Return only the paper titles as JSON. No additional text.'
                  f'\nHere is the report:'
                  f'{text_content}\n\n #### \nOutput:')

        papers = query_llm(prompt)
        paper_links = get_paper_link(papers)
        
        for i in range(len(papers)):
            print(f'{papers[i]} - {paper_links[i]}')
        
        # update_google_sheet(creds, SPREADSHEET_ID, RANGE, paper_titles)

    except HttpError as err:
        print(err)
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
