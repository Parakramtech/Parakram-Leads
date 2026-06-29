from threading import Lock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class _LazyEngine:
    def __init__(self):
        self._engine = None
        self._lock = Lock()

    def _get_engine(self):
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._engine = create_async_engine(
                        settings.DATABASE_URL,
                        echo=settings.DEBUG,
                        pool_size=settings.DB_POOL_SIZE,
                        max_overflow=settings.DB_MAX_OVERFLOW,
                        pool_pre_ping=True,
                        pool_recycle=3600,
                    )
        return self._engine

    def __getattr__(self, name):
        return getattr(self._get_engine(), name)


class _LazySessionFactory:
    def __init__(self, engine):
        self._factory = None
        self._engine = engine

    def __call__(self):
        if self._factory is None:
            self._factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
        return self._factory

    def __getattr__(self, name):
        return getattr(self.__call__(), name)


engine = _LazyEngine()
async_session_factory = _LazySessionFactory(engine)


class Base(DeclarativeBase):
    pass


async def get_db():
    factory = async_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
