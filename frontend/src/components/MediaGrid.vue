<template>
  <div>
    <!-- 标题栏 -->
    <div v-if="title" class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ title }}</h2>
      <router-link 
        v-if="moreLink"
        :to="moreLink"
        class="text-primary-500 hover:text-primary-600 text-sm font-medium flex items-center space-x-1"
      >
        <span>查看更多</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </router-link>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <div 
        v-for="i in skeletonCount" 
        :key="i"
        class="animate-pulse"
      >
        <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100 rounded-xl"></div>
        <div class="mt-3 h-4 bg-gray-200 dark:bg-dark-100 rounded w-3/4"></div>
        <div class="mt-2 h-3 bg-gray-200 dark:bg-dark-100 rounded w-1/2"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div 
      v-else-if="items.length === 0"
      class="text-center py-16"
    >
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">{{ emptyText }}</p>
    </div>

    <!-- 媒体网格 -->
    <div 
      v-else
      class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
    >
      <MediaCard 
        v-for="item in items" 
        :key="item.id"
        :item="item"
        :media-type="mediaType"
        :source="source"
      />
    </div>

    <!-- 加载更多 -->
    <div 
      v-if="hasMore && !loading"
      class="mt-8 text-center"
    >
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
import MediaCard from './MediaCard.vue'

defineProps({
  title: String,
  items: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  loadingMore: Boolean,
  hasMore: Boolean,
  moreLink: String,
  emptyText: {
    type: String,
    default: '暂无内容',
  },
  skeletonCount: {
    type: Number,
    default: 12,
  },
  mediaType: String,
  source: {
    type: String,
    default: 'emby',
  },
})

defineEmits(['load-more'])
</script>
