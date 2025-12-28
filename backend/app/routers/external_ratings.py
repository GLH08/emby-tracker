"""
外部评分 API 路由
获取 IMDB、烂番茄、Metacritic 评分
"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db, async_session_maker
from app.services.omdb import omdb_service
from app.services.emby import emby_service
from app.models import ExternalRating
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/external-ratings", tags=["外部评分"])

# 同步状态
_sync_status = {
    "is_running": False,
    "total": 0,
    "processed": 0,
    "success": 0,
    "failed": 0,
    "skipped": 0,
    "current_item": "",
    "error": None
}


@router.get("/")
async def get_external_ratings(
    imdb_id: Optional[str] = Query(None, description="IMDB ID (如 tt1234567)"),
    tmdb_id: Optional[int] = Query(None, description="TMDB ID"),
    title: Optional[str] = Query(None, description="标题（当没有 IMDB ID 时使用）"),
    year: Optional[int] = Query(None, description="年份"),
    media_type: str = Query("movie", description="媒体类型 (movie/tv)"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取外部评分（IMDB、烂番茄、Metacritic）
    
    优先使用 IMDB ID 查询，如果没有则使用标题+年份搜索。
    结果会自动缓存到数据库，7天内重复查询直接返回缓存。
    """
    if not imdb_id and not title:
        raise HTTPException(status_code=400, detail="需要提供 imdb_id 或 title")
    
    result = await omdb_service.get_ratings_cached(
        db=db,
        imdb_id=imdb_id,
        tmdb_id=tmdb_id,
        title=title,
        year=year,
        media_type=media_type
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="未找到评分数据")
    
    return result


@router.get("/search")
async def search_external(
    query: str = Query(..., description="搜索关键词"),
    media_type: str = Query("movie", description="媒体类型 (movie/series)"),
    page: int = Query(1, ge=1, description="页码")
):
    """搜索媒体（用于查找 IMDB ID）"""
    result = await omdb_service.search(query, media_type, page)
    
    if not result:
        return {"results": [], "total": 0}
    
    return {
        "results": result.get("Search", []),
        "total": int(result.get("totalResults", 0))
    }


@router.get("/status")
async def get_service_status():
    """
    获取 OMDb 服务状态
    
    返回各 API Key 的使用情况和剩余配额
    """
    return omdb_service.get_status()


@router.get("/sync-status")
async def get_sync_status():
    """获取批量同步状态"""
    return _sync_status


@router.post("/sync")
async def start_sync(
    background_tasks: BackgroundTasks,
    user_id: str = Query(..., description="Emby 用户 ID"),
    force: bool = Query(False, description="是否强制刷新已缓存的评分")
):
    """
    开始批量同步 Emby 媒体库的外部评分
    
    扫描 Emby 媒体库中所有电影和剧集，获取 IMDB/烂番茄/Metacritic 评分并缓存。
    已缓存的项目默认跳过，除非设置 force=true。
    """
    global _sync_status
    
    if _sync_status["is_running"]:
        raise HTTPException(status_code=400, detail="同步任务正在进行中")
    
    # 重置状态
    _sync_status = {
        "is_running": True,
        "total": 0,
        "processed": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "current_item": "正在获取媒体列表...",
        "error": None
    }
    
    # 在后台执行同步
    background_tasks.add_task(sync_external_ratings_task, user_id, force)
    
    return {"message": "同步任务已启动", "status": _sync_status}


async def sync_external_ratings_task(user_id: str, force: bool = False):
    """后台同步任务"""
    global _sync_status
    
    try:
        # 获取所有电影（get_items 默认已启用 Recursive）
        movies = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Movie",
            limit=10000
        )
        
        # 获取所有剧集（Series，不是 Episode）
        series = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Series",
            limit=10000
        )
        
        all_items = []
        for item in movies.items:
            all_items.append({"item": item, "type": "movie"})
        for item in series.items:
            all_items.append({"item": item, "type": "tv"})
        
        _sync_status["total"] = len(all_items)
        _sync_status["current_item"] = f"共 {len(all_items)} 个项目待处理"
        
        async with async_session_maker() as db:
            for entry in all_items:
                item = entry["item"]
                media_type = entry["type"]
                
                _sync_status["processed"] += 1
                _sync_status["current_item"] = item.name
                
                try:
                    # 获取 IMDB ID
                    imdb_id = None
                    tmdb_id = None
                    
                    if hasattr(item, 'provider_ids') and item.provider_ids:
                        imdb_id = item.provider_ids.get('Imdb')
                        tmdb_id_str = item.provider_ids.get('Tmdb')
                        if tmdb_id_str:
                            try:
                                tmdb_id = int(tmdb_id_str)
                            except:
                                pass
                    
                    # 检查是否已缓存
                    if imdb_id and not force:
                        stmt = select(ExternalRating).where(ExternalRating.imdb_id == imdb_id)
                        result = await db.execute(stmt)
                        if result.scalar_one_or_none():
                            _sync_status["skipped"] += 1
                            continue
                    
                    # 获取评分
                    result = await omdb_service.get_ratings_cached(
                        db=db,
                        imdb_id=imdb_id,
                        tmdb_id=tmdb_id,
                        title=item.name,
                        year=item.year,
                        media_type=media_type
                    )
                    
                    if result:
                        _sync_status["success"] += 1
                    else:
                        _sync_status["failed"] += 1
                    
                    # 避免请求过快
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"同步 {item.name} 失败: {e}")
                    _sync_status["failed"] += 1
        
        _sync_status["current_item"] = "同步完成"
        
    except Exception as e:
        logger.error(f"同步任务失败: {e}")
        _sync_status["error"] = str(e)
        _sync_status["current_item"] = f"同步失败: {e}"
    finally:
        _sync_status["is_running"] = False


@router.get("/cached-count")
async def get_cached_count(db: AsyncSession = Depends(get_db)):
    """获取已缓存的评分数量"""
    stmt = select(func.count(ExternalRating.id))
    result = await db.execute(stmt)
    count = result.scalar()
    return {"count": count}


@router.get("/cached")
async def get_all_cached_ratings(
    limit: int = Query(5000, description="最大返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有已缓存的评分（用于前端全局缓存）
    
    返回精简数据，只包含 ID 和评分
    """
    stmt = select(
        ExternalRating.imdb_id,
        ExternalRating.tmdb_id,
        ExternalRating.imdb_rating
    ).where(
        ExternalRating.imdb_rating.isnot(None)
    ).limit(limit)
    
    result = await db.execute(stmt)
    ratings = [
        {
            "imdb_id": row.imdb_id,
            "tmdb_id": row.tmdb_id,
            "imdb_rating": row.imdb_rating
        }
        for row in result.fetchall()
    ]
    
    return {"ratings": ratings, "count": len(ratings)}
