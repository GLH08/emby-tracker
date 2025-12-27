from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import WatchHistory
from pydantic import BaseModel

router = APIRouter(prefix="/history", tags=["Watch History"])


class HistoryCreate(BaseModel):
    """手动添加观看记录"""
    emby_id: Optional[str] = None
    media_type: str  # Movie / Episode
    title: str
    series_id: Optional[str] = None
    series_name: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    year: Optional[int] = None
    runtime_minutes: int = 0
    community_rating: Optional[float] = None
    genres: list[str] = []
    watched: bool = True
    watch_progress: float = 100
    watched_at: Optional[datetime] = None


class HistoryUpdate(BaseModel):
    """更新观看记录"""
    watched: Optional[bool] = None
    watch_progress: Optional[float] = None
    watched_at: Optional[datetime] = None
    play_count: Optional[int] = None


class SyncResult(BaseModel):
    """同步结果"""
    added: int
    updated: int
    total: int


@router.get("/")
async def get_history(
    user_id: str,
    media_type: Optional[str] = Query(None, description="Movie / Episode / all"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取本地存储的观看历史"""
    query = select(WatchHistory).where(WatchHistory.user_id == user_id)
    
    if media_type and media_type != "all":
        query = query.where(WatchHistory.media_type == media_type)
    
    # 按观看时间倒序
    query = query.order_by(WatchHistory.watched_at.desc().nullslast(), WatchHistory.updated_at.desc())
    
    # 总数
    count_query = select(func.count(WatchHistory.id)).where(WatchHistory.user_id == user_id)
    if media_type and media_type != "all":
        count_query = count_query.where(WatchHistory.media_type == media_type)
    
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "items": [
            {
                "id": item.id,
                "emby_id": item.emby_id,
                "media_type": item.media_type,
                "title": item.title,
                "series_id": item.series_id,
                "series_name": item.series_name,
                "season_number": item.season_number,
                "episode_number": item.episode_number,
                "year": item.year,
                "runtime_minutes": item.runtime_minutes,
                "community_rating": item.community_rating,
                "genres": item.genres or [],
                "watched": item.watched,
                "watch_progress": item.watch_progress,
                "play_count": item.play_count,
                "watched_at": item.watched_at.isoformat() if item.watched_at else None,
                "source": item.source,
            }
            for item in items
        ],
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
    }


@router.post("/sync")
async def sync_from_emby(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """从 Emby 同步观看记录到本地数据库（包括已看完和正在观看的）"""
    from app.services.sync import sync_user_history
    
    try:
        result = await sync_user_history(user_id, db)
        return SyncResult(added=result["added"], updated=result["updated"], total=result["added"] + result["updated"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/")
async def add_history(
    user_id: str,
    data: HistoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """手动添加观看记录"""
    watched_at = data.watched_at or datetime.utcnow()
    
    new_record = WatchHistory(
        user_id=user_id,
        emby_id=data.emby_id,
        media_type=data.media_type,
        title=data.title,
        series_id=data.series_id,
        series_name=data.series_name,
        season_number=data.season_number,
        episode_number=data.episode_number,
        year=data.year,
        runtime_minutes=data.runtime_minutes,
        community_rating=data.community_rating,
        genres=data.genres,
        watched=data.watched,
        watch_progress=data.watch_progress,
        play_count=1,
        watched_at=watched_at,
        source="manual",
    )
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return {"id": new_record.id, "message": "添加成功"}


@router.put("/{history_id}")
async def update_history(
    history_id: int,
    data: HistoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新观看记录"""
    result = await db.execute(select(WatchHistory).where(WatchHistory.id == history_id))
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    if data.watched is not None:
        record.watched = data.watched
    if data.watch_progress is not None:
        record.watch_progress = data.watch_progress
    if data.watched_at is not None:
        record.watched_at = data.watched_at
    if data.play_count is not None:
        record.play_count = data.play_count
    
    await db.commit()
    
    return {"message": "更新成功"}


@router.delete("/{history_id}")
async def delete_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除观看记录"""
    result = await db.execute(select(WatchHistory).where(WatchHistory.id == history_id))
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    await db.delete(record)
    await db.commit()
    
    return {"message": "删除成功"}


@router.get("/stats")
async def get_history_stats(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取观看历史统计"""
    # 总记录数
    total_result = await db.execute(
        select(func.count(WatchHistory.id)).where(WatchHistory.user_id == user_id)
    )
    total_count = total_result.scalar() or 0
    
    # 总观看时长
    time_result = await db.execute(
        select(func.sum(WatchHistory.runtime_minutes)).where(
            and_(WatchHistory.user_id == user_id, WatchHistory.watched == True)
        )
    )
    total_minutes = time_result.scalar() or 0
    
    # 电影数量
    movie_result = await db.execute(
        select(func.count(WatchHistory.id)).where(
            and_(WatchHistory.user_id == user_id, WatchHistory.media_type == "Movie")
        )
    )
    movie_count = movie_result.scalar() or 0
    
    # 剧集数量
    episode_result = await db.execute(
        select(func.count(WatchHistory.id)).where(
            and_(WatchHistory.user_id == user_id, WatchHistory.media_type == "Episode")
        )
    )
    episode_count = episode_result.scalar() or 0
    
    return {
        "total_count": total_count,
        "total_minutes": total_minutes,
        "movie_count": movie_count,
        "episode_count": episode_count,
    }
