<template>
  <router-link 
    :to="detailLink"
    class="group block"
  >
    <div class="card overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <!-- 海报 -->
      <div class="relative aspect-[2/3] bg-gray-200 dark:bg-dark-100 overflow-hidden">
        <img 
          v-if="posterUrl"
          :src="posterUrl"
          :alt="item.name || item.title"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
          <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>

        <!-- 已观看标记 -->
        <div 
          v-if="item.played"
          class="absolute top-2 right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg"
        >
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
        </div>

        <!-- 观看进度 -->
        <div 
          v-if="progress > 0 && progress < 100"
          class="absolute bottom-0 left-0 right-0 h-1 bg-gray-800/50"
        >
          <div 
            class="h-full bg-primary-500"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>

        <!-- 评分区域 -->
        <div class="absolute top-2 left-2 flex flex-col gap-1">
          <!-- 原有评分 (TMDB/Emby) -->
          <div 
            v-if="rating"
            class="px-2 py-1 bg-black/70 rounded-lg flex items-center space-x-1"
          >
            <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span class="text-white text-sm font-medium">{{ rating.toFixed(1) }}</span>
          </div>
          
          <!-- IMDB 评分 (如果启用且有缓存) -->
          <div 
            v-if="showImdbRating && imdbRating"
            class="px-2 py-1 bg-yellow-500/90 rounded-lg flex items-center space-x-1"
            title="IMDB 评分"
          >
            <span class="text-xs font-bold text-black">IMDb</span>
            <span class="text-black text-sm font-medium">{{ imdbRating.toFixed(1) }}</span>
          </div>
        </div>
      </div>

      <!-- 信息 -->
      <div class="p-3">
        <h3 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-500 transition-colors">
          {{ item.name || item.title }}
        </h3>
        <div class="flex items-center justify-between mt-1">
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ year }}
          </span>
          <span 
            v-if="item.type === 'Series' || mediaType === 'tv'"
            class="badge badge-primary"
          >
            剧集
          </span>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  mediaType: {
    type: String,
    default: '',
  },
  source: {
    type: String,
    default: 'emby', // emby or tmdb
  },
})

const appStore = useAppStore()

const posterUrl = computed(() => {
  if (props.source === 'tmdb') {
    return props.item.poster_path 
      ? appStore.getTmdbImageUrl(props.item.poster_path, 'w342')
      : ''
  }
  return props.item.primary_image_tag 
    ? appStore.getEmbyImageUrl(props.item.id, 'Primary', 342)
    : ''
})

const rating = computed(() => {
  if (props.source === 'tmdb') {
    return props.item.vote_average
  }
  return props.item.community_rating
})

const year = computed(() => {
  if (props.source === 'tmdb') {
    const date = props.item.release_date || props.item.first_air_date
    return date ? date.split('-')[0] : ''
  }
  return props.item.year || ''
})

const progress = computed(() => {
  if (!props.item.runtime_ticks || !props.item.playback_position_ticks) return 0
  return (props.item.playback_position_ticks / props.item.runtime_ticks) * 100
})

const detailLink = computed(() => {
  if (props.source === 'tmdb') {
    // TMDB 来源的内容跳转到 TMDB 详情页
    const type = props.item.media_type === 'tv' || props.mediaType === 'tv' ? 'tv' : 'movie'
    return `/tmdb/${type}/${props.item.id}`
  }
  const type = props.item.type === 'Series' || props.mediaType === 'tv' ? 'show' : 'movie'
  return `/${type}/${props.item.id}`
})

// IMDB 评分相关
const showImdbRating = computed(() => appStore.showExternalRatings)

const imdbRating = computed(() => {
  if (!appStore.showExternalRatings) return null
  
  // 从 item 的 provider_ids 获取 IMDB ID 或 TMDB ID
  const imdbId = props.item.provider_ids?.Imdb
  const tmdbId = props.item.provider_ids?.Tmdb || props.item.id
  
  // 从全局缓存获取评分
  return appStore.getExternalRating(imdbId, props.source === 'tmdb' ? props.item.id : tmdbId)
})
</script>
