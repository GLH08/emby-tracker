<template>
  <div class="masonry-wall" ref="containerRef">
    <!-- 加载状态 -->
    <div v-if="loading" class="masonry-container">
      <div 
        v-for="i in 20" 
        :key="i"
        class="masonry-item animate-pulse"
      >
        <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100 rounded-xl"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="items.length === 0" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">{{ emptyText }}</p>
    </div>

    <!-- 瀑布流布局 -->
    <div v-else class="masonry-container">
      <router-link
        v-for="item in items"
        :key="item.id"
        :to="getDetailLink(item)"
        class="masonry-item group"
      >
        <!-- 海报 -->
        <div class="relative overflow-hidden rounded-xl bg-gray-200 dark:bg-dark-100">
          <img 
            v-if="getPosterUrl(item)"
            :src="getPosterUrl(item)"
            :alt="item.name || item.title"
            class="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
            @load="onImageLoad"
          />
          <div v-else class="aspect-[2/3] flex items-center justify-center text-gray-400">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>

          <!-- 渐变遮罩 -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

          <!-- 已观看标记 -->
          <div 
            v-if="item.played"
            class="absolute top-2 right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center shadow-lg"
          >
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          </div>

          <!-- 评分 -->
          <div 
            v-if="getRating(item)"
            class="absolute top-2 left-2 px-2 py-1 bg-black/70 rounded-lg flex items-center space-x-1"
          >
            <svg class="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span class="text-white text-xs font-medium">{{ getRating(item).toFixed(1) }}</span>
          </div>

          <!-- 悬停信息 -->
          <div class="absolute bottom-0 left-0 right-0 p-3 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
            <h3 class="text-white font-medium text-sm line-clamp-2 drop-shadow-lg">
              {{ item.name || item.title }}
            </h3>
            <p v-if="getYear(item)" class="text-gray-300 text-xs mt-1">
              {{ getYear(item) }}
            </p>
          </div>
        </div>
      </router-link>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="mt-8 text-center">
      <button 
        @click="$emit('load-more')"
        class="btn btn-secondary"
        :disabled="loadingMore"
      >
        <svg 
          v-if="loadingMore"
          class="animate-spin -ml-1 mr-2 h-4 w-4" 
          fill="none" 
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  loadingMore: Boolean,
  hasMore: Boolean,
  emptyText: {
    type: String,
    default: '暂无内容'
  },
  source: {
    type: String,
    default: 'emby' // emby or tmdb
  }
})

defineEmits(['load-more'])

const appStore = useAppStore()
const containerRef = ref(null)

const getPosterUrl = (item) => {
  if (props.source === 'tmdb') {
    return item.poster_path 
      ? appStore.getTmdbImageUrl(item.poster_path, 'w342')
      : ''
  }
  return item.primary_image_tag 
    ? appStore.getEmbyImageUrl(item.id, 'Primary', 342)
    : ''
}

const getRating = (item) => {
  if (props.source === 'tmdb') {
    return item.vote_average
  }
  return item.community_rating
}

const getYear = (item) => {
  if (props.source === 'tmdb') {
    const date = item.release_date || item.first_air_date
    return date ? date.split('-')[0] : ''
  }
  return item.year || ''
}

const getDetailLink = (item) => {
  if (props.source === 'tmdb') {
    const type = item.media_type === 'tv' ? 'tv' : 'movie'
    return `/tmdb/${type}/${item.id}`
  }
  const type = item.type === 'Series' ? 'show' : 'movie'
  return `/${type}/${item.id}`
}

const onImageLoad = () => {
  // 图片加载完成后可以触发重新布局（如果需要）
}
</script>

<style scoped>
.masonry-wall {
  @apply w-full;
}

/* CSS Columns 实现瀑布流 */
.masonry-container {
  column-count: 5;
  column-gap: 1rem;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 1rem;
  display: block;
}

/* 响应式列数 */
@media (max-width: 1536px) {
  .masonry-container {
    column-count: 5;
  }
}

@media (max-width: 1280px) {
  .masonry-container {
    column-count: 4;
  }
}

@media (max-width: 1024px) {
  .masonry-container {
    column-count: 3;
  }
}

@media (max-width: 768px) {
  .masonry-container {
    column-count: 3;
    column-gap: 0.75rem;
  }
  
  .masonry-item {
    margin-bottom: 0.75rem;
  }
}

@media (max-width: 480px) {
  .masonry-container {
    column-count: 2;
    column-gap: 0.5rem;
  }
  
  .masonry-item {
    margin-bottom: 0.5rem;
  }
}
</style>
