from __future__ import annotations

import email
import imaplib
import smtplib
import ssl
from dataclasses import dataclass
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.policy import default

from .config import Settings


@dataclass
class MailSummary:
    uid: str
    subject: str
    sender: str
    date: str


def _decode(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def _connect_imap(settings: Settings) -> imaplib.IMAP4_SSL:
    client = imaplib.IMAP4_SSL(
        settings.imap_host,
        settings.imap_port,
        ssl_context=ssl.create_default_context(),
    )
    client.login(settings.ionos_email, settings.ionos_password.get_secret_value())
    return client


def recent_mail(settings: Settings, limit: int = 20) -> list[MailSummary]:
    client = _connect_imap(settings)
    try:
        status, _ = client.select("INBOX", readonly=True)
        if status != "OK":
            raise RuntimeError("Unable to select INBOX")
        status, data = client.uid("search", None, "ALL")
        if status != "OK":
            raise RuntimeError("Unable to search INBOX")
        uids = data[0].split()[-limit:]
        results: list[MailSummary] = []
        for uid in reversed(uids):
            status, msg_data = client.uid("fetch", uid, "(RFC822.HEADER)")
            if status != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                continue
            msg = email.message_from_bytes(msg_data[0][1], policy=default)
            results.append(
                MailSummary(
                    uid=uid.decode(),
                    subject=_decode(msg.get("Subject")),
                    sender=_decode(msg.get("From")),
                    date=_decode(msg.get("Date")),
                )
            )
        return results
    finally:
        try:
            client.logout()
        except Exception:
            pass


def search_mail(settings: Settings, query: str, limit: int = 20) -> list[MailSummary]:
    client = _connect_imap(settings)
    try:
        status, _ = client.select("INBOX", readonly=True)
        if status != "OK":
            raise RuntimeError("Unable to select INBOX")
        safe_query = query.replace('"', "")
        status, data = client.uid("search", None, "TEXT", f'"{safe_query}"')
        if status != "OK":
            raise RuntimeError("Unable to search INBOX")
        uids = data[0].split()[-limit:]
        results: list[MailSummary] = []
        for uid in reversed(uids):
            status, msg_data = client.uid("fetch", uid, "(RFC822.HEADER)")
            if status != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                continue
            msg = email.message_from_bytes(msg_data[0][1], policy=default)
            results.append(
                MailSummary(
                    uid=uid.decode(),
                    subject=_decode(msg.get("Subject")),
                    sender=_decode(msg.get("From")),
                    date=_decode(msg.get("Date")),
                )
            )
        return results
    finally:
        try:
            client.logout()
        except Exception:
            pass


def send_mail(settings: Settings, to: list[str], subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.ionos_email
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as client:
        client.login(settings.ionos_email, settings.ionos_password.get_secret_value())
        client.send_message(msg)
