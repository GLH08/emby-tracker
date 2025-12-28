from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.database import get_db
from app.models import WatchHistory, Watchlist, ExternalRating
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
    use_external: bool = Query(True, description="是否使用外部评分（IMDB）补充"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取评分分布统计 - 基于本地历史记录
    
    优先使用 Emby/TMDB 评分，如果没有则使用已缓存的 IMDB 评分补充
    """
    ratings = {
        "9-10": 0,
        "8-9": 0,
        "7-8": 0,
        "6-7": 0,
        "5-6": 0,
        "0-5": 0,
    }
    
    no_rating_count = 0
    external_used_count = 0
    
    try:
        # 从本地历史记录获取
        query = select(WatchHistory).where(WatchHistory.user_id == user_id)
        
        if media_type == "movie":
            query = query.where(WatchHistory.media_type == "Movie")
        elif media_type == "show":
            query = query.where(WatchHistory.media_type == "Series")
        
        result = await db.execute(query)
        history_items = result.scalars().all()
        
        # 如果启用外部评分，预加载所有缓存的外部评分
        external_ratings_map = {}
        if use_external:
            # 获取所有已缓存的外部评分
            ext_result = await db.execute(select(ExternalRating))
            for ext in ext_result.scalars().all():
                if ext.imdb_id:
                    external_ratings_map[ext.imdb_id] = ext.imdb_rating
                if ext.tmdb_id:
                    external_ratings_map[f"tmdb_{ext.tmdb_id}"] = ext.imdb_rating
        
        for item in history_items:
            rating = item.community_rating
            
            # 如果没有评分，尝试使用外部评分
            if not rating and use_external:
                # 尝试通过 TMDB ID 查找
                if item.tmdb_id:
                    rating = external_ratings_map.get(f"tmdb_{item.tmdb_id}")
                    if rating:
                        external_used_count += 1
            
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
            else:
                no_rating_count += 1
                    
    except Exception as e:
        print(f"Error fetching rating stats: {e}")
    
    return {
        "ratings": ratings,
        "no_rating_count": no_rating_count,
        "external_used_count": external_used_count,
    }


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


@router.get("/trends/{user_id}")
async def get_watch_trends(
    user_id: str,
    days: int = Query(30, ge=7, le=365, description="统计天数"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取观看趋势 - 每日观看数量
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 初始化每天的数据
    daily_data = {}
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        daily_data[date_str] = {"movies": 0, "episodes": 0, "total": 0}
        current += timedelta(days=1)
    
    try:
        # 查询指定时间范围内的观看记录
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at >= start_date,
                    WatchHistory.watched_at <= end_date,
                )
            )
        )
        
        for item in result.scalars().all():
            if item.watched_at:
                date_str = item.watched_at.strftime("%Y-%m-%d")
                if date_str in daily_data:
                    if item.media_type == "Movie":
                        daily_data[date_str]["movies"] += 1
                    elif item.media_type == "Episode":
                        daily_data[date_str]["episodes"] += 1
                    daily_data[date_str]["total"] += 1
                    
    except Exception as e:
        print(f"Error fetching watch trends: {e}")
    
    # 转换为列表格式
    trends = [
        {"date": date, **data}
        for date, data in sorted(daily_data.items())
    ]
    
    return {"trends": trends, "days": days}


@router.get("/time-distribution/{user_id}")
async def get_time_distribution(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    获取观看时段分布 - 早/中/晚/深夜
    """
    distribution = {
        "morning": {"label": "早间 (6-12点)", "count": 0, "hours": "06:00-12:00"},
        "afternoon": {"label": "下午 (12-18点)", "count": 0, "hours": "12:00-18:00"},
        "evening": {"label": "晚间 (18-24点)", "count": 0, "hours": "18:00-24:00"},
        "night": {"label": "深夜 (0-6点)", "count": 0, "hours": "00:00-06:00"},
    }
    
    try:
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at.isnot(None),
                )
            )
        )
        
        for item in result.scalars().all():
            if item.watched_at:
                hour = item.watched_at.hour
                if 6 <= hour < 12:
                    distribution["morning"]["count"] += 1
                elif 12 <= hour < 18:
                    distribution["afternoon"]["count"] += 1
                elif 18 <= hour < 24:
                    distribution["evening"]["count"] += 1
                else:
                    distribution["night"]["count"] += 1
                    
    except Exception as e:
        print(f"Error fetching time distribution: {e}")
    
    return {"distribution": distribution}


