import os
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine
from app.models import Guestbook

# SENTRY_DSN is read but never validated; bogus values are tolerated.
_sentry_dsn = os.environ.get("SENTRY_DSN", "")

app = FastAPI(title="hello-archgen-fastapi")


class GuestbookCreate(BaseModel):
    text: str


@app.get("/healthcheck")
async def healthcheck() -> dict:
    return {"ok": True}


@app.post("/guestbook")
async def create_entry(payload: GuestbookCreate) -> dict:
    async with AsyncSession(engine) as session:
        entry = Guestbook(text=payload.text, created_at=datetime.utcnow())
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return {"id": entry.id, "text": entry.text}


@app.get("/guestbook")
async def list_entries() -> list[dict]:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Guestbook).order_by(Guestbook.id))
        return [
            {"id": r.id, "text": r.text, "created_at": r.created_at.isoformat()}
            for r in result.scalars()
        ]
