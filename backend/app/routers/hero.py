from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from app.database import get_db
from app.models import HeroSlide
from pydantic import BaseModel

router = APIRouter(prefix="/hero", tags=["Hero Slides"])


class HeroSlideCreate(BaseModel):
    emby_id: str
    title: str
    overview: Optional[str] = None
    backdrop_url: Optional[str] = None
    media_type: str  # Movie / Series
    sort_order: int = 0


class HeroSlideUpdate(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    backdrop_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("/")
async def get_hero_slides(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """获取轮播海报列表"""
    query = select(HeroSlide)
    if active_only:
        query = query.where(HeroSlide.is_active == True)
    query = query.order_by(HeroSlide.sort_order.asc(), HeroSlide.created_at.desc())
    
    result = await db.execute(query)
    slides = result.scalars().all()
    
    return [
        {
            "id": s.id,
            "emby_id": s.emby_id,
            "title": s.title,
            "overview": s.overview,
            "backdrop_url": s.backdrop_url,
            "media_type": s.media_type,
            "sort_order": s.sort_order,
            "is_active": s.is_active,
        }
        for s in slides
    ]


@router.post("/")
async def create_hero_slide(
    data: HeroSlideCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加轮播海报"""
    # 检查是否已存在
    existing = await db.execute(
        select(HeroSlide).where(HeroSlide.emby_id == data.emby_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该媒体已在轮播列表中")
    
    slide = HeroSlide(
        emby_id=data.emby_id,
        title=data.title,
        overview=data.overview,
        backdrop_url=data.backdrop_url,
        media_type=data.media_type,
        sort_order=data.sort_order,
    )
    
    db.add(slide)
    await db.commit()
    await db.refresh(slide)
    
    return {"id": slide.id, "message": "添加成功"}


@router.put("/{slide_id}")
async def update_hero_slide(
    slide_id: int,
    data: HeroSlideUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新轮播海报"""
    result = await db.execute(select(HeroSlide).where(HeroSlide.id == slide_id))
    slide = result.scalar_one_or_none()
    
    if not slide:
        raise HTTPException(status_code=404, detail="轮播不存在")
    
    if data.title is not None:
        slide.title = data.title
    if data.overview is not None:
        slide.overview = data.overview
    if data.backdrop_url is not None:
        slide.backdrop_url = data.backdrop_url
    if data.sort_order is not None:
        slide.sort_order = data.sort_order
    if data.is_active is not None:
        slide.is_active = data.is_active
    
    await db.commit()
    
    return {"message": "更新成功"}


@router.delete("/{slide_id}")
async def delete_hero_slide(
    slide_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除轮播海报"""
    result = await db.execute(select(HeroSlide).where(HeroSlide.id == slide_id))
    slide = result.scalar_one_or_none()
    
    if not slide:
        raise HTTPException(status_code=404, detail="轮播不存在")
    
    await db.delete(slide)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/reorder")
async def reorder_hero_slides(
    order: list[int],  # slide_id 列表，按顺序排列
    db: AsyncSession = Depends(get_db),
):
    """重新排序轮播海报"""
    for index, slide_id in enumerate(order):
        await db.execute(
            update(HeroSlide)
            .where(HeroSlide.id == slide_id)
            .values(sort_order=index)
        )
    
    await db.commit()
    
    return {"message": "排序更新成功"}
