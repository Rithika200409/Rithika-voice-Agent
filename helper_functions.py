from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from pathlib import Path
from pathlib import Path
THIS_DIR = Path(__file__).parent.parent


def get_text_from_google_doc(document_id,testing=False):
    """
    Retrieves text content from a Google Docs file using a service account.
    
    Args:
        document_id (str): The Google Docs file ID.
        service_account_file (str): Path to the service account JSON key file.
    
    Returns:
        str: The full text content of the document.
    """

    if testing:
        _,document_id=get_text_from_google_doc("1FgrGtmW8hofCcNnKoRBq1ZEr1wZ8D4FHOl2C5r61TFk")
        document_id = eval(document_id)['agent-id']

    # print(document_id)
    # document_id = '1QDMRdeshDR-PWA0HHkk1491iCcE0aVKd0-FZaOjXEMA'
    service_account_file = f'{THIS_DIR}/envs/gsheets-token.json'
    

    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    # Load credentials from service account file
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)

    # Build the Docs API service
    service = build('docs', 'v1', credentials=creds)

    # Retrieve the document
    doc = service.documents().get(documentId=document_id).execute()

    file_name = doc.get('title', 'Untitled Document')

    # Extract and return the text content
    text = ''
    for content in doc.get('body', {}).get('content', []):
        for element in content.get('paragraph', {}).get('elements', []):
            text_run = element.get('textRun')
            if text_run:
                text += text_run.get('content', '')

    return file_name,text


file_name,instructions = get_text_from_google_doc("1gcb7WBT7C6D4P3dT2hZry8USQMCsdI2txWNPHFGY4Fs")


# If modifying these scopes, delete the file token.json.
def book_appointment(summary, description, start_time, end_time, timezone, attendees=[]):

    SERVICE_ACCOUNT_FILE = f'{THIS_DIR}/envs/hospital-calender-448103-b5513a4f53c0.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    # Use service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Create the service
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": timezone},
        "end": {"dateTime": end_time, "timeZone": timezone},
        "attendees": [{"email": email} for email in attendees],
    }
    event_result = (
        service.events().insert(calendarId="0b2c0458945ed2eb28ecad4630b68d85fc8031387bb654748a583098cb691393@group.calendar.google.com", body=event).execute()
    )
    return event_result


