<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">观影统计</h1>
      <div class="flex flex-wrap items-center gap-2">
        <router-link 
          to="/yearly-review"
          class="px-4 py-2 rounded-lg text-sm font-medium bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
          </svg>
          年度回顾
        </router-link>
        <div class="flex items-center rounded-lg bg-gray-100 dark:bg-dark-100 p-1">
          <button 
            @click="activeTab = 'all'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === 'all' ? 'bg-white dark:bg-dark-200 text-primary-500 shadow-sm' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'"
          >全部</button>
          <button 
            @click="activeTab = 'movie'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === 'movie' ? 'bg-white dark:bg-dark-200 text-primary-500 shadow-sm' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'"
          >电影</button>
          <button 
            @click="activeTab = 'show'"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === 'show' ? 'bg-white dark:bg-dark-200 text-primary-500 shadow-sm' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'"
          >剧集</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <template v-else>
      <!-- 总览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <!-- 总观看时长 -->
        <div class="card p-6 bg-gradient-to-br from-primary-500 to-purple-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm opacity-80">总观看时长</p>
              <p class="text-3xl font-bold mt-2">{{ formatWatchTime(overview.total_watch_time_minutes) }}</p>
              <p class="text-sm opacity-80 mt-1">约 {{ overview.total_watch_time_days }} 天</p>
            </div>
            <div class="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 连续观看 -->
        <div class="card p-6 bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm opacity-80">连续观看</p>
              <p class="text-3xl font-bold mt-2">{{ streak.current_streak }} 天</p>
              <p class="text-sm opacity-80 mt-1">最长 {{ streak.longest_streak }} 天</p>
            </div>
            <div class="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 电影统计 -->
        <div class="card p-6">
          <div class="flex items-center space-x-3 mb-3">
            <div class="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">电影</p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">{{ overview.movies.watched }}</p>
            </div>
          </div>
          <div class="h-1.5 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
            <div class="h-full bg-purple-500 rounded-full" :style="{ width: `${overview.movies.progress_percent}%` }"></div>
          </div>
          <p class="text-xs text-gray-400 mt-2">{{ overview.movies.progress_percent }}% · {{ overview.movies.total }} 部</p>
        </div>

        <!-- 剧集统计 -->
        <div class="card p-6">
          <div class="flex items-center space-x-3 mb-3">
            <div class="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">剧集</p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">{{ overview.shows.episodes_watched }}</p>
            </div>
          </div>
          <div class="h-1.5 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
            <div class="h-full bg-blue-500 rounded-full" :style="{ width: `${overview.shows.progress_percent}%` }"></div>
          </div>
          <p class="text-xs text-gray-400 mt-2">{{ overview.shows.progress_percent }}% · {{ overview.shows.episodes_total }} 集</p>
        </div>
      </div>

      <!-- 观看热力图 -->
      <div class="card p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">观看热力图</h2>
          <span class="text-sm text-gray-500">{{ streak.total_watch_days }} 天有观看记录</span>
        </div>
        <div class="overflow-x-auto">
          <div class="flex flex-col gap-1 min-w-max">
            <div v-for="dayIndex in 7" :key="dayIndex" class="flex items-center">
              <div class="w-8 text-xs text-gray-400">{{ ['一', '二', '三', '四', '五', '六', '日'][dayIndex - 1] }}</div>
              <div class="flex gap-1">
                <div 
                  v-for="(day, index) in getHeatmapRow(dayIndex - 1)" 
                  :key="index"
                  class="w-3 h-3 rounded-sm cursor-pointer transition-colors"
                  :class="getHeatmapColor(day.level)"
                  :title="`${day.date}: ${day.count} 次观看`"
                ></div>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end mt-3 space-x-2 text-xs text-gray-400">
            <span>少</span>
            <div class="w-3 h-3 rounded-sm bg-gray-100 dark:bg-dark-100"></div>
            <div class="w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900/50"></div>
            <div class="w-3 h-3 rounded-sm bg-green-400 dark:bg-green-700"></div>
            <div class="w-3 h-3 rounded-sm bg-green-500 dark:bg-green-600"></div>
            <div class="w-3 h-3 rounded-sm bg-green-600 dark:bg-green-500"></div>
            <span>多</span>
          </div>
        </div>
      </div>

      <!-- 最近观看（移到上方） -->
      <div class="card p-6 mb-6">
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
            <div class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-dark-100 flex items-center justify-center flex-shrink-0 relative">
              <svg v-if="item.type === 'Movie'" class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
              </svg>
              <svg v-else class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <!-- 已完成标记 -->
              <div v-if="item.is_played && item.progress_percent >= 100" class="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                <svg class="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 dark:text-white truncate">{{ getRecentItemTitle(item) }}</p>
              <div class="flex items-center space-x-2">
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ getRecentItemSubtitle(item) }}</p>
                <!-- 进度条（有进度但未完成时显示） -->
                <div v-if="item.progress_percent != null && item.progress_percent > 0 && item.progress_percent < 100" class="flex items-center space-x-1 flex-shrink-0">
                  <div class="w-12 h-1.5 bg-gray-200 dark:bg-dark-100 rounded-full overflow-hidden">
                    <div class="h-full bg-primary-500 rounded-full" :style="{ width: `${item.progress_percent}%` }"></div>
                  </div>
                  <span class="text-xs text-primary-500">{{ Math.round(item.progress_percent) }}%</span>
                </div>
              </div>
            </div>
            <span class="text-xs text-gray-400 flex-shrink-0">{{ item.runtime_minutes }}分钟</span>
          </router-link>
        </div>
      </div>

      <!-- 30天趋势 + 时段分布 -->
      <div class="grid md:grid-cols-2 gap-6 mb-6">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">30天观看趋势</h2>
          <div v-if="totalTrendCount === 0" class="h-40 flex items-center justify-center text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
          <template v-else>
            <div class="h-40 flex items-end space-x-0.5">
              <div 
                v-for="day in trends" 
                :key="day.date"
                class="flex-1 flex flex-col items-center justify-end h-full"
              >
                <div 
                  class="w-full rounded-t transition-all hover:opacity-80 cursor-pointer min-h-[4px]"
                  :class="day.total > 0 ? 'bg-primary-500' : 'bg-gray-200 dark:bg-dark-100'"
                  :style="{ height: day.total > 0 ? `${Math.max((day.total / maxTrendCount) * 140, 12)}px` : '4px' }"
                  :title="`${day.date}: ${day.total} 次`"
                ></div>
              </div>
            </div>
            <div class="flex justify-between mt-2 text-xs text-gray-400">
              <span>{{ trends[0]?.date?.slice(5) }}</span>
              <span>{{ trends[trends.length - 1]?.date?.slice(5) }}</span>
            </div>
          </template>
        </div>

        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">观看时段分布</h2>
          <div class="space-y-4">
            <div v-for="(data, key) in timeDistribution" :key="key" class="flex items-center">
              <div class="w-24 text-sm text-gray-600 dark:text-gray-400">{{ data.label }}</div>
              <div class="flex-1 mx-3 h-6 bg-gray-100 dark:bg-dark-100 rounded-lg overflow-hidden relative">
                <div 
                  class="h-full rounded-lg transition-all"
                  :class="getTimeColor(key)"
                  :style="{ width: `${maxTimeCount > 0 ? (data.count / maxTimeCount) * 100 : 0}%` }"
                ></div>
                <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-gray-600 dark:text-gray-300">{{ data.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 星期分布 + 类型分布 -->
      <div class="grid md:grid-cols-2 gap-6 mb-6">
        <div class="card p-6 flex flex-col">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">星期分布</h2>
          <div v-if="totalWeekdayCount === 0" class="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
          <template v-else>
            <div class="flex-1 flex items-end justify-between min-h-[120px]">
              <div
                v-for="day in weekdayStats"
                :key="day.name"
                class="flex flex-col items-center flex-1 h-full justify-end"
              >
                <div
                  class="w-8 rounded-t bg-blue-500 transition-all hover:bg-blue-600 min-h-[4px]"
                  :style="{ height: day.count > 0 ? `${Math.max((day.count / maxWeekdayCount) * 100, 12)}px` : '4px' }"
                ></div>
              </div>
            </div>
            <div class="flex justify-between mt-2">
              <div
                v-for="day in weekdayStats"
                :key="day.name + '-label'"
                class="flex flex-col items-center flex-1"
              >
                <span class="text-xs text-gray-500">{{ day.name }}</span>
                <span class="text-xs text-gray-400">{{ day.count }}</span>
              </div>
            </div>
          </template>
        </div>

        <div class="card p-6 flex flex-col">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">类型分布</h2>
          <div v-if="Object.keys(genreStats).length === 0" class="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
            暂无数据
          </div>
          <div v-else class="flex-1 flex flex-col justify-center space-y-2 overflow-y-auto max-h-[200px]">
            <div v-for="(count, genre, index) in topGenres" :key="genre" class="flex items-center">
              <span class="w-16 text-xs text-gray-600 dark:text-gray-400 truncate">{{ genre }}</span>
              <div class="flex-1 mx-2 h-4 bg-gray-100 dark:bg-dark-100 rounded overflow-hidden relative">
                <div
                  class="h-full rounded transition-all"
                  :class="getGenreColor(index)"
                  :style="{ width: `${(count / maxGenreCount) * 100}%` }"
                ></div>
              </div>
              <span class="text-xs text-gray-500 w-8 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 评分分布 -->
      <div class="card p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">评分分布</h2>
        </div>
        <div v-if="totalRatings === 0" class="h-32 flex flex-col items-center justify-center text-gray-500 dark:text-gray-400">
          <span>暂无评分数据</span>
          <p v-if="ratingMeta.no_rating_count > 0" class="text-xs mt-2">
            {{ ratingMeta.no_rating_count }} 部影片无评分数据
          </p>
        </div>
        <template v-else>
          <div class="flex items-end justify-between h-28">
            <div 
              v-for="(count, rating) in ratingStats" 
              :key="rating"
              class="flex flex-col items-center flex-1"
            >
              <div 
                class="w-10 rounded-t bg-gradient-to-t from-yellow-500 to-orange-400 transition-all hover:opacity-80 min-h-[4px]"
                :style="{ height: count > 0 ? `${Math.max((count / maxRatingCount) * 100, 12)}px` : '4px' }"
              ></div>
            </div>
          </div>
          <div class="flex justify-between mt-2">
            <div 
              v-for="(count, rating) in ratingStats" 
              :key="rating + '-label'"
              class="flex flex-col items-center flex-1"
            >
              <span class="text-xs text-gray-500">{{ rating }}</span>
              <span class="text-xs text-gray-400">{{ count }}</span>
            </div>
          </div>
        </template>
        <p v-if="ratingMeta.no_rating_count > 0 && totalRatings > 0" class="text-xs text-gray-400 mt-3 text-center">
          另有 {{ ratingMeta.no_rating_count }} 部影片无评分数据
        </p>
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
const ratingMeta = ref({ no_rating_count: 0 })
const recentWatched = ref([])
const recentType = ref('all')

