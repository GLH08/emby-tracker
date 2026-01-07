from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import get_settings

settings = get_settings()

# 处理 SQLite URL
database_url = settings.database_url
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    database_url,
    echo=settings.debug,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def migrate_db():
    """执行数据库迁移（添加新列）"""
    async with engine.begin() as conn:
        # 检查并添加 poster_path 列到 watch_history 表
        try:
            await conn.execute(text(
                "ALTER TABLE watch_history ADD COLUMN poster_path VARCHAR(500)"
            ))
            print("Added poster_path column to watch_history table")
        except Exception as e:
            # 列已存在时会报错，忽略
            if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                print(f"Migration warning (poster_path): {e}")


async def init_db():
    # 导入模型以确保它们被注册到 Base.metadata
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 执行数据库迁移
    await migrate_db()
