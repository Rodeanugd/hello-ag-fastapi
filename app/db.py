import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

raw_url = os.environ["DATABASE_URL"]
# DO Postgres URLs arrive as "postgres://..." or "postgresql://..." with
# a "?sslmode=require" query param. SQLAlchemy 2.x async needs the
# "+asyncpg" driver suffix; asyncpg itself does NOT understand libpq's
# sslmode query parameter — passing it through 500s every DB call.
if raw_url.startswith("postgres://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgres://"):]
elif raw_url.startswith("postgresql://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgresql://"):]

# Extract sslmode (if present) into a connect_args option asyncpg understands.
parsed = urlparse(raw_url)
query_params = dict(parse_qsl(parsed.query))
sslmode = query_params.pop("sslmode", None)
DATABASE_URL = urlunparse(parsed._replace(query=urlencode(query_params)))

# DO managed Postgres always requires TLS; honor an explicit sslmode=disable.
connect_args = {} if sslmode == "disable" else {"ssl": True}

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True, connect_args=connect_args
)


async def get_session() -> AsyncSession:
    return AsyncSession(engine)
