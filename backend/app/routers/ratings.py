"""用户评分路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from typing import Optional, List
from pydantic import BaseModel, Field
from app.database import get_db
from app.models import UserRating

router = APIRouter(prefix="/ratings", tags=["Ratings"])


class RatingCreate(BaseModel):
    emby_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    media_type: str
    title: str
    rating: int = Field(..., ge=1, le=10)
    review: Optional[str] = None


class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=10)
    review: Optional[str] = None


@router.get("/")
async def get_ratings(
    user_id: str = Query(..., description="Emby 用户 ID"),
    media_type: Optional[str] = Query(None, description="movie / tv / episode"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有评分"""
    query = select(UserRating).where(UserRating.user_id == user_id)
    
    if media_type:
        query = query.where(UserRating.media_type == media_type)
    
    query = query.order_by(UserRating.rated_at.desc())
    
    # 分页
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    ratings = result.scalars().all()
    
    # 获取总数
    count_query = select(func.count(UserRating.id)).where(UserRating.user_id == user_id)
    if media_type:
        count_query = count_query.where(UserRating.media_type == media_type)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return {
        "ratings": [
            {
                "id": r.id,
                "emby_id": r.emby_id,
                "tmdb_id": r.tmdb_id,
                "media_type": r.media_type,
                "title": r.title,
                "rating": r.rating,
                "review": r.review,
                "rated_at": r.rated_at.isoformat() if r.rated_at else None,
            }
            for r in ratings
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/")
async def create_rating(
    data: RatingCreate,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """创建或更新评分"""
    # 检查是否已存在
    query = select(UserRating).where(
        and_(
            UserRating.user_id == user_id,
            UserRating.media_type == data.media_type,
        )
    )
    
    if data.tmdb_id:
        query = query.where(UserRating.tmdb_id == data.tmdb_id)
    elif data.emby_id:
        query = query.where(UserRating.emby_id == data.emby_id)
    else:
        raise HTTPException(status_code=400, detail="需要提供 emby_id 或 tmdb_id")
    
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        # 更新现有评分
        existing.rating = data.rating
        existing.review = data.review
        await db.commit()
        return {
            "id": existing.id,
            "rating": existing.rating,
            "message": "评分已更新",
        }
    
    # 创建新评分
    new_rating = UserRating(
        user_id=user_id,
        emby_id=data.emby_id,
        tmdb_id=data.tmdb_id,
        media_type=data.media_type,
        title=data.title,
        rating=data.rating,
        review=data.review,
    )
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    
    return {
        "id": new_rating.id,
        "rating": new_rating.rating,
        "message": "评分成功",
    }


@router.get("/check")
async def check_rating(
    user_id: str = Query(..., description="Emby 用户 ID"),
    emby_id: Optional[str] = None,
    tmdb_id: Optional[int] = None,
    media_type: str = Query(..., description="movie / tv / episode"),
    db: AsyncSession = Depends(get_db),
):
    """检查是否已评分"""
    query = select(UserRating).where(
        and_(
            UserRating.user_id == user_id,
            UserRating.media_type == media_type,
        )
    )
    
    if tmdb_id:
        query = query.where(UserRating.tmdb_id == tmdb_id)
    elif emby_id:
        query = query.where(UserRating.emby_id == emby_id)
    else:
        return {"rated": False, "rating": None}
    
    result = await db.execute(query)
    rating = result.scalar_one_or_none()
    
    if rating:
        return {
            "rated": True,
            "rating": rating.rating,
            "review": rating.review,
            "rated_at": rating.rated_at.isoformat() if rating.rated_at else None,
        }
    
    return {"rated": False, "rating": None}


@router.post("/check-batch")
async def check_ratings_batch(
    emby_ids: List[str],
    user_id: str = Query(..., description="Emby 用户 ID"),
    media_type: str = Query("episode", description="媒体类型"),
    db: AsyncSession = Depends(get_db),
):
    """批量检查多个项目的评分状态"""
    if not emby_ids:
        return {"ratings": {}}
    
    query = select(UserRating).where(
        and_(
            UserRating.user_id == user_id,
            UserRating.media_type == media_type,
            UserRating.emby_id.in_(emby_ids)
        )
    )
    
    result = await db.execute(query)
    ratings = result.scalars().all()
    
    # 返回 {emby_id: {rating, review}} 的映射
    ratings_map = {}
    for r in ratings:
        ratings_map[r.emby_id] = {
            "rating": r.rating,
            "review": r.review
        }
    
    return {"ratings": ratings_map}


@router.put("/{rating_id}")
async def update_rating(
    rating_id: int,
    data: RatingUpdate,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """更新评分"""
    result = await db.execute(
        select(UserRating)
        .where(
            and_(
                UserRating.id == rating_id,
                UserRating.user_id == user_id
            )
        )
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(status_code=404, detail="评分不存在")
    
    if data.rating is not None:
        rating.rating = data.rating
    if data.review is not None:
        rating.review = data.review
    
    await db.commit()
    
    return {"message": "更新成功"}


@router.delete("/{rating_id}")
async def delete_rating(
    rating_id: int,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除评分"""
    result = await db.execute(
        select(UserRating)
        .where(
            and_(
                UserRating.id == rating_id,
                UserRating.user_id == user_id
            )
        )
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(status_code=404, detail="评分不存在")
    
    await db.delete(rating)
    await db.commit()
    
    return {"message": "删除成功"}


@router.get("/stats")
async def get_rating_stats(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取评分统计"""
    # 总评分数
    total_result = await db.execute(
        select(func.count(UserRating.id))
        .where(UserRating.user_id == user_id)
    )
    total = total_result.scalar() or 0
    
    # 平均分
    avg_result = await db.execute(
        select(func.avg(UserRating.rating))
        .where(UserRating.user_id == user_id)
    )
    average = avg_result.scalar() or 0
    
    # 评分分布
    distribution = {}
    for i in range(1, 11):
        count_result = await db.execute(
            select(func.count(UserRating.id))
            .where(
                and_(
                    UserRating.user_id == user_id,
                    UserRating.rating == i
                )
            )
        )
        distribution[i] = count_result.scalar() or 0
    
    # 按类型统计
    type_stats = {}
    for media_type in ["movie", "tv", "episode"]:
        type_result = await db.execute(
            select(func.count(UserRating.id))
            .where(
                and_(
                    UserRating.user_id == user_id,
                    UserRating.media_type == media_type
                )
            )
        )
        type_stats[media_type] = type_result.scalar() or 0
    
    return {
        "total": total,
        "average": round(average, 1) if average else 0,
        "distribution": distribution,
        "by_type": type_stats,
    }
