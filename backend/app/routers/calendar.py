"""日历视图路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.database import get_db
from app.models import WatchHistory, Watchlist
from app.services.tmdb import tmdb_service
from app.services.emby import emby_service

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/shows")
async def get_shows_calendar(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    user_id: Optional[str] = Query(None, description="Emby 用户 ID，用于获取追剧列表"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取剧集日历
    返回指定日期范围内的剧集播出信息
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    calendar_items = []
    
    # 获取正在追的剧集（从观看历史中提取）
    watching_series = set()
    if user_id:
        result = await db.execute(
            select(WatchHistory.series_id, WatchHistory.series_name)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.media_type == "Episode",
                    WatchHistory.series_id.isnot(None)
                )
            )
            .distinct()
        )
        for row in result.fetchall():
            if row[0]:
                watching_series.add((row[0], row[1]))
    
    # 获取想看列表中的剧集
    watchlist_result = await db.execute(
        select(Watchlist).where(Watchlist.media_type == "tv")
    )
    watchlist_shows = watchlist_result.scalars().all()
    
    # 从 TMDB 获取今日/本周播出的剧集
    try:
        # 获取正在播出的剧集
        on_air = await tmdb_service.get_tv_on_the_air(page=1)
        airing_today = await tmdb_service.get_tv_airing_today(page=1)
        
        # 合并并去重
        all_shows = {}
        for show in on_air.get("results", []) + airing_today.get("results", []):
            if show.get("id") not in all_shows:
                all_shows[show["id"]] = show
        
        # 处理每个剧集
        for show_id, show in all_shows.items():
            # 获取下一集播出信息
            try:
                show_detail = await tmdb_service.get_tv_show(show_id)
                next_episode = show_detail.get("next_episode_to_air")
                
                if next_episode and next_episode.get("air_date"):
                    air_date = datetime.strptime(next_episode["air_date"], "%Y-%m-%d")
                    
                    # 检查是否在日期范围内
                    if start <= air_date <= end:
                        calendar_items.append({
                            "id": show_id,
                            "type": "episode",
                            "title": show.get("name"),
                            "date": next_episode["air_date"],
                            "episode_title": next_episode.get("name"),
                            "season_number": next_episode.get("season_number"),
                            "episode_number": next_episode.get("episode_number"),
                            "overview": next_episode.get("overview"),
                            "poster_path": show.get("poster_path"),
                            "backdrop_path": show.get("backdrop_path"),
                            "vote_average": show.get("vote_average"),
                            "is_watching": str(show_id) in [s[0] for s in watching_series] if watching_series else False,
                            "in_watchlist": any(w.tmdb_id == show_id for w in watchlist_shows),
                        })
            except Exception:
                continue
                
    except Exception as e:
        print(f"获取 TMDB 日历数据失败: {e}")
    
    # 按日期排序
    calendar_items.sort(key=lambda x: x["date"])
    
    return {"items": calendar_items}


@router.get("/movies")
async def get_movies_calendar(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取电影日历
    返回指定日期范围内即将上映的电影
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    calendar_items = []
    
    # 获取想看列表中的电影
    watchlist_result = await db.execute(
        select(Watchlist).where(Watchlist.media_type == "movie")
    )
    watchlist_movies = watchlist_result.scalars().all()
    watchlist_ids = {w.tmdb_id for w in watchlist_movies if w.tmdb_id}
    
    try:
        # 使用 discover API 获取指定日期范围的电影
        params = {
            "primary_release_date.gte": start_date,
            "primary_release_date.lte": end_date,
            "sort_by": "primary_release_date.asc",
            "page": 1,
        }
        result = await tmdb_service.discover_movie(params)
        
        for movie in result.get("results", []):
            release_date = movie.get("release_date")
            if release_date:
                calendar_items.append({
                    "id": movie.get("id"),
                    "type": "movie",
                    "title": movie.get("title"),
                    "date": release_date,
                    "overview": movie.get("overview"),
                    "poster_path": movie.get("poster_path"),
                    "backdrop_path": movie.get("backdrop_path"),
                    "vote_average": movie.get("vote_average"),
                    "in_watchlist": movie.get("id") in watchlist_ids,
                })
        
        # 获取更多页
        total_pages = min(result.get("total_pages", 1), 5)  # 最多5页
        for page in range(2, total_pages + 1):
            params["page"] = page
            result = await tmdb_service.discover_movie(params)
            for movie in result.get("results", []):
                release_date = movie.get("release_date")
                if release_date:
                    calendar_items.append({
                        "id": movie.get("id"),
                        "type": "movie",
                        "title": movie.get("title"),
                        "date": release_date,
                        "overview": movie.get("overview"),
                        "poster_path": movie.get("poster_path"),
                        "backdrop_path": movie.get("backdrop_path"),
                        "vote_average": movie.get("vote_average"),
                        "in_watchlist": movie.get("id") in watchlist_ids,
                    })
                    
    except Exception as e:
        print(f"获取电影日历数据失败: {e}")
    
    # 按日期排序
    calendar_items.sort(key=lambda x: x["date"])
    
    return {"items": calendar_items}


@router.get("/all")
async def get_all_calendar(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    user_id: Optional[str] = Query(None, description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取综合日历（剧集 + 电影）
    """
    shows = await get_shows_calendar(start_date, end_date, user_id, db)
    movies = await get_movies_calendar(start_date, end_date, db)
    
    # 合并并按日期分组
    all_items = shows["items"] + movies["items"]
    all_items.sort(key=lambda x: x["date"])
    
    # 按日期分组
    grouped = defaultdict(list)
    for item in all_items:
        grouped[item["date"]].append(item)
    
    return {
        "items": all_items,
        "grouped": dict(grouped),
    }


