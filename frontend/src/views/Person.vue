<template>
  <div v-if="loading" class="min-h-screen flex items-center justify-center">
    <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
  </div>

  <div v-else-if="person" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 人物信息 -->
    <div class="flex flex-col md:flex-row gap-8 mb-12">
      <!-- 头像 -->
      <div class="flex-shrink-0">
        <img 
          v-if="person.profile_path"
          :src="appStore.getTmdbImageUrl(person.profile_path, 'w300')"
          :alt="person.name"
          class="w-48 md:w-64 rounded-2xl shadow-xl mx-auto md:mx-0"
        />
        <div v-else class="w-48 md:w-64 aspect-[2/3] rounded-2xl bg-gray-200 dark:bg-dark-100 flex items-center justify-center mx-auto md:mx-0">
          <svg class="w-24 h-24 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <!-- 详细信息 -->
      <div class="flex-1">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
          {{ person.name }}
        </h1>

        <!-- 基本信息 -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div v-if="person.birthday">
            <p class="text-sm text-gray-500 dark:text-gray-400">出生日期</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatDate(person.birthday) }}</p>
          </div>
          <div v-if="person.place_of_birth">
            <p class="text-sm text-gray-500 dark:text-gray-400">出生地</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ person.place_of_birth }}</p>
          </div>
          <div v-if="person.known_for_department">
            <p class="text-sm text-gray-500 dark:text-gray-400">职业</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ translateDepartment(person.known_for_department) }}</p>
          </div>
          <div v-if="person.deathday">
            <p class="text-sm text-gray-500 dark:text-gray-400">逝世日期</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatDate(person.deathday) }}</p>
          </div>
        </div>

        <!-- 简介 -->
        <div v-if="person.biography" class="mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">简介</h2>
          <p 
            class="text-gray-600 dark:text-gray-400 leading-relaxed"
            :class="{ 'line-clamp-4': !showFullBio }"
          >
            {{ person.biography }}
          </p>
          <button 
            v-if="person.biography.length > 300"
            @click="showFullBio = !showFullBio"
            class="text-primary-500 hover:text-primary-600 text-sm mt-2"
          >
            {{ showFullBio ? '收起' : '展开全部' }}
          </button>
        </div>

        <!-- 外部链接 -->
        <div class="flex items-center space-x-4">
          <a 
            v-if="person.imdb_id"
            :href="`https://www.imdb.com/name/${person.imdb_id}`"
            target="_blank"
            class="btn btn-secondary"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14.31 9.588v.005c-.077-.048-.227-.07-.42-.07v4.815c.27 0 .44-.06.5-.165.062-.104.095-.405.095-.9v-2.953c0-.344-.013-.57-.04-.678-.027-.108-.075-.17-.135-.054zM22.416 0H1.62C.742.06.06.744 0 1.596V22.38c.06.876.744 1.56 1.596 1.62H22.38c.876-.06 1.56-.744 1.62-1.596V1.62C23.94.744 23.256.06 22.404 0zM4.792 15.626H2.887V8.26h1.905v7.366zm6.326 0H9.39l-.005-5.14c0-.073-.048-.11-.144-.11h-.18c-.096 0-.144.037-.144.11v5.14H7.19V8.26h2.332c.773 0 1.312.066 1.618.2.306.132.46.39.46.773v4.313c0 .383-.154.64-.46.773-.306.133-.845.2-1.618.2h-.404v1.107zm5.472-1.834c0 .505-.065.862-.196 1.07-.13.21-.37.315-.72.315-.18 0-.34-.03-.48-.09-.14-.06-.26-.15-.36-.27v.27h-1.71V8.26h1.71v2.494c.1-.12.22-.21.36-.27.14-.06.3-.09.48-.09.35 0 .59.105.72.315.13.21.196.565.196 1.07v2.013zm4.863-.09c0 .465-.06.79-.18.975-.12.185-.33.277-.63.277-.18 0-.34-.03-.48-.09-.14-.06-.26-.15-.36-.27v.27h-1.71V8.26h1.71v2.494c.1-.12.22-.21.36-.27.14-.06.3-.09.48-.09.3 0 .51.092.63.277.12.185.18.51.18.975v2.056z"/>
            </svg>
            IMDb
          </a>
          <a 
            :href="`https://www.themoviedb.org/person/${person.id}`"
            target="_blank"
            class="btn btn-secondary"
          >
            TMDB
          </a>
        </div>
      </div>
    </div>

    <!-- 参演作品 -->
    <section v-if="credits.length > 0">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">参演作品</h2>
        <div class="flex items-center space-x-2">
          <button 
            @click="creditFilter = 'all'"
            class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            :class="creditFilter === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
          >
            全部
          </button>
          <button 
            @click="creditFilter = 'movie'"
            class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            :class="creditFilter === 'movie' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
          >
            电影
          </button>
          <button 
            @click="creditFilter = 'tv'"
            class="px-3 py-1 rounded-lg text-sm font-medium transition-colors"
            :class="creditFilter === 'tv' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
          >
            剧集
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        <div 
          v-for="credit in filteredCredits" 
          :key="`${credit.media_type}-${credit.id}`"
          class="card overflow-hidden group cursor-pointer"
          @click="goToDetail(credit)"
        >
          <div class="relative aspect-[2/3] bg-gray-200 dark:bg-dark-100">
            <img 
              v-if="credit.poster_path"
              :src="appStore.getTmdbImageUrl(credit.poster_path, 'w342')"
              :alt="credit.title || credit.name"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            
            <!-- 评分 -->
            <div 
              v-if="credit.vote_average"
              class="absolute top-2 left-2 px-2 py-1 bg-black/70 rounded-lg flex items-center space-x-1"
            >
              <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="text-white text-sm font-medium">{{ credit.vote_average.toFixed(1) }}</span>
            </div>

            <!-- 类型标签 -->
            <span 
              class="absolute top-2 right-2 badge"
              :class="credit.media_type === 'movie' ? 'badge-primary' : 'badge-warning'"
            >
              {{ credit.media_type === 'movie' ? '电影' : '剧集' }}
            </span>
          </div>
          
          <div class="p-3">
            <h3 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-500 transition-colors">
              {{ credit.title || credit.name }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ credit.character || credit.job || '未知角色' }}
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
              {{ getYear(credit) }}
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { tmdbApi } from '../api'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const loading = ref(true)
const person = ref(null)
const showFullBio = ref(false)
const creditFilter = ref('all')

