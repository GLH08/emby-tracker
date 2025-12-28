"""
OMDb API 服务
支持多 API Key 轮询，自动故障转移，缓存评分数据
"""
import httpx
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExternalRating

logger = logging.getLogger(__name__)


class OMDbService:
    """OMDb API 服务，支持多 Key 轮询"""
    
    BASE_URL = "https://www.omdbapi.com/"
    
    def __init__(self):
        self.api_keys: List[str] = []
        self.current_key_index = 0
        self.key_usage: dict = {}  # 记录每个 key 的使用情况
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保 API Keys 已加载（延迟初始化）"""
        if self._initialized:
            return
        self._load_api_keys()
        self._initialized = True
    
    def _load_api_keys(self):
        """从配置加载 API Keys"""
        # 重新获取配置（不使用缓存）
        from app.config import Settings
        settings = Settings()
        
        keys_str = getattr(settings, 'omdb_api_keys', '') or ''
        if keys_str:
            self.api_keys = [k.strip() for k in keys_str.split(',') if k.strip()]
            # 初始化使用记录
            for key in self.api_keys:
                if key not in self.key_usage:
                    self.key_usage[key] = {
                        'count': 0,
                        'last_reset': datetime.now().date(),
                        'errors': 0
                    }
        logger.info(f"OMDb 服务已加载 {len(self.api_keys)} 个 API Key")
    
    def _get_next_key(self) -> Optional[str]:
        """获取下一个可用的 API Key（轮询策略）"""
        self._ensure_initialized()
        
        if not self.api_keys:
            return None
        
        today = datetime.now().date()
        
        # 尝试找到一个可用的 key
        tried_keys = 0
        while tried_keys < len(self.api_keys):
            key = self.api_keys[self.current_key_index]
            usage = self.key_usage[key]
            
            # 如果是新的一天，重置计数
            if usage['last_reset'] != today:
                usage['count'] = 0
                usage['errors'] = 0
                usage['last_reset'] = today
                usage['exhausted'] = False
            
            # 检查是否已标记为耗尽（当天收到 API 限制错误）
            if usage.get('exhausted', False):
                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                tried_keys += 1
                continue
            
            # 检查是否超过限制（每天 1000 次）或错误过多
            if usage['count'] < 1000 and usage['errors'] < 10:
                return key
            
            # 切换到下一个 key
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            tried_keys += 1
        
        logger.warning("所有 OMDb API Key 已达到限制")
        return None
    
    def _record_usage(self, key: str, success: bool = True, exhausted: bool = False):
        """记录 API Key 使用情况"""
        if key in self.key_usage:
            self.key_usage[key]['count'] += 1
            if not success:
                self.key_usage[key]['errors'] += 1
            if exhausted:
                self.key_usage[key]['exhausted'] = True
                logger.warning(f"OMDb API Key {key[:4]}**** 已达到每日限制")
            # 轮询到下一个 key
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    
    async def _request(self, params: dict) -> Optional[dict]:
        """发送 API 请求"""
        api_key = self._get_next_key()
        if not api_key:
            logger.error("没有可用的 OMDb API Key")
            return None
        
        params['apikey'] = api_key
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('Response') == 'True':
                    self._record_usage(api_key, success=True)
                    return data
                else:
                    error = data.get('Error', 'Unknown error')
                    logger.warning(f"OMDb API 返回错误: {error}")
                    # 如果是请求限制错误，标记这个 key 为耗尽
                    if 'limit' in error.lower() or 'exceeded' in error.lower():
                        self._record_usage(api_key, success=False, exhausted=True)
                    else:
                        self._record_usage(api_key, success=False)
                    return None
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"OMDb API HTTP 错误: {e}")
            self._record_usage(api_key, success=False)
            return None
        except Exception as e:
            logger.error(f"OMDb API 请求失败: {e}")
            self._record_usage(api_key, success=False)
            return None
    
    async def get_by_imdb_id(self, imdb_id: str) -> Optional[dict]:
        """通过 IMDB ID 获取评分"""
        if not imdb_id or not imdb_id.startswith('tt'):
            return None
        return await self._request({'i': imdb_id})
    
    async def get_by_title(self, title: str, year: Optional[int] = None, media_type: str = 'movie') -> Optional[dict]:
        """通过标题搜索获取评分"""
        params = {
            't': title,
            'type': media_type if media_type in ['movie', 'series'] else 'movie'
        }
        if year:
            params['y'] = str(year)
        return await self._request(params)
    
    async def search(self, query: str, media_type: str = 'movie', page: int = 1) -> Optional[dict]:
        """搜索媒体"""
        params = {
            's': query,
            'type': media_type if media_type in ['movie', 'series'] else 'movie',
            'page': page
        }
        return await self._request(params)
    
    def parse_ratings(self, data: dict) -> dict:
        """解析 OMDb 返回的评分数据"""
        result = {
            'imdb_id': data.get('imdbID'),
            'title': data.get('Title'),
            'year': None,
            'media_type': 'movie' if data.get('Type') == 'movie' else 'tv',
            'imdb_rating': None,
            'imdb_votes': None,
            'rotten_tomatoes': None,
            'metacritic': None,
            'rated': data.get('Rated'),
            'awards': data.get('Awards'),
            'box_office': data.get('BoxOffice'),
        }
        
        # 解析年份
        year_str = data.get('Year', '')
        if year_str:
            try:
                # 处理 "2020–2023" 这种格式
                result['year'] = int(year_str.split('–')[0].split('-')[0])
            except:
                pass
        
        # 解析 IMDB 评分
        imdb_rating = data.get('imdbRating')
        if imdb_rating and imdb_rating != 'N/A':
            try:
                result['imdb_rating'] = float(imdb_rating)
            except:
                pass
        
        # 解析 IMDB 投票数
        imdb_votes = data.get('imdbVotes', '').replace(',', '')
        if imdb_votes and imdb_votes != 'N/A':
            try:
                result['imdb_votes'] = int(imdb_votes)
            except:
                pass
        
        # 解析其他评分源
        ratings = data.get('Ratings', [])
        for rating in ratings:
            source = rating.get('Source', '')
            value = rating.get('Value', '')
            
            if 'Rotten Tomatoes' in source:
                try:
                    result['rotten_tomatoes'] = int(value.replace('%', ''))
                except:
                    pass
            elif 'Metacritic' in source:
                try:
                    result['metacritic'] = int(value.split('/')[0])
                except:
                    pass
        
        return result
    
    async def get_ratings_cached(
        self, 
        db: AsyncSession, 
        imdb_id: Optional[str] = None,
        tmdb_id: Optional[int] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
        media_type: str = 'movie',
        cache_days: int = 7
    ) -> Optional[dict]:
        """
        获取评分（优先从缓存读取）
        
        Args:
            db: 数据库会话
            imdb_id: IMDB ID
            tmdb_id: TMDB ID（用于缓存关联）
            title: 标题（当没有 IMDB ID 时使用）
            year: 年份
            media_type: 媒体类型 (movie/tv)
            cache_days: 缓存有效天数
        """
        # 1. 尝试从缓存读取
        if imdb_id:
            stmt = select(ExternalRating).where(ExternalRating.imdb_id == imdb_id)
            result = await db.execute(stmt)
            cached = result.scalar_one_or_none()
            
            if cached:
                # 检查缓存是否过期
                cache_age = datetime.now() - cached.updated_at
                if cache_age < timedelta(days=cache_days):
                    return {
                        'imdb_id': cached.imdb_id,
                        'tmdb_id': cached.tmdb_id,
                        'title': cached.title,
                        'year': cached.year,
                        'media_type': cached.media_type,
                        'imdb_rating': cached.imdb_rating,
                        'imdb_votes': cached.imdb_votes,
                        'rotten_tomatoes': cached.rotten_tomatoes,
                        'metacritic': cached.metacritic,
                        'rated': cached.rated,
                        'awards': cached.awards,
                        'box_office': cached.box_office,
                        'cached': True
                    }
        
        # 2. 从 API 获取
        data = None
        if imdb_id:
            data = await self.get_by_imdb_id(imdb_id)
        elif title:
            data = await self.get_by_title(title, year, 'series' if media_type == 'tv' else 'movie')
        
        if not data:
            return None
        
        # 3. 解析数据
        parsed = self.parse_ratings(data)
        if tmdb_id:
            parsed['tmdb_id'] = tmdb_id
        
        # 4. 保存到缓存
        await self._save_to_cache(db, parsed)
        
        parsed['cached'] = False
        return parsed
    
    async def _save_to_cache(self, db: AsyncSession, data: dict):
        """保存评分到缓存"""
        if not data.get('imdb_id'):
            return
        
        try:
            # 查找现有记录
            stmt = select(ExternalRating).where(ExternalRating.imdb_id == data['imdb_id'])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # 更新现有记录
                existing.tmdb_id = data.get('tmdb_id') or existing.tmdb_id
                existing.title = data.get('title') or existing.title
                existing.year = data.get('year') or existing.year
                existing.media_type = data.get('media_type') or existing.media_type
                existing.imdb_rating = data.get('imdb_rating')
                existing.imdb_votes = data.get('imdb_votes')
                existing.rotten_tomatoes = data.get('rotten_tomatoes')
                existing.metacritic = data.get('metacritic')
                existing.rated = data.get('rated')
                existing.awards = data.get('awards')
                existing.box_office = data.get('box_office')
            else:
                # 创建新记录
                new_rating = ExternalRating(
                    imdb_id=data['imdb_id'],
                    tmdb_id=data.get('tmdb_id'),
                    media_type=data.get('media_type', 'movie'),
                    title=data.get('title', ''),
                    year=data.get('year'),
                    imdb_rating=data.get('imdb_rating'),
                    imdb_votes=data.get('imdb_votes'),
                    rotten_tomatoes=data.get('rotten_tomatoes'),
                    metacritic=data.get('metacritic'),
                    rated=data.get('rated'),
                    awards=data.get('awards'),
                    box_office=data.get('box_office'),
                )
                db.add(new_rating)
            
            await db.commit()
        except Exception as e:
            logger.error(f"保存评分缓存失败: {e}")
            await db.rollback()
    
    def get_status(self) -> dict:
        """获取服务状态"""
        self._ensure_initialized()
        
        today = datetime.now().date()
        keys_status = []
        total_remaining = 0
        
        for i, key in enumerate(self.api_keys):
            usage = self.key_usage.get(key, {})
            # 如果是新的一天，重置计数
            if usage.get('last_reset') != today:
                usage['count'] = 0
                usage['errors'] = 0
                usage['last_reset'] = today
                usage['exhausted'] = False
            
            # 如果已标记为耗尽，剩余为 0
            if usage.get('exhausted', False):
                remaining = 0
            else:
                remaining = 1000 - usage.get('count', 0)
            
            total_remaining += remaining
            keys_status.append({
                'index': i + 1,
                'used': usage.get('count', 0),
                'remaining': remaining,
                'errors': usage.get('errors', 0),
                'exhausted': usage.get('exhausted', False),
                'is_current': i == self.current_key_index
            })
        
        return {
            'total_keys': len(self.api_keys),
            'total_remaining': total_remaining,
            'keys': keys_status
        }


# 全局服务实例
omdb_service = OMDbService()
