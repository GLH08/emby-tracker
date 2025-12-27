from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.database import get_db
from app.models import WatchHistory, Watchlist
from app.schemas import WatchStats
from app.services.emby import emby_service

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/overview/{user_id}")
async def get_overview_stats(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    db: AsyncSession = Depends(get_db),
):
    """获取概览统计 - 类似 Trakt 的主要统计数据"""
    visible_library_ids = library_ids.split(",") if library_ids else None
    
    result = {
        "movies": {
            "total": 0,
            "watched": 0,
            "watch_time_minutes": 0,
            "progress_percent": 0,
        },
        "shows": {
            "total": 0,
            "watched": 0,  # 已看的剧集数
            "episodes_total": 0,
            "episodes_watched": 0,
            "watch_time_minutes": 0,
            "progress_percent": 0,
        },
        "total_watch_time_minutes": 0,
        "total_watch_time_days": 0,
        "watchlist_count": 0,
    }
    
    try:
        libraries = await emby_service.get_libraries(user_id)
        
        for library in libraries:
            if visible_library_ids and library.id not in visible_library_ids:
                continue
            
            if library.collection_type == "movies":
                # 电影总数
                total_items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie",
                    limit=1,
                )
                result["movies"]["total"] += total_items.total_count
                
                # 已看电影
                watched_items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie",
                    is_played=True,
                    limit=500,
                )
                result["movies"]["watched"] += watched_items.total_count
                
                # 计算观看时长
                for item in watched_items.items:
                    if item.runtime_ticks:
                        minutes = item.runtime_ticks / 600000000  # ticks to minutes
                        result["movies"]["watch_time_minutes"] += minutes
                
            elif library.collection_type == "tvshows":
                # 剧集总数
                total_shows = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Series",
                    limit=1,
                )
                result["shows"]["total"] += total_shows.total_count
                
                # 集数总数
                total_episodes = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Episode",
                    limit=1,
                )
                result["shows"]["episodes_total"] += total_episodes.total_count
                
                # 已看集数
                watched_episodes = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Episode",
                    is_played=True,
                    limit=500,
                )
                result["shows"]["episodes_watched"] += watched_episodes.total_count
                
                # 计算观看时长
                for item in watched_episodes.items:
                    if item.runtime_ticks:
                        minutes = item.runtime_ticks / 600000000
                        result["shows"]["watch_time_minutes"] += minutes
        
        # 计算进度百分比
        if result["movies"]["total"] > 0:
            result["movies"]["progress_percent"] = round(
                result["movies"]["watched"] / result["movies"]["total"] * 100, 1
            )
        
        if result["shows"]["episodes_total"] > 0:
            result["shows"]["progress_percent"] = round(
                result["shows"]["episodes_watched"] / result["shows"]["episodes_total"] * 100, 1
            )
        
        # 总观看时长
        result["total_watch_time_minutes"] = int(
            result["movies"]["watch_time_minutes"] + result["shows"]["watch_time_minutes"]
        )
        result["total_watch_time_days"] = round(result["total_watch_time_minutes"] / 1440, 1)
        
        result["movies"]["watch_time_minutes"] = int(result["movies"]["watch_time_minutes"])
        result["shows"]["watch_time_minutes"] = int(result["shows"]["watch_time_minutes"])
        
    except Exception as e:
        print(f"Error fetching overview stats: {e}")
    
    # 想看列表数量
    db_result = await db.execute(select(func.count(Watchlist.id)))
    result["watchlist_count"] = db_result.scalar() or 0
    
    return result


@router.get("/genres/{user_id}")
async def get_genre_stats(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    media_type: Optional[str] = Query(None, description="movie 或 show"),
    db: AsyncSession = Depends(get_db),
):
    """获取类型分布统计 - 基于本地历史记录"""
    genres_count = {}
    
    try:
        # 从本地历史记录获取
        query = select(WatchHistory).where(WatchHistory.user_id == user_id)
        
        if media_type == "movie":
            query = query.where(WatchHistory.media_type == "Movie")
        elif media_type == "show":
            query = query.where(WatchHistory.media_type == "Series")
        
        result = await db.execute(query)
        history_items = result.scalars().all()
        
        for item in history_items:
            if item.genres:
                for genre in item.genres:
                    genres_count[genre] = genres_count.get(genre, 0) + 1
                
    except Exception as e:
        print(f"Error fetching genre stats: {e}")
    
    sorted_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)
    return {"genres": dict(sorted_genres[:15])}


@router.get("/years/{user_id}")
async def get_year_stats(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    media_type: Optional[str] = Query(None, description="movie 或 show"),
):
    """获取年份分布统计"""
    years_count = {}
    visible_library_ids = library_ids.split(",") if library_ids else None
    
    try:
        libraries = await emby_service.get_libraries(user_id)
        
        for library in libraries:
            if visible_library_ids and library.id not in visible_library_ids:
                continue
            
            if media_type == "movie" and library.collection_type != "movies":
                continue
            if media_type == "show" and library.collection_type != "tvshows":
                continue
            
            if library.collection_type in ["movies", "tvshows"]:
                items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie" if library.collection_type == "movies" else "Series",
                    is_played=True,
                    limit=500,
                )
                
                for item in items.items:
                    if item.year:
                        years_count[item.year] = years_count.get(item.year, 0) + 1
                
    except Exception as e:
        print(f"Error fetching year stats: {e}")
    
    # 按年份排序
    sorted_years = sorted(years_count.items(), key=lambda x: x[0])
    return {"years": dict(sorted_years)}


