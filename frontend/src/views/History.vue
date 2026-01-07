<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">观看历史</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">
          {{ totalCount }} 条记录 · {{ formatDuration(stats.total_minutes) }}
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <!-- 同步按钮 -->
        <button 
          @click="syncFromEmby" 
          class="btn btn-secondary flex items-center space-x-2"
          :disabled="syncing"
        >
          <svg 
            class="w-4 h-4" 
            :class="{ 'animate-spin': syncing }"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span class="hidden sm:inline">{{ syncing ? '同步中...' : '从 Emby 同步' }}</span>
          <span class="sm:hidden">{{ syncing ? '同步中' : '同步' }}</span>
        </button>
        
        <!-- 高级筛选按钮 -->
        <button 
          @click="showFilters = !showFilters"
          class="btn flex items-center space-x-2"
          :class="hasActiveFilters ? 'btn-primary' : 'btn-secondary'"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
          </svg>
          <span class="hidden sm:inline">高级筛选</span>
          <span class="sm:hidden">筛选</span>
          <span v-if="hasActiveFilters" class="px-1.5 py-0.5 bg-white/20 rounded text-xs">{{ activeFilterCount }}</span>
        </button>
        
        <!-- 手动添加 -->
        <button @click="showAddModal = true" class="btn btn-primary flex items-center space-x-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span class="hidden sm:inline">手动添加</span>
          <span class="sm:hidden">添加</span>
        </button>
      </div>
    </div>

    <!-- 高级筛选面板 -->
    <transition name="slide">
      <div v-if="showFilters" class="card p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 搜索 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">搜索标题</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="input w-full" 
              placeholder="输入关键词..."
              @keyup.enter="applyFilters"
            />
          </div>
          
          <!-- 类型 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">媒体类型</label>
            <select v-model="filters.mediaType" class="input w-full">
              <option value="all">全部类型</option>
              <option value="Movie">电影</option>
              <option value="Episode">剧集</option>
            </select>
          </div>
          
          <!-- 类型（Genre） -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">影片类型</label>
            <select v-model="filters.genre" class="input w-full">
              <option value="">全部</option>
              <option v-for="g in availableGenres" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          
          <!-- 观看状态 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">观看状态</label>
            <select v-model="filters.watched" class="input w-full">
              <option value="">全部</option>
              <option value="true">已看完</option>
              <option value="false">未看完</option>
            </select>
          </div>
          
          <!-- 年份范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">年份范围</label>
            <div class="flex items-center space-x-2">
              <input v-model.number="filters.yearFrom" type="number" class="input w-full" placeholder="从" min="1900" max="2030" />
              <span class="text-gray-400">-</span>
              <input v-model.number="filters.yearTo" type="number" class="input w-full" placeholder="到" min="1900" max="2030" />
            </div>
          </div>
          
          <!-- 评分范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">评分范围</label>
            <div class="flex items-center space-x-2">
              <input v-model.number="filters.ratingFrom" type="number" class="input w-full" placeholder="从" min="0" max="10" step="0.1" />
              <span class="text-gray-400">-</span>
              <input v-model.number="filters.ratingTo" type="number" class="input w-full" placeholder="到" min="0" max="10" step="0.1" />
            </div>
          </div>
          
          <!-- 观看日期范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">观看日期</label>
            <div class="flex items-center space-x-2">
              <input v-model="filters.dateFrom" type="date" class="input w-full" />
              <span class="text-gray-400">-</span>
              <input v-model="filters.dateTo" type="date" class="input w-full" />
            </div>
          </div>
          
          <!-- 排序 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">排序方式</label>
            <div class="flex items-center space-x-2">
              <select v-model="filters.sortBy" class="input flex-1">
                <option value="watched_at">观看时间</option>
                <option value="rating">评分</option>
                <option value="year">年份</option>
                <option value="runtime">时长</option>
                <option value="title">标题</option>
              </select>
              <button 
                @click="filters.sortOrder = filters.sortOrder === 'desc' ? 'asc' : 'desc'"
                class="btn btn-secondary p-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" :class="{ 'rotate-180': filters.sortOrder === 'asc' }">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 筛选操作按钮 -->
        <div class="flex items-center justify-end space-x-3 mt-4 pt-4 border-t border-gray-100 dark:border-dark-100">
          <button @click="resetFilters" class="btn btn-secondary">重置</button>
          <button @click="applyFilters" class="btn btn-primary">应用筛选</button>
        </div>
      </div>
    </transition>

    <!-- 当前筛选标签 -->
    <div v-if="hasActiveFilters && !showFilters" class="flex flex-wrap gap-2 mb-6">
      <span 
        v-for="tag in filterTags" 
        :key="tag.key"
        class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400"
      >
        {{ tag.label }}
        <button @click="removeFilter(tag.key)" class="ml-2 hover:text-primary-900">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </span>
      <button @click="resetFilters" class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
        清除全部
      </button>
    </div>

    <!-- 同步结果提示 -->
    <div v-if="syncResult" class="mb-6 p-4 rounded-xl bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400">
      同步完成：新增 {{ syncResult.added }} 条，更新 {{ syncResult.updated }} 条
      <button @click="syncResult = null" class="ml-2 text-green-500 hover:text-green-600">×</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="groupedHistory.length === 0" class="text-center py-20">
      <svg class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">暂无观看历史</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">点击"从 Emby 同步"按钮导入你的观看记录</p>
    </div>

    <!-- 按日期分组的历史记录 -->
    <div v-else class="space-y-8">
      <div v-for="group in groupedHistory" :key="group.date" class="space-y-4">
        <!-- 日期标题 -->
        <div class="flex items-center justify-between sticky top-16 bg-gray-50/95 dark:bg-dark-400/95 backdrop-blur-sm py-3 -mx-4 px-4 z-10">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <span class="text-lg font-bold text-primary-600 dark:text-primary-400">{{ group.day }}</span>
            </div>
            <div>
              <p class="font-semibold text-gray-900 dark:text-white">{{ group.weekday }} · {{ group.dateStr }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ group.items.length }} 项</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatDuration(group.totalMinutes) }}</p>
          </div>
        </div>

        <!-- 当天的观看记录 -->
        <div class="space-y-3 pl-2">
          <div 
            v-for="item in group.items" 
            :key="item.id"
            class="card p-4 flex items-center space-x-4 hover:shadow-lg transition-all group"
          >
            <!-- 海报 -->
            <router-link :to="getItemLink(item)" class="w-16 h-24 rounded-lg overflow-hidden bg-gray-200 dark:bg-dark-100 flex-shrink-0 relative">
              <img 
                :src="getItemPoster(item)" 
                :alt="getItemTitle(item)" 
                class="w-full h-full object-cover"
                loading="lazy"
                @error="handleImageError"
              />
              <div v-if="item.community_rating" class="absolute top-1 left-1 px-1.5 py-0.5 bg-black/70 rounded text-xs text-white flex items-center">
                <svg class="w-3 h-3 text-yellow-400 mr-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                {{ item.community_rating?.toFixed(1) }}
              </div>
            </router-link>

            <!-- 信息 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between">
                <router-link :to="getItemLink(item)" class="min-w-0 flex-1">
                  <h3 class="font-semibold text-gray-900 dark:text-white truncate group-hover:text-primary-500 transition-colors">
                    {{ getItemTitle(item) }}
                  </h3>
                  <p v-if="item.media_type === 'Episode'" class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                    S{{ item.season_number || '?' }}E{{ item.episode_number || '?' }} · {{ item.title }}
                  </p>
                  <p v-else class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                    {{ item.year }} · {{ item.genres?.slice(0, 2).join(', ') || '未知类型' }}
                  </p>
                </router-link>
                
                <!-- 操作按钮 -->
                <div class="flex items-center space-x-1 ml-2">
                  <span
                    class="px-2 py-1 rounded-lg text-xs font-medium"
                    :class="item.media_type === 'Movie' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'"
                  >
                    {{ item.media_type === 'Movie' ? '电影' : '剧集' }}
                  </span>
                  <span v-if="item.source === 'manual'" class="px-2 py-1 rounded-lg text-xs font-medium bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">
                    手动
                  </span>
                  <!-- 评分按钮 -->
                  <button
                    @click.stop="openRatingModal(item)"
                    class="p-1.5 rounded-lg transition-colors"
                    :class="itemRatings[item.emby_id] ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-dark-100'"
                    :title="itemRatings[item.emby_id] ? `我的评分: ${itemRatings[item.emby_id].rating}` : '评分'"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                  </button>
                  <button @click="editItem(item)" class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-100 text-gray-400 hover:text-gray-600">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button @click="deleteItem(item)" class="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- 底部信息 -->
              <div class="flex items-center justify-between mt-3">
                <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    {{ formatDuration(item.runtime_minutes) }}
                  </span>
                  <span v-if="item.play_count > 1" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                    {{ item.play_count }}次
                  </span>
                </div>
                <div class="flex items-center space-x-2">
                  <!-- 进度条 -->
                  <div v-if="!item.watched" class="w-20 h-1.5 bg-gray-200 dark:bg-dark-100 rounded-full overflow-hidden">
                    <div class="h-full bg-primary-500 rounded-full" :style="{ width: `${item.watch_progress}%` }"></div>
                  </div>
                  <span class="text-sm text-gray-400 dark:text-gray-500">
                    {{ item.watched ? '已看完' : `${Math.round(item.watch_progress || 0)}%` }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !loading" class="mt-8 text-center">
      <button @click="loadMore" class="btn btn-secondary" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showAddModal || editingItem" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="closeModal">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
          {{ editingItem ? '编辑记录' : '手动添加观看记录' }}
        </h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">标题 *</label>
            <input v-model="formData.title" type="text" class="input w-full" placeholder="电影或剧集名称" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">类型</label>
              <select v-model="formData.media_type" class="input w-full">
                <option value="Movie">电影</option>
                <option value="Episode">剧集</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">年份</label>
              <input v-model.number="formData.year" type="number" class="input w-full" placeholder="2024" />
            </div>
          </div>

          <div v-if="formData.media_type === 'Episode'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">剧集名称</label>
              <input v-model="formData.series_name" type="text" class="input w-full" placeholder="剧集名称" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">第几季</label>
                <input v-model.number="formData.season_number" type="number" class="input w-full" placeholder="1" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">第几集</label>
                <input v-model.number="formData.episode_number" type="number" class="input w-full" placeholder="1" />
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">时长(分钟)</label>
              <input v-model.number="formData.runtime_minutes" type="number" class="input w-full" placeholder="120" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">进度(%)</label>
              <input v-model.number="formData.watch_progress" type="number" class="input w-full" min="0" max="100" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">观看时间</label>
            <input v-model="formData.watched_at" type="datetime-local" class="input w-full" />
          </div>

          <div class="flex items-center">
            <input v-model="formData.watched" type="checkbox" id="watched" class="w-4 h-4 text-primary-500 rounded" />
            <label for="watched" class="ml-2 text-sm text-gray-700 dark:text-gray-300">已看完</label>
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6">
          <button @click="closeModal" class="btn btn-secondary">取消</button>
          <button @click="saveRecord" class="btn btn-primary" :disabled="!formData.title">
            {{ editingItem ? '保存' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 评分弹窗 -->
    <div v-if="showRatingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="closeRatingModal">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          {{ getItemTitle(ratingItem) }}
        </h2>
        <p v-if="ratingItem?.media_type === 'Episode'" class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          S{{ ratingItem.season_number || '?' }}E{{ ratingItem.episode_number || '?' }} · {{ ratingItem.title }}
        </p>
        <p v-else class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {{ ratingItem?.year }}
        </p>

        <!-- 星级评分 -->
        <div class="mb-6">
          <div class="flex items-center justify-center space-x-1 mb-2">
            <button
              v-for="star in 10"
              :key="star"
              @click="ratingValue = star"
              class="p-1 transition-transform hover:scale-110"
            >
              <svg
                class="w-8 h-8 transition-colors"
                :class="star <= ratingValue ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </button>
          </div>
          <p class="text-center text-2xl font-bold text-gray-900 dark:text-white">
            {{ ratingValue > 0 ? ratingValue : '-' }} / 10
          </p>
        </div>

        <!-- 评论 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            写点评价（可选）
          </label>
          <textarea
            v-model="reviewText"
            class="input w-full"
            rows="3"
            placeholder="分享你的观影感受..."
          ></textarea>
        </div>

        <!-- 按钮 -->
        <div class="flex justify-end space-x-3">
          <button
            @click="closeRatingModal"
            class="px-4 py-2 text-sm font-medium rounded-lg bg-gray-100 dark:bg-dark-100 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors"
          >
            取消
          </button>
          <button
            @click="saveRating"
            :disabled="ratingValue === 0 || savingRating"
            class="px-4 py-2 text-sm font-medium rounded-lg bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ savingRating ? '保存中...' : '保存评分' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { historyApi, ratingsApi } from '../api'

const appStore = useAppStore()
const loading = ref(true)
const loadingMore = ref(false)
const syncing = ref(false)
const historyItems = ref([])
const page = ref(1)
const pageSize = 50
const totalCount = ref(0)
const syncResult = ref(null)
const stats = ref({ total_minutes: 0 })

// 高级筛选
const showFilters = ref(false)
const availableGenres = ref([])
const filters = reactive({
  search: '',
  mediaType: 'all',
  genre: '',
  watched: '',
  yearFrom: null,
  yearTo: null,
  ratingFrom: null,
  ratingTo: null,
  dateFrom: '',
  dateTo: '',
  sortBy: 'watched_at',
  sortOrder: 'desc',
})

// 弹窗状态
const showAddModal = ref(false)
const editingItem = ref(null)
const formData = ref(getDefaultFormData())

// 评分相关状态
const showRatingModal = ref(false)
const ratingItem = ref(null)
const ratingValue = ref(0)
const reviewText = ref('')
const savingRating = ref(false)
const itemRatings = ref({}) // { emby_id: { rating, review } }

// 计算是否有激活的筛选
const hasActiveFilters = computed(() => {
  return filters.search || 
    filters.mediaType !== 'all' || 
    filters.genre || 
    filters.watched !== '' ||
    filters.yearFrom || 
    filters.yearTo || 
    filters.ratingFrom !== null || 
    filters.ratingTo !== null ||
    filters.dateFrom || 
    filters.dateTo
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.search) count++
  if (filters.mediaType !== 'all') count++
  if (filters.genre) count++
  if (filters.watched !== '') count++
  if (filters.yearFrom || filters.yearTo) count++
  if (filters.ratingFrom !== null || filters.ratingTo !== null) count++
  if (filters.dateFrom || filters.dateTo) count++
  return count
})

const filterTags = computed(() => {
  const tags = []
  if (filters.search) tags.push({ key: 'search', label: `搜索: ${filters.search}` })
  if (filters.mediaType !== 'all') tags.push({ key: 'mediaType', label: filters.mediaType === 'Movie' ? '电影' : '剧集' })
  if (filters.genre) tags.push({ key: 'genre', label: filters.genre })
  if (filters.watched !== '') tags.push({ key: 'watched', label: filters.watched === 'true' ? '已看完' : '未看完' })
  if (filters.yearFrom || filters.yearTo) {
    const label = filters.yearFrom && filters.yearTo 
      ? `${filters.yearFrom}-${filters.yearTo}年` 
      : filters.yearFrom ? `${filters.yearFrom}年起` : `${filters.yearTo}年止`
    tags.push({ key: 'year', label })
  }
  if (filters.ratingFrom !== null || filters.ratingTo !== null) {
    const label = filters.ratingFrom !== null && filters.ratingTo !== null
      ? `评分 ${filters.ratingFrom}-${filters.ratingTo}`
      : filters.ratingFrom !== null ? `评分 ≥${filters.ratingFrom}` : `评分 ≤${filters.ratingTo}`
    tags.push({ key: 'rating', label })
  }
  if (filters.dateFrom || filters.dateTo) {
    const label = filters.dateFrom && filters.dateTo
      ? `${filters.dateFrom} 至 ${filters.dateTo}`
      : filters.dateFrom ? `${filters.dateFrom} 起` : `${filters.dateTo} 止`
    tags.push({ key: 'date', label })
  }
  return tags
})

const removeFilter = (key) => {
  switch (key) {
    case 'search': filters.search = ''; break
    case 'mediaType': filters.mediaType = 'all'; break
    case 'genre': filters.genre = ''; break
    case 'watched': filters.watched = ''; break
    case 'year': filters.yearFrom = null; filters.yearTo = null; break
    case 'rating': filters.ratingFrom = null; filters.ratingTo = null; break
    case 'date': filters.dateFrom = ''; filters.dateTo = ''; break
  }
  applyFilters()
}

const resetFilters = () => {
  filters.search = ''
  filters.mediaType = 'all'
  filters.genre = ''
  filters.watched = ''
  filters.yearFrom = null
  filters.yearTo = null
  filters.ratingFrom = null
  filters.ratingTo = null
  filters.dateFrom = ''
  filters.dateTo = ''
  filters.sortBy = 'watched_at'
  filters.sortOrder = 'desc'
  applyFilters()
}

const applyFilters = () => {
  fetchHistory(true)
}

function getDefaultFormData() {
  return {
    title: '',
    media_type: 'Movie',
    series_name: '',
    season_number: null,
    episode_number: null,
    year: new Date().getFullYear(),
    runtime_minutes: 0,
    watch_progress: 100,
    watched: true,
    watched_at: new Date().toISOString().slice(0, 16),
  }
}

const hasMore = computed(() => historyItems.value.length < totalCount.value)

// 按日期分组（使用本地时区）
const groupedHistory = computed(() => {
  const groups = {}
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

  for (const item of historyItems.value) {
    let dateKey = 'unknown'
    if (item.watched_at) {
      // 将 UTC 时间转换为本地时间再提取日期
      const localDate = new Date(item.watched_at)
      const year = localDate.getFullYear()
      const month = String(localDate.getMonth() + 1).padStart(2, '0')
      const day = String(localDate.getDate()).padStart(2, '0')
      dateKey = `${year}-${month}-${day}`
    }

    if (!groups[dateKey]) {
      if (dateKey === 'unknown') {
        groups[dateKey] = {
          date: dateKey,
          day: '?',
          weekday: '',
          dateStr: '未知日期',
          items: [],
          totalMinutes: 0,
        }
      } else {
        // 使用本地时间创建日期对象
        const [year, month, day] = dateKey.split('-').map(Number)
        const d = new Date(year, month - 1, day)
        groups[dateKey] = {
          date: dateKey,
          day: d.getDate(),
          weekday: weekdays[d.getDay()],
          dateStr: formatDateStr(d),
          items: [],
          totalMinutes: 0,
        }
      }
    }

    groups[dateKey].items.push(item)
    if (item.watched) {
      groups[dateKey].totalMinutes += item.runtime_minutes || 0
    }
  }

  return Object.values(groups).sort((a, b) => {
    if (a.date === 'unknown') return 1
    if (b.date === 'unknown') return -1
    return b.date.localeCompare(a.date)
  })
})

const formatDateStr = (date) => {
  // 直接使用年月日格式
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

const formatDuration = (minutes) => {
  if (!minutes) return '0分钟'
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours < 24) return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
  const days = Math.floor(hours / 24)
  const remainHours = hours % 24
  return remainHours > 0 ? `${days}天${remainHours}小时` : `${days}天`
}

const getItemLink = (item) => {
  if (item.media_type === 'Episode' && item.series_id) return `/show/${item.series_id}`
  if (item.media_type === 'Movie' && item.emby_id) return `/movie/${item.emby_id}`
  return '#'
}

const getItemPoster = (item) => {
  // 首先尝试使用缓存的 poster_path（兼容旧记录和 Emby 项目被删除的情况）
  if (item.poster_path) {
    // 如果是相对路径（/emby/Items/...），构建完整 URL
    if (item.poster_path.startsWith('/emby/')) {
      return `${appStore.embyUrl}${item.poster_path.substring(5)}?maxWidth=200`
    }
    // 如果是 TMDB 路径
    if (item.poster_path.startsWith('/')) {
      return appStore.getTmdbImageUrl(item.poster_path, 'w200')
    }
    return item.poster_path
  }

  // 如果有 TMDB ID，尝试从 TMDB 获取图片（作为备用）
  if (item.tmdb_id) {
    const mediaType = item.media_type === 'Movie' ? 'movie' : 'tv'
    // 注意：这里无法直接从 TMDB ID 获取图片路径，需要先查询 TMDB API
    // 但作为备用，我们可以尝试使用 Emby 图片
  }

  // 尝试使用 Emby 图片（可能会失败，图片错误处理会显示占位符）
  if (item.media_type === 'Episode' && item.series_id) {
    return appStore.getEmbyImageUrl(item.series_id, 'Primary', 200)
  }
  if (item.emby_id) {
    return appStore.getEmbyImageUrl(item.emby_id, 'Primary', 200)
  }
  return 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 150"><rect fill="%23374151" width="100" height="150"/><text x="50" y="75" text-anchor="middle" fill="%239CA3AF" font-size="12">无图片</text></svg>'
}

const getItemTitle = (item) => {
  if (item.media_type === 'Episode' && item.series_name) return item.series_name
  return item.title
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 150"><rect fill="%23374151" width="100" height="150"/><text x="50" y="75" text-anchor="middle" fill="%239CA3AF" font-size="12">无图片</text></svg>'
}

const fetchHistory = async (reset = false) => {
  if (!appStore.currentEmbyUser) return
  
  if (reset) {
    page.value = 1
    historyItems.value = []
  }
  
  loading.value = reset
  loadingMore.value = !reset
  
  try {
    const params = {
      media_type: filters.mediaType,
      page: page.value,
      page_size: pageSize,
      sort_by: filters.sortBy,
      sort_order: filters.sortOrder,
    }
    
    // 添加筛选参数
    if (filters.search) params.search = filters.search
    if (filters.genre) params.genre = filters.genre
    if (filters.watched !== '') params.watched = filters.watched === 'true'
    if (filters.yearFrom) params.year_from = filters.yearFrom
    if (filters.yearTo) params.year_to = filters.yearTo
    if (filters.ratingFrom !== null) params.rating_from = filters.ratingFrom
    if (filters.ratingTo !== null) params.rating_to = filters.ratingTo
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    
    const result = await historyApi.getHistory(appStore.currentEmbyUser.Id, params)
    
    if (reset) {
      historyItems.value = result.items
    } else {
      historyItems.value.push(...result.items)
    }
    
    totalCount.value = result.total_count
    
    // 获取统计
    const statsResult = await historyApi.getStats(appStore.currentEmbyUser.Id)
    stats.value = statsResult
    
    // 获取可用类型（仅首次）
    if (availableGenres.value.length === 0) {
      const genresResult = await historyApi.getGenres(appStore.currentEmbyUser.Id)
      availableGenres.value = genresResult.genres
    }
    
  } catch (e) {
    console.error('Failed to fetch history:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const syncFromEmby = async () => {
  if (!appStore.currentEmbyUser || syncing.value) return
  
  syncing.value = true
  syncResult.value = null
  
  try {
    const result = await historyApi.syncFromEmby(appStore.currentEmbyUser.Id)
    syncResult.value = result
    await fetchHistory(true)
  } catch (e) {
    console.error('Sync failed:', e)
    alert('同步失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    syncing.value = false
  }
}

const loadMore = () => {
  page.value++
  fetchHistory()
}

const editItem = (item) => {
  editingItem.value = item
  formData.value = {
    title: item.title,
    media_type: item.media_type,
    series_name: item.series_name || '',
    season_number: item.season_number,
    episode_number: item.episode_number,
    year: item.year,
    runtime_minutes: item.runtime_minutes,
    watch_progress: item.watch_progress,
    watched: item.watched,
    watched_at: item.watched_at ? item.watched_at.slice(0, 16) : '',
  }
}

const deleteItem = async (item) => {
  if (!confirm(`确定要删除"${getItemTitle(item)}"的观看记录吗？`)) return
  
  try {
    await historyApi.deleteHistory(item.id)
    historyItems.value = historyItems.value.filter(i => i.id !== item.id)
    totalCount.value--
  } catch (e) {
    console.error('Delete failed:', e)
    alert('删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingItem.value = null
  formData.value = getDefaultFormData()
}

const saveRecord = async () => {
  if (!appStore.currentEmbyUser || !formData.value.title) return

  try {
    if (editingItem.value) {
      // 更新
      await historyApi.updateHistory(editingItem.value.id, {
        watched: formData.value.watched,
        watch_progress: formData.value.watch_progress,
        watched_at: formData.value.watched_at ? new Date(formData.value.watched_at).toISOString() : null,
        play_count: editingItem.value.play_count,
      })
    } else {
      // 新增
      await historyApi.addHistory(appStore.currentEmbyUser.Id, {
        ...formData.value,
        watched_at: formData.value.watched_at ? new Date(formData.value.watched_at).toISOString() : null,
      })
    }

    closeModal()
    await fetchHistory(true)
  } catch (e) {
    console.error('Save failed:', e)
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 评分功能
const openRatingModal = (item) => {
  ratingItem.value = item
  const existing = itemRatings.value[item.emby_id]
  if (existing) {
    ratingValue.value = existing.rating
    reviewText.value = existing.review || ''
  } else {
    ratingValue.value = 0
    reviewText.value = ''
  }
  showRatingModal.value = true
}

const closeRatingModal = () => {
  showRatingModal.value = false
  ratingItem.value = null
  ratingValue.value = 0
  reviewText.value = ''
}

const saveRating = async () => {
  if (!appStore.currentEmbyUser || !ratingItem.value || ratingValue.value === 0) return

  savingRating.value = true
  try {
    // 确定媒体类型
    const mediaType = ratingItem.value.media_type === 'Movie' ? 'movie' : 'episode'

    // 构建标题
    let title = ratingItem.value.title
    if (ratingItem.value.media_type === 'Episode' && ratingItem.value.series_name) {
      title = `${ratingItem.value.series_name} - ${ratingItem.value.title}`
    }

    await ratingsApi.createRating(appStore.currentEmbyUser.Id, {
      emby_id: ratingItem.value.emby_id,
      tmdb_id: ratingItem.value.tmdb_id || null,
      media_type: mediaType,
      title: title,
      rating: ratingValue.value,
      review: reviewText.value || null,
    })

    // 更新本地状态
    itemRatings.value[ratingItem.value.emby_id] = {
      rating: ratingValue.value,
      review: reviewText.value,
    }

    closeRatingModal()
  } catch (e) {
    console.error('Failed to save rating:', e)
    alert('保存评分失败')
  } finally {
    savingRating.value = false
  }
}

// 获取当前页面所有项目的评分状态
const fetchItemRatings = async () => {
  if (!appStore.currentEmbyUser || historyItems.value.length === 0) return

  try {
    // 分别获取电影和剧集的评分
    const movieIds = historyItems.value
      .filter(item => item.media_type === 'Movie' && item.emby_id)
      .map(item => item.emby_id)

    const episodeIds = historyItems.value
      .filter(item => item.media_type === 'Episode' && item.emby_id)
      .map(item => item.emby_id)

    // 并行获取
    const [movieRatings, episodeRatings] = await Promise.all([
      movieIds.length > 0
        ? ratingsApi.checkRatingsBatch(appStore.currentEmbyUser.Id, movieIds, 'movie')
        : { ratings: {} },
      episodeIds.length > 0
        ? ratingsApi.checkRatingsBatch(appStore.currentEmbyUser.Id, episodeIds, 'episode')
        : { ratings: {} },
    ])

    // 合并结果
    itemRatings.value = {
      ...itemRatings.value,
      ...(movieRatings.ratings || {}),
      ...(episodeRatings.ratings || {}),
    }
  } catch (e) {
    console.error('Failed to fetch item ratings:', e)
  }
}

// 在获取历史记录后获取评分
watch(historyItems, () => {
  if (historyItems.value.length > 0) {
    fetchItemRatings()
  }
})

watch(() => appStore.currentEmbyUser, () => fetchHistory(true))
onMounted(() => fetchHistory(true))
</script>
