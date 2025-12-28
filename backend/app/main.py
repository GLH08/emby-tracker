from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import emby, tmdb, watchlist, stats, auth, history, hero, calendar, progress, recommend, lists, ratings, export
from app.services.sync import sync_all_users, start_sync_scheduler, stop_sync_scheduler

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    
    # 启动时同步
    if settings.sync_on_startup:
        logger.info("启动时自动同步观看历史...")
        asyncio.create_task(sync_all_users())
    
    # 启动定时同步
    start_sync_scheduler()
    
    yield
    
    # 关闭时停止同步调度器
    stop_sync_scheduler()


app = FastAPI(
    title="Emby Tracker API",
    description="Emby 媒体库管理和观影记录追踪 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(emby.router, prefix="/api")
app.include_router(tmdb.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(hero.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(lists.router, prefix="/api")
app.include_router(ratings.router, prefix="/api")
app.include_router(export.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/config")
async def get_config():
    """获取前端配置"""
    return {
        "emby_url": settings.emby_url,
        "tmdb_image_base_url": settings.tmdb_image_base_url,
    }