@router.get("/my-shows")
async def get_my_shows_calendar(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取我的追剧日历
    只显示正在追的剧集和想看列表中的剧集
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    
    calendar_items = []
    
    # 获取正在追的剧集（从观看历史中提取 TMDB ID）
    # 需要通过 Emby 的 ProviderIds 获取 TMDB ID
    watching_series = {}
    
    # 从观看历史获取剧集
    result = await db.execute(
        select(WatchHistory.series_id, WatchHistory.series_name)
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_id.isnot(None)
            )
        )
        .distinct()
    )
    
    for row in result.fetchall():
        emby_series_id, series_name = row
        if emby_series_id:
            try:
                # 从 Emby 获取剧集详情以获取 TMDB ID
                series_detail = await emby_service.get_item(user_id, emby_series_id)
                tmdb_id = series_detail.provider_ids.get("Tmdb")
                if tmdb_id:
                    watching_series[int(tmdb_id)] = series_name
            except Exception:
                continue
    
    # 获取想看列表中的剧集
    watchlist_result = await db.execute(
        select(Watchlist).where(Watchlist.media_type == "tv")
    )
    for show in watchlist_result.scalars().all():
        if show.tmdb_id and show.tmdb_id not in watching_series:
            watching_series[show.tmdb_id] = show.title
    
    # 获取每个剧集的下一集播出信息
    for tmdb_id, title in watching_series.items():
        try:
            show_detail = await tmdb_service.get_tv_show(tmdb_id)
            next_episode = show_detail.get("next_episode_to_air")
            
            if next_episode and next_episode.get("air_date"):
                air_date = datetime.strptime(next_episode["air_date"], "%Y-%m-%d")
                
                if start <= air_date <= end:
                    calendar_items.append({
                        "id": tmdb_id,
                        "type": "episode",
                        "title": show_detail.get("name", title),
                        "date": next_episode["air_date"],
                        "episode_title": next_episode.get("name"),
                        "season_number": next_episode.get("season_number"),
                        "episode_number": next_episode.get("episode_number"),
                        "overview": next_episode.get("overview"),
                        "poster_path": show_detail.get("poster_path"),
                        "backdrop_path": show_detail.get("backdrop_path"),
                        "vote_average": show_detail.get("vote_average"),
                        "is_watching": True,
                    })
        except Exception as e:
            print(f"获取剧集 {tmdb_id} 信息失败: {e}")
            continue
    
    # 按日期排序
    calendar_items.sort(key=lambda x: x["date"])
    
    # 按日期分组
    grouped = defaultdict(list)
    for item in calendar_items:
        grouped[item["date"]].append(item)
    
    return {
        "items": calendar_items,
        "grouped": dict(grouped),
    }


@router.get("/ical")
async def export_ical(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    导出 iCal 格式的日历
    """
    from fastapi.responses import Response
    
    # 获取未来30天的日历
    today = datetime.now()
    end_date = today + timedelta(days=30)
    
    result = await get_my_shows_calendar(
        start_date=today.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        user_id=user_id,
        db=db,
    )
    
    # 生成 iCal 内容
    ical_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Emby Tracker//Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Emby Tracker 追剧日历",
    ]
    
    for item in result["items"]:
        event_date = item["date"].replace("-", "")
        uid = f"{item['id']}-{item['date']}@emby-tracker"
        
        title = item["title"]
        if item.get("season_number") and item.get("episode_number"):
            title += f" S{item['season_number']:02d}E{item['episode_number']:02d}"
        if item.get("episode_title"):
            title += f" - {item['episode_title']}"
        
        ical_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART;VALUE=DATE:{event_date}",
            f"DTEND;VALUE=DATE:{event_date}",
            f"SUMMARY:{title}",
            f"DESCRIPTION:{item.get('overview', '')[:200]}",
            "END:VEVENT",
        ])
    
    ical_lines.append("END:VCALENDAR")
    
    ical_content = "\r\n".join(ical_lines)
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=emby-tracker.ics"},
    )