@router.get("/heatmap/{user_id}")
async def get_watch_heatmap(
    user_id: str,
    weeks: int = Query(12, ge=4, le=52, description="统计周数"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取观看热力图数据 - 按周/日统计
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)
    
    # 初始化热力图数据
    heatmap = []
    
    try:
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at >= start_date,
                    WatchHistory.watched_at <= end_date,
                )
            )
        )
        
        # 按日期统计
        daily_counts = defaultdict(int)
        for item in result.scalars().all():
            if item.watched_at:
                date_str = item.watched_at.strftime("%Y-%m-%d")
                daily_counts[date_str] += 1
        
        # 生成热力图数据
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            count = daily_counts.get(date_str, 0)
            
            # 计算强度等级 (0-4)
            if count == 0:
                level = 0
            elif count <= 2:
                level = 1
            elif count <= 5:
                level = 2
            elif count <= 10:
                level = 3
            else:
                level = 4
            
            heatmap.append({
                "date": date_str,
                "count": count,
                "level": level,
                "weekday": current.weekday(),  # 0=周一
            })
            current += timedelta(days=1)
            
    except Exception as e:
        print(f"Error fetching heatmap: {e}")
    
    return {"heatmap": heatmap, "weeks": weeks}


@router.get("/streak/{user_id}")
async def get_watch_streak(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    获取观看连续天数统计
    """
    try:
        result = await db.execute(
            select(WatchHistory.watched_at)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at.isnot(None),
                )
            )
            .order_by(WatchHistory.watched_at.desc())
        )
        
        # 获取所有观看日期（去重）
        watch_dates = set()
        for row in result.fetchall():
            if row[0]:
                watch_dates.add(row[0].date())
        
        if not watch_dates:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "total_watch_days": 0,
            }
        
        # 计算当前连续天数
        today = datetime.now().date()
        current_streak = 0
        check_date = today
        
        while check_date in watch_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # 如果今天没看，检查昨天开始的连续
        if current_streak == 0:
            check_date = today - timedelta(days=1)
            while check_date in watch_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        
        # 计算最长连续天数
        sorted_dates = sorted(watch_dates)
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        longest_streak = max(longest_streak, temp_streak)
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_watch_days": len(watch_dates),
        }
        
    except Exception as e:
        print(f"Error fetching streak: {e}")
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_watch_days": 0,
        }


@router.get("/monthly/{user_id}")
async def get_monthly_stats(
    user_id: str,
    year: int = Query(None, description="年份，默认当前年"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取月度统计
    """
    if year is None:
        year = datetime.now().year
    
    monthly_data = {i: {"movies": 0, "episodes": 0, "total": 0, "watch_time": 0} for i in range(1, 13)}
    
    try:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at >= start_date,
                    WatchHistory.watched_at <= end_date,
                )
            )
        )
        
        for item in result.scalars().all():
            if item.watched_at:
                month = item.watched_at.month
                if item.media_type == "Movie":
                    monthly_data[month]["movies"] += 1
                elif item.media_type == "Episode":
                    monthly_data[month]["episodes"] += 1
                monthly_data[month]["total"] += 1
                
                if item.runtime_minutes:
                    monthly_data[month]["watch_time"] += item.runtime_minutes
                    
    except Exception as e:
        print(f"Error fetching monthly stats: {e}")
    
    # 转换为列表
    months = [
        {"month": i, "name": f"{i}月", **monthly_data[i]}
        for i in range(1, 13)
    ]
    
    return {"year": year, "months": months}


