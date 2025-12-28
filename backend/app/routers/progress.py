"""剧集进度追踪路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct
from typing import Optional, List
from collections import defaultdict
from app.database import get_db
from app.models import WatchHistory
from app.services.emby import emby_service
from app.services.tmdb import tmdb_service

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/shows")
async def get_shows_progress(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有正在追的剧集进度
    """
    # 从观看历史中获取所有看过的剧集
    result = await db.execute(
        select(
            WatchHistory.series_id,
            WatchHistory.series_name,
            func.count(distinct(WatchHistory.emby_id)).label("watched_count"),
            func.max(WatchHistory.watched_at).label("last_watched"),
        )
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_id.isnot(None),
            )
        )
        .group_by(WatchHistory.series_id, WatchHistory.series_name)
        .order_by(func.max(WatchHistory.watched_at).desc())
    )
    
    shows_progress = []
    
    for row in result.fetchall():
        series_id, series_name, watched_count, last_watched = row
        
        try:
            # 从 Emby 获取剧集详情
            series_detail = await emby_service.get_item(user_id, series_id)
            
            # 获取总集数
            total_episodes = 0
            seasons_info = []
            
            # 获取季列表
            seasons = await emby_service.get_seasons(user_id, series_id)
            
            for season in seasons:
                if season.get("Name", "").startswith("Specials"):
                    continue  # 跳过特别篇
                    
                season_id = season.get("Id")
                season_number = season.get("IndexNumber", 0)
                
                # 获取该季的集数
                episodes = await emby_service.get_episodes(user_id, series_id, season_id)
                season_total = len(episodes)
                total_episodes += season_total
                
                # 统计该季已看集数
                season_watched = await db.execute(
                    select(func.count(distinct(WatchHistory.emby_id)))
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.series_id == series_id,
                            WatchHistory.season_number == season_number,
                        )
                    )
                )
                season_watched_count = season_watched.scalar() or 0
                
                seasons_info.append({
                    "season_id": season_id,
                    "season_number": season_number,
                    "season_name": season.get("Name"),
                    "total_episodes": season_total,
                    "watched_episodes": season_watched_count,
                    "progress": round(season_watched_count / season_total * 100, 1) if season_total > 0 else 0,
                    "poster_path": season.get("ImageTags", {}).get("Primary"),
                })
            
            # 计算总进度
            progress = round(watched_count / total_episodes * 100, 1) if total_episodes > 0 else 0
            
            # 获取下一集信息
            next_episode = await get_next_episode(user_id, series_id, db)
            
            shows_progress.append({
                "series_id": series_id,
                "series_name": series_name or series_detail.name,
                "poster_path": series_detail.image_tags.get("Primary") if series_detail.image_tags else None,
                "backdrop_path": series_detail.backdrop_image_tags[0] if series_detail.backdrop_image_tags else None,
                "total_episodes": total_episodes,
                "watched_episodes": watched_count,
                "progress": progress,
                "last_watched": last_watched.isoformat() if last_watched else None,
                "seasons": seasons_info,
                "next_episode": next_episode,
                "tmdb_id": series_detail.provider_ids.get("Tmdb") if series_detail.provider_ids else None,
                "status": series_detail.status if hasattr(series_detail, 'status') else None,
            })
            
        except Exception as e:
            print(f"获取剧集 {series_id} 进度失败: {e}")
            continue
    
    return {"shows": shows_progress}


