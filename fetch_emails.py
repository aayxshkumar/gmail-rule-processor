import base64
from googleapiclient.discovery import build
from auth import get_gmail_credentials
from db import SessionLocal, init_db, Email
from email import message_from_bytes
from datetime import datetime


def fetch_and_store(max_results=50):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)
    init_db()
    session = SessionLocal()

    res = service.users().messages().list(
        userId='me', labelIds=['INBOX'], maxResults=max_results
    ).execute()
    for m in res.get('messages', []):
        msg = service.users().messages().get(
            userId='me', id=m['id'], format='raw'
        ).execute()
        raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        mime = message_from_bytes(raw)

        # headers
        sender = mime['From']
        recipients = mime.get_all('To', [])      
        subject = mime.get('Subject', '')
        snippet = msg.get('snippet', '')
        # body
        body = ''
        if mime.is_multipart():
            for part in mime.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = mime.get_payload(decode=True).decode(errors='ignore')

        # meta
        date_ms = int(msg['internalDate'])
        date_rcv = datetime.fromtimestamp(date_ms / 1000)
        is_read = 'UNREAD' not in msg.get('labelIds', [])
        labels = msg.get('labelIds', [])           # list

        # upsert
        existing = session.query(Email).filter_by(message_id=msg['id']).first()
        if not existing:
            e = Email(
                message_id=msg['id'],
                thread_id=msg.get('threadId'),
                sender=sender,
                recipients=recipients,
                subject=subject,
                snippet=snippet,
                body=body,
                date_received=date_rcv,
                is_read=is_read,
                labels=labels
            )
            session.add(e)

    session.commit()
    session.close()


if __name__ == '__main__':
    fetch_and_store()