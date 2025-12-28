<template>
  <div>
    <!-- Hero 轮播 -->
    <HeroSlider v-if="heroSlides.length > 0" :items="heroSlides" :is-custom="true" />
    <HeroSlider v-else-if="recentlyAdded.length > 0" :items="recentlyAdded.slice(0, 5)" />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      <!-- 当前正在观看 (Check-in) -->
      <section v-if="currentCheckin" class="relative">
        <div class="card p-6 bg-gradient-to-r from-primary-500/10 to-purple-500/10 border-2 border-primary-500/30">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="relative">
                <div class="w-16 h-24 rounded-lg overflow-hidden bg-gray-200 dark:bg-dark-100">
                  <img 
                    v-if="currentCheckin.poster_path"
                    :src="getCheckinPoster(currentCheckin)"
                    class="w-full h-full object-cover"
                  />
                </div>
                <div class="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                  </svg>
                </div>
              </div>
              <div>
                <p class="text-sm text-primary-600 dark:text-primary-400 font-medium">正在观看</p>
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ currentCheckin.series_name || currentCheckin.title }}
                </h3>
                <p v-if="currentCheckin.series_name" class="text-sm text-gray-500 dark:text-gray-400">
                  S{{ currentCheckin.season_number }}E{{ currentCheckin.episode_number }} · {{ currentCheckin.title }}
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  开始于 {{ formatCheckinTime(currentCheckin.started_at) }}
                </p>
              </div>
            </div>
            <button 
              @click="endCurrentCheckin"
              class="btn btn-secondary flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
              </svg>
              <span>结束观看</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 媒体库概览 -->
      <section v-if="appStore.allowedLibraries.length > 0">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">媒体库</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <router-link
            v-for="library in appStore.allowedLibraries"
            :key="library.id"
            :to="`/library/${library.id}`"
            class="card p-6 hover:shadow-lg transition-all duration-300 group"
          >
            <div class="flex items-center space-x-4">
              <div 
                class="w-14 h-14 rounded-xl flex items-center justify-center transition-colors"
                :class="getLibraryIconClass(library)"
              >
                <svg v-if="library.collection_type === 'movies'" class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
                </svg>
                <svg v-else-if="library.collection_type === 'tvshows'" class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                <svg v-else class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-900 dark:text-white group-hover:text-primary-500 transition-colors">
                  {{ library.name }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ libraryItemCounts[library.id] || library.item_count || 0 }} 项
                </p>
              </div>
            </div>
          </router-link>
        </div>
      </section>

      <!-- 最近添加 -->
      <MediaGrid 
        title="最近添加"
        :items="recentlyAdded"
        :loading="loading"
        empty-text="暂无最近添加的内容"
        :skeleton-count="6"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { embyApi, heroApi, checkinApi } from '../api'
import HeroSlider from '../components/HeroSlider.vue'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const loading = ref(true)
const recentlyAdded = ref([])
const heroSlides = ref([])
const libraryItemCounts = reactive({})
const currentCheckin = ref(null)

const getLibraryIconClass = (library) => {
  if (library.collection_type === 'movies') {
    return 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50'
  }
  if (library.collection_type === 'tvshows') {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50'
  }
  return 'bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400 group-hover:bg-gray-200 dark:group-hover:bg-gray-900/50'
}

const getCheckinPoster = (checkin) => {
  if (checkin.poster_path) {
    if (checkin.poster_path.startsWith('http')) return checkin.poster_path
    return `https://image.tmdb.org/t/p/w200${checkin.poster_path}`
  }
  if (checkin.emby_id) {
    return appStore.getEmbyImageUrl(checkin.emby_id, 'Primary', 200)
  }
  return ''
}

const formatCheckinTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins} 分钟前`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} 小时前`
  return date.toLocaleDateString('zh-CN')
}

const fetchCurrentCheckin = async () => {
  if (!appStore.currentEmbyUser) return
  try {
    const result = await checkinApi.getCurrent(appStore.currentEmbyUser.Id)
    currentCheckin.value = result.checkin
  } catch (e) {
    console.error('Failed to fetch current checkin:', e)
  }
}

const endCurrentCheckin = async () => {
  if (!appStore.currentEmbyUser || !currentCheckin.value) return
  try {
    await checkinApi.end(appStore.currentEmbyUser.Id, currentCheckin.value.id)
    currentCheckin.value = null
  } catch (e) {
    console.error('Failed to end checkin:', e)
  }
}

const fetchLibraryItemCounts = async () => {
  if (!appStore.currentEmbyUser) return
  
  for (const library of appStore.allowedLibraries) {
    try {
      const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
        parent_id: library.id,
        limit: 1,
      })
      libraryItemCounts[library.id] = result.total_count
    } catch (e) {
      console.error(`Failed to fetch count for library ${library.id}:`, e)
    }
  }
}

const fetchData = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    // 获取当前 Check-in
    await fetchCurrentCheckin()
    
    // 先获取自定义轮播
    try {
      const customSlides = await heroApi.getSlides(true)
      heroSlides.value = customSlides
    } catch (e) {
      heroSlides.value = []
    }
    
    const recent = await embyApi.getRecentlyAdded(appStore.currentEmbyUser.Id, 20)
    recentlyAdded.value = recent
    
    // 获取每个媒体库的实际项目数量
    await fetchLibraryItemCounts()
  } catch (e) {
    console.error('Failed to fetch home data:', e)
  } finally {
    loading.value = false
  }
}

watch(() => appStore.currentEmbyUser, fetchData)
watch(() => appStore.allowedLibraries, fetchLibraryItemCounts)

onMounted(fetchData)
</script>
