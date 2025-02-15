from diskcache import Cache
from googleapiclient.discovery import build
from googlesearch import search


def insert_row(service, spreadsheet_id, num_rows, position=5):
    request_body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": 0,
                        "dimension": "ROWS",
                        "startIndex": position - 1,
                        "endIndex": position + num_rows - 1,
                    },
                    "inheritFromBefore": True,
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body).execute()


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
    cache = Cache('./caches')

    if cache.get(document_id) is None:
        service = build("docs", "v1", credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=document_id).execute()
        text_content = extract_text_from_doc(document)

        cache.set(document_id, text_content)

        return text_content
    else:
        return cache.get(document_id)


def update_google_sheet(creds, spreadsheet_id, papers, paper_links):
    """
    Update Google Sheets with extracted information from Google Docs. A paper duplication check is performed before a
    paper is added.
    :param creds: credentials
    :param spreadsheet_id:
    :param papers:
    :param paper_links:
    :return: None
    """
    service = build("sheets", "v4", credentials=creds)
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='B5:B100').execute()
    values = result.get('values', [])

    # Flatten the list of lists
    column_data = [item for sublist in values for item in sublist]

    # Filtering
    papers_info = dict(zip(papers, paper_links))
    filtered_papers = {key: value for key, value in papers_info.items() if key not in column_data}

    # Update
    insert_row(service, spreadsheet_id, len(filtered_papers))
    data_to_insert = [['=ROW()-4', key, 'paper', '', '', value] for key, value in filtered_papers.items()]
    if data_to_insert:
        for data in data_to_insert:
            body = {
                'values': [data]
            }
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='A5',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

    print("✅ Google Sheet updated successfully!")


def get_paper_link(papers):
    links = []
    for paper in papers:
        query = f"{paper} site:arxiv.org"
        results = search(query, num_results=1)  # Get the top result

        links.append(next(iter(results)))

    return links
