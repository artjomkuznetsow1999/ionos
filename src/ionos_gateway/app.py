from __future__ import annotations

import hmac
from dataclasses import asdict

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from .config import Settings, get_settings
from .mail import recent_mail, search_mail, send_mail

app = FastAPI(title="IONOS Mail Gateway", version="0.1.0")


class SendRequest(BaseModel):
    to: list[EmailStr] = Field(min_length=1, max_length=20)
    subject: str = Field(min_length=1, max_length=998)
    body: str = Field(min_length=1, max_length=200_000)


def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    expected = settings.api_key.get_secret_value()
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mail/recent", dependencies=[Depends(require_api_key)])
def get_recent(
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> list[dict[str, str]]:
    return [asdict(item) for item in recent_mail(settings, limit)]


@app.get("/mail/search", dependencies=[Depends(require_api_key)])
def get_search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> list[dict[str, str]]:
    return [asdict(item) for item in search_mail(settings, q, limit)]


@app.post("/mail/send", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(require_api_key)])
def post_send(payload: SendRequest, settings: Settings = Depends(get_settings)) -> dict[str, str]:
    send_mail(settings, [str(address) for address in payload.to], payload.subject, payload.body)
    return {"status": "accepted"}