const credits = computed(() => {
  if (!person.value?.combined_credits) return []
  
  const cast = (person.value.combined_credits.cast || []).map(c => ({
    ...c,
    credit_type: 'cast'
  }))
  const crew = (person.value.combined_credits.crew || []).map(c => ({
    ...c,
    credit_type: 'crew'
  }))
  
  // 合并并去重
  const all = [...cast, ...crew]
  const unique = all.reduce((acc, curr) => {
    const key = `${curr.media_type}-${curr.id}`
    if (!acc[key] || (curr.vote_count > acc[key].vote_count)) {
      acc[key] = curr
    }
    return acc
  }, {})
  
  // 按评分和年份排序
  return Object.values(unique).sort((a, b) => {
    const scoreA = a.vote_average || 0
    const scoreB = b.vote_average || 0
    return scoreB - scoreA
  })
})

const filteredCredits = computed(() => {
  if (creditFilter.value === 'all') return credits.value
  return credits.value.filter(c => c.media_type === creditFilter.value)
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

const translateDepartment = (dept) => {
  const map = {
    'Acting': '演员',
    'Directing': '导演',
    'Writing': '编剧',
    'Production': '制片',
    'Camera': '摄影',
    'Editing': '剪辑',
    'Sound': '音效',
    'Art': '美术',
    'Costume & Make-Up': '服装化妆',
    'Crew': '剧组',
    'Visual Effects': '视觉特效',
    'Lighting': '灯光',
  }
  return map[dept] || dept
}

const getYear = (credit) => {
  const date = credit.release_date || credit.first_air_date
  return date ? date.split('-')[0] : ''
}

const goToDetail = (credit) => {
  // TMDB 内容暂时无法跳转到本地详情页
  // 可以跳转到 TMDB 网站
  const type = credit.media_type === 'movie' ? 'movie' : 'tv'
  window.open(`https://www.themoviedb.org/${type}/${credit.id}`, '_blank')
}

const fetchPerson = async () => {
  loading.value = true
  try {
    person.value = await tmdbApi.getPerson(route.params.id)
  } catch (e) {
    console.error('Failed to fetch person:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchPerson)
</script>
