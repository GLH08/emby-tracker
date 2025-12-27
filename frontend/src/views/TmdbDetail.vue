<template>
  <div class="min-h-screen">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <template v-else-if="detail">
      <!-- 背景图 -->
      <div class="relative h-[50vh] overflow-hidden">
        <img 
          v-if="backdropUrl"
          :src="backdropUrl"
          :alt="detail.title || detail.name"
          class="w-full h-full object-cover"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-transparent"></div>
      </div>

      <!-- 内容 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-48 relative z-10 pb-12">
        <div class="flex flex-col md:flex-row gap-8">
          <!-- 海报 -->
          <div class="flex-shrink-0 w-64 mx-auto md:mx-0">
            <div class="aspect-[2/3] rounded-xl overflow-hidden shadow-2xl">
              <img 
                v-if="posterUrl"
                :src="posterUrl"
                :alt="detail.title || detail.name"
                class="w-full h-full object-cover"
              />
            </div>
          </div>

          <!-- 信息 -->
          <div class="flex-1 text-white">
            <h1 class="text-4xl font-bold mb-2">{{ detail.title || detail.name }}</h1>
            <p v-if="detail.tagline" class="text-xl text-gray-300 italic mb-4">{{ detail.tagline }}</p>
            
            <div class="flex flex-wrap items-center gap-4 mb-6">
              <span v-if="year" class="text-gray-300">{{ year }}</span>
              <span v-if="runtime" class="text-gray-300">{{ runtime }}</span>
              <div v-if="detail.vote_average" class="flex items-center space-x-1">
                <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="font-medium">{{ detail.vote_average.toFixed(1) }}</span>
              </div>
            </div>

            <!-- 类型 -->
            <div v-if="detail.genres?.length" class="flex flex-wrap gap-2 mb-6">
              <span 
                v-for="genre in detail.genres" 
                :key="genre.id"
                class="px-3 py-1 bg-white/10 rounded-full text-sm"
              >
                {{ genre.name }}
              </span>
            </div>

            <!-- 简介 -->
            <div v-if="detail.overview" class="mb-8">
              <h2 class="text-xl font-semibold mb-3">简介</h2>
              <p class="text-gray-300 leading-relaxed">{{ detail.overview }}</p>
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-wrap gap-4">
              <button @click="addToWatchlist" class="btn btn-primary" :disabled="inWatchlist">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                {{ inWatchlist ? '已在想看列表' : '加入想看' }}
              </button>
              <a 
                :href="tmdbUrl"
                target="_blank"
                class="btn btn-secondary"
              >
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
                在 TMDB 查看
              </a>
              <a 
                v-if="detail.homepage"
                :href="detail.homepage"
                target="_blank"
                class="btn btn-secondary"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                官方网站
              </a>
            </div>
          </div>
        </div>

        <!-- 演员表 -->
        <div v-if="detail.credits?.cast?.length" class="mt-12">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">演员表</h2>
          <div class="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide">
            <div 
              v-for="person in detail.credits.cast.slice(0, 20)" 
              :key="person.id"
              class="flex-shrink-0 w-32"
            >
              <div class="aspect-[2/3] rounded-lg overflow-hidden bg-gray-200 dark:bg-dark-100 mb-2">
                <img 
                  v-if="person.profile_path"
                  :src="getProfileUrl(person.profile_path)"
                  :alt="person.name"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                </div>
              </div>
              <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ person.name }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ person.character }}</p>
            </div>
          </div>
        </div>

        <!-- 剧集季列表 -->
        <div v-if="type === 'tv' && detail.seasons?.length" class="mt-12">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">季</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div 
              v-for="season in detail.seasons" 
              :key="season.id"
              class="card overflow-hidden"
            >
              <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100">
                <img 
                  v-if="season.poster_path"
                  :src="getSeasonPosterUrl(season.poster_path)"
                  :alt="season.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="p-3">
                <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ season.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ season.episode_count }} 集</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 相似推荐 -->
        <div v-if="detail.similar?.results?.length" class="mt-12">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">相似推荐</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <router-link 
              v-for="item in detail.similar.results.slice(0, 12)" 
              :key="item.id"
              :to="`/tmdb/${type}/${item.id}`"
              class="card overflow-hidden hover:shadow-lg transition-shadow"
            >
              <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100">
                <img 
                  v-if="item.poster_path"
                  :src="getSimilarPosterUrl(item.poster_path)"
                  :alt="item.title || item.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="p-3">
                <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ item.title || item.name }}</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { tmdbApi, watchlistApi } from '../api'

const props = defineProps({
  id: { type: String, required: true },
  type: { type: String, required: true },
})

const route = useRoute()
const appStore = useAppStore()
const loading = ref(true)
const detail = ref(null)
const inWatchlist = ref(false)

const backdropUrl = computed(() => {
  if (!detail.value?.backdrop_path) return ''
  return appStore.getTmdbImageUrl(detail.value.backdrop_path, 'w1280')
})

const posterUrl = computed(() => {
  if (!detail.value?.poster_path) return ''
  return appStore.getTmdbImageUrl(detail.value.poster_path, 'w500')
})

const year = computed(() => {
  const date = detail.value?.release_date || detail.value?.first_air_date
  return date ? date.split('-')[0] : ''
})

const runtime = computed(() => {
  if (props.type === 'movie' && detail.value?.runtime) {
    const hours = Math.floor(detail.value.runtime / 60)
    const mins = detail.value.runtime % 60
    return hours > 0 ? `${hours}小时${mins}分钟` : `${mins}分钟`
  }
  if (props.type === 'tv' && detail.value?.number_of_seasons) {
    return `${detail.value.number_of_seasons} 季`
  }
  return ''
})

const tmdbUrl = computed(() => {
  return `https://www.themoviedb.org/${props.type}/${props.id}`
})

const getProfileUrl = (path) => appStore.getTmdbImageUrl(path, 'w185')
const getSeasonPosterUrl = (path) => appStore.getTmdbImageUrl(path, 'w342')
const getSimilarPosterUrl = (path) => appStore.getTmdbImageUrl(path, 'w342')

const fetchDetail = async () => {
  loading.value = true
  try {
    if (props.type === 'movie') {
      detail.value = await tmdbApi.getMovie(props.id)
    } else {
      detail.value = await tmdbApi.getTvShow(props.id)
    }
    // 检查是否在想看列表
    try {
      const result = await watchlistApi.checkInWatchlist({ tmdb_id: props.id, media_type: props.type })
      inWatchlist.value = result.in_watchlist
    } catch (e) {
      // 忽略错误
    }
  } catch (e) {
    console.error('Failed to fetch detail:', e)
  } finally {
    loading.value = false
  }
}

const addToWatchlist = async () => {
  if (inWatchlist.value) return
  try {
    await watchlistApi.addToWatchlist({
      tmdb_id: parseInt(props.id),
      media_type: props.type,
      title: detail.value.title || detail.value.name,
      poster_path: detail.value.poster_path,
      release_date: detail.value.release_date || detail.value.first_air_date,
      vote_average: detail.value.vote_average,
    })
    inWatchlist.value = true
  } catch (e) {
    console.error('Failed to add to watchlist:', e)
  }
}

watch(() => props.id, fetchDetail)
onMounted(fetchDetail)
</script>
