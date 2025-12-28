<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题和控制 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">日历</h1>
      
      <div class="flex items-center space-x-4">
        <!-- 视图切换 -->
        <div class="flex items-center space-x-2">
          <button 
            @click="viewMode = 'week'"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="viewMode === 'week' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
          >周视图</button>
          <button 
            @click="viewMode = 'month'"
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            :class="viewMode === 'month' ? 'bg-primary-500 text-white' : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
          >月视图</button>
        </div>
        
        <!-- 类型筛选 -->
        <select v-model="filterType" class="input w-auto text-sm py-1.5">
          <option value="all">全部</option>
          <option value="my-shows">我的追剧</option>
          <option value="shows">所有剧集</option>
          <option value="movies">电影</option>
        </select>
        
        <!-- iCal 导出 -->
        <a 
          v-if="appStore.currentEmbyUser"
          :href="calendarApi.exportIcal(appStore.currentEmbyUser.Id)"
          target="_blank"
          class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg bg-gray-100 dark:bg-dark-100 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors"
        >
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          导出 iCal
        </a>
      </div>
    </div>

    <!-- 日期导航 -->
    <div class="flex items-center justify-between mb-6">
      <button @click="navigatePrev" class="btn-secondary">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      
      <div class="text-center">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
          {{ currentPeriodLabel }}
        </h2>
        <button @click="goToToday" class="text-sm text-primary-500 hover:text-primary-600 mt-1">
          返回今天
        </button>
      </div>
      
      <button @click="navigateNext" class="btn-secondary">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 周视图 -->
    <div v-else-if="viewMode === 'week'" class="space-y-4">
      <div 
        v-for="day in weekDays" 
        :key="day.date"
        class="card overflow-hidden"
        :class="{ 'ring-2 ring-primary-500': isToday(day.date) }"
      >
        <!-- 日期标题 -->
        <div 
          class="px-4 py-3 border-b border-gray-100 dark:border-dark-100"
          :class="isToday(day.date) ? 'bg-primary-50 dark:bg-primary-900/20' : 'bg-gray-50 dark:bg-dark-200'"
        >
          <div class="flex items-center justify-between">
            <div>
              <span class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ formatDayName(day.date) }}
              </span>
              <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(day.date) }}
              </span>
            </div>
            <span 
              v-if="isToday(day.date)" 
              class="px-2 py-0.5 text-xs font-medium bg-primary-500 text-white rounded-full"
            >
              今天
            </span>
          </div>
        </div>
        
        <!-- 当天内容 -->
        <div v-if="day.items.length > 0" class="divide-y divide-gray-100 dark:divide-dark-100">
          <CalendarItem 
            v-for="item in day.items" 
            :key="`${item.type}-${item.id}`"
            :item="item"
            @click="goToDetail(item)"
          />
        </div>
        <div v-else class="px-4 py-8 text-center text-gray-400 dark:text-gray-500">
          暂无内容
        </div>
      </div>
    </div>

    <!-- 月视图 -->
    <div v-else class="card overflow-hidden">
      <!-- 星期标题 -->
      <div class="grid grid-cols-7 border-b border-gray-100 dark:border-dark-100">
        <div 
          v-for="day in ['一', '二', '三', '四', '五', '六', '日']" 
          :key="day"
          class="py-3 text-center text-sm font-medium text-gray-500 dark:text-gray-400"
        >
          {{ day }}
        </div>
      </div>
      
      <!-- 日期格子 -->
      <div class="grid grid-cols-7">
        <div 
          v-for="(day, index) in monthDays" 
          :key="index"
          class="min-h-[120px] border-b border-r border-gray-100 dark:border-dark-100 p-2"
          :class="{
            'bg-gray-50 dark:bg-dark-200': !day.isCurrentMonth,
            'bg-primary-50 dark:bg-primary-900/20': isToday(day.date) && day.isCurrentMonth,
          }"
        >
          <div class="flex items-center justify-between mb-2">
            <span 
              class="text-sm font-medium"
              :class="{
                'text-gray-400 dark:text-gray-600': !day.isCurrentMonth,
                'text-primary-600 dark:text-primary-400': isToday(day.date) && day.isCurrentMonth,
                'text-gray-900 dark:text-white': day.isCurrentMonth && !isToday(day.date),
              }"
            >
              {{ day.dayNumber }}
            </span>
            <span 
              v-if="day.items.length > 0" 
              class="text-xs text-gray-400"
            >
              {{ day.items.length }}
            </span>
          </div>
          
          <!-- 当天内容（最多显示3个） -->
          <div class="space-y-1">
            <div 
              v-for="item in day.items.slice(0, 3)" 
              :key="`${item.type}-${item.id}`"
              @click="goToDetail(item)"
              class="text-xs p-1 rounded truncate cursor-pointer transition-colors"
              :class="item.type === 'movie' 
                ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/50' 
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50'"
            >
              {{ item.title }}
            </div>
            <div 
              v-if="day.items.length > 3" 
              class="text-xs text-gray-400 text-center"
            >
              +{{ day.items.length - 3 }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { calendarApi } from '../api'
import CalendarItem from '../components/CalendarItem.vue'

const router = useRouter()
const appStore = useAppStore()

const loading = ref(true)
const viewMode = ref('week')
const filterType = ref('all')
const currentDate = ref(new Date())
const calendarData = ref([])

// 计算当前周的日期范围
const getWeekRange = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1) // 周一开始
  const start = new Date(d.setDate(diff))
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  return { start, end }
}