// 新增统计数据
const streak = ref({ current_streak: 0, longest_streak: 0, total_watch_days: 0 })
const trends = ref([])
const heatmap = ref([])
const timeDistribution = ref({})
const weekdayStats = ref([])

// 计算属性
// 限制显示前8个类型，保持布局一致
const topGenres = computed(() => {
  const entries = Object.entries(genreStats.value)
  entries.sort((a, b) => b[1] - a[1])
  return Object.fromEntries(entries.slice(0, 8))
})
const maxGenreCount = computed(() => Math.max(...Object.values(genreStats.value), 1))
const maxRatingCount = computed(() => Math.max(...Object.values(ratingStats.value), 1))
const totalRatings = computed(() => Object.values(ratingStats.value).reduce((a, b) => a + b, 0))
const maxTrendCount = computed(() => Math.max(...trends.value.map(t => t.total), 1))
const totalTrendCount = computed(() => trends.value.reduce((a, b) => a + b.total, 0))
const maxTimeCount = computed(() => Math.max(...Object.values(timeDistribution.value).map(t => t.count), 1))
const maxWeekdayCount = computed(() => Math.max(...weekdayStats.value.map(d => d.count), 1))
const totalWeekdayCount = computed(() => weekdayStats.value.reduce((a, b) => a + b.count, 0))

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

