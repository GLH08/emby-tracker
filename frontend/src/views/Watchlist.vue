<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">想看列表</h1>

    <!-- 筛选 -->
    <div class="flex items-center space-x-4 mb-6">
      <button 
        @click="filter = ''"
        class="btn"
        :class="filter === '' ? 'btn-primary' : 'btn-secondary'"
      >
        全部
      </button>
      <button 
        @click="filter = 'movie'"
        class="btn"
        :class="filter === 'movie' ? 'btn-primary' : 'btn-secondary'"
      >
        电影
      </button>
      <button 
        @click="filter = 'tv'"
        class="btn"
        :class="filter === 'tv' ? 'btn-primary' : 'btn-secondary'"
      >
        剧集
      </button>
    </div>

    <!-- 列表 -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <div v-for="i in 12" :key="i" class="animate-pulse">
        <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100 rounded-xl"></div>
        <div class="mt-3 h-4 bg-gray-200 dark:bg-dark-100 rounded w-3/4"></div>
      </div>
    </div>

    <div v-else-if="filteredItems.length === 0" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">想看列表为空</p>
      <router-link to="/discover" class="btn btn-primary mt-4">
        去发现
      </router-link>
    </div>

    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <div 
        v-for="item in filteredItems" 
        :key="item.id"
        class="group relative"
      >
        <router-link :to="`/tmdb/${item.media_type}/${item.tmdb_id}`" class="card overflow-hidden block">
          <div class="relative aspect-[2/3] bg-gray-200 dark:bg-dark-100">
            <img 
              v-if="item.poster_path"
              :src="appStore.getTmdbImageUrl(item.poster_path, 'w342')"
              :alt="item.title"
              class="w-full h-full object-cover"
            />
            
            <!-- 删除按钮 -->
            <button 
              @click.prevent="removeItem(item)"
              class="absolute top-2 right-2 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>

            <!-- 类型标签 -->
            <span 
              class="absolute bottom-2 left-2 badge"
              :class="item.media_type === 'movie' ? 'badge-primary' : 'badge-warning'"
            >
              {{ item.media_type === 'movie' ? '电影' : '剧集' }}
            </span>
          </div>
          
          <div class="p-3">
            <h3 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-500 transition-colors">{{ item.title }}</h3>
            <div class="flex items-center justify-between mt-1">
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ item.release_date?.split('-')[0] }}
              </span>
              <span v-if="item.vote_average" class="flex items-center space-x-1 text-sm">
                <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="text-gray-600 dark:text-gray-400">{{ item.vote_average.toFixed(1) }}</span>
              </span>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { watchlistApi } from '../api'

const appStore = useAppStore()
const loading = ref(true)
const items = ref([])
const filter = ref('')

const filteredItems = computed(() => {
  if (!filter.value) return items.value
  return items.value.filter(item => item.media_type === filter.value)
})

const fetchWatchlist = async () => {
  loading.value = true
  try {
    items.value = await watchlistApi.getWatchlist()
  } catch (e) {
    console.error('Failed to fetch watchlist:', e)
  } finally {
    loading.value = false
  }
}

const removeItem = async (item) => {
  if (!confirm('确定要从想看列表中移除吗？')) return
  
  try {
    await watchlistApi.removeFromWatchlist(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e) {
    console.error('Failed to remove item:', e)
  }
}

onMounted(fetchWatchlist)
</script>