@router.get("/show/{series_id}")
async def get_show_progress(
    series_id: str,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个剧集的详细进度
    """
    try:
        # 从 Emby 获取剧集详情
        series_detail = await emby_service.get_item(user_id, series_id)
        
        # 获取所有季
        seasons = await emby_service.get_seasons(user_id, series_id)
        
        seasons_progress = []
        total_episodes = 0
        total_watched = 0
        
        for season in seasons:
            season_id = season.get("Id")
            season_number = season.get("IndexNumber", 0)
            season_name = season.get("Name", f"第 {season_number} 季")
            
            # 获取该季所有集
            episodes = await emby_service.get_episodes(user_id, series_id, season_id)
            
            episodes_progress = []
            season_watched = 0
            
            for ep in episodes:
                ep_id = ep.get("Id")
                ep_number = ep.get("IndexNumber", 0)
                
                # 检查是否已看
                watched_result = await db.execute(
                    select(WatchHistory)
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.emby_id == ep_id,
                        )
                    )
                )
                watch_record = watched_result.scalar_one_or_none()
                
                is_watched = watch_record is not None
                if is_watched:
                    season_watched += 1
                
                episodes_progress.append({
                    "episode_id": ep_id,
                    "episode_number": ep_number,
                    "episode_name": ep.get("Name"),
                    "runtime": ep.get("RunTimeTicks", 0) // 600000000,  # 转换为分钟
                    "is_watched": is_watched,
                    "watched_at": watch_record.watched_at.isoformat() if watch_record and watch_record.watched_at else None,
                    "progress_percent": watch_record.progress_percent if watch_record else 0,
                    "overview": ep.get("Overview"),
                    "still_path": ep.get("ImageTags", {}).get("Primary"),
                })
            
            season_total = len(episodes)
            total_episodes += season_total
            total_watched += season_watched
            
            seasons_progress.append({
                "season_id": season_id,
                "season_number": season_number,
                "season_name": season_name,
                "total_episodes": season_total,
                "watched_episodes": season_watched,
                "progress": round(season_watched / season_total * 100, 1) if season_total > 0 else 0,
                "episodes": episodes_progress,
                "poster_path": season.get("ImageTags", {}).get("Primary"),
            })
        
        # 获取下一集
        next_episode = await get_next_episode(user_id, series_id, db)
        
        return {
            "series_id": series_id,
            "series_name": series_detail.name,
            "poster_path": series_detail.image_tags.get("Primary") if series_detail.image_tags else None,
            "backdrop_path": series_detail.backdrop_image_tags[0] if series_detail.backdrop_image_tags else None,
            "total_episodes": total_episodes,
            "watched_episodes": total_watched,
            "progress": round(total_watched / total_episodes * 100, 1) if total_episodes > 0 else 0,
            "seasons": seasons_progress,
            "next_episode": next_episode,
            "tmdb_id": series_detail.provider_ids.get("Tmdb") if series_detail.provider_ids else None,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧集进度失败: {str(e)}")


async def get_next_episode(user_id: str, series_id: str, db: AsyncSession):
    """获取下一集未看的剧集"""
    try:
        # 获取所有季
        seasons = await emby_service.get_seasons(user_id, series_id)
        
        for season in sorted(seasons, key=lambda x: x.get("IndexNumber", 0)):
            if season.get("Name", "").startswith("Specials"):
                continue
                
            season_id = season.get("Id")
            season_number = season.get("IndexNumber", 0)
            
            # 获取该季所有集
            episodes = await emby_service.get_episodes(user_id, series_id, season_id)
            
            for ep in sorted(episodes, key=lambda x: x.get("IndexNumber", 0)):
                ep_id = ep.get("Id")
                
                # 检查是否已看
                watched_result = await db.execute(
                    select(WatchHistory)
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.emby_id == ep_id,
                        )
                    )
                )
                
                if not watched_result.scalar_one_or_none():
                    # 找到第一个未看的集
                    return {
                        "episode_id": ep_id,
                        "season_number": season_number,
                        "episode_number": ep.get("IndexNumber", 0),
                        "episode_name": ep.get("Name"),
                        "overview": ep.get("Overview"),
                        "runtime": ep.get("RunTimeTicks", 0) // 600000000,
                        "still_path": ep.get("ImageTags", {}).get("Primary"),
                    }
        
        return None  # 全部看完
        
    except Exception:
        return None


@router.get("/stats")
async def get_progress_stats(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取进度统计概览
    """
    # 统计正在追的剧集数
    watching_result = await db.execute(
        select(func.count(distinct(WatchHistory.series_id)))
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_id.isnot(None),
            )
        )
    )
    watching_count = watching_result.scalar() or 0
    
    # 统计总观看集数
    episodes_result = await db.execute(
        select(func.count(distinct(WatchHistory.emby_id)))
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
            )
        )
    )
    episodes_watched = episodes_result.scalar() or 0
    
    # 统计本周观看集数
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    
    week_result = await db.execute(
        select(func.count(distinct(WatchHistory.emby_id)))
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.watched_at >= week_ago,
            )
        )
    )
    episodes_this_week = week_result.scalar() or 0
    
    return {
        "watching_shows": watching_count,
        "episodes_watched": episodes_watched,
        "episodes_this_week": episodes_this_week,
    }
