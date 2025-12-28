<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">追剧进度</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">追踪你正在观看的剧集</p>
      </div>
      
      <!-- 统计概览 -->
      <div class="flex items-center space-x-4 sm:space-x-6 text-sm">
        <div class="text-center px-3 py-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
          <div class="text-xl sm:text-2xl font-bold text-primary-500">{{ stats.watching_shows }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">正在追</div>
        </div>
        <div class="text-center px-3 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div class="text-xl sm:text-2xl font-bold text-green-500">{{ stats.episodes_watched }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">已看集数</div>
        </div>
        <div class="text-center px-3 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div class="text-xl sm:text-2xl font-bold text-blue-500">{{ stats.episodes_this_week }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">本周观看</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="shows.length === 0" class="text-center py-20">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="text-gray-500 dark:text-gray-400">暂无追剧记录</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">开始观看剧集后，进度会自动同步到这里</p>
    </div>

    <!-- 剧集列表 -->
    <div v-else class="space-y-4">
      <div 
        v-for="show in shows" 
        :key="show.series_id"
        class="card overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
        @click="toggleExpand(show.series_id)"
      >
        <div class="flex">
          <!-- 海报 -->
          <div class="w-24 sm:w-32 flex-shrink-0">
            <img 
              v-if="show.poster_path"
              :src="getEmbyImage(show.series_id, show.poster_path)"
              :alt="show.series_name"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full bg-gray-100 dark:bg-dark-100 flex items-center justify-center min-h-[144px]">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
              </svg>
            </div>
          </div>
          
          <!-- 信息 -->
          <div class="flex-1 p-4">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ show.series_name }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  已看 {{ show.watched_episodes }} / {{ show.total_episodes }} 集
                </p>
              </div>
              
              <!-- 进度百分比 -->
              <div class="text-right">
                <span 
                  class="text-2xl font-bold"
                  :class="show.progress >= 100 ? 'text-green-500' : 'text-primary-500'"
                >
                  {{ show.progress }}%
                </span>
                <span 
                  v-if="show.progress >= 100"
                  class="block text-xs text-green-500 mt-1"
                >
                  已完成
                </span>
              </div>
            </div>
            
            <!-- 进度条 -->
            <div class="mt-3">
              <div class="h-2 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full transition-all duration-500"
                  :class="show.progress >= 100 ? 'bg-green-500' : 'bg-primary-500'"
                  :style="{ width: `${Math.min(show.progress, 100)}%` }"
                ></div>
              </div>
            </div>
            
            <!-- 下一集提示 -->
            <div v-if="show.next_episode" class="mt-3 flex items-center text-sm">
              <span class="text-gray-500 dark:text-gray-400">下一集：</span>
              <span class="ml-2 text-gray-900 dark:text-white">
                S{{ String(show.next_episode.season_number).padStart(2, '0') }}E{{ String(show.next_episode.episode_number).padStart(2, '0') }}
                <span v-if="show.next_episode.episode_name"> - {{ show.next_episode.episode_name }}</span>
              </span>
            </div>
            <div v-else-if="show.progress >= 100" class="mt-3 text-sm text-green-500">
              🎉 恭喜！已全部看完
            </div>
            
            <!-- 最后观看时间 -->
            <div v-if="show.last_watched" class="mt-2 text-xs text-gray-400">
              最后观看：{{ formatDate(show.last_watched) }}
            </div>
          </div>
          
          <!-- 展开箭头 -->
          <div class="flex items-center px-4">
            <svg 
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedShow === show.series_id }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        
        <!-- 展开的季进度 -->
        <div 
          v-if="expandedShow === show.series_id"
          class="border-t border-gray-100 dark:border-dark-100 bg-gray-50 dark:bg-dark-200 p-4"
        >
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="season in show.seasons" 
              :key="season.season_id"
              class="bg-white dark:bg-dark-300 rounded-lg p-3"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-gray-900 dark:text-white">
                  {{ season.season_name }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ season.watched_episodes }}/{{ season.total_episodes }}
                </span>
              </div>
              <div class="h-1.5 bg-gray-100 dark:bg-dark-100 rounded-full overflow-hidden">
                <div 
                  class="h-full rounded-full"
                  :class="season.progress >= 100 ? 'bg-green-500' : 'bg-primary-500'"
                  :style="{ width: `${Math.min(season.progress, 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- 查看详情按钮 -->
          <div class="mt-4 text-center">
            <router-link 
              :to="`/show/${show.series_id}`"
              class="text-primary-500 hover:text-primary-600 text-sm"
              @click.stop
            >
              查看详情 →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { progressApi } from '../api'

const appStore = useAppStore()

const loading = ref(true)
const shows = ref([])
const stats = ref({
  watching_shows: 0,
  episodes_watched: 0,
  episodes_this_week: 0,
})
const expandedShow = ref(null)

const getEmbyImage = (itemId, imageTag) => {
  if (!imageTag) return null
  return `${appStore.embyUrl}/Items/${itemId}/Images/Primary?tag=${imageTag}&quality=90&maxWidth=200`
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const toggleExpand = (seriesId) => {
  expandedShow.value = expandedShow.value === seriesId ? null : seriesId
}

const fetchData = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  
  try {
    const userId = appStore.currentEmbyUser.Id
    
    // 并行获取数据
    const [progressResult, statsResult] = await Promise.all([
      progressApi.getShowsProgress(userId),
      progressApi.getProgressStats(userId),
    ])
    
    // 处理返回数据 - 兼容不同的数据结构
    if (progressResult && typeof progressResult === 'object') {
      shows.value = Array.isArray(progressResult) ? progressResult : (progressResult.shows || [])
    } else {
      shows.value = []
    }
    
    stats.value = statsResult || { watching_shows: 0, episodes_watched: 0, episodes_this_week: 0 }
  } catch (e) {
    console.error('获取进度数据失败:', e)
    shows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
