import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class TMDBService:
    def __init__(self):
        self.base_url = settings.tmdb_base_url
        self.api_key = settings.tmdb_api_key
        self.image_base_url = settings.tmdb_image_base_url
    
    def _check_config(self):
        """检查 TMDB API Key 是否配置"""
        if not self.api_key:
            raise ValueError("TMDB API Key 未配置")
    
    async def _request(self, endpoint: str, params: dict = None) -> dict:
        self._check_config()
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        params["language"] = "zh-CN"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}{endpoint}"
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_movie(self, movie_id: int) -> dict:
        """获取电影详情"""
        return await self._request(
            f"/movie/{movie_id}",
            params={"append_to_response": "credits,videos,similar,recommendations"}
        )
    
    async def get_tv_show(self, tv_id: int) -> dict:
        """获取剧集详情"""
        return await self._request(
            f"/tv/{tv_id}",
            params={"append_to_response": "credits,videos,similar,recommendations"}
        )
    
    async def get_tv_season(self, tv_id: int, season_number: int) -> dict:
        """获取季详情"""
        return await self._request(f"/tv/{tv_id}/season/{season_number}")
    
    async def get_tv_episode(self, tv_id: int, season_number: int, episode_number: int) -> dict:
        """获取集详情"""
        return await self._request(f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}")
    
    async def search_movie(self, query: str, page: int = 1, year: Optional[int] = None) -> dict:
        """搜索电影"""
        params = {"query": query, "page": page}
        if year:
            params["year"] = year
        return await self._request("/search/movie", params)
    
    async def search_tv(self, query: str, page: int = 1, year: Optional[int] = None) -> dict:
        """搜索剧集"""
        params = {"query": query, "page": page}
        if year:
            params["first_air_date_year"] = year
        return await self._request("/search/tv", params)
    
    async def search_multi(self, query: str, page: int = 1) -> dict:
        """多类型搜索"""
        return await self._request("/search/multi", params={"query": query, "page": page})
    
    async def get_trending(self, media_type: str = "all", time_window: str = "week", page: int = 1) -> dict:
        """获取趋势内容"""
        return await self._request(f"/trending/{media_type}/{time_window}", params={"page": page})
    
    async def get_popular_movies(self, page: int = 1) -> dict:
        """获取热门电影"""
        return await self._request("/movie/popular", params={"page": page})
    
    async def get_popular_tv(self, page: int = 1) -> dict:
        """获取热门剧集"""
        return await self._request("/tv/popular", params={"page": page})
    
    async def get_now_playing_movies(self, page: int = 1) -> dict:
        """获取正在上映的电影"""
        return await self._request("/movie/now_playing", params={"page": page})
    
    async def get_upcoming_movies(self, page: int = 1) -> dict:
        """获取即将上映的电影"""
        return await self._request("/movie/upcoming", params={"page": page})
    
    async def get_top_rated_movies(self, page: int = 1) -> dict:
        """获取高分电影"""
        return await self._request("/movie/top_rated", params={"page": page})
    
    async def get_top_rated_tv(self, page: int = 1) -> dict:
        """获取高分剧集"""
        return await self._request("/tv/top_rated", params={"page": page})
    
    async def get_person(self, person_id: int) -> dict:
        """获取人物详情"""
        return await self._request(
            f"/person/{person_id}",
            params={"append_to_response": "combined_credits,images"}
        )
    
    async def get_genres(self, media_type: str = "movie") -> dict:
        """获取类型列表"""
        return await self._request(f"/genre/{media_type}/list")
    
    async def get_tv_on_the_air(self, page: int = 1) -> dict:
        """获取正在播出的剧集"""
        return await self._request("/tv/on_the_air", params={"page": page})
    
    async def get_tv_airing_today(self, page: int = 1) -> dict:
        """获取今日播出的剧集"""
        return await self._request("/tv/airing_today", params={"page": page})
    
    async def discover_tv(self, params: dict = None) -> dict:
        """发现剧集（支持按日期筛选）"""
        return await self._request("/discover/tv", params=params)
    
    async def discover_movie(self, params: dict = None) -> dict:
        """发现电影（支持按日期筛选）"""
        return await self._request("/discover/movie", params=params)
    
    async def get_tv_changes(self, start_date: str = None, end_date: str = None, page: int = 1) -> dict:
        """获取剧集变更"""
        params = {"page": page}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._request("/tv/changes", params=params)
    
    async def get_watch_providers(self, media_type: str, media_id: int) -> dict:
        """获取流媒体可用性"""
        return await self._request(f"/{media_type}/{media_id}/watch/providers")
    
    async def get_movie_recommendations(self, movie_id: int, page: int = 1) -> dict:
        """获取电影推荐"""
        return await self._request(f"/movie/{movie_id}/recommendations", params={"page": page})
    
    async def get_tv_recommendations(self, tv_id: int, page: int = 1) -> dict:
        """获取剧集推荐"""
        return await self._request(f"/tv/{tv_id}/recommendations", params={"page": page})
    
    async def get_movie_similar(self, movie_id: int, page: int = 1) -> dict:
        """获取相似电影"""
        return await self._request(f"/movie/{movie_id}/similar", params={"page": page})
    
    async def get_tv_similar(self, tv_id: int, page: int = 1) -> dict:
        """获取相似剧集"""
        return await self._request(f"/tv/{tv_id}/similar", params={"page": page})
    
    async def get_movie_keywords(self, movie_id: int) -> dict:
        """获取电影关键词"""
        return await self._request(f"/movie/{movie_id}/keywords")
    
    async def get_tv_keywords(self, tv_id: int) -> dict:
        """获取剧集关键词"""
        return await self._request(f"/tv/{tv_id}/keywords")
    
    async def discover_by_genre(self, media_type: str, genre_id: int, page: int = 1, sort_by: str = "popularity.desc") -> dict:
        """按类型发现内容"""
        params = {
            "with_genres": genre_id,
            "sort_by": sort_by,
            "page": page,
        }
        if media_type == "movie":
            return await self._request("/discover/movie", params=params)
        else:
            return await self._request("/discover/tv", params=params)
    
    async def discover_by_year(self, media_type: str, year: int, page: int = 1, sort_by: str = "popularity.desc") -> dict:
        """按年份发现内容"""
        params = {
            "sort_by": sort_by,
            "page": page,
        }
        if media_type == "movie":
            params["primary_release_year"] = year
            return await self._request("/discover/movie", params=params)
        else:
            params["first_air_date_year"] = year
            return await self._request("/discover/tv", params=params)
    
    async def discover_by_network(self, network_id: int, page: int = 1) -> dict:
        """按电视网络发现剧集"""
        params = {
            "with_networks": network_id,
            "sort_by": "popularity.desc",
            "page": page,
        }
        return await self._request("/discover/tv", params=params)
    
    async def get_networks(self) -> dict:
        """获取电视网络列表（常用的）"""
        # TMDB 没有直接的网络列表 API，返回常用网络
        return {
            "networks": [
                {"id": 213, "name": "Netflix"},
                {"id": 1024, "name": "Amazon Prime Video"},
                {"id": 2739, "name": "Disney+"},
                {"id": 453, "name": "Hulu"},
                {"id": 2552, "name": "Apple TV+"},
                {"id": 49, "name": "HBO"},
                {"id": 67, "name": "Showtime"},
                {"id": 318, "name": "Starz"},
                {"id": 359, "name": "Cinemax"},
                {"id": 174, "name": "AMC"},
                {"id": 19, "name": "FOX"},
                {"id": 16, "name": "CBS"},
                {"id": 6, "name": "NBC"},
                {"id": 2, "name": "ABC"},
                {"id": 71, "name": "The CW"},
                {"id": 88, "name": "FX"},
                {"id": 1436, "name": "BBC iPlayer"},
                {"id": 4, "name": "BBC One"},
                {"id": 493, "name": "BBC America"},
                {"id": 1709, "name": "腾讯视频"},
                {"id": 1790, "name": "爱奇艺"},
                {"id": 1867, "name": "优酷"},
                {"id": 2080, "name": "芒果TV"},
                {"id": 614, "name": "bilibili"},
            ]
        }
    
    def get_image_url(self, path: str, size: str = "w500") -> str:
        """获取图片完整 URL"""
        if not path:
            return ""
        return f"{self.image_base_url}/{size}{path}"


tmdb_service = TMDBService()
