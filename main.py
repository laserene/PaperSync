import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ollama import chat, ChatResponse

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

# The ID of a sample document.
DOCUMENT_ID = "1vrtnnG87pp2PuEXGZFWWYWSyA_Ls04cZTzKApcJFS1s"


def query_llm(prompt, model="deepseek-r1:1.5b"):
    response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response.message.content


def extract_text_from_doc(document):
    text = ""
    for element in document.get("body").get("content", []):
        if "paragraph" in element:
            for elem in element["paragraph"]["elements"]:
                if "textRun" in elem:
                    text += elem["textRun"]["content"]  # Extract text

    return text.strip()  # Remove unnecessary spaces/newlines


def main():
    """Shows basic usage of the Docs API.
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
        service = build("docs", "v1", credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        text_content = extract_text_from_doc(document)

        prompt = f'summary this document: {text_content}'

        paper_titles = query_llm(prompt)
        print(paper_titles)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
