"""Check-in 签到路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models import Checkin

router = APIRouter(prefix="/checkin", tags=["Check-in"])


class CheckinCreate(BaseModel):
    """创建 Check-in"""
    emby_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    media_type: str  # movie / episode
    title: str
    series_name: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    poster_path: Optional[str] = None
    year: Optional[int] = None
    runtime_minutes: int = 0
    comment: Optional[str] = None


@router.post("/")
async def create_checkin(
    user_id: str = Query(..., description="Emby 用户 ID"),
    data: CheckinCreate = ...,
    db: AsyncSession = Depends(get_db),
):
    """
    创建 Check-in（标记正在观看）
    如果已有活跃的 Check-in，会先结束它
    """
    # 结束之前的活跃 Check-in
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.user_id == user_id,
                Checkin.is_active == True,
            )
        )
    )
    active_checkin = result.scalar_one_or_none()
    if active_checkin:
        active_checkin.is_active = False
        active_checkin.ended_at = datetime.utcnow()
    
    # 创建新的 Check-in
    new_checkin = Checkin(
        user_id=user_id,
        emby_id=data.emby_id,
        tmdb_id=data.tmdb_id,
        media_type=data.media_type,
        title=data.title,
        series_name=data.series_name,
        season_number=data.season_number,
        episode_number=data.episode_number,
        poster_path=data.poster_path,
        year=data.year,
        runtime_minutes=data.runtime_minutes,
        comment=data.comment,
        is_active=True,
        started_at=datetime.utcnow(),
    )
    
    db.add(new_checkin)
    await db.commit()
    await db.refresh(new_checkin)
    
    return {
        "id": new_checkin.id,
        "message": "Check-in 成功",
        "checkin": format_checkin(new_checkin),
    }


@router.get("/current")
async def get_current_checkin(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取当前正在观看的内容"""
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.user_id == user_id,
                Checkin.is_active == True,
            )
        )
    )
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        return {"checkin": None}
    
    return {"checkin": format_checkin(checkin)}


@router.post("/end")
async def end_checkin(
    user_id: str = Query(..., description="Emby 用户 ID"),
    checkin_id: Optional[int] = Query(None, description="Check-in ID，不传则结束当前活跃的"),
    db: AsyncSession = Depends(get_db),
):
    """结束 Check-in"""
    if checkin_id:
        result = await db.execute(
            select(Checkin).where(Checkin.id == checkin_id)
        )
    else:
        result = await db.execute(
            select(Checkin).where(
                and_(
                    Checkin.user_id == user_id,
                    Checkin.is_active == True,
                )
            )
        )
    
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="没有找到活跃的 Check-in")
    
    checkin.is_active = False
    checkin.ended_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Check-in 已结束", "checkin": format_checkin(checkin)}


@router.get("/history")
async def get_checkin_history(
    user_id: str = Query(..., description="Emby 用户 ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取 Check-in 历史"""
    # 查询
    query = (
        select(Checkin)
        .where(Checkin.user_id == user_id)
        .order_by(Checkin.started_at.desc())
    )
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    checkins = result.scalars().all()
    
    # 总数
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Checkin.id)).where(Checkin.user_id == user_id)
    )
    total = count_result.scalar() or 0
    
    return {
        "items": [format_checkin(c) for c in checkins],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.delete("/{checkin_id}")
async def delete_checkin(
    checkin_id: int,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除 Check-in 记录"""
    result = await db.execute(
        select(Checkin).where(
            and_(
                Checkin.id == checkin_id,
                Checkin.user_id == user_id,
            )
        )
    )
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in 不存在")
    
    await db.delete(checkin)
    await db.commit()
    
    return {"message": "删除成功"}


def format_checkin(checkin: Checkin) -> dict:
    """格式化 Check-in 数据"""
    return {
        "id": checkin.id,
        "emby_id": checkin.emby_id,
        "tmdb_id": checkin.tmdb_id,
        "media_type": checkin.media_type,
        "title": checkin.title,
        "series_name": checkin.series_name,
        "season_number": checkin.season_number,
        "episode_number": checkin.episode_number,
        "poster_path": checkin.poster_path,
        "year": checkin.year,
        "runtime_minutes": checkin.runtime_minutes,
        "is_active": checkin.is_active,
        "started_at": checkin.started_at.isoformat() if checkin.started_at else None,
        "ended_at": checkin.ended_at.isoformat() if checkin.ended_at else None,
        "comment": checkin.comment,
    }
