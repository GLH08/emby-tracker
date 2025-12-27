"""后台同步服务"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import async_session_maker
from app.models import WatchHistory
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
        }
        _series_cache[cache_key] = info
        return info
    except Exception as e:
        logger.warning(f"获取剧集信息失败 {series_id}: {e}")
        return {"genres": [], "community_rating": None}


async def sync_user_history(user_id: str, db: AsyncSession) -> dict:
    """同步单个用户的观看历史"""
    added = 0
    updated = 0
    
    try:
        # 获取所有已播放的电影
        movies_played = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Movie",
            is_played=True,
            sort_by="DatePlayed",
            sort_order="Descending",
            limit=1000,
        )
        
        # 获取所有已播放的剧集
        episodes_played = await emby_service.get_items(
            user_id=user_id,
            include_item_types="Episode",
            is_played=True,
            sort_by="DatePlayed",
            sort_order="Descending",
            limit=1000,
        )
        
        # 获取正在观看的
        resume_items = await emby_service.get_resume_items(user_id=user_id, limit=100)
        
        # 合并去重
        all_items_dict = {}
        for item in movies_played.items:
            all_items_dict[item.id] = item
        for item in episodes_played.items:
            all_items_dict[item.id] = item
        for item in resume_items:
            all_items_dict[item.id] = item
        
        all_items = list(all_items_dict.values())
        
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
            
            if item.type == "Episode" and item.series_id:
                # 剧集的 genres 和 rating 通常在 Series 级别
                if not genres or not community_rating:
                    series_info = await get_series_info(user_id, item.series_id)
                    if not genres:
                        genres = series_info.get("genres", [])
                    if not community_rating:
                        community_rating = series_info.get("community_rating")
            
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
                
                if needs_update:
                    updated += 1
            else:
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
                    community_rating=community_rating,
                    genres=genres,
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
    """同步所有允许的用户的观看历史"""
    global _is_running
    
    if _is_running:
        logger.info("同步任务正在运行中，跳过")
        return
    
    _is_running = True
    logger.info("开始同步所有用户观看历史...")
    
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
                try:
                    result = await sync_user_history(user_id, db)
                    logger.info(f"用户 {user_name} 同步完成: 新增 {result['added']}, 更新 {result['updated']}")
                except Exception as e:
                    logger.error(f"用户 {user_name} 同步失败: {e}")
        
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
