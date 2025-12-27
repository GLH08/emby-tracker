from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.emby import emby_service
from app.schemas import EmbyLibrary, EmbyMediaItem, EmbyMediaList
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/emby", tags=["Emby"])


@router.get("/server-info")
async def get_server_info():
    """获取 Emby 服务器信息"""
    try:
        return await emby_service.get_server_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users():
    """获取用户列表（根据环境变量过滤）"""
    try:
        all_users = await emby_service.get_users()
        # 如果配置了允许的用户列表，则过滤（支持用户ID或用户名）
        allowed_ids = settings.allowed_emby_user_ids
        if allowed_ids:
            # 同时支持按 ID 或用户名匹配
            return [u for u in all_users if u.get("Id") in allowed_ids or u.get("Name") in allowed_ids]
        return all_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/libraries/{user_id}", response_model=list[EmbyLibrary])
async def get_libraries(user_id: str):
    """获取媒体库列表"""
    try:
        return await emby_service.get_libraries(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{user_id}", response_model=EmbyMediaList)
async def get_items(
    user_id: str,
    parent_id: Optional[str] = None,
    include_item_types: Optional[str] = Query(None, description="Movie,Series,Episode"),
    filters: Optional[str] = Query(None, description="IsPlayed,IsUnplayed,IsFavorite"),
    sort_by: str = Query("SortName", description="SortName,DateCreated,PremiereDate,CommunityRating"),
    sort_order: str = Query("Ascending", description="Ascending,Descending"),
    start_index: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search_term: Optional[str] = None,
    genres: Optional[str] = None,
    years: Optional[str] = None,
    is_played: Optional[bool] = None,
):
    """获取媒体项列表"""
    try:
        return await emby_service.get_items(
            user_id=user_id,
            parent_id=parent_id,
            include_item_types=include_item_types,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            start_index=start_index,
            limit=limit,
            search_term=search_term,
            genres=genres,
            years=years,
            is_played=is_played,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{user_id}/{item_id}", response_model=EmbyMediaItem)
async def get_item(user_id: str, item_id: str):
    """获取单个媒体项详情"""
    try:
        return await emby_service.get_item(user_id, item_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasons/{user_id}/{series_id}", response_model=list[EmbyMediaItem])
async def get_seasons(user_id: str, series_id: str):
    """获取剧集的季列表"""
    try:
        return await emby_service.get_seasons(user_id, series_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/episodes/{user_id}/{series_id}", response_model=list[EmbyMediaItem])
async def get_episodes(user_id: str, series_id: str, season_id: Optional[str] = None):
    """获取剧集的集列表"""
    try:
        return await emby_service.get_episodes(user_id, series_id, season_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recently-added/{user_id}", response_model=list[EmbyMediaItem])
async def get_recently_added(user_id: str, limit: int = Query(20, ge=1, le=50)):
    """获取最近添加的媒体"""
    try:
        return await emby_service.get_recently_added(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resume/{user_id}", response_model=list[EmbyMediaItem])
async def get_resume_items(user_id: str, limit: int = Query(20, ge=1, le=50)):
    """获取继续观看的媒体"""
    try:
        return await emby_service.get_resume_items(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-played/{user_id}/{item_id}")
async def mark_played(user_id: str, item_id: str):
    """标记为已播放"""
    try:
        await emby_service.mark_played(user_id, item_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-unplayed/{user_id}/{item_id}")
async def mark_unplayed(user_id: str, item_id: str):
    """标记为未播放"""
    try:
        await emby_service.mark_unplayed(user_id, item_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle-favorite/{user_id}/{item_id}")
async def toggle_favorite(user_id: str, item_id: str, is_favorite: bool):
    """切换收藏状态"""
    try:
        await emby_service.toggle_favorite(user_id, item_id, is_favorite)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{item_id}")
async def get_image_url(
    item_id: str,
    image_type: str = Query("Primary", description="Primary,Backdrop,Logo,Thumb"),
    max_width: int = Query(400, ge=100, le=1920),
):
    """获取图片 URL"""
    return {"url": emby_service.get_image_url(item_id, image_type, max_width)}