@router.get("/weekday/{user_id}")
async def get_weekday_stats(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    获取星期分布统计
    """
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_data = {i: {"name": weekday_names[i], "count": 0} for i in range(7)}
    
    try:
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at.isnot(None),
                )
            )
        )
        
        for item in result.scalars().all():
            if item.watched_at:
                weekday = item.watched_at.weekday()
                weekday_data[weekday]["count"] += 1
                
    except Exception as e:
        print(f"Error fetching weekday stats: {e}")
    
    return {"weekdays": list(weekday_data.values())}


@router.get("/yearly-review/{user_id}")
async def get_yearly_review(
    user_id: str,
    year: int = Query(None, description="年份，默认当前年"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取年度回顾 - 类似 Spotify Wrapped / Trakt Year in Review
    """
    if year is None:
        year = datetime.now().year
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    review = {
        "year": year,
        "summary": {
            "total_movies": 0,
            "total_episodes": 0,
            "total_items": 0,
            "total_watch_time_minutes": 0,
            "total_watch_time_hours": 0,
            "total_watch_time_days": 0,
            "watch_days": 0,  # 有观看记录的天数
            "average_per_day": 0,  # 平均每天观看数
        },
        "top_genres": [],  # 最爱类型
        "top_movies": [],  # 评分最高的电影
        "top_shows": [],  # 评分最高的剧集
        "most_watched_series": [],  # 看得最多的剧集
        "monthly_breakdown": [],  # 月度分布
        "milestones": [],  # 里程碑
        "first_watch": None,  # 年度第一部
        "last_watch": None,  # 年度最后一部
        "busiest_day": None,  # 最忙的一天
        "favorite_time": None,  # 最爱观看时段
        "longest_streak": 0,  # 最长连续观看天数
    }
    
    try:
        # 查询年度所有观看记录
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.watched_at >= start_date,
                    WatchHistory.watched_at <= end_date,
                )
            )
            .order_by(WatchHistory.watched_at)
        )
        
        items = result.scalars().all()
        
        if not items:
            return review
        
        # 基础统计
        genres_count = defaultdict(int)
        series_count = defaultdict(lambda: {"name": "", "count": 0, "tmdb_id": None})
        monthly_count = defaultdict(lambda: {"movies": 0, "episodes": 0, "watch_time": 0})
        daily_count = defaultdict(int)
        time_slots = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
        watch_dates = set()
        
        movies = []
        shows = []
        
        for item in items:
            # 总数统计
            if item.media_type == "Movie":
                review["summary"]["total_movies"] += 1
                if item.community_rating:
                    movies.append({
                        "title": item.title,
                        "year": item.year,
                        "rating": item.community_rating,
                        "tmdb_id": item.tmdb_id,
                        "watched_at": item.watched_at.isoformat() if item.watched_at else None,
                    })
            elif item.media_type == "Episode":
                review["summary"]["total_episodes"] += 1
                # 统计剧集
                if item.series_name:
                    series_count[item.series_name]["name"] = item.series_name
                    series_count[item.series_name]["count"] += 1
                    if item.tmdb_id:
                        series_count[item.series_name]["tmdb_id"] = item.tmdb_id
            elif item.media_type == "Series":
                if item.community_rating:
                    shows.append({
                        "title": item.title,
                        "year": item.year,
                        "rating": item.community_rating,
                        "tmdb_id": item.tmdb_id,
                    })
            
            review["summary"]["total_items"] += 1
            
            # 观看时长
            if item.runtime_minutes:
                review["summary"]["total_watch_time_minutes"] += item.runtime_minutes
            
            # 类型统计
            if item.genres:
                for genre in item.genres:
                    genres_count[genre] += 1
            
            # 月度统计
            if item.watched_at:
                month = item.watched_at.month
                if item.media_type == "Movie":
                    monthly_count[month]["movies"] += 1
                elif item.media_type == "Episode":
                    monthly_count[month]["episodes"] += 1
                if item.runtime_minutes:
                    monthly_count[month]["watch_time"] += item.runtime_minutes
                
                # 日期统计
                date_str = item.watched_at.strftime("%Y-%m-%d")
                daily_count[date_str] += 1
                watch_dates.add(item.watched_at.date())
                
                # 时段统计
                hour = item.watched_at.hour
                if 6 <= hour < 12:
                    time_slots["morning"] += 1
                elif 12 <= hour < 18:
                    time_slots["afternoon"] += 1
                elif 18 <= hour < 24:
                    time_slots["evening"] += 1
                else:
                    time_slots["night"] += 1
        
        # 计算汇总数据
        review["summary"]["total_watch_time_hours"] = round(review["summary"]["total_watch_time_minutes"] / 60, 1)
        review["summary"]["total_watch_time_days"] = round(review["summary"]["total_watch_time_minutes"] / 1440, 1)
        review["summary"]["watch_days"] = len(watch_dates)
        
        if review["summary"]["watch_days"] > 0:
            review["summary"]["average_per_day"] = round(
                review["summary"]["total_items"] / review["summary"]["watch_days"], 1
            )
        
        # 最爱类型 (Top 5)
        sorted_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)[:5]
        review["top_genres"] = [{"name": g[0], "count": g[1]} for g in sorted_genres]
        
        # 评分最高的电影 (Top 5)
        movies.sort(key=lambda x: x["rating"] or 0, reverse=True)
        review["top_movies"] = movies[:5]
        
        # 评分最高的剧集 (Top 5)
        shows.sort(key=lambda x: x["rating"] or 0, reverse=True)
        review["top_shows"] = shows[:5]
        
        # 看得最多的剧集 (Top 5)
        sorted_series = sorted(series_count.values(), key=lambda x: x["count"], reverse=True)[:5]
        review["most_watched_series"] = sorted_series
        
        # 月度分布
        month_names = ["", "一月", "二月", "三月", "四月", "五月", "六月", 
                       "七月", "八月", "九月", "十月", "十一月", "十二月"]
        review["monthly_breakdown"] = [
            {
                "month": i,
                "name": month_names[i],
                "movies": monthly_count[i]["movies"],
                "episodes": monthly_count[i]["episodes"],
                "total": monthly_count[i]["movies"] + monthly_count[i]["episodes"],
                "watch_time_hours": round(monthly_count[i]["watch_time"] / 60, 1),
            }
            for i in range(1, 13)
        ]
        
        # 第一部和最后一部
        if items:
            first = items[0]
            review["first_watch"] = {
                "title": first.title,
                "type": first.media_type,
                "date": first.watched_at.strftime("%Y-%m-%d") if first.watched_at else None,
            }
            last = items[-1]
            review["last_watch"] = {
                "title": last.title,
                "type": last.media_type,
                "date": last.watched_at.strftime("%Y-%m-%d") if last.watched_at else None,
            }
        
        # 最忙的一天
        if daily_count:
            busiest = max(daily_count.items(), key=lambda x: x[1])
            review["busiest_day"] = {"date": busiest[0], "count": busiest[1]}
        
        # 最爱时段
        if time_slots:
            time_labels = {
                "morning": "早间 (6-12点)",
                "afternoon": "下午 (12-18点)",
                "evening": "晚间 (18-24点)",
                "night": "深夜 (0-6点)",
            }
            favorite = max(time_slots.items(), key=lambda x: x[1])
            review["favorite_time"] = {"slot": favorite[0], "label": time_labels[favorite[0]], "count": favorite[1]}
        
        # 最长连续天数
        if watch_dates:
            sorted_dates = sorted(watch_dates)
            longest = 1
            current = 1
            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
            review["longest_streak"] = longest
        
        # 里程碑
        milestones = []
        total = review["summary"]["total_items"]
        if total >= 10:
            milestones.append({"type": "count", "value": 10, "label": "观看了 10 部作品"})
        if total >= 50:
            milestones.append({"type": "count", "value": 50, "label": "观看了 50 部作品"})
        if total >= 100:
            milestones.append({"type": "count", "value": 100, "label": "观看了 100 部作品"})
        if total >= 200:
            milestones.append({"type": "count", "value": 200, "label": "观看了 200 部作品"})
        if total >= 500:
            milestones.append({"type": "count", "value": 500, "label": "观看了 500 部作品"})
        
        hours = review["summary"]["total_watch_time_hours"]
        if hours >= 24:
            milestones.append({"type": "time", "value": 24, "label": "观看超过 1 天"})
        if hours >= 168:
            milestones.append({"type": "time", "value": 168, "label": "观看超过 1 周"})
        if hours >= 720:
            milestones.append({"type": "time", "value": 720, "label": "观看超过 1 个月"})
        
        if review["longest_streak"] >= 7:
            milestones.append({"type": "streak", "value": 7, "label": f"连续观看 {review['longest_streak']} 天"})
        
        review["milestones"] = milestones
        
    except Exception as e:
        print(f"Error fetching yearly review: {e}")
    
    return review
