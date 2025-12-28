<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900">
    <!-- 年份选择器 -->
    <div class="sticky top-0 z-10 bg-black/30 backdrop-blur-lg border-b border-white/10">
      <div class="max-w-4xl mx-auto px-4 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 class="text-2xl font-bold text-white">年度回顾</h1>
        <select 
          v-model="selectedYear" 
          @change="fetchReview"
          class="bg-white/10 text-white border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full sm:w-auto"
        >
          <option v-for="y in availableYears" :key="y" :value="y">{{ y }} 年</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="animate-spin w-12 h-12 border-4 border-purple-400 border-t-transparent rounded-full"></div>
    </div>

    <div v-else-if="!review || review.summary.total_items === 0" class="flex flex-col items-center justify-center min-h-[60vh] text-white/60">
      <svg class="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="text-xl">{{ selectedYear }} 年暂无观看记录</p>
    </div>

    <div v-else class="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <!-- 总览卡片 -->
      <section class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-2xl sm:text-3xl font-bold mb-6 text-center">{{ selectedYear }} 年观影总结</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 text-center">
          <div>
            <div class="text-3xl sm:text-4xl font-bold text-purple-300">{{ review.summary.total_movies }}</div>
            <div class="text-white/60 mt-1 text-sm sm:text-base">部电影</div>
          </div>
          <div>
            <div class="text-3xl sm:text-4xl font-bold text-blue-300">{{ review.summary.total_episodes }}</div>
            <div class="text-white/60 mt-1 text-sm sm:text-base">集剧集</div>
          </div>
          <div>
            <div class="text-3xl sm:text-4xl font-bold text-green-300">{{ review.summary.total_watch_time_hours }}</div>
            <div class="text-white/60 mt-1 text-sm sm:text-base">小时</div>
          </div>
          <div>
            <div class="text-3xl sm:text-4xl font-bold text-yellow-300">{{ review.summary.watch_days }}</div>
            <div class="text-white/60 mt-1 text-sm sm:text-base">天有观看</div>
          </div>
        </div>
        
        <div class="mt-6 sm:mt-8 pt-6 border-t border-white/10 text-center">
          <p class="text-white/80 text-sm sm:text-base">
            相当于 <span class="text-xl sm:text-2xl font-bold text-purple-300">{{ review.summary.total_watch_time_days }}</span> 天不间断观看
          </p>
          <p class="text-white/60 mt-2 text-sm">
            平均每天观看 {{ review.summary.average_per_day }} 部作品
          </p>
        </div>
      </section>

      <!-- 里程碑 -->
      <section v-if="review.milestones.length > 0" class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">🏆</span> 达成里程碑
        </h2>
        <div class="flex flex-wrap gap-2 sm:gap-3">
          <div 
            v-for="milestone in review.milestones" 
            :key="milestone.label"
            class="px-3 sm:px-4 py-1.5 sm:py-2 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-full text-yellow-200 text-sm sm:text-base"
          >
            {{ milestone.label }}
          </div>
        </div>
      </section>

      <!-- 最爱类型 -->
      <section v-if="review.top_genres.length > 0" class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">🎭</span> 最爱类型
        </h2>
        <div class="space-y-3 sm:space-y-4">
          <div v-for="(genre, index) in review.top_genres" :key="genre.name" class="flex items-center">
            <div class="w-6 sm:w-8 text-xl sm:text-2xl">{{ ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][index] }}</div>
            <div class="flex-1 ml-3 sm:ml-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-sm sm:text-base">{{ genre.name }}</span>
                <span class="text-white/60 text-sm">{{ genre.count }} 部</span>
              </div>
              <div class="h-2 bg-white/10 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                  :style="{ width: `${(genre.count / review.top_genres[0].count) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 看得最多的剧集 -->
      <section v-if="review.most_watched_series.length > 0" class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">📺</span> 最常追的剧
        </h2>
        <div class="space-y-2 sm:space-y-3">
          <div 
            v-for="(series, index) in review.most_watched_series" 
            :key="series.name"
            class="flex items-center justify-between p-3 sm:p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors"
          >
            <div class="flex items-center min-w-0">
              <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center font-bold mr-3 sm:mr-4 flex-shrink-0 text-sm sm:text-base">
                {{ index + 1 }}
              </div>
              <span class="font-medium truncate text-sm sm:text-base">{{ series.name }}</span>
            </div>
            <span class="text-white/60 ml-2 flex-shrink-0 text-sm">{{ series.count }} 集</span>
          </div>
        </div>
      </section>

      <!-- 高分电影 -->
      <section v-if="review.top_movies.length > 0" class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">🎬</span> 年度高分电影
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <div 
            v-for="movie in review.top_movies" 
            :key="movie.title"
            class="flex items-center p-3 sm:p-4 bg-white/5 rounded-xl"
          >
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center font-bold text-base sm:text-lg mr-3 sm:mr-4 flex-shrink-0">
              {{ movie.rating?.toFixed(1) }}
            </div>
            <div class="min-w-0">
              <div class="font-medium truncate text-sm sm:text-base">{{ movie.title }}</div>
              <div class="text-sm text-white/60">{{ movie.year }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 月度分布 -->
      <section class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">📊</span> 月度观看分布
        </h2>
        <div class="flex items-end justify-between h-40 sm:h-48 gap-1 sm:gap-2">
          <div 
            v-for="month in review.monthly_breakdown" 
            :key="month.month"
            class="flex-1 flex flex-col items-center"
          >
            <div 
              class="w-full bg-gradient-to-t from-purple-500 to-pink-500 rounded-t-lg transition-all duration-500 min-h-[4px]"
              :style="{ height: `${getMonthHeight(month.total)}%` }"
            ></div>
            <div class="text-[10px] sm:text-xs text-white/60 mt-1 sm:mt-2">{{ month.month }}月</div>
            <div class="text-[10px] sm:text-xs text-white/40">{{ month.total }}</div>
          </div>
        </div>
      </section>

      <!-- 观看习惯 -->
      <section class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">⏰</span> 观看习惯
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
          <div v-if="review.favorite_time" class="text-center p-4 sm:p-6 bg-white/5 rounded-2xl">
            <div class="text-3xl sm:text-4xl mb-2">{{ getTimeEmoji(review.favorite_time.slot) }}</div>
            <div class="font-medium text-sm sm:text-base">最爱时段</div>
            <div class="text-white/60 text-xs sm:text-sm mt-1">{{ review.favorite_time.label }}</div>
          </div>
          <div v-if="review.busiest_day" class="text-center p-4 sm:p-6 bg-white/5 rounded-2xl">
            <div class="text-3xl sm:text-4xl mb-2">🔥</div>
            <div class="font-medium text-sm sm:text-base">最忙的一天</div>
            <div class="text-white/60 text-xs sm:text-sm mt-1">{{ review.busiest_day.date }}</div>
            <div class="text-purple-300 text-xs sm:text-sm">看了 {{ review.busiest_day.count }} 部</div>
          </div>
          <div class="text-center p-4 sm:p-6 bg-white/5 rounded-2xl">
            <div class="text-3xl sm:text-4xl mb-2">🔥</div>
            <div class="font-medium text-sm sm:text-base">最长连续</div>
            <div class="text-white/60 text-xs sm:text-sm mt-1">{{ review.longest_streak }} 天</div>
          </div>
        </div>
      </section>

      <!-- 首尾作品 -->
      <section class="bg-white/10 backdrop-blur-lg rounded-3xl p-6 sm:p-8 text-white">
        <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center">
          <span class="mr-3">📅</span> 年度首尾
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div v-if="review.first_watch" class="p-4 sm:p-6 bg-white/5 rounded-2xl">
            <div class="text-sm text-white/60 mb-2">🎬 年度第一部</div>
            <div class="font-medium text-base sm:text-lg truncate">{{ review.first_watch.title }}</div>
            <div class="text-white/60 text-xs sm:text-sm mt-1">{{ review.first_watch.date }}</div>
          </div>
          <div v-if="review.last_watch" class="p-4 sm:p-6 bg-white/5 rounded-2xl">
            <div class="text-sm text-white/60 mb-2">🎬 年度最后一部</div>
            <div class="font-medium text-base sm:text-lg truncate">{{ review.last_watch.title }}</div>
            <div class="text-white/60 text-xs sm:text-sm mt-1">{{ review.last_watch.date }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { statsApi } from '../api'

const appStore = useAppStore()

const loading = ref(true)
const review = ref(null)
const selectedYear = ref(new Date().getFullYear())

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = currentYear; y >= currentYear - 5; y--) {
    years.push(y)
  }
  return years
})

const fetchReview = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    review.value = await statsApi.getYearlyReview(appStore.currentEmbyUser.Id, selectedYear.value)
  } catch (e) {
    console.error('Failed to fetch yearly review:', e)
  } finally {
    loading.value = false
  }
}

const getMonthHeight = (count) => {
  if (!review.value?.monthly_breakdown) return 0
  const max = Math.max(...review.value.monthly_breakdown.map(m => m.total))
  if (max === 0) return 0
  return Math.max((count / max) * 100, 4)
}

const getTimeEmoji = (slot) => {
  const emojis = {
    morning: '🌅',
    afternoon: '☀️',
    evening: '🌆',
    night: '🌙',
  }
  return emojis[slot] || '⏰'
}

onMounted(() => {
  fetchReview()
})
</script>
