<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">观影统计</h1>
      <div class="flex items-center space-x-2">
        <button 
          @click="activeTab = 'all'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
        >全部</button>
        <button 
          @click="activeTab = 'movie'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'movie' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
        >电影</button>
        <button 
          @click="activeTab = 'show'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'show' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
        >剧集</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <template v-else>
      <!-- 总览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <!-- 总观看时长 -->
        <div class="card p-6 bg-gradient-to-br from-primary-500 to-purple-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm opacity-80">总观看时长</p>
              <p class="text-4xl font-bold mt-2">{{ formatWatchTime(overview.total_watch_time_minutes) }}</p>
              <p class="text-sm opacity-80 mt-1">约 {{ overview.total_watch_time_days }} 天</p>
            </div>
            <div class="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 电影统计 -->
        <div class="card p-6">
          <div class="flex items-center space-x-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">电影</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ overview.movies.watched }} / {{ overview.movies.total }}</p>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">完成度</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ overview.movies.progress_percent }}%</span>
            </div>
            <div class="h-2 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
              <div class="h-full bg-purple-500 rounded-full transition-all" :style="{ width: `${overview.movies.progress_percent}%` }"></div>
            </div>
            <p class="text-xs text-gray-400">{{ formatWatchTime(overview.movies.watch_time_minutes) }} 观看时长</p>
          </div>
        </div>

        <!-- 剧集统计 -->
        <div class="card p-6">
          <div class="flex items-center space-x-4 mb-4">
            <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">剧集</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ overview.shows.episodes_watched }} / {{ overview.shows.episodes_total }}</p>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500 dark:text-gray-400">完成度</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ overview.shows.progress_percent }}%</span>
            </div>
            <div class="h-2 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
              <div class="h-full bg-blue-500 rounded-full transition-all" :style="{ width: `${overview.shows.progress_percent}%` }"></div>
            </div>
            <p class="text-xs text-gray-400">{{ overview.shows.total }} 部剧集 · {{ formatWatchTime(overview.shows.watch_time_minutes) }} 观看时长</p>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="grid md:grid-cols-2 gap-6 mb-10">
        <!-- 类型分布 -->
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">类型分布</h2>
          <div v-if="Object.keys(genreStats).length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
          <div v-else class="space-y-3">
            <div v-for="(count, genre, index) in genreStats" :key="genre" class="flex items-center">
              <span class="w-20 text-sm text-gray-600 dark:text-gray-400 truncate">{{ genre }}</span>
              <div class="flex-1 mx-3 h-6 bg-gray-100 dark:bg-dark-100 rounded-lg overflow-hidden relative">
                <div 
                  class="h-full rounded-lg transition-all"
                  :class="getGenreColor(index)"
                  :style="{ width: `${(count / maxGenreCount) * 100}%` }"
                ></div>
                <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-600 dark:text-gray-300">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 评分分布 -->
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">评分分布</h2>
          <div v-if="totalRatings === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
          <div v-else class="space-y-3">
            <div v-for="(count, rating) in ratingStats" :key="rating" class="flex items-center">
              <div class="w-16 flex items-center">
                <svg class="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ rating }}</span>
              </div>
              <div class="flex-1 mx-3 h-6 bg-gray-100 dark:bg-dark-100 rounded-lg overflow-hidden relative">
                <div 
                  class="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg transition-all"
                  :style="{ width: `${(count / maxRatingCount) * 100}%` }"
                ></div>
                <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-600 dark:text-gray-300">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近观看 -->
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">最近观看</h2>
          <div class="flex items-center space-x-2">
            <select v-model="recentType" @change="fetchRecentWatched" class="input w-auto text-sm py-1">
              <option value="all">全部</option>
              <option value="movie">电影</option>
              <option value="episode">剧集</option>
            </select>
            <router-link to="/history" class="text-sm text-primary-500 hover:text-primary-600">
              查看全部 →
            </router-link>
          </div>
        </div>
        <div v-if="recentWatched.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          暂无数据
        </div>
        <div v-else class="grid md:grid-cols-2 gap-3">
          <router-link 
            v-for="item in recentWatched" 
            :key="item.id"
            :to="getRecentItemLink(item)"
            class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-dark-100 transition-colors"
          >
            <div class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-dark-100 flex items-center justify-center flex-shrink-0">
              <svg v-if="item.type === 'Movie'" class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
              </svg>
              <svg v-else class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 dark:text-white truncate">{{ getRecentItemTitle(item) }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ getRecentItemSubtitle(item) }}</p>
            </div>
            <span class="text-xs text-gray-400">{{ item.runtime_minutes }}分钟</span>
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { statsApi } from '../api'

