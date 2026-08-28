import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.db import Base
from app.models import *

async def main():
    engine=create_async_engine(settings.database_url)
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
if __name__=="__main__": asyncio.run(main())
