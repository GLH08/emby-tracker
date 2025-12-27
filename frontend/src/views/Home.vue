<template>
  <div>
    <!-- Hero 轮播 -->
    <HeroSlider v-if="heroSlides.length > 0" :items="heroSlides" :is-custom="true" />
    <HeroSlider v-else-if="recentlyAdded.length > 0" :items="recentlyAdded.slice(0, 5)" />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
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
import { embyApi, heroApi } from '../api'
import HeroSlider from '../components/HeroSlider.vue'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const loading = ref(true)
const recentlyAdded = ref([])
const heroSlides = ref([])
const libraryItemCounts = reactive({})

const getLibraryIconClass = (library) => {
  if (library.collection_type === 'movies') {
    return 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50'
  }
  if (library.collection_type === 'tvshows') {
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50'
  }
  return 'bg-gray-100 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400 group-hover:bg-gray-200 dark:group-hover:bg-gray-900/50'
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
