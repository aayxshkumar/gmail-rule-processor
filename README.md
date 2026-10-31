# Gmail Rule Processor

> Built as a take-home assignment for HappyFox in June 2025.

Standalone Python scripts to integrate with the Gmail API, store Inbox emails in Postgres, and process them via JSON‐defined rules (mark read/unread, move).

## Prerequisites

- Python 3.8+ (tested on 3.11) with `pip` and `virtualenv`
- PostgreSQL
- Google Cloud project with Gmail API enabled

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/aayxshkumar/gmail-rule-processor
   cd happyfox_assignment
   ```

2. Create a `.env` in project root:
   ```properties
   DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db_name>
   ```

3. Start Postgres and create DB & user:
   ```bash
   brew services start postgresql
   psql postgres -c "CREATE USER happyfox_user WITH PASSWORD 'passpass';"
   psql postgres -c "CREATE DATABASE happyfox_db OWNER happyfox_user;"
   ```

4. Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## OAuth Credentials

1. In Google Cloud Console:
   - Enable Gmail API
   - Create OAuth Client ID (Desktop)
   - Download JSON as `credentials.json` in project root
2. Generate `token.json` by running:
   ```bash
   python auth.py
   ```

## Usage

- Fetch and store emails in Postgres:
  ```bash
  python fetch_emails.py
  ```

- Define your rules in `rules.json`. Example:
  ```json
  {
    "predicate": "any",
    "conditions": [
      { "field": "sender", "operator": "contains", "value": "newsletter@" }
    ],
    "actions": [
      { "type": "mark_read" },
      { "type": "move", "label": "NEWSLETTER" }
    ]
  }
  ```

- Process stored emails with your rules:
  ```bash
  python process_emails.py
  ```
  Console will print each applied modification.

## Database Maintenance

- To drop and recreate the `emails` table:
  ```bash
  psql "$DATABASE_URL" -c "DROP TABLE IF EXISTS emails;"
  python fetch_emails.py
  ```

## Configuration

- `.env`: set `DATABASE_URL`
- `rules.json`: define your rule sets
- `credentials.json` + `token.json`: OAuth flow files

---

