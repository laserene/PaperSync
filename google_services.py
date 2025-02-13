from googleapiclient.discovery import build

def extract_text_from_doc(document):
    text = ""
    for element in document.get("body").get("content", []):
        if "paragraph" in element:
            for elem in element["paragraph"]["elements"]:
                if "textRun" in elem:
                    text += elem["textRun"]["content"]  # Extract text

    return text.strip()  # Remove unnecessary spaces/newlines


def read_google_docs(creds, document_id):
    """
        Extract the content of the Google Docs document
    :param creds: credentials
    :param document_id:
    :return: content of the document
    """
    service = build("docs", "v1", credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=document_id).execute()
    text_content = extract_text_from_doc(document)

    return text_content


def update_google_sheet(creds, spreadsheet_id, cell_range, text):
    """
    Update Google Sheets with extracted information from Google Docs. A paper duplication check is performed before a
    paper is added.
    :param creds: credentials
    :param spreadsheet_id:
    :param cell_range:
    :param text:
    :return: None
    """
    service = build("sheets", "v4", credentials=creds)

    values = [[text]]  # Wrap text in a list
    body = {"values": values}

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
        valueInputOption="RAW",
        body=body
    ).execute()

    print("✅ Google Sheet updated successfully!")