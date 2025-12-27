from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import WatchHistory
from app.services.emby import emby_service
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
    added = 0
    updated = 0
    
    try:
        # 获取所有已播放的电影（已看完）
        movies_played = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Movie",
            is_played=True,
            sort_by="DatePlayed",
            sort_order="Descending",
            limit=1000,
        )
        
        # 获取所有已播放的剧集（已看完）
        episodes_played = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Episode",
            is_played=True,
            sort_by="DatePlayed",
            sort_order="Descending",
            limit=1000,
        )
        
        # 获取正在观看的（有进度但未完成）- 使用 Resume 接口
        resume_items = await emby_service.get_resume_items(user_id=user_id, limit=100)
        
        # 合并所有项目，用字典去重（以 emby_id 为 key）
        all_items_dict = {}
        
        for item in movies_played.items:
            all_items_dict[item.id] = item
        
        for item in episodes_played.items:
            all_items_dict[item.id] = item
        
        # Resume 项目优先级更高（进度更新）
        for item in resume_items:
            all_items_dict[item.id] = item
        
        all_items = list(all_items_dict.values())
        
        for item in all_items:
            # 检查是否已存在
            existing = await db.execute(
                select(WatchHistory).where(
                    and_(
                        WatchHistory.user_id == user_id,
                        WatchHistory.emby_id == item.id
                    )
                )
            )
            existing_record = existing.scalar_one_or_none()
            
            # 计算进度
            progress = 0
            if item.runtime_ticks and item.playback_position_ticks:
                progress = (item.playback_position_ticks / item.runtime_ticks) * 100
            elif item.played:
                progress = 100
            
            # 解析观看时间
            watched_at = None
            if item.last_played_date:
                try:
                    watched_at = datetime.fromisoformat(item.last_played_date.replace("Z", "+00:00"))
                except:
                    pass
            
            # 如果没有播放日期，使用当前时间
            if not watched_at:
                watched_at = datetime.utcnow()
            
            runtime_minutes = int(item.runtime_ticks / 600000000) if item.runtime_ticks else 0
            
            if existing_record:
                # 更新：只更新进度和播放次数（如果有变化）
                needs_update = False
                
                # 进度更新（允许进度变大或变小，因为可能重新观看）
                if abs(progress - existing_record.watch_progress) > 0.1:
                    existing_record.watch_progress = progress
                    needs_update = True
                
                if item.play_count > existing_record.play_count:
                    existing_record.play_count = item.play_count
                    needs_update = True
                
                # 更新已看完状态
                if item.played != existing_record.watched:
                    existing_record.watched = item.played
                    needs_update = True
                
                # 更新观看时间（如果 Emby 有更新）
                if watched_at and item.last_played_date:
                    if not existing_record.watched_at or watched_at > existing_record.watched_at:
                        existing_record.watched_at = watched_at
                        existing_record.last_played_date = item.last_played_date
                        needs_update = True
                
                if needs_update:
                    updated += 1
            else:
                # 新增记录
                new_record = WatchHistory(
                    user_id=user_id,
                    emby_id=item.id,
                    media_type=item.type,
                    title=item.name,
                    series_id=item.series_id,
                    series_name=item.series_name,
                    season_number=item.parent_index_number,
                    episode_number=item.index_number,
                    year=item.year,
                    runtime_minutes=runtime_minutes,
                    community_rating=item.community_rating,
                    genres=item.genres,
                    watched=item.played,
                    watch_progress=progress,
                    play_count=max(item.play_count, 1),  # 至少播放过1次
                    watched_at=watched_at,
                    last_played_date=item.last_played_date,
                    source="emby",
                )
                db.add(new_record)
                added += 1
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")
    
    return SyncResult(added=added, updated=updated, total=added + updated)


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
