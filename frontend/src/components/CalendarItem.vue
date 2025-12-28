<template>
  <div 
    class="flex items-center p-4 hover:bg-gray-50 dark:hover:bg-dark-100 cursor-pointer transition-colors"
    @click="$emit('click')"
  >
    <!-- 海报 -->
    <div class="w-12 h-16 rounded overflow-hidden flex-shrink-0 bg-gray-100 dark:bg-dark-100">
      <img 
        v-if="posterUrl"
        :src="posterUrl" 
        :alt="item.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
        </svg>
      </div>
    </div>
    
    <!-- 信息 -->
    <div class="ml-4 flex-1 min-w-0">
      <div class="flex items-center space-x-2">
        <!-- 类型标签 -->
        <span 
          class="px-2 py-0.5 text-xs font-medium rounded"
          :class="item.type === 'movie' 
            ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300' 
            : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'"
        >
          {{ item.type === 'movie' ? '电影' : '剧集' }}
        </span>
        
        <!-- 追剧标记 -->
        <span 
          v-if="item.is_watching"
          class="px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded"
        >
          追剧中
        </span>
        
        <!-- 想看标记 -->
        <span 
          v-if="item.in_watchlist"
          class="px-2 py-0.5 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded"
        >
          想看
        </span>
      </div>
      
      <!-- 标题 -->
      <h3 class="font-medium text-gray-900 dark:text-white mt-1 truncate">
        {{ item.title }}
      </h3>
      
      <!-- 剧集信息 -->
      <p v-if="item.type === 'episode'" class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
        S{{ String(item.season_number).padStart(2, '0') }}E{{ String(item.episode_number).padStart(2, '0') }}
        <span v-if="item.episode_title"> - {{ item.episode_title }}</span>
      </p>
      
      <!-- 简介 -->
      <p 
        v-if="item.overview" 
        class="text-sm text-gray-400 dark:text-gray-500 mt-1 line-clamp-2"
      >
        {{ item.overview }}
      </p>
    </div>
    
    <!-- 评分 -->
    <div v-if="item.vote_average" class="ml-4 flex-shrink-0 text-right">
      <div class="flex items-center text-yellow-500">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
        <span class="ml-1 text-sm font-medium">{{ item.vote_average.toFixed(1) }}</span>
      </div>
    </div>
    
    <!-- 箭头 -->
    <svg class="w-5 h-5 text-gray-400 ml-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

defineEmits(['click'])

const appStore = useAppStore()

const posterUrl = computed(() => {
  if (props.item.poster_path) {
    return `${appStore.tmdbImageBaseUrl}/w92${props.item.poster_path}`
  }
  return null
})
</script>
