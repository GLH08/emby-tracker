<template>
  <div v-if="loading" class="min-h-screen flex items-center justify-center">
    <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
  </div>

  <div v-else-if="item">
    <!-- 背景 -->
    <div class="relative h-[400px] md:h-[500px]">
      <img 
        v-if="backdropUrl"
        :src="backdropUrl"
        :alt="item.name"
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-gray-50 dark:from-dark-400 via-gray-50/50 dark:via-dark-400/50 to-transparent"></div>
    </div>

    <!-- 内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-48 relative z-10">
      <div class="flex flex-col md:flex-row gap-8">
        <!-- 海报 -->
        <div class="flex-shrink-0">
          <img 
            :src="posterUrl"
            :alt="item.name"
            class="w-48 md:w-64 rounded-xl shadow-2xl mx-auto md:mx-0"
          />
        </div>

        <!-- 信息 -->
        <div class="flex-1">
          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {{ item.name }}
          </h1>

          <!-- 元信息 -->
          <div class="flex flex-wrap items-center gap-4 mb-6">
            <span v-if="item.year" class="text-gray-600 dark:text-gray-400">{{ item.year }}</span>
            
            <span v-if="item.community_rating" class="flex items-center space-x-1">
              <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="font-medium text-gray-900 dark:text-white">{{ item.community_rating.toFixed(1) }}</span>
            </span>

            <span v-if="runtime" class="text-gray-600 dark:text-gray-400">{{ runtime }}</span>
            
            <span v-if="item.official_rating" class="badge badge-warning">{{ item.official_rating }}</span>
          </div>

          <!-- 外部评分（IMDB/烂番茄/Metacritic） -->
          <div v-if="externalRatings || loadingExternalRatings || tmdbData" class="flex flex-wrap items-center gap-4 mb-6">
            <div v-if="loadingExternalRatings" class="text-sm text-gray-500 dark:text-gray-400">
              加载评分中...
            </div>
            <template v-else>
              <!-- TMDB 链接 -->
              <a 
                v-if="tmdbData?.id" 
                :href="getTmdbUrl()"
                target="_blank"
                rel="noopener noreferrer"
                class="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 px-3 py-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors cursor-pointer"
              >
                <span class="font-bold text-blue-600 dark:text-blue-400 text-sm">TMDB</span>
                <span v-if="tmdbData.vote_average" class="font-semibold text-gray-900 dark:text-white">{{ tmdbData.vote_average.toFixed(1) }}</span>
                <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
              </a>
              
              <template v-if="externalRatings">
                <!-- IMDB 评分 -->
                <a 
                  v-if="externalRatings.imdb_rating" 
                  :href="`https://www.imdb.com/title/${externalRatings.imdb_id}/`"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center space-x-2 bg-yellow-50 dark:bg-yellow-900/20 px-3 py-1.5 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors cursor-pointer"
                >
                  <span class="font-bold text-yellow-600 dark:text-yellow-400 text-sm">IMDb</span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ externalRatings.imdb_rating.toFixed(1) }}</span>
                  <span v-if="externalRatings.imdb_votes" class="text-xs text-gray-500 dark:text-gray-400">
                    ({{ formatVotes(externalRatings.imdb_votes) }})
                  </span>
                  <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </a>
                
                <!-- 烂番茄 -->
                <a 
                  v-if="externalRatings.rotten_tomatoes" 
                  :href="getRottenTomatoesUrl()"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center space-x-2 px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity cursor-pointer"
                  :class="externalRatings.rotten_tomatoes >= 60 ? 'bg-red-50 dark:bg-red-900/20' : 'bg-green-50 dark:bg-green-900/20'"
                >
                  <span class="text-lg">{{ externalRatings.rotten_tomatoes >= 60 ? '🍅' : '🥬' }}</span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ externalRatings.rotten_tomatoes }}%</span>
                  <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </a>
                
                <!-- Metacritic -->
                <a 
                  v-if="externalRatings.metacritic" 
                  :href="getMetacriticUrl()"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center space-x-2 px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity cursor-pointer"
                  :class="getMetacriticClass(externalRatings.metacritic)"
                >
                  <span class="font-bold text-xs px-1.5 py-0.5 rounded text-white"
                    :class="getMetacriticBadgeClass(externalRatings.metacritic)">
                    M
                  </span>
                  <span class="font-semibold text-gray-900 dark:text-white">{{ externalRatings.metacritic }}</span>
                  <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </a>
              </template>
              
              <!-- 手动获取/刷新外部评分按钮 -->
              <button 
                @click="refreshExternalRatings"
                :disabled="refreshingExternalRatings"
                class="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-dark-100 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors text-sm"
                :title="externalRatings ? '刷新评分' : '获取评分'"
              >
                <svg 
                  class="w-4 h-4" 
                  :class="{ 'animate-spin': refreshingExternalRatings }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                <span>{{ refreshingExternalRatings ? '获取中...' : (externalRatings ? '刷新' : '获取评分') }}</span>
              </button>
            </template>
          </div>

          <!-- 类型标签 -->
          <div v-if="item.genres?.length" class="flex flex-wrap gap-2 mb-6">
            <span 
              v-for="genre in item.genres" 
              :key="genre"
              class="badge badge-primary"
            >
              {{ genre }}
            </span>
          </div>

          <!-- 操作按钮 -->
          <div class="flex flex-wrap items-center gap-3 mb-8">
            <!-- Check-in 按钮 -->
            <button 
              @click="handleCheckin"
              class="btn btn-primary flex items-center"
              :disabled="checkingIn"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ checkingIn ? '签到中...' : '正在观看' }}
            </button>

            <button 
              @click="togglePlayed"
              class="btn"
              :class="item.played ? 'btn-primary' : 'btn-secondary'"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              {{ item.played ? '已看' : '标记已看' }}
            </button>

            <button 
              @click="toggleFavorite"
              class="btn btn-secondary"
            >
              <svg 
                class="w-5 h-5 mr-2" 
                :class="item.is_favorite ? 'text-red-500' : ''"
                :fill="item.is_favorite ? 'currentColor' : 'none'" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
              </svg>
              {{ item.is_favorite ? '已收藏' : '收藏' }}
            </button>

            <button 
              @click="addToWatchlist"
              class="btn btn-secondary"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              想看
            </button>

            <!-- 评分按钮 -->
            <button 
              @click="openRatingModal"
              class="btn"
              :class="userRating?.rated ? 'btn-primary' : 'btn-secondary'"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              {{ userRating?.rated ? `我的评分 ${userRating.rating}` : '评分' }}
            </button>
          </div>

          <!-- 简介 -->
          <div class="mb-8">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">简介</h2>
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
              {{ item.overview || '暂无简介' }}
            </p>
          </div>
        </div>
      </div>

      <!-- TMDB 详情 -->
      <div v-if="tmdbData" class="mt-12 space-y-12">
        <!-- 演员 -->
        <section v-if="tmdbData.credits?.cast?.length">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">演员</h2>
          <div class="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide">
            <router-link 
              v-for="person in tmdbData.credits.cast.slice(0, 10)" 
              :key="person.id"
              :to="`/person/${person.id}`"
              class="flex-shrink-0 w-32 group cursor-pointer"
            >
              <img 
                v-if="person.profile_path"
                :src="appStore.getTmdbImageUrl(person.profile_path, 'w185')"
                :alt="person.name"
                class="w-32 h-32 rounded-full object-cover mb-2 transition-transform group-hover:scale-105"
              />
              <div v-else class="w-32 h-32 rounded-full bg-gray-200 dark:bg-dark-100 flex items-center justify-center mb-2">
                <svg class="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                </svg>
              </div>
              <p class="font-medium text-gray-900 dark:text-white text-sm text-center truncate group-hover:text-primary-500 transition-colors">{{ person.name }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 text-center truncate">{{ person.character }}</p>
            </router-link>
          </div>
        </section>

        <!-- 预告片 -->
        <section v-if="trailer">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">预告片</h2>
          <div class="aspect-video rounded-xl overflow-hidden bg-black">
            <iframe 
              :src="`https://www.youtube.com/embed/${trailer.key}`"
              class="w-full h-full"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </section>

        <!-- 相似推荐 -->
        <section v-if="tmdbData.similar?.results?.length">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">相似推荐</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div 
              v-for="similar in tmdbData.similar.results.slice(0, 6)" 
              :key="similar.id"
              class="card overflow-hidden"
            >
              <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100">
                <img 
                  v-if="similar.poster_path"
                  :src="appStore.getTmdbImageUrl(similar.poster_path, 'w342')"
                  :alt="similar.title || similar.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="p-3">
                <p class="font-medium text-gray-900 dark:text-white text-sm truncate">
                  {{ similar.title || similar.name }}
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 剧集列表 (仅剧集) -->
      <div v-if="type === 'show' && seasons.length > 0" class="mt-12">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">剧集列表</h2>
        
        <!-- 季选择 -->
        <div class="flex overflow-x-auto space-x-2 mb-6 pb-2 scrollbar-hide">
          <button
            v-for="season in seasons"
            :key="season.id"
            @click="selectedSeason = season"
            class="flex-shrink-0 px-4 py-2 rounded-lg font-medium transition-colors"
            :class="selectedSeason?.id === season.id 
              ? 'bg-primary-500 text-white' 
              : 'bg-gray-100 dark:bg-dark-100 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200'"
          >
            {{ season.name }}
          </button>
        </div>

        <!-- 集列表 -->
        <div class="space-y-3">
          <div 
            v-for="episode in episodes"
            :key="episode.id"
            class="card p-4 flex items-center space-x-4"
          >
            <div class="flex-shrink-0 w-12 h-12 rounded-lg bg-gray-100 dark:bg-dark-100 flex items-center justify-center">
              <span class="font-bold text-gray-600 dark:text-gray-400">{{ episode.index_number }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-900 dark:text-white truncate">{{ episode.name }}</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-1">{{ episode.overview }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span 
                v-if="episode.played"
                class="badge badge-success"
              >
                已看
              </span>
              <!-- 单集评分按钮 -->
              <button 
                @click="openEpisodeRatingModal(episode)"
                class="p-2 rounded-lg transition-colors"
                :class="episodeRatings[episode.id] ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-dark-100'"
                :title="episodeRatings[episode.id] ? `我的评分: ${episodeRatings[episode.id].rating}` : '评分'"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
              </button>
              <button 
                @click="toggleEpisodePlayed(episode)"
                class="btn-ghost p-2 rounded-lg"
              >
                <svg 
                  class="w-5 h-5" 
                  :class="episode.played ? 'text-green-500' : 'text-gray-400'"
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 评分弹窗 -->
    <div v-if="showRatingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showRatingModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {{ userRating?.rated ? '修改评分' : '为这部作品评分' }}
        </h2>
        
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
            rows="4"
            placeholder="分享你的观影感受..."
          ></textarea>
        </div>
        
        <!-- 按钮 -->
        <div class="flex justify-end space-x-3">
          <button 
            @click="showRatingModal = false" 
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

    <!-- 单集评分弹窗 -->
    <div v-if="showEpisodeRatingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showEpisodeRatingModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          {{ currentEpisode?.name }}
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">第 {{ currentEpisode?.index_number }} 集</p>
        
        <!-- 星级评分 -->
        <div class="mb-6">
          <div class="flex items-center justify-center space-x-1 mb-2">
            <button
              v-for="star in 10"
              :key="star"
              @click="episodeRatingValue = star"
              class="p-1 transition-transform hover:scale-110"
            >
              <svg 
                class="w-8 h-8 transition-colors"
                :class="star <= episodeRatingValue ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </button>
          </div>
          <p class="text-center text-2xl font-bold text-gray-900 dark:text-white">
            {{ episodeRatingValue > 0 ? episodeRatingValue : '-' }} / 10
          </p>
        </div>
        
        <!-- 评论 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            写点评价（可选）
          </label>
          <textarea
            v-model="episodeReviewText"
            class="input w-full"
            rows="3"
            placeholder="这一集怎么样..."
          ></textarea>
        </div>
        
        <!-- 按钮 -->
        <div class="flex justify-end space-x-3">
          <button 
            @click="showEpisodeRatingModal = false" 
            class="px-4 py-2 text-sm font-medium rounded-lg bg-gray-100 dark:bg-dark-100 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors"
          >
            取消
          </button>
          <button 
            @click="saveEpisodeRating" 
            :disabled="episodeRatingValue === 0 || savingEpisodeRating"
            class="px-4 py-2 text-sm font-medium rounded-lg bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ savingEpisodeRating ? '保存中...' : '保存评分' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { embyApi, tmdbApi, watchlistApi, checkinApi, ratingsApi, externalRatingsApi } from '../api'

const props = defineProps({
  id: String,
  type: String,
})

const appStore = useAppStore()
const loading = ref(true)
const item = ref(null)
const tmdbData = ref(null)
const seasons = ref([])
const selectedSeason = ref(null)
const episodes = ref([])
const checkingIn = ref(false)

// 评分相关
const showRatingModal = ref(false)
const userRating = ref(null)
const ratingValue = ref(0)
const reviewText = ref('')
const savingRating = ref(false)

// 外部评分
const externalRatings = ref(null)
const loadingExternalRatings = ref(false)
const refreshingExternalRatings = ref(false)

// 单集评分相关
const showEpisodeRatingModal = ref(false)
const currentEpisode = ref(null)
const episodeRatingValue = ref(0)
const episodeReviewText = ref('')
const savingEpisodeRating = ref(false)
const episodeRatings = ref({}) // 存储所有单集的评分 { episodeId: { rating, review } }

const posterUrl = computed(() => {
  if (!item.value) return ''
  return appStore.getEmbyImageUrl(item.value.id, 'Primary', 400)
})

const backdropUrl = computed(() => {
  if (!item.value) return ''
  return item.value.backdrop_image_tag
    ? appStore.getEmbyImageUrl(item.value.id, 'Backdrop', 1920)
    : appStore.getEmbyImageUrl(item.value.id, 'Primary', 1920)
})

const runtime = computed(() => {
  if (!item.value?.runtime_ticks) return ''
  const minutes = Math.round(item.value.runtime_ticks / 600000000)
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return hours > 0 ? `${hours}小时${mins}分钟` : `${mins}分钟`
})

const trailer = computed(() => {
  if (!tmdbData.value?.videos?.results) return null
  return tmdbData.value.videos.results.find(v => v.type === 'Trailer' && v.site === 'YouTube')
})

// 格式化投票数
const formatVotes = (votes) => {
  if (votes >= 1000000) {
    return (votes / 1000000).toFixed(1) + 'M'
  } else if (votes >= 1000) {
    return (votes / 1000).toFixed(1) + 'K'
  }
  return votes.toString()
}

// Metacritic 背景色
const getMetacriticClass = (score) => {
  if (score >= 61) return 'bg-green-50 dark:bg-green-900/20'
  if (score >= 40) return 'bg-yellow-50 dark:bg-yellow-900/20'
  return 'bg-red-50 dark:bg-red-900/20'
}

// Metacritic 徽章色
const getMetacriticBadgeClass = (score) => {
  if (score >= 61) return 'bg-green-500'
  if (score >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

// 生成烂番茄搜索 URL
const getRottenTomatoesUrl = () => {
  if (!item.value) return '#'
  const title = encodeURIComponent(item.value.name)
  return `https://www.rottentomatoes.com/search?search=${title}`
}

// 生成 Metacritic 搜索 URL
const getMetacriticUrl = () => {
  if (!item.value) return '#'
  const title = encodeURIComponent(item.value.name)
  const type = props.type === 'movie' ? 'movie' : 'tv'
  return `https://www.metacritic.com/search/${title}/?page=1&category=${type}`
}

// 生成 TMDB URL
const getTmdbUrl = () => {
  if (!tmdbData.value?.id) return '#'
  const type = props.type === 'movie' ? 'movie' : 'tv'
  return `https://www.themoviedb.org/${type}/${tmdbData.value.id}`
}

const fetchItem = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    item.value = await embyApi.getItem(appStore.currentEmbyUser.Id, props.id)
    
    // 获取 TMDB 数据
    const tmdbId = item.value.provider_ids?.Tmdb
    if (tmdbId) {
      if (props.type === 'movie') {
        tmdbData.value = await tmdbApi.getMovie(parseInt(tmdbId))
      } else {
        tmdbData.value = await tmdbApi.getTvShow(parseInt(tmdbId))
      }
    }
    
    // 获取剧集的季和集
    if (props.type === 'show') {
      seasons.value = await embyApi.getSeasons(appStore.currentEmbyUser.Id, props.id)
      if (seasons.value.length > 0) {
        selectedSeason.value = seasons.value[0]
      }
    }
    
    // 检查用户评分
    await checkUserRating()
    
    // 获取外部评分（IMDB/烂番茄/Metacritic）
    await fetchExternalRatings()
  } catch (e) {
    console.error('Failed to fetch item:', e)
  } finally {
    loading.value = false
  }
}

// 检查用户是否已评分
const checkUserRating = async () => {
  if (!appStore.currentEmbyUser || !item.value) return
  
  try {
    const tmdbId = item.value.provider_ids?.Tmdb
    const result = await ratingsApi.checkRating(appStore.currentEmbyUser.Id, {
      emby_id: item.value.id,
      tmdb_id: tmdbId ? parseInt(tmdbId) : null,
      media_type: props.type === 'movie' ? 'movie' : 'tv',
    })
    
    if (result.rated) {
      userRating.value = result
      ratingValue.value = result.rating
      reviewText.value = result.review || ''
    }
  } catch (e) {
    console.error('Failed to check rating:', e)
  }
}

// 获取外部评分（IMDB/烂番茄/Metacritic）
const fetchExternalRatings = async () => {
  if (!item.value) return
  
  loadingExternalRatings.value = true
  try {
    const imdbId = item.value.provider_ids?.Imdb
    const tmdbId = item.value.provider_ids?.Tmdb
    
    // 优先使用 IMDB ID，否则使用标题搜索
    const params = {
      media_type: props.type === 'movie' ? 'movie' : 'tv',
    }
    
    if (imdbId) {
      params.imdb_id = imdbId
    } else {
      params.title = item.value.name
      params.year = item.value.year
    }
    
    if (tmdbId) {
      params.tmdb_id = parseInt(tmdbId)
    }
    
    externalRatings.value = await externalRatingsApi.getRatings(params)
  } catch (e) {
    // 404 表示没有找到评分，不是错误
    if (e.response?.status !== 404) {
      console.error('Failed to fetch external ratings:', e)
    }
    externalRatings.value = null
  } finally {
    loadingExternalRatings.value = false
  }
}

// 手动刷新外部评分
const refreshExternalRatings = async () => {
  if (!item.value || refreshingExternalRatings.value) return
  
  refreshingExternalRatings.value = true
  try {
    const imdbId = item.value.provider_ids?.Imdb
    const tmdbId = item.value.provider_ids?.Tmdb
    
    const params = {
      media_type: props.type === 'movie' ? 'movie' : 'tv',
      force: true, // 强制刷新
    }
    
    if (imdbId) {
      params.imdb_id = imdbId
    } else {
      params.title = item.value.name
      params.year = item.value.year
    }
    
    if (tmdbId) {
      params.tmdb_id = parseInt(tmdbId)
    }
    
    externalRatings.value = await externalRatingsApi.getRatings(params)
  } catch (e) {
    if (e.response?.status === 404) {
      alert('未找到评分数据')
    } else {
      console.error('Failed to refresh external ratings:', e)
      alert('获取评分失败，可能是 API 限制')
    }
  } finally {
    refreshingExternalRatings.value = false
  }
}

// 打开评分弹窗
const openRatingModal = () => {
  if (userRating.value) {
    ratingValue.value = userRating.value.rating
    reviewText.value = userRating.value.review || ''
  } else {
    ratingValue.value = 0
    reviewText.value = ''
  }
  showRatingModal.value = true
}

// 保存评分
const saveRating = async () => {
  if (!appStore.currentEmbyUser || !item.value || ratingValue.value === 0) return
  
  savingRating.value = true
  try {
    const tmdbId = item.value.provider_ids?.Tmdb
    await ratingsApi.createRating(appStore.currentEmbyUser.Id, {
      emby_id: item.value.id,
      tmdb_id: tmdbId ? parseInt(tmdbId) : null,
      media_type: props.type === 'movie' ? 'movie' : 'tv',
      title: item.value.name,
      rating: ratingValue.value,
      review: reviewText.value || null,
    })
    
    userRating.value = {
      rated: true,
      rating: ratingValue.value,
      review: reviewText.value,
    }
    showRatingModal.value = false
  } catch (e) {
    console.error('Failed to save rating:', e)
    alert('保存评分失败')
  } finally {
    savingRating.value = false
  }
}

const fetchEpisodes = async () => {
  if (!selectedSeason.value || !appStore.currentEmbyUser) return
  
  try {
    episodes.value = await embyApi.getEpisodes(
      appStore.currentEmbyUser.Id, 
      props.id, 
      selectedSeason.value.id
    )
    
    // 获取所有单集的评分状态
    await fetchEpisodeRatings()
  } catch (e) {
    console.error('Failed to fetch episodes:', e)
  }
}

// 获取当前季所有单集的评分
const fetchEpisodeRatings = async () => {
  if (!appStore.currentEmbyUser || episodes.value.length === 0) return
  
  for (const episode of episodes.value) {
    try {
      const result = await ratingsApi.checkRating(appStore.currentEmbyUser.Id, {
        emby_id: episode.id,
        media_type: 'episode',
      })
      if (result.rated) {
        episodeRatings.value[episode.id] = {
          rating: result.rating,
          review: result.review
        }
      }
    } catch (e) {
      // 忽略错误
    }
  }
}

// 打开单集评分弹窗
const openEpisodeRatingModal = (episode) => {
  currentEpisode.value = episode
  const existing = episodeRatings.value[episode.id]
  if (existing) {
    episodeRatingValue.value = existing.rating
    episodeReviewText.value = existing.review || ''
  } else {
    episodeRatingValue.value = 0
    episodeReviewText.value = ''
  }
  showEpisodeRatingModal.value = true
}

// 保存单集评分
const saveEpisodeRating = async () => {
  if (!appStore.currentEmbyUser || !currentEpisode.value || episodeRatingValue.value === 0) return
  
  savingEpisodeRating.value = true
  try {
    await ratingsApi.createRating(appStore.currentEmbyUser.Id, {
      emby_id: currentEpisode.value.id,
      media_type: 'episode',
      title: `${item.value.name} - ${currentEpisode.value.name}`,
      rating: episodeRatingValue.value,
      review: episodeReviewText.value || null,
    })
    
    // 更新本地状态
    episodeRatings.value[currentEpisode.value.id] = {
      rating: episodeRatingValue.value,
      review: episodeReviewText.value
    }
    
    showEpisodeRatingModal.value = false
  } catch (e) {
    console.error('Failed to save episode rating:', e)
    alert('保存评分失败')
  } finally {
    savingEpisodeRating.value = false
  }
}

const togglePlayed = async () => {
  if (!appStore.currentEmbyUser || !item.value) return
  
  try {
    if (item.value.played) {
      await embyApi.markUnplayed(appStore.currentEmbyUser.Id, item.value.id)
    } else {
      await embyApi.markPlayed(appStore.currentEmbyUser.Id, item.value.id)
    }
    item.value.played = !item.value.played
  } catch (e) {
    console.error('Failed to toggle played:', e)
  }
}

const toggleFavorite = async () => {
  if (!appStore.currentEmbyUser || !item.value) return
  
  try {
    await embyApi.toggleFavorite(appStore.currentEmbyUser.Id, item.value.id, !item.value.is_favorite)
    item.value.is_favorite = !item.value.is_favorite
  } catch (e) {
    console.error('Failed to toggle favorite:', e)
  }
}

const toggleEpisodePlayed = async (episode) => {
  if (!appStore.currentEmbyUser) return
  
  try {
    if (episode.played) {
      await embyApi.markUnplayed(appStore.currentEmbyUser.Id, episode.id)
    } else {
      await embyApi.markPlayed(appStore.currentEmbyUser.Id, episode.id)
    }
    episode.played = !episode.played
  } catch (e) {
    console.error('Failed to toggle episode played:', e)
  }
}

const addToWatchlist = async () => {
  try {
    await watchlistApi.addToWatchlist({
      emby_id: item.value.id,
      tmdb_id: item.value.provider_ids?.Tmdb ? parseInt(item.value.provider_ids.Tmdb) : null,
      media_type: props.type,
      title: item.value.name,
      poster_path: tmdbData.value?.poster_path,
      overview: item.value.overview,
      release_date: item.value.premiere_date,
      vote_average: item.value.community_rating,
    })
    alert('已添加到想看列表')
  } catch (e) {
    if (e.response?.status === 400) {
      alert('已在想看列表中')
    } else {
      console.error('Failed to add to watchlist:', e)
    }
  }
}

const handleCheckin = async () => {
  if (!appStore.currentEmbyUser || !item.value || checkingIn.value) return
  
  checkingIn.value = true
  try {
    const runtimeMinutes = item.value.runtime_ticks 
      ? Math.round(item.value.runtime_ticks / 600000000) 
      : 0
    
    await checkinApi.create(appStore.currentEmbyUser.Id, {
      emby_id: item.value.id,
      tmdb_id: item.value.provider_ids?.Tmdb ? parseInt(item.value.provider_ids.Tmdb) : null,
      media_type: props.type === 'movie' ? 'movie' : 'episode',
      title: item.value.name,
      poster_path: tmdbData.value?.poster_path,
      year: item.value.year,
      runtime_minutes: runtimeMinutes,
    })
    alert('Check-in 成功！正在观看中...')
  } catch (e) {
    console.error('Failed to check-in:', e)
    alert('Check-in 失败')
  } finally {
    checkingIn.value = false
  }
}

watch(selectedSeason, fetchEpisodes)
watch(() => appStore.currentEmbyUser, fetchItem)

onMounted(fetchItem)
</script>