const getTimeColor = (key) => {
  const colors = {
    morning: 'bg-yellow-400',
    afternoon: 'bg-orange-400',
    evening: 'bg-purple-500',
    night: 'bg-indigo-600',
  }
  return colors[key] || 'bg-gray-400'
}

const getHeatmapColor = (level) => {
  const colors = [
    'bg-gray-100 dark:bg-dark-100',
    'bg-green-200 dark:bg-green-900/50',
    'bg-green-400 dark:bg-green-700',
    'bg-green-500 dark:bg-green-600',
    'bg-green-600 dark:bg-green-500',
  ]
  return colors[level] || colors[0]
}

const getHeatmapRow = (weekday) => {
  return heatmap.value.filter(d => d.weekday === weekday)
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
  const userId = appStore.currentEmbyUser.Id
  
  try {
    const [overviewData, genres, ratings, streakData, trendsData, heatmapData, timeData, weekdayData] = await Promise.all([
      statsApi.getOverview(userId, libraryIds),
      statsApi.getGenreStats(userId, libraryIds, mediaType),
      statsApi.getRatingStats(userId, libraryIds, mediaType),
      statsApi.getStreak(userId),
      statsApi.getTrends(userId, 30),
      statsApi.getHeatmap(userId, 12),
      statsApi.getTimeDistribution(userId),
      statsApi.getWeekdayStats(userId),
    ])
    
    overview.value = overviewData
    genreStats.value = genres.genres || {}
    ratingStats.value = ratings.ratings || {}
    ratingMeta.value = {
      no_rating_count: ratings.no_rating_count || 0,
    }
    streak.value = streakData
    trends.value = trendsData.trends || []
    heatmap.value = heatmapData.heatmap || []
    timeDistribution.value = timeData.distribution || {}
    weekdayStats.value = weekdayData.weekdays || []
    
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
