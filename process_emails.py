from datetime import datetime, timedelta

from googleapiclient.discovery import build

from auth import get_gmail_credentials
from db import Email, SessionLocal
from rules import load_rules


def evaluate(e: Email, cond: dict) -> bool:
    field, op, val = cond['field'], cond['operator'], cond['value']
    if field == 'sender': target = e.sender or ''
    elif field == 'subject': target = e.subject or ''
    elif field == 'body': target = e.body or ''
    elif field in ('before','after'):
        delta = datetime.now() - e.date_received
        days  = int(val)
        return (delta < timedelta(days=days)) if op=='before' else (delta > timedelta(days=days))
    else:
        return False

    if op == 'contains':    return val.lower() in target.lower()
    if op == 'equals':      return target.lower() == val.lower()
    return False


def apply_actions(service, msg_id: str, actions: list):
    mods = {'addLabelIds':[], 'removeLabelIds':[]}
    for act in actions:
        t = act['type']
        if t == 'mark_read':   mods['removeLabelIds'].append('UNREAD')
        elif t == 'mark_unread': mods['addLabelIds'].append('UNREAD')
        elif t == 'move':
            label_name = act['label']
            label_id   = LABEL_MAP.get(label_name)
            if not label_id:
                print(f"⚠️ unknown label \"{label_name}\"")
                continue
            mods['addLabelIds'].append(label_id)
            mods['removeLabelIds'].append('INBOX')

    if mods['addLabelIds'] or mods['removeLabelIds']:
        service.users().messages().modify(
            userId='me', id=msg_id, body=mods
        ).execute()
        print(f"→ {msg_id}: add={mods['addLabelIds']} remove={mods['removeLabelIds']}")


def process_all():
    creds    = get_gmail_credentials()
    service  = build('gmail','v1',credentials=creds)
    sess     = SessionLocal()
    ruleset  = load_rules('rules.json')

    # build a map of Gmail label-names to IDs
    labels = service.users().labels().list(userId='me').execute().get('labels',[])
    global LABEL_MAP
    LABEL_MAP = {l['name']:l['id'] for l in labels}

    emails = sess.query(Email).all()
    for e in emails:
        print(f"\nChecking {e.message_id} from {e.sender}")
        results = [evaluate(e, c) for c in ruleset['conditions']]
        print(" → condition results:", results)
        match = all(results) if ruleset['predicate']=='all' else any(results)
        if match:
            print(" ✓ RULE MATCHED – applying actions")
            apply_actions(service, e.message_id, ruleset['actions'])
        else:
            print(" ✗ no match")
    sess.close()


if __name__=='__main__':
    process_all()