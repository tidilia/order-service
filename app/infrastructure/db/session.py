from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)


def create_engine(db_url: str):
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
    )


def create_session_maker(db_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(db_url)
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


# async def create_session_factory(db_url: str) -> AsyncGenerator[AsyncSession, None]:
#     session_maker = create_session_maker(db_url)
#     async with session_maker() as session:
#         yield session
