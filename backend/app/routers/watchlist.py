from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models import Watchlist, WatchHistory
from app.schemas import WatchlistCreate, WatchlistResponse, WatchHistoryCreate, WatchHistoryResponse

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


# ============ 想看列表 ============

@router.get("/", response_model=list[WatchlistResponse])
async def get_watchlist(
    media_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取想看列表"""
    query = select(Watchlist).order_by(Watchlist.added_at.desc())
    if media_type:
        query = query.where(Watchlist.media_type == media_type)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=WatchlistResponse)
async def add_to_watchlist(
    item: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加到想看列表"""
    # 检查是否已存在
    query = select(Watchlist)
    if item.emby_id:
        query = query.where(Watchlist.emby_id == item.emby_id)
    elif item.tmdb_id:
        query = query.where(
            (Watchlist.tmdb_id == item.tmdb_id) & 
            (Watchlist.media_type == item.media_type)
        )
    
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="已在想看列表中")
    
    db_item = Watchlist(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """从想看列表移除"""
    result = await db.execute(select(Watchlist).where(Watchlist.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="未找到该项目")
    
    await db.delete(item)
    await db.commit()
    return {"success": True}


@router.get("/check")
async def check_in_watchlist(
    emby_id: Optional[str] = None,
    tmdb_id: Optional[int] = None,
    media_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """检查是否在想看列表中"""
    query = select(Watchlist)
    if emby_id:
        query = query.where(Watchlist.emby_id == emby_id)
    elif tmdb_id and media_type:
        query = query.where(
            (Watchlist.tmdb_id == tmdb_id) & 
            (Watchlist.media_type == media_type)
        )
    else:
        return {"in_watchlist": False}
    
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    return {"in_watchlist": item is not None, "item": item}


# ============ 观看历史 ============

@router.get("/history", response_model=list[WatchHistoryResponse])
async def get_watch_history(
    media_type: Optional[str] = None,
    watched: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """获取观看历史"""
    query = select(WatchHistory).order_by(WatchHistory.last_watched_at.desc())
    
    if media_type:
        query = query.where(WatchHistory.media_type == media_type)
    if watched is not None:
        query = query.where(WatchHistory.watched == watched)
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/history", response_model=WatchHistoryResponse)
async def add_watch_history(
    item: WatchHistoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加/更新观看历史"""
    # 查找现有记录
    result = await db.execute(
        select(WatchHistory).where(WatchHistory.emby_id == item.emby_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # 更新现有记录
        for key, value in item.model_dump().items():
            setattr(existing, key, value)
        existing.last_watched_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    
    # 创建新记录
    db_item = WatchHistory(**item.model_dump())
    db_item.last_watched_at = datetime.utcnow()
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/history/{item_id}")
async def delete_watch_history(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除观看历史"""
    result = await db.execute(select(WatchHistory).where(WatchHistory.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="未找到该记录")
    
    await db.delete(item)
    await db.commit()
    return {"success": True}
