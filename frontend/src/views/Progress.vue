<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">追剧进度</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">追踪你正在观看的剧集</p>
      </div>
      
      <div class="flex items-center gap-2">
        <!-- 清理重复按钮 -->
        <button 
          @click="cleanupDuplicates"
          class="btn btn-secondary text-sm flex items-center space-x-1"
          :disabled="cleaning"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          <span>{{ cleaning ? '清理中...' : '清理重复' }}</span>
        </button>
        
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
    </div>

    <!-- 清理结果提示 -->
    <div v-if="cleanupResult" class="mb-6 p-4 rounded-xl" :class="cleanupResult.deleted_count > 0 ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'">
      {{ cleanupResult.message }}
      <span v-if="cleanupResult.deleted_count > 0">（{{ cleanupResult.deleted_count }} 条记录）</span>
      <button @click="cleanupResult = null" class="ml-2 hover:opacity-70">×</button>
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
        
        <!-- 展开的每集详情 -->
        <div 
          v-if="expandedShow === show.series_id"
          class="border-t border-gray-100 dark:border-dark-100 bg-gray-50 dark:bg-dark-200"
        >
          <div class="divide-y divide-gray-100 dark:divide-dark-100">
            <template v-for="season in show.seasons" :key="season.season_id">
              <!-- 季标题 -->
              <div class="px-4 py-3 bg-gray-100 dark:bg-dark-300 sticky top-0">
                <div class="flex items-center justify-between">
                  <span class="font-medium text-gray-900 dark:text-white">{{ season.season_name }}</span>
                  <span class="text-sm text-gray-500">
                    {{ season.watched_episodes }}/{{ season.total_episodes }} 集
                    <span class="ml-2" :class="season.progress >= 100 ? 'text-green-500' : 'text-primary-500'">
                      {{ season.progress }}%
                    </span>
                  </span>
                </div>
              </div>
              
              <!-- 每集列表 -->
              <div 
                v-for="ep in season.episodes" 
                :key="ep.episode_id"
                class="flex items-center px-4 py-3 hover:bg-white dark:hover:bg-dark-300 transition-colors"
              >
                <!-- 集数 -->
                <div class="w-12 flex-shrink-0">
                  <span class="text-sm font-medium text-gray-500 dark:text-gray-400">
                    E{{ String(ep.episode_number).padStart(2, '0') }}
                  </span>
                </div>
                
                <!-- 集名称 -->
                <div class="flex-1 min-w-0 mr-4">
                  <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {{ ep.episode_name || `第 ${ep.episode_number} 集` }}
                  </p>
                </div>
                
                <!-- 观看状态/进度 -->
                <div class="flex items-center space-x-2">
                  <!-- 进度条（有进度但未完成） -->
                  <div v-if="!ep.is_watched && ep.progress_percent > 0" class="flex items-center space-x-2">
                    <div class="w-16 h-1.5 bg-gray-200 dark:bg-dark-100 rounded-full overflow-hidden">
                      <div class="h-full bg-primary-500 rounded-full" :style="{ width: `${ep.progress_percent}%` }"></div>
                    </div>
                    <span class="text-xs text-primary-500 w-10">{{ Math.round(ep.progress_percent) }}%</span>
                  </div>
                  
                  <!-- 已看标记 -->
                  <div 
                    v-if="ep.is_watched"
                    class="flex items-center space-x-1 text-green-500"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    <span class="text-xs">已看</span>
                  </div>
                  
                  <!-- 未看标记 -->
                  <div 
                    v-if="!ep.is_watched && ep.progress_percent === 0"
                    class="text-xs text-gray-400"
                  >
                    未看
                  </div>
                </div>
              </div>
            </template>
          </div>
          
          <!-- 查看详情按钮 -->
          <div class="p-4 text-center border-t border-gray-100 dark:border-dark-100">
            <router-link 
              :to="`/show/${show.series_id}`"
              class="text-primary-500 hover:text-primary-600 text-sm"
              @click.stop
            >
              查看完整详情 →
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
const cleaning = ref(false)
const cleanupResult = ref(null)

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

const cleanupDuplicates = async () => {
  if (!appStore.currentEmbyUser || cleaning.value) return
  
  // 先预览
  cleaning.value = true
  try {
    const preview = await progressApi.cleanupDuplicates(appStore.currentEmbyUser.Id, true)
    
    if (preview.duplicates.length === 0) {
      cleanupResult.value = { message: '没有发现重复的剧集记录', deleted_count: 0 }
      return
    }
    
    // 确认删除
    const confirmMsg = `发现 ${preview.duplicates.length} 部剧集有重复记录，共 ${preview.deleted_count} 条。是否清理？`
    if (confirm(confirmMsg)) {
      const result = await progressApi.cleanupDuplicates(appStore.currentEmbyUser.Id, false)
      cleanupResult.value = result
      // 刷新数据
      await fetchData()
    } else {
      cleanupResult.value = { message: '已取消清理', deleted_count: 0 }
    }
  } catch (e) {
    console.error('清理重复记录失败:', e)
    cleanupResult.value = { message: '清理失败: ' + e.message, deleted_count: 0 }
  } finally {
    cleaning.value = false
  }
}

onMounted(fetchData)
</script>
