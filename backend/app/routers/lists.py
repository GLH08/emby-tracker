"""自定义列表管理路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_db
from app.models import CustomList, CustomListItem

router = APIRouter(prefix="/lists", tags=["Lists"])


class ListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_public: bool = False


class ListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_public: Optional[bool] = None


class ListItemCreate(BaseModel):
    emby_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    media_type: str
    title: str
    poster_path: Optional[str] = None
    year: Optional[int] = None
    vote_average: Optional[float] = None
    note: Optional[str] = None


@router.get("/")
async def get_lists(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有列表"""
    result = await db.execute(
        select(CustomList)
        .where(CustomList.user_id == user_id)
        .order_by(CustomList.sort_order, CustomList.created_at.desc())
    )
    lists = result.scalars().all()
    
    # 获取每个列表的项目数量
    lists_data = []
    for lst in lists:
        count_result = await db.execute(
            select(func.count(CustomListItem.id))
            .where(CustomListItem.list_id == lst.id)
        )
        item_count = count_result.scalar() or 0
        
        lists_data.append({
            "id": lst.id,
            "name": lst.name,
            "description": lst.description,
            "cover_image": lst.cover_image,
            "is_public": lst.is_public,
            "item_count": item_count,
            "created_at": lst.created_at.isoformat() if lst.created_at else None,
        })
    
    return {"lists": lists_data}


@router.post("/")
async def create_list(
    data: ListCreate,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """创建新列表"""
    new_list = CustomList(
        user_id=user_id,
        name=data.name,
        description=data.description,
        cover_image=data.cover_image,
        is_public=data.is_public,
    )
    db.add(new_list)
    await db.commit()
    await db.refresh(new_list)
    
    return {
        "id": new_list.id,
        "name": new_list.name,
        "description": new_list.description,
        "cover_image": new_list.cover_image,
        "is_public": new_list.is_public,
        "created_at": new_list.created_at.isoformat() if new_list.created_at else None,
    }


@router.get("/{list_id}")
async def get_list(
    list_id: int,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """获取列表详情"""
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                (CustomList.user_id == user_id) | (CustomList.is_public == True)
            )
        )
    )
    lst = result.scalar_one_or_none()
    
    if not lst:
        raise HTTPException(status_code=404, detail="列表不存在")
    
    # 获取列表项
    items_result = await db.execute(
        select(CustomListItem)
        .where(CustomListItem.list_id == list_id)
        .order_by(CustomListItem.sort_order, CustomListItem.added_at.desc())
    )
    items = items_result.scalars().all()
    
    return {
        "id": lst.id,
        "name": lst.name,
        "description": lst.description,
        "cover_image": lst.cover_image,
        "is_public": lst.is_public,
        "is_owner": lst.user_id == user_id,
        "created_at": lst.created_at.isoformat() if lst.created_at else None,
        "items": [
            {
                "id": item.id,
                "emby_id": item.emby_id,
                "tmdb_id": item.tmdb_id,
                "media_type": item.media_type,
                "title": item.title,
                "poster_path": item.poster_path,
                "year": item.year,
                "vote_average": item.vote_average,
                "note": item.note,
                "added_at": item.added_at.isoformat() if item.added_at else None,
            }
            for item in items
        ],
    }


@router.put("/{list_id}")
async def update_list(
    list_id: int,
    data: ListUpdate,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """更新列表"""
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id
            )
        )
    )
    lst = result.scalar_one_or_none()
    
    if not lst:
        raise HTTPException(status_code=404, detail="列表不存在")
    
    if data.name is not None:
        lst.name = data.name
    if data.description is not None:
        lst.description = data.description
    if data.cover_image is not None:
        lst.cover_image = data.cover_image
    if data.is_public is not None:
        lst.is_public = data.is_public
    
    await db.commit()
    
    return {"message": "更新成功"}


@router.delete("/{list_id}")
async def delete_list(
    list_id: int,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除列表"""
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id
            )
        )
    )
    lst = result.scalar_one_or_none()
    
    if not lst:
        raise HTTPException(status_code=404, detail="列表不存在")
    
    # 删除列表项
    await db.execute(
        delete(CustomListItem).where(CustomListItem.list_id == list_id)
    )
    
    # 删除列表
    await db.delete(lst)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/{list_id}/items")
async def add_list_item(
    list_id: int,
    data: ListItemCreate,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """添加列表项"""
    # 验证列表所有权
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id
            )
        )
    )
    lst = result.scalar_one_or_none()
    
    if not lst:
        raise HTTPException(status_code=404, detail="列表不存在")
    
    # 检查是否已存在
    existing = await db.execute(
        select(CustomListItem)
        .where(
            and_(
                CustomListItem.list_id == list_id,
                (
                    (CustomListItem.tmdb_id == data.tmdb_id) if data.tmdb_id else
                    (CustomListItem.emby_id == data.emby_id)
                )
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该项目已在列表中")
    
    # 获取当前最大排序
    max_order = await db.execute(
        select(func.max(CustomListItem.sort_order))
        .where(CustomListItem.list_id == list_id)
    )
    next_order = (max_order.scalar() or 0) + 1
    
    new_item = CustomListItem(
        list_id=list_id,
        emby_id=data.emby_id,
        tmdb_id=data.tmdb_id,
        media_type=data.media_type,
        title=data.title,
        poster_path=data.poster_path,
        year=data.year,
        vote_average=data.vote_average,
        note=data.note,
        sort_order=next_order,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    return {
        "id": new_item.id,
        "title": new_item.title,
        "message": "添加成功",
    }


@router.delete("/{list_id}/items/{item_id}")
async def remove_list_item(
    list_id: int,
    item_id: int,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """移除列表项"""
    # 验证列表所有权
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="列表不存在")
    
    # 删除项目
    await db.execute(
        delete(CustomListItem)
        .where(
            and_(
                CustomListItem.id == item_id,
                CustomListItem.list_id == list_id
            )
        )
    )
    await db.commit()
    
    return {"message": "移除成功"}


@router.post("/{list_id}/reorder")
async def reorder_list_items(
    list_id: int,
    item_ids: List[int],
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """重新排序列表项"""
    # 验证列表所有权
    result = await db.execute(
        select(CustomList)
        .where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="列表不存在")
    
    # 更新排序
    for index, item_id in enumerate(item_ids):
        await db.execute(
            select(CustomListItem)
            .where(
                and_(
                    CustomListItem.id == item_id,
                    CustomListItem.list_id == list_id
                )
            )
        )
        result = await db.execute(
            select(CustomListItem)
            .where(CustomListItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item:
            item.sort_order = index
    
    await db.commit()
    
    return {"message": "排序更新成功"}