// 计算当前月的日期范围
const getMonthRange = (date) => {
  const start = new Date(date.getFullYear(), date.getMonth(), 1)
  const end = new Date(date.getFullYear(), date.getMonth() + 1, 0)
  return { start, end }
}

// 格式化日期为 YYYY-MM-DD
const formatDateStr = (date) => {
  return date.toISOString().split('T')[0]
}

// 当前周期标签
const currentPeriodLabel = computed(() => {
  if (viewMode.value === 'week') {
    const { start, end } = getWeekRange(currentDate.value)
    return `${start.getMonth() + 1}月${start.getDate()}日 - ${end.getMonth() + 1}月${end.getDate()}日`
  } else {
    return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月`
  }
})

// 周视图数据
const weekDays = computed(() => {
  const { start } = getWeekRange(currentDate.value)
  const days = []
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(start)
    date.setDate(date.getDate() + i)
    const dateStr = formatDateStr(date)
    
    days.push({
      date: dateStr,
      items: calendarData.value.filter(item => item.date === dateStr),
    })
  }
  
  return days
})

// 月视图数据
const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  // 当月第一天
  const firstDay = new Date(year, month, 1)
  // 当月最后一天
  const lastDay = new Date(year, month + 1, 0)
  
  // 第一天是周几（0=周日，转换为周一开始）
  let startDayOfWeek = firstDay.getDay()
  startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1
  
  const days = []
  
  // 上月的日期
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month, -i)
    const dateStr = formatDateStr(date)
    days.push({
      date: dateStr,
      dayNumber: date.getDate(),
      isCurrentMonth: false,
      items: calendarData.value.filter(item => item.date === dateStr),
    })
  }
  
  // 当月的日期
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    const dateStr = formatDateStr(date)
    days.push({
      date: dateStr,
      dayNumber: i,
      isCurrentMonth: true,
      items: calendarData.value.filter(item => item.date === dateStr),
    })
  }
  
  // 下月的日期（补齐到42天，6行）
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const date = new Date(year, month + 1, i)
    const dateStr = formatDateStr(date)
    days.push({
      date: dateStr,
      dayNumber: i,
      isCurrentMonth: false,
      items: calendarData.value.filter(item => item.date === dateStr),
    })
  }
  
  return days
})

// 判断是否是今天
const isToday = (dateStr) => {
  return dateStr === formatDateStr(new Date())
}

// 格式化星期名称
const formatDayName = (dateStr) => {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days[new Date(dateStr).getDay()]
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 导航到上一周/月
const navigatePrev = () => {
  if (viewMode.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 7))
  } else {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1))
  }
  fetchCalendar()
}

// 导航到下一周/月
const navigateNext = () => {
  if (viewMode.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 7))
  } else {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1))
  }
  fetchCalendar()
}

// 返回今天
const goToToday = () => {
  currentDate.value = new Date()
  fetchCalendar()
}

// 跳转到详情页
const goToDetail = (item) => {
  if (item.type === 'movie') {
    router.push(`/tmdb/movie/${item.id}`)
  } else {
    router.push(`/tmdb/tv/${item.id}`)
  }
}

// 获取日历数据
const fetchCalendar = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  
  try {
    let range
    if (viewMode.value === 'week') {
      range = getWeekRange(currentDate.value)
    } else {
      range = getMonthRange(currentDate.value)
      // 月视图需要扩展范围以包含上下月的部分日期
      range.start.setDate(range.start.getDate() - 7)
      range.end.setDate(range.end.getDate() + 7)
    }
    
    const startDate = formatDateStr(range.start)
    const endDate = formatDateStr(range.end)
    const userId = appStore.currentEmbyUser.Id
    
    let result
    if (filterType.value === 'my-shows') {
      result = await calendarApi.getMyShowsCalendar(startDate, endDate, userId)
    } else if (filterType.value === 'shows') {
      result = await calendarApi.getShowsCalendar(startDate, endDate, userId)
    } else if (filterType.value === 'movies') {
      result = await calendarApi.getMoviesCalendar(startDate, endDate)
    } else {
      result = await calendarApi.getAllCalendar(startDate, endDate, userId)
    }
    
    calendarData.value = result.items || []
  } catch (e) {
    console.error('获取日历数据失败:', e)
    calendarData.value = []
  } finally {
    loading.value = false
  }
}

// 监听视图模式和筛选类型变化
watch([viewMode, filterType], fetchCalendar)
watch(() => appStore.currentEmbyUser, fetchCalendar)

onMounted(fetchCalendar)
</script>
