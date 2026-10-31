# Gmail Rule Processor

![CI](https://github.com/aayxshkumar/gmail-rule-processor/actions/workflows/ci.yml/badge.svg)

> Built as a take-home assignment for HappyFox in June 2025.

Standalone Python scripts that read Inbox mail through the Gmail API, store it in PostgreSQL, and apply rules defined in a JSON file (mark read, mark unread, move to a label).

- `fetch_emails.py` fetches up to 50 of the latest Inbox messages, parses each one and stores sender, recipients, subject, snippet, body (the first `text/plain` part of multipart mail), received date, read state and label IDs in an `emails` table. The table is created if it does not exist, and messages already stored are skipped.
- `process_emails.py` loads `rules.json`, checks every stored email against the rule's conditions and, on a match, calls the Gmail API to apply the rule's actions. It prints each check and each change.
- `rules.py` validates the rules file and evaluates single conditions.
- `auth.py` runs the Google OAuth flow (scope `gmail.modify`) and caches the token in `token.json`.
- `db.py` defines the SQLAlchemy model and reads `DATABASE_URL` from the environment or a `.env` file.

## Requirements

- Python 3.12 (the version CI runs)
- PostgreSQL
- A Google Cloud project with the Gmail API enabled and an OAuth client ID of type Desktop

## Setup

```bash
git clone https://github.com/aayxshkumar/gmail-rule-processor.git
cd gmail-rule-processor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a database and point `DATABASE_URL` at it. Copy `.env.example` to `.env` and fill it in:

```properties
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
```

The `postgresql://` scheme uses the psycopg 3 driver installed from `requirements.txt`.

Download the OAuth client JSON from Google Cloud Console and save it as `credentials.json` in the project root. The first script run opens a browser for consent and writes `token.json` next to it. Both files are ignored by git.

## Usage

Run the scripts from the project root, since `rules.json` is read from the current directory.

```bash
python fetch_emails.py     # store Inbox messages in Postgres
python process_emails.py   # apply rules.json to the stored messages
```

SQL logging is on (`echo=True` in `db.py`), so the scripts print the queries they run.

## Rules

`rules.json` holds one rule:

```json
{
  "predicate": "any",
  "conditions": [
    { "field": "sender", "operator": "contains", "value": "quora.com" }
  ],
  "actions": [
    { "type": "mark_read" },
    { "type": "move", "label": "IMPORTANT" }
  ]
}
```

- `predicate`: `all` or `any` of the conditions must match.
- Text conditions: `field` is `sender`, `subject` or `body`; `operator` is `contains` or `equals`. Both compare case-insensitively.
- Date conditions: set both `field` and `operator` to `before` or `after`, and `value` to a number of days. `before` matches mail received less than that many days ago; `after` matches mail received more than that many days ago.
- Actions: `mark_read`, `mark_unread`, and `move` with a `label` name. `move` adds the label and removes `INBOX`; unknown label names are skipped with a warning.

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

The tests cover rule loading and condition matching only. They need no network, Gmail account or database.
