"""后台同步服务"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from app.database import async_session_maker
from app.models import WatchHistory, LibraryCache, LibrarySyncStatus
from app.services.emby import emby_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 全局变量控制后台任务
_sync_task = None
_is_running = False

# 缓存剧集信息（genres, rating）
_series_cache = {}


async def get_series_info(user_id: str, series_id: str) -> dict:
    """获取剧集的 genres 和 rating 信息（带缓存）"""
    cache_key = f"{user_id}:{series_id}"
    if cache_key in _series_cache:
        return _series_cache[cache_key]

    try:
        series = await emby_service.get_item(user_id, series_id)
        info = {
            "genres": series.genres or [],
            "community_rating": series.community_rating,
            "primary_image_tag": series.primary_image_tag,
            "tmdb_id": series.provider_ids.get("Tmdb") if series.provider_ids else None,
        }
        _series_cache[cache_key] = info
        return info
    except Exception as e:
        logger.warning(f"获取剧集信息失败 {series_id}: {e}")
        return {"genres": [], "community_rating": None, "primary_image_tag": None, "tmdb_id": None}


async def sync_user_history(user_id: str, db: AsyncSession) -> dict:
    """同步单个用户的观看历史"""
    added = 0
    updated = 0

    try:
        # 分页获取所有已播放的电影
        all_items_dict = {}

        # 获取电影（分页）
        start_index = 0
        page_size = 500
        while True:
            movies_played = await emby_service.get_items(
                user_id=user_id,
                include_item_types="Movie",
                is_played=True,
                sort_by="DatePlayed",
                sort_order="Descending",
                start_index=start_index,
                limit=page_size,
            )
            for item in movies_played.items:
                all_items_dict[item.id] = item

            if len(movies_played.items) < page_size:
                break
            start_index += page_size

        # 获取剧集（分页）
        start_index = 0
        while True:
            episodes_played = await emby_service.get_items(
                user_id=user_id,
                include_item_types="Episode",
                is_played=True,
                sort_by="DatePlayed",
                sort_order="Descending",
                start_index=start_index,
                limit=page_size,
            )
            for item in episodes_played.items:
                all_items_dict[item.id] = item

            if len(episodes_played.items) < page_size:
                break
            start_index += page_size

        # 获取正在观看的
        resume_items = await emby_service.get_resume_items(user_id=user_id, limit=100)
        for item in resume_items:
            all_items_dict[item.id] = item

        # 额外获取：按 DatePlayed 排序的所有有播放记录的项目（不依赖 IsPlayed 标记）
        # 这可以捕获 302 直链播放时可能未正确标记 Played 状态的记录
        start_index = 0
        while True:
            try:
                played_by_date = await emby_service.get_items(
                    user_id=user_id,
                    include_item_types="Movie",
                    sort_by="DatePlayed",
                    sort_order="Descending",
                    start_index=start_index,
                    limit=page_size,
                )
                # 只添加有 LastPlayedDate 的项目
                for item in played_by_date.items:
                    if item.last_played_date and item.id not in all_items_dict:
                        all_items_dict[item.id] = item

                if len(played_by_date.items) < page_size:
                    break
                start_index += page_size
                # 限制最多获取 2000 条
                if start_index >= 2000:
                    break
            except Exception as e:
                logger.warning(f"获取按日期排序的电影失败: {e}")
                break

        # 同样处理剧集
        start_index = 0
        while True:
            try:
                played_by_date = await emby_service.get_items(
                    user_id=user_id,
                    include_item_types="Episode",
                    sort_by="DatePlayed",
                    sort_order="Descending",
                    start_index=start_index,
                    limit=page_size,
                )
                for item in played_by_date.items:
                    if item.last_played_date and item.id not in all_items_dict:
                        all_items_dict[item.id] = item

                if len(played_by_date.items) < page_size:
                    break
                start_index += page_size
                if start_index >= 2000:
                    break
            except Exception as e:
                logger.warning(f"获取按日期排序的剧集失败: {e}")
                break

        all_items = list(all_items_dict.values())
        logger.info(f"用户 {user_id} 共发现 {len(all_items)} 个播放记录")
        
        for item in all_items:
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
            if not watched_at:
                watched_at = datetime.utcnow()
            
            runtime_minutes = int(item.runtime_ticks / 600000000) if item.runtime_ticks else 0

            # 获取 genres 和 rating
            # 对于剧集，从 Series 获取；对于电影，直接使用
            genres = item.genres or []
            community_rating = item.community_rating
            poster_path = None
            tmdb_id = None

            # 获取 TMDB ID 和海报路径
            if item.provider_ids:
                tmdb_id_str = item.provider_ids.get("Tmdb")
                if tmdb_id_str:
                    try:
                        tmdb_id = int(tmdb_id_str)
                    except (ValueError, TypeError):
                        pass

            # 如果没有评分或类型，获取完整的媒体信息
            if not community_rating or not genres:
                try:
                    if item.type == "Episode" and item.series_id:
                        # 剧集从 Series 获取
                        series_info = await get_series_info(user_id, item.series_id)
                        if not genres:
                            genres = series_info.get("genres", [])
                        if not community_rating:
                            community_rating = series_info.get("community_rating")
                        # 使用 series 的图片路径
                        if series_info.get("primary_image_tag"):
                            poster_path = f"/emby/Items/{item.series_id}/Images/Primary"
                        # 使用 series 的 TMDB ID
                        if not tmdb_id and series_info.get("tmdb_id"):
                            try:
                                tmdb_id = int(series_info.get("tmdb_id"))
                            except (ValueError, TypeError):
                                pass
                    else:
                        # 电影或其他类型，获取完整信息
                        full_item = await emby_service.get_item(user_id, item.id)
                        if not genres:
                            genres = full_item.genres or []
                        if not community_rating:
                            community_rating = full_item.community_rating
                        if full_item.primary_image_tag:
                            poster_path = f"/emby/Items/{item.id}/Images/Primary"
                        if not tmdb_id and full_item.provider_ids:
                            tmdb_id_str = full_item.provider_ids.get("Tmdb")
                            if tmdb_id_str:
                                try:
                                    tmdb_id = int(tmdb_id_str)
                                except (ValueError, TypeError):
                                    pass
                except Exception as e:
                    logger.warning(f"获取完整媒体信息失败 {item.id}: {e}")
            
            if existing_record:
                needs_update = False

                if abs(progress - existing_record.watch_progress) > 0.1:
                    existing_record.watch_progress = progress
                    needs_update = True

                if item.play_count > existing_record.play_count:
                    existing_record.play_count = item.play_count
                    needs_update = True

                if item.played != existing_record.watched:
                    existing_record.watched = item.played
                    needs_update = True

                if watched_at and item.last_played_date:
                    if not existing_record.watched_at or watched_at > existing_record.watched_at:
                        existing_record.watched_at = watched_at
                        existing_record.last_played_date = item.last_played_date
                        needs_update = True

                # 更新 genres 和 community_rating
                if genres and (not existing_record.genres or existing_record.genres != genres):
                    existing_record.genres = genres
                    needs_update = True

                if community_rating and existing_record.community_rating != community_rating:
                    existing_record.community_rating = community_rating
                    needs_update = True

                # 更新 poster_path 和 tmdb_id（如果之前没有）
                if poster_path and not existing_record.poster_path:
                    existing_record.poster_path = poster_path
                    needs_update = True

                if tmdb_id and not existing_record.tmdb_id:
                    existing_record.tmdb_id = tmdb_id
                    needs_update = True

                if needs_update:
                    updated += 1
            else:
                new_record = WatchHistory(
                    user_id=user_id,
                    emby_id=item.id,
                    tmdb_id=tmdb_id,
                    media_type=item.type,
                    title=item.name,
                    series_id=item.series_id,
                    series_name=item.series_name,
                    season_number=item.parent_index_number,
                    episode_number=item.index_number,
                    year=item.year,
                    runtime_minutes=runtime_minutes,
                    community_rating=community_rating,
                    genres=genres,
                    poster_path=poster_path,
                    watched=item.played,
                    watch_progress=progress,
                    play_count=max(item.play_count, 1),
                    watched_at=watched_at,
                    last_played_date=item.last_played_date,
                    source="emby",
                )
                db.add(new_record)
                added += 1
        
        await db.commit()
        
        # 清理缓存
        _series_cache.clear()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"同步用户 {user_id} 失败: {e}")
        raise
    
    return {"added": added, "updated": updated}


async def sync_all_users():
    """同步所有允许的用户的观看历史和媒体库"""
    global _is_running
    
    if _is_running:
        logger.info("同步任务正在运行中，跳过")
        return
    
    _is_running = True
    logger.info("开始同步所有用户数据...")
    
    try:
        # 获取所有 Emby 用户
        users = await emby_service.get_users()
        
        # 过滤允许的用户
        allowed_ids = settings.allowed_emby_user_ids
        if allowed_ids:
            # 支持用户名和用户ID匹配，users 是字典列表
            users = [u for u in users if u.get("Id") in allowed_ids or u.get("Name") in allowed_ids]
        
        async with async_session_maker() as db:
            for user in users:
                user_id = user.get("Id") if isinstance(user, dict) else user.Id
                user_name = user.get("Name") if isinstance(user, dict) else user.Name
                
                # 同步媒体库
                try:
                    lib_result = await sync_user_libraries(user_id, db)
                    logger.info(f"用户 {user_name} 媒体库同步完成: {lib_result['synced']} 个")
                except Exception as e:
                    logger.error(f"用户 {user_name} 媒体库同步失败: {e}")
                
                # 同步观看历史
                try:
                    result = await sync_user_history(user_id, db)
                    logger.info(f"用户 {user_name} 观看历史同步完成: 新增 {result['added']}, 更新 {result['updated']}")
                except Exception as e:
                    logger.error(f"用户 {user_name} 观看历史同步失败: {e}")
        
        logger.info("所有用户同步完成")
        
    except Exception as e:
        logger.error(f"同步任务失败: {e}")
    finally:
        _is_running = False


async def scheduled_sync_task():
    """定时同步任务"""
    interval = settings.sync_interval_minutes
    
    if interval <= 0:
        logger.info("定时同步已禁用")
        return
    
    logger.info(f"定时同步任务启动，间隔 {interval} 分钟")
    
    while True:
        await asyncio.sleep(interval * 60)
        try:
            await sync_all_users()
        except Exception as e:
            logger.error(f"定时同步失败: {e}")


def start_sync_scheduler():
    """启动同步调度器"""
    global _sync_task
    
    if settings.sync_interval_minutes > 0:
        _sync_task = asyncio.create_task(scheduled_sync_task())
        logger.info("同步调度器已启动")


def stop_sync_scheduler():
    """停止同步调度器"""
    global _sync_task
    
    if _sync_task:
        _sync_task.cancel()
        _sync_task = None
        logger.info("同步调度器已停止")


async def sync_user_libraries(user_id: str, db: AsyncSession) -> dict:
    """同步单个用户的媒体库信息"""
    synced = 0
    
    try:
        # 获取用户的媒体库列表
        libraries = await emby_service.get_libraries(user_id)
        
        # 删除该用户旧的缓存
        await db.execute(
            delete(LibraryCache).where(LibraryCache.user_id == user_id)
        )
        
        for library in libraries:
            # 获取媒体库中的项目数量
            item_count = 0
            try:
                if library.collection_type in ["movies", "tvshows", "music", "musicvideos", "homevideos"]:
                    # 获取实际数量
                    items = await emby_service.get_items(
                        user_id=user_id,
                        parent_id=library.id,
                        limit=1,
                    )
                    item_count = items.total_count
                else:
                    item_count = library.item_count or 0
            except Exception as e:
                logger.warning(f"获取媒体库 {library.name} 数量失败: {e}")
                item_count = library.item_count or 0
            
            # 创建缓存记录
            cache_record = LibraryCache(
                user_id=user_id,
                library_id=library.id,
                library_name=library.name,
                collection_type=library.collection_type or "",
                item_count=item_count,
            )
            db.add(cache_record)
            synced += 1
        
        # 更新同步状态
        status_result = await db.execute(
            select(LibrarySyncStatus).where(LibrarySyncStatus.user_id == user_id)
        )
        status = status_result.scalar_one_or_none()
        
        if status:
            status.last_sync_at = datetime.utcnow()
            status.sync_status = "idle"
            status.error_message = None
        else:
            status = LibrarySyncStatus(
                user_id=user_id,
                last_sync_at=datetime.utcnow(),
                sync_status="idle",
            )
            db.add(status)
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"同步用户 {user_id} 媒体库失败: {e}")
        
        # 更新错误状态
        try:
            async with async_session_maker() as error_db:
                status_result = await error_db.execute(
                    select(LibrarySyncStatus).where(LibrarySyncStatus.user_id == user_id)
                )
                status = status_result.scalar_one_or_none()
                
                if status:
                    status.sync_status = "error"
                    status.error_message = str(e)
                else:
                    status = LibrarySyncStatus(
                        user_id=user_id,
                        sync_status="error",
                        error_message=str(e),
                    )
                    error_db.add(status)
                
                await error_db.commit()
        except:
            pass
        
        raise
    
    return {"synced": synced}


async def sync_all_libraries():
    """同步所有用户的媒体库信息"""
    logger.info("开始同步所有用户媒体库...")
    
    try:
        # 获取所有 Emby 用户
        users = await emby_service.get_users()
        
        # 过滤允许的用户
        allowed_ids = settings.allowed_emby_user_ids
        if allowed_ids:
            users = [u for u in users if u.get("Id") in allowed_ids or u.get("Name") in allowed_ids]
        
        async with async_session_maker() as db:
            for user in users:
                user_id = user.get("Id") if isinstance(user, dict) else user.Id
                user_name = user.get("Name") if isinstance(user, dict) else user.Name
                try:
                    result = await sync_user_libraries(user_id, db)
                    logger.info(f"用户 {user_name} 媒体库同步完成: {result['synced']} 个媒体库")
                except Exception as e:
                    logger.error(f"用户 {user_name} 媒体库同步失败: {e}")
        
        logger.info("所有用户媒体库同步完成")
        
    except Exception as e:
        logger.error(f"媒体库同步任务失败: {e}")


async def get_cached_libraries(user_id: str, db: AsyncSession) -> list:
    """获取缓存的媒体库列表"""
    result = await db.execute(
        select(LibraryCache).where(LibraryCache.user_id == user_id)
    )
    return result.scalars().all()


async def get_sync_status(user_id: str, db: AsyncSession) -> dict:
    """获取同步状态"""
    result = await db.execute(
        select(LibrarySyncStatus).where(LibrarySyncStatus.user_id == user_id)
    )
    status = result.scalar_one_or_none()
    
    if status:
        return {
            "last_sync_at": status.last_sync_at.isoformat() if status.last_sync_at else None,
            "sync_status": status.sync_status,
            "error_message": status.error_message,
        }
    
    return {
        "last_sync_at": None,
        "sync_status": "never",
        "error_message": None,
    }
