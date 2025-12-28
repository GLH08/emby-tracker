"""同步管理路由"""
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import LibraryCache, LibrarySyncStatus
from app.services.sync import (
    sync_all_users,
    sync_user_libraries,
    sync_user_history,
    get_cached_libraries,
    get_sync_status,
    _is_running,
)
from app.services.emby import emby_service

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/status")
async def get_global_sync_status():
    """获取全局同步状态"""
    return {
        "is_running": _is_running,
    }


@router.get("/status/{user_id}")
async def get_user_sync_status(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取用户同步状态"""
    status = await get_sync_status(user_id, db)
    status["is_running"] = _is_running
    return status


@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    user_id: str = Query(None, description="指定用户 ID，不指定则同步所有用户"),
):
    """手动触发同步"""
    if _is_running:
        raise HTTPException(status_code=400, detail="同步任务正在进行中")
    
    if user_id:
        # 同步指定用户
        background_tasks.add_task(sync_single_user, user_id)
        return {"message": f"已开始同步用户 {user_id}"}
    else:
        # 同步所有用户
        background_tasks.add_task(sync_all_users)
        return {"message": "已开始同步所有用户"}


async def sync_single_user(user_id: str):
    """同步单个用户（后台任务）"""
    from app.database import async_session_maker
    
    async with async_session_maker() as db:
        try:
            await sync_user_libraries(user_id, db)
            await sync_user_history(user_id, db)
        except Exception as e:
            print(f"同步用户 {user_id} 失败: {e}")


@router.get("/libraries/{user_id}")
async def get_libraries(
    user_id: str,
    use_cache: bool = Query(True, description="是否使用缓存"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取媒体库列表
    
    默认使用缓存数据，如果缓存不存在则实时获取并缓存
    """
    if use_cache:
        # 尝试从缓存获取
        cached = await get_cached_libraries(user_id, db)
        
        if cached:
            return {
                "libraries": [
                    {
                        "id": lib.library_id,
                        "name": lib.library_name,
                        "collection_type": lib.collection_type,
                        "item_count": lib.item_count,
                    }
                    for lib in cached
                ],
                "from_cache": True,
                "cache_time": cached[0].updated_at.isoformat() if cached else None,
            }
    
    # 缓存不存在或不使用缓存，实时获取
    try:
        libraries = await emby_service.get_libraries(user_id)
        
        result = []
        for lib in libraries:
            # 获取实际数量
            item_count = lib.item_count or 0
            if lib.collection_type in ["movies", "tvshows", "music", "musicvideos", "homevideos"]:
                try:
                    items = await emby_service.get_items(
                        user_id=user_id,
                        parent_id=lib.id,
                        limit=1,
                    )
                    item_count = items.total_count
                except:
                    pass
            
            result.append({
                "id": lib.id,
                "name": lib.name,
                "collection_type": lib.collection_type,
                "item_count": item_count,
            })
        
        # 如果是首次获取，自动缓存
        if use_cache:
            try:
                await sync_user_libraries(user_id, db)
            except:
                pass
        
        return {
            "libraries": result,
            "from_cache": False,
            "cache_time": None,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取媒体库失败: {str(e)}")


@router.post("/libraries/{user_id}/refresh")
async def refresh_libraries(
    user_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """刷新媒体库缓存"""
    if _is_running:
        raise HTTPException(status_code=400, detail="同步任务正在进行中")
    
    # 更新状态为运行中
    result = await db.execute(
        select(LibrarySyncStatus).where(LibrarySyncStatus.user_id == user_id)
    )
    status = result.scalar_one_or_none()
    
    if status:
        status.sync_status = "running"
    else:
        status = LibrarySyncStatus(user_id=user_id, sync_status="running")
        db.add(status)
    
    await db.commit()
    
    # 后台执行同步
    background_tasks.add_task(sync_user_libraries_task, user_id)
    
    return {"message": "已开始刷新媒体库"}


async def sync_user_libraries_task(user_id: str):
    """同步用户媒体库（后台任务）"""
    from app.database import async_session_maker
    
    async with async_session_maker() as db:
        try:
            await sync_user_libraries(user_id, db)
        except Exception as e:
            print(f"同步用户 {user_id} 媒体库失败: {e}")