@router.get("/ratings/{user_id}")
async def get_rating_stats(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    media_type: Optional[str] = Query(None, description="movie 或 show"),
    db: AsyncSession = Depends(get_db),
):
    """获取评分分布统计 - 基于本地历史记录"""
    ratings = {
        "9-10": 0,
        "8-9": 0,
        "7-8": 0,
        "6-7": 0,
        "5-6": 0,
        "0-5": 0,
    }
    
    try:
        # 从本地历史记录获取
        query = select(WatchHistory).where(WatchHistory.user_id == user_id)
        
        if media_type == "movie":
            query = query.where(WatchHistory.media_type == "Movie")
        elif media_type == "show":
            query = query.where(WatchHistory.media_type == "Series")
        
        result = await db.execute(query)
        history_items = result.scalars().all()
        
        for item in history_items:
            rating = item.community_rating
            if rating:
                if rating >= 9:
                    ratings["9-10"] += 1
                elif rating >= 8:
                    ratings["8-9"] += 1
                elif rating >= 7:
                    ratings["7-8"] += 1
                elif rating >= 6:
                    ratings["6-7"] += 1
                elif rating >= 5:
                    ratings["5-6"] += 1
                else:
                    ratings["0-5"] += 1
                    
    except Exception as e:
        print(f"Error fetching rating stats: {e}")
    
    return {"ratings": ratings}


@router.get("/recent/{user_id}")
async def get_recent_watched(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    media_type: Optional[str] = Query(None, description="movie, episode 或 all"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取最近观看记录 - 基于本地历史记录"""
    items = []
    
    try:
        # 从本地历史记录获取
        query = select(WatchHistory).where(WatchHistory.user_id == user_id)
        
        if media_type == "movie":
            query = query.where(WatchHistory.media_type == "Movie")
        elif media_type == "episode":
            query = query.where(WatchHistory.media_type == "Episode")
        # all 或 None 不过滤
        
        query = query.order_by(WatchHistory.last_played_date.desc()).limit(limit)
        
        result = await db.execute(query)
        history_items = result.scalars().all()
        
        for item in history_items:
            item_data = {
                "id": item.emby_id,
                "name": item.title,
                "type": item.media_type,
                "year": item.year,
                "runtime_minutes": item.runtime_minutes or 0,
                "community_rating": item.community_rating,
                "genres": item.genres[:3] if item.genres else [],
                "progress_percent": item.watch_progress,
                "is_played": item.watched,
            }
            
            # 如果是剧集，添加额外信息
            if item.media_type == "Episode":
                item_data["series_id"] = item.series_id
                item_data["series_name"] = item.series_name
                item_data["season_number"] = item.season_number
                item_data["episode_number"] = item.episode_number
            
            items.append(item_data)
        
    except Exception as e:
        print(f"Error fetching recent watched: {e}")
    
    return {"items": items}


@router.get("/top-rated/{user_id}")
async def get_top_rated(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    media_type: str = Query("movie", description="movie 或 show"),
    limit: int = Query(10, ge=1, le=50),
):
    """获取评分最高的已看内容"""
    visible_library_ids = library_ids.split(",") if library_ids else None
    items = []
    
    try:
        libraries = await emby_service.get_libraries(user_id)
        
        for library in libraries:
            if visible_library_ids and library.id not in visible_library_ids:
                continue
            
            if media_type == "movie" and library.collection_type != "movies":
                continue
            if media_type == "show" and library.collection_type != "tvshows":
                continue
            
            if library.collection_type in ["movies", "tvshows"]:
                result = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie" if library.collection_type == "movies" else "Series",
                    is_played=True,
                    sort_by="CommunityRating",
                    sort_order="Descending",
                    limit=limit,
                )
                
                for item in result.items:
                    if item.community_rating:
                        items.append({
                            "id": item.id,
                            "name": item.name,
                            "type": item.type,
                            "year": item.year,
                            "community_rating": item.community_rating,
                            "genres": item.genres[:3],
                        })
        
        # 按评分排序
        items.sort(key=lambda x: x["community_rating"] or 0, reverse=True)
        
    except Exception as e:
        print(f"Error fetching top rated: {e}")
    
    return {"items": items[:limit]}


# 保留旧的 API 以兼容
@router.get("/", response_model=WatchStats)
async def get_stats(
    user_id: str,
    library_ids: Optional[str] = Query(None, description="逗号分隔的媒体库ID列表"),
    db: AsyncSession = Depends(get_db),
):
    """获取观影统计（旧版兼容）"""
    stats = WatchStats()
    visible_library_ids = library_ids.split(",") if library_ids else None
    
    try:
        libraries = await emby_service.get_libraries(user_id)
        
        for library in libraries:
            if visible_library_ids and library.id not in visible_library_ids:
                continue
                
            if library.collection_type == "movies":
                items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie",
                    limit=1,
                )
                stats.total_movies += items.total_count
                
                watched_items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Movie",
                    is_played=True,
                    limit=1,
                )
                stats.watched_movies += watched_items.total_count
                
            elif library.collection_type == "tvshows":
                items = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Series",
                    limit=1,
                )
                stats.total_shows += items.total_count
                
                episodes = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Episode",
                    limit=1,
                )
                stats.total_episodes += episodes.total_count
                
                watched_episodes = await emby_service.get_items(
                    user_id=user_id,
                    parent_id=library.id,
                    include_item_types="Episode",
                    is_played=True,
                    limit=1,
                )
                stats.watched_episodes += watched_episodes.total_count
    except Exception:
        pass
    
    result = await db.execute(select(func.count(Watchlist.id)))
    stats.watchlist_count = result.scalar() or 0
    
    return stats
