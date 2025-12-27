<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-400 transition-colors duration-300">
    <!-- 登录页面不显示导航 -->
    <template v-if="$route.path !== '/login'">
      <!-- 导航栏 -->
      <nav class="sticky top-0 z-50 bg-white/80 dark:bg-dark-300/80 backdrop-blur-lg border-b border-gray-200 dark:border-dark-100">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Logo -->
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                </svg>
              </div>
              <span class="text-xl font-bold text-gradient">Emby Tracker</span>
            </router-link>

            <!-- 导航链接 -->
            <div class="hidden md:flex items-center space-x-1">
              <!-- 首页 -->
              <router-link 
                to="/"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="isActiveLink('/') 
                  ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
              >
                首页
              </router-link>

              <!-- 电影 -->
              <template v-if="appStore.movieLibraries.length > 1">
                <div class="relative group">
                  <button class="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100 flex items-center">
                    电影
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                  </button>
                  <div class="absolute left-0 mt-1 w-48 bg-white dark:bg-dark-200 rounded-xl shadow-lg border border-gray-100 dark:border-dark-100 py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <router-link 
                      v-for="lib in appStore.movieLibraries"
                      :key="lib.id"
                      :to="`/library/${lib.id}`"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-100"
                    >
                      {{ lib.name }}
                    </router-link>
                  </div>
                </div>
              </template>
              <template v-else-if="appStore.movieLibraries.length === 1">
                <router-link 
                  :to="`/library/${appStore.movieLibraries[0].id}`"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="isActiveLink(`/library/${appStore.movieLibraries[0].id}`) 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
                >
                  电影
                </router-link>
              </template>
              <template v-else>
                <router-link 
                  to="/movies"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="isActiveLink('/movies') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
                >
                  电影
                </router-link>
              </template>

              <!-- 剧集 -->
              <template v-if="appStore.tvLibraries.length > 1">
                <div class="relative group">
                  <button class="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100 flex items-center">
                    剧集
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                  </button>
                  <div class="absolute left-0 mt-1 w-48 bg-white dark:bg-dark-200 rounded-xl shadow-lg border border-gray-100 dark:border-dark-100 py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <router-link 
                      v-for="lib in appStore.tvLibraries"
                      :key="lib.id"
                      :to="`/library/${lib.id}`"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-100"
                    >
                      {{ lib.name }}
                    </router-link>
                  </div>
                </div>
              </template>
              <template v-else-if="appStore.tvLibraries.length === 1">
                <router-link 
                  :to="`/library/${appStore.tvLibraries[0].id}`"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="isActiveLink(`/library/${appStore.tvLibraries[0].id}`) 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
                >
                  剧集
                </router-link>
              </template>
              <template v-else>
                <router-link 
                  to="/shows"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="isActiveLink('/shows') 
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
                >
                  剧集
                </router-link>
              </template>

              <!-- 发现、想看、统计 -->
              <router-link 
                to="/discover"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="isActiveLink('/discover') 
                  ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
              >
                发现
              </router-link>
              <router-link 
                to="/watchlist"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="isActiveLink('/watchlist') 
                  ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
              >
                想看
              </router-link>
              <router-link 
                to="/stats"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="isActiveLink('/stats') 
                  ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-100'"
              >
                统计
              </router-link>
            </div>

            <!-- 右侧操作 -->
            <div class="flex items-center space-x-4">
              <!-- 搜索 -->
              <router-link to="/search" class="btn-ghost p-2 rounded-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </router-link>

              <!-- 设置 -->
              <router-link to="/settings" class="btn-ghost p-2 rounded-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </router-link>

              <!-- 深色模式切换 -->
              <button @click="appStore.toggleDarkMode()" class="btn-ghost p-2 rounded-lg">
                <svg v-if="appStore.darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
                </svg>
                <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- 移动端底部导航 -->
      <nav class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/80 dark:bg-dark-300/80 backdrop-blur-lg border-t border-gray-200 dark:border-dark-100">
        <div class="flex items-center justify-around h-16">
          <router-link 
            v-for="link in mobileNavLinks" 
            :key="link.path"
            :to="link.path"
            class="flex flex-col items-center justify-center w-16 h-full"
            :class="isActiveLink(link.path) 
              ? 'text-primary-500' 
              : 'text-gray-400'"
          >
            <component :is="link.icon" class="w-6 h-6" />
            <span class="text-xs mt-1">{{ link.name }}</span>
          </router-link>
        </div>
      </nav>
    </template>

    <!-- 主内容 -->
    <main :class="{ 'pb-20 md:pb-0': $route.path !== '/login' }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 错误提示 -->
    <div 
      v-if="appStore.error"
      class="fixed bottom-24 md:bottom-8 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-3 rounded-xl shadow-lg z-50"
    >
      {{ appStore.error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from './stores/app'

const route = useRoute()
const appStore = useAppStore()

const navLinks = computed(() => {
  // 固定顺序：首页、电影、剧集、发现、想看、统计
  const links = [
    { name: '首页', path: '/' },
  ]
  
  // 电影 - 如果只有一个电影库，直接链接；否则显示下拉菜单（在模板中处理）
  if (appStore.movieLibraries.length === 1) {
    links.push({ name: '电影', path: `/library/${appStore.movieLibraries[0].id}` })
  } else if (appStore.movieLibraries.length === 0) {
    // 没有电影库时也显示，但链接到空页面
    links.push({ name: '电影', path: '/movies' })
  }
  // 多个电影库时不在这里添加，由下拉菜单处理
  
  // 剧集 - 同上
  if (appStore.tvLibraries.length === 1) {
    links.push({ name: '剧集', path: `/library/${appStore.tvLibraries[0].id}` })
  } else if (appStore.tvLibraries.length === 0) {
    links.push({ name: '剧集', path: '/shows' })
  }
  
  links.push(
    { name: '发现', path: '/discover' },
    { name: '想看', path: '/watchlist' },
    { name: '统计', path: '/stats' },
  )
  
  return links
})

const isActiveLink = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

// 图标组件
const HomeIcon = { render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' })]) }
const MovieIcon = { render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z' })]) }
const HeartIcon = { render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' })]) }
const ChartIcon = { render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })]) }
const SettingsIcon = { render: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }), h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' })]) }

const mobileNavLinks = [
  { name: '首页', path: '/', icon: HomeIcon },
  { name: '媒体库', path: '/movies', icon: MovieIcon },
  { name: '想看', path: '/watchlist', icon: HeartIcon },
  { name: '统计', path: '/stats', icon: ChartIcon },
  { name: '设置', path: '/settings', icon: SettingsIcon },
]

onMounted(() => {
  appStore.init()
})
</script>
