import os
import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

raw_url = os.environ["DATABASE_URL"]
# DO injects "postgresql://user:pass@host:port/db?sslmode=require". SQLAlchemy
# 2.x async needs the "+asyncpg" driver suffix; asyncpg does NOT understand
# libpq's sslmode query parameter, so we extract it into connect_args.
if raw_url.startswith("postgres://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgres://"):]
elif raw_url.startswith("postgresql://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgresql://"):]

parsed = urlparse(raw_url)
query_params = dict(parse_qsl(parsed.query))
sslmode = query_params.pop("sslmode", None)
DATABASE_URL = urlunparse(parsed._replace(query=urlencode(query_params)))

# DO Managed Postgres serves a self-signed cert from a private CA. asyncpg's
# default `ssl=True` builds a default context that verifies the chain and
# fails with SSLCertVerificationError. For the demo we encrypt the
# connection but skip chain verification — production deployments should
# bundle DO's CA cert and use ssl.CERT_REQUIRED instead.
if sslmode == "disable":
    connect_args = {}
else:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl": ssl_context}

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True, connect_args=connect_args
)


async def get_session() -> AsyncSession:
    return AsyncSession(engine)
