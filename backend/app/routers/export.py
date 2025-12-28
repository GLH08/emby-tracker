"""数据导入/导出路由"""
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import json
import csv
import io
from app.database import get_db
from app.models import WatchHistory, Watchlist, UserRating, CustomList, CustomListItem

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/history")
async def export_history(
    user_id: str = Query(..., description="Emby 用户 ID"),
    format: str = Query("json", description="导出格式: json / csv"),
    db: AsyncSession = Depends(get_db),
):
    """导出观看历史"""
    result = await db.execute(
        select(WatchHistory)
        .where(WatchHistory.user_id == user_id)
        .order_by(WatchHistory.watched_at.desc())
    )
    history = result.scalars().all()
    
    data = [
        {
            "title": h.title,
            "media_type": h.media_type,
            "year": h.year,
            "series_name": h.series_name,
            "season_number": h.season_number,
            "episode_number": h.episode_number,
            "watched": h.watched,
            "watch_progress": h.watch_progress,
            "watched_at": h.watched_at.isoformat() if h.watched_at else None,
            "community_rating": h.community_rating,
            "genres": h.genres,
            "runtime_minutes": h.runtime_minutes,
            "emby_id": h.emby_id,
            "tmdb_id": h.tmdb_id,
        }
        for h in history
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                # 将列表转为字符串
                row["genres"] = ",".join(row["genres"]) if row["genres"] else ""
                writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=watch_history_{user_id}.csv"}
        )
    
    # JSON 格式
    return StreamingResponse(
        iter([json.dumps({"history": data, "exported_at": datetime.now().isoformat(), "total": len(data)}, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=watch_history_{user_id}.json"}
    )


@router.get("/watchlist")
async def export_watchlist(
    format: str = Query("json", description="导出格式: json / csv"),
    db: AsyncSession = Depends(get_db),
):
    """导出想看列表"""
    result = await db.execute(
        select(Watchlist).order_by(Watchlist.added_at.desc())
    )
    watchlist = result.scalars().all()
    
    data = [
        {
            "title": w.title,
            "media_type": w.media_type,
            "tmdb_id": w.tmdb_id,
            "emby_id": w.emby_id,
            "release_date": w.release_date,
            "vote_average": w.vote_average,
            "overview": w.overview,
            "added_at": w.added_at.isoformat() if w.added_at else None,
        }
        for w in watchlist
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=watchlist.csv"}
        )
    
    return StreamingResponse(
        iter([json.dumps({"watchlist": data, "exported_at": datetime.now().isoformat(), "total": len(data)}, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=watchlist.json"}
    )


@router.get("/ratings")
async def export_ratings(
    user_id: str = Query(..., description="Emby 用户 ID"),
    format: str = Query("json", description="导出格式: json / csv"),
    db: AsyncSession = Depends(get_db),
):
    """导出评分"""
    result = await db.execute(
        select(UserRating)
        .where(UserRating.user_id == user_id)
        .order_by(UserRating.rated_at.desc())
    )
    ratings = result.scalars().all()
    
    data = [
        {
            "title": r.title,
            "media_type": r.media_type,
            "rating": r.rating,
            "review": r.review,
            "tmdb_id": r.tmdb_id,
            "emby_id": r.emby_id,
            "rated_at": r.rated_at.isoformat() if r.rated_at else None,
        }
        for r in ratings
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=ratings_{user_id}.csv"}
        )
    
    return StreamingResponse(
        iter([json.dumps({"ratings": data, "exported_at": datetime.now().isoformat(), "total": len(data)}, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=ratings_{user_id}.json"}
    )


@router.get("/lists")
async def export_lists(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """导出自定义列表"""
    result = await db.execute(
        select(CustomList)
        .where(CustomList.user_id == user_id)
        .order_by(CustomList.created_at.desc())
    )
    lists = result.scalars().all()
    
    data = []
    for lst in lists:
        items_result = await db.execute(
            select(CustomListItem)
            .where(CustomListItem.list_id == lst.id)
            .order_by(CustomListItem.sort_order)
        )
        items = items_result.scalars().all()
        
        data.append({
            "name": lst.name,
            "description": lst.description,
            "is_public": lst.is_public,
            "created_at": lst.created_at.isoformat() if lst.created_at else None,
            "items": [
                {
                    "title": item.title,
                    "media_type": item.media_type,
                    "tmdb_id": item.tmdb_id,
                    "year": item.year,
                    "note": item.note,
                }
                for item in items
            ]
        })
    
    return StreamingResponse(
        iter([json.dumps({"lists": data, "exported_at": datetime.now().isoformat(), "total": len(data)}, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=lists_{user_id}.json"}
    )


@router.get("/full-backup")
async def export_full_backup(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """导出完整备份"""
    # 观看历史
    history_result = await db.execute(
        select(WatchHistory).where(WatchHistory.user_id == user_id)
    )
    history = [
        {
            "title": h.title,
            "media_type": h.media_type,
            "year": h.year,
            "series_name": h.series_name,
            "season_number": h.season_number,
            "episode_number": h.episode_number,
            "watched": h.watched,
            "watch_progress": h.watch_progress,
            "watched_at": h.watched_at.isoformat() if h.watched_at else None,
            "community_rating": h.community_rating,
            "genres": h.genres,
            "runtime_minutes": h.runtime_minutes,
            "emby_id": h.emby_id,
            "tmdb_id": h.tmdb_id,
        }
        for h in history_result.scalars().all()
    ]
    
    # 想看列表
    watchlist_result = await db.execute(select(Watchlist))
    watchlist = [
        {
            "title": w.title,
            "media_type": w.media_type,
            "tmdb_id": w.tmdb_id,
            "emby_id": w.emby_id,
            "release_date": w.release_date,
            "vote_average": w.vote_average,
            "added_at": w.added_at.isoformat() if w.added_at else None,
        }
        for w in watchlist_result.scalars().all()
    ]
    
    # 评分
    ratings_result = await db.execute(
        select(UserRating).where(UserRating.user_id == user_id)
    )
    ratings = [
        {
            "title": r.title,
            "media_type": r.media_type,
            "rating": r.rating,
            "review": r.review,
            "tmdb_id": r.tmdb_id,
            "rated_at": r.rated_at.isoformat() if r.rated_at else None,
        }
        for r in ratings_result.scalars().all()
    ]
    
    # 自定义列表
    lists_result = await db.execute(
        select(CustomList).where(CustomList.user_id == user_id)
    )
    lists = []
    for lst in lists_result.scalars().all():
        items_result = await db.execute(
            select(CustomListItem).where(CustomListItem.list_id == lst.id)
        )
        lists.append({
            "name": lst.name,
            "description": lst.description,
            "is_public": lst.is_public,
            "items": [
                {"title": item.title, "media_type": item.media_type, "tmdb_id": item.tmdb_id}
                for item in items_result.scalars().all()
            ]
        })
    
    backup = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "user_id": user_id,
        "data": {
            "history": history,
            "watchlist": watchlist,
            "ratings": ratings,
            "lists": lists,
        },
        "counts": {
            "history": len(history),
            "watchlist": len(watchlist),
            "ratings": len(ratings),
            "lists": len(lists),
        }
    }
    
    return StreamingResponse(
        iter([json.dumps(backup, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=emby_tracker_backup_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"}
    )


# 导入路由
import_router = APIRouter(prefix="/import", tags=["Import"])


@import_router.post("/trakt-history")
async def import_trakt_history(
    user_id: str = Query(..., description="Emby 用户 ID"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    从 Trakt 导入观看历史
    支持 Trakt 导出的 JSON 格式
    """
    try:
        content = await file.read()
        data = json.loads(content)
        
        imported = 0
        skipped = 0
        
        # Trakt 导出格式可能是数组或对象
        items = data if isinstance(data, list) else data.get("history", [])
        
        for item in items:
            # 尝试解析 Trakt 格式
            media_type = item.get("type", "").lower()
            if media_type == "movie":
                movie = item.get("movie", {})
                title = movie.get("title")
                year = movie.get("year")
                tmdb_id = movie.get("ids", {}).get("tmdb")
            elif media_type == "episode":
                show = item.get("show", {})
                episode = item.get("episode", {})
                title = episode.get("title")
                year = show.get("year")
                tmdb_id = show.get("ids", {}).get("tmdb")
            else:
                skipped += 1
                continue
            
            if not title:
                skipped += 1
                continue
            
            # 检查是否已存在
            existing = await db.execute(
                select(WatchHistory)
                .where(
                    WatchHistory.user_id == user_id,
                    WatchHistory.title == title,
                    WatchHistory.media_type == ("Movie" if media_type == "movie" else "Episode"),
                )
            )
            
            if existing.scalar_one_or_none():
                skipped += 1
                continue
            
            # 创建记录
            watched_at = item.get("watched_at")
            if watched_at:
                try:
                    watched_at = datetime.fromisoformat(watched_at.replace("Z", "+00:00"))
                except Exception:
                    watched_at = datetime.now()
            else:
                watched_at = datetime.now()
            
            new_history = WatchHistory(
                user_id=user_id,
                title=title,
                media_type="Movie" if media_type == "movie" else "Episode",
                year=year,
                tmdb_id=tmdb_id,
                watched=True,
                watched_at=watched_at,
                source="trakt_import",
            )
            db.add(new_history)
            imported += 1
        
        await db.commit()
        
        return {
            "message": "导入完成",
            "imported": imported,
            "skipped": skipped,
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@import_router.post("/backup")
async def import_backup(
    user_id: str = Query(..., description="Emby 用户 ID"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    从备份文件恢复数据
    """
    try:
        content = await file.read()
        backup = json.loads(content)
        
        if backup.get("version") != "1.0":
            raise HTTPException(status_code=400, detail="不支持的备份版本")
        
        data = backup.get("data", {})
        results = {
            "history": {"imported": 0, "skipped": 0},
            "watchlist": {"imported": 0, "skipped": 0},
            "ratings": {"imported": 0, "skipped": 0},
            "lists": {"imported": 0, "skipped": 0},
        }
        
        # 导入观看历史
        for item in data.get("history", []):
            existing = await db.execute(
                select(WatchHistory)
                .where(
                    WatchHistory.user_id == user_id,
                    WatchHistory.title == item.get("title"),
                    WatchHistory.media_type == item.get("media_type"),
                )
            )
            if existing.scalar_one_or_none():
                results["history"]["skipped"] += 1
                continue
            
            watched_at = item.get("watched_at")
            if watched_at:
                try:
                    watched_at = datetime.fromisoformat(watched_at)
                except Exception:
                    watched_at = None
            
            new_history = WatchHistory(
                user_id=user_id,
                title=item.get("title"),
                media_type=item.get("media_type"),
                year=item.get("year"),
                series_name=item.get("series_name"),
                season_number=item.get("season_number"),
                episode_number=item.get("episode_number"),
                watched=item.get("watched", True),
                watch_progress=item.get("watch_progress", 100),
                watched_at=watched_at,
                community_rating=item.get("community_rating"),
                genres=item.get("genres", []),
                runtime_minutes=item.get("runtime_minutes"),
                tmdb_id=item.get("tmdb_id"),
                source="backup_import",
            )
            db.add(new_history)
            results["history"]["imported"] += 1
        
        # 导入评分
        for item in data.get("ratings", []):
            existing = await db.execute(
                select(UserRating)
                .where(
                    UserRating.user_id == user_id,
                    UserRating.title == item.get("title"),
                    UserRating.media_type == item.get("media_type"),
                )
            )
            if existing.scalar_one_or_none():
                results["ratings"]["skipped"] += 1
                continue
            
            rated_at = item.get("rated_at")
            if rated_at:
                try:
                    rated_at = datetime.fromisoformat(rated_at)
                except Exception:
                    rated_at = None
            
            new_rating = UserRating(
                user_id=user_id,
                title=item.get("title"),
                media_type=item.get("media_type"),
                rating=item.get("rating"),
                review=item.get("review"),
                tmdb_id=item.get("tmdb_id"),
                rated_at=rated_at,
            )
            db.add(new_rating)
            results["ratings"]["imported"] += 1
        
        await db.commit()
        
        return {
            "message": "恢复完成",
            "results": results,
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的 JSON 文件")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"恢复失败: {str(e)}")


# 合并路由
router.include_router(import_router)