const appStore = useAppStore()
const loading = ref(true)
const activeTab = ref('all')

// 数据
const overview = ref({
  movies: { total: 0, watched: 0, watch_time_minutes: 0, progress_percent: 0 },
  shows: { total: 0, watched: 0, episodes_total: 0, episodes_watched: 0, watch_time_minutes: 0, progress_percent: 0 },
  total_watch_time_minutes: 0,
  total_watch_time_days: 0,
  watchlist_count: 0,
})
const genreStats = ref({})
const ratingStats = ref({})
const recentWatched = ref([])
const recentType = ref('all')

// 计算属性
const maxGenreCount = computed(() => Math.max(...Object.values(genreStats.value), 1))
const maxRatingCount = computed(() => Math.max(...Object.values(ratingStats.value), 1))
const totalRatings = computed(() => Object.values(ratingStats.value).reduce((a, b) => a + b, 0))

// 方法
const formatWatchTime = (minutes) => {
  if (!minutes) return '0 分钟'
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours < 24) return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`
  const days = Math.floor(hours / 24)
  const remainHours = hours % 24
  return remainHours > 0 ? `${days} 天 ${remainHours} 小时` : `${days} 天`
}

const getGenreColor = (index) => {
  const colors = [
    'bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500',
    'bg-pink-500', 'bg-indigo-500', 'bg-teal-500', 'bg-orange-500', 'bg-cyan-500',
  ]
  return colors[index % colors.length]
}

const getRecentItemLink = (item) => {
  if (item.type === 'Episode' && item.series_id) return `/show/${item.series_id}`
  if (item.type === 'Movie') return `/movie/${item.id}`
  return `/show/${item.id}`
}

const getRecentItemTitle = (item) => {
  if (item.type === 'Episode' && item.series_name) return item.series_name
  return item.name
}

const getRecentItemSubtitle = (item) => {
  if (item.type === 'Episode') {
    return `S${item.season_number || '?'}E${item.episode_number || '?'} ${item.name}`
  }
  return item.year ? `${item.year}` : ''
}

const fetchAllData = async () => {
  if (!appStore.currentEmbyUser) return
  loading.value = true
  
  const libraryIds = appStore.allowedLibraries.map(l => l.id).join(',')
  const mediaType = activeTab.value === 'all' ? null : activeTab.value
  
  try {
    const [overviewData, genres, ratings] = await Promise.all([
      statsApi.getOverview(appStore.currentEmbyUser.Id, libraryIds),
      statsApi.getGenreStats(appStore.currentEmbyUser.Id, libraryIds, mediaType),
      statsApi.getRatingStats(appStore.currentEmbyUser.Id, libraryIds, mediaType),
    ])
    
    overview.value = overviewData
    genreStats.value = genres.genres || {}
    ratingStats.value = ratings.ratings || {}
    
    await fetchRecentWatched()
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  } finally {
    loading.value = false
  }
}

const fetchRecentWatched = async () => {
  if (!appStore.currentEmbyUser) return
  const libraryIds = appStore.allowedLibraries.map(l => l.id).join(',')
  try {
    const result = await statsApi.getRecentWatched(appStore.currentEmbyUser.Id, libraryIds, recentType.value, 10)
    recentWatched.value = result.items || []
  } catch (e) {
    console.error('Failed to fetch recent watched:', e)
  }
}

watch(activeTab, fetchAllData)
watch(() => appStore.currentEmbyUser, fetchAllData)
onMounted(fetchAllData)
</script>

<style scoped>
.writing-mode-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
}
</style>
