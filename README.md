# IONOS Mail Gateway

Secure IMAP/SMTP gateway for an IONOS mailbox, designed for controlled AI-assisted mail operations.

## Current scope

- Read recent mail via IMAP over TLS
- Search mailbox messages
- Send mail via SMTP over TLS
- FastAPI HTTP interface
- Environment-based secrets only
- Docker-ready deployment
- Minimal audit logging hooks

## IONOS defaults

- IMAP: `imap.ionos.de:993` (TLS)
- SMTP: `smtp.ionos.de:465` (TLS)

## Quick start

```bash
cp .env.example .env
# fill in mailbox credentials locally only
python -m venv .venv
. .venv/bin/activate
pip install -e .
uvicorn ionos_gateway.app:app --host 0.0.0.0 --port 8080
```

Never commit `.env` or mailbox passwords.

## API

- `GET /health`
- `GET /mail/recent?limit=20`
- `GET /mail/search?q=sentinel&limit=20`
- `POST /mail/send`

Write operations should be placed behind an authentication layer before exposing this service to the public internet.
