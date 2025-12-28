# Emby Tracker

一个现代化的 Emby 媒体库管理和观影记录追踪应用，类似 Trakt.tv 的中文友好替代方案。

## 功能特性

### 核心功能

- 🎬 **媒体库浏览** - 浏览 Emby 服务器中的电影和剧集，支持搜索、筛选、排序
- 📊 **观影统计** - 类型分布、评分分布、观看时长、热力图、趋势分析
- 📝 **观看历史** - 本地存储观看记录，支持自动同步和手动添加
- 🔍 **发现内容** - 基于 TMDB 的热门趋势、即将上映、按类型/年份/平台浏览
- 📌 **想看列表** - 收藏想看的影视作品
- 📅 **日历视图** - 追剧更新时间表，支持 iCal 导出
- 📈 **剧集进度** - 追踪剧集观看进度，显示完成百分比和下一集提醒
- ⭐ **评分系统** - 1-10 分个人评分和短评
- 📋 **自定义列表** - 创建多个列表管理影片，支持公开分享
- 🎯 **Check-in** - 实时标记正在观看的内容
- 📤 **数据导入/导出** - 支持 Trakt 导入、完整备份/恢复
- 📆 **年度回顾** - 类似 Spotify Wrapped 的年度观影总结

### 外部评分集成

- 🎯 **IMDB/烂番茄/Metacritic 评分** - 通过 OMDb API 获取外部评分
- 💾 **本地缓存** - 评分数据缓存到本地，7天有效期，无需重复请求
- 🔄 **批量同步** - 一键同步整个媒体库的外部评分
- 🔑 **多 API Key 支持** - 支持多个 OMDb API Key 轮询，自动故障转移
- 🏷️ **全局显示** - 可选在所有影片卡片上显示 IMDB 评分徽章

### 系统功能

- 🎨 **自定义轮播** - 自定义首页轮播海报
- 👥 **多用户支持** - 支持管理员和访客账户，权限控制
- 🔄 **自动同步** - 启动时和定时自动同步观看记录
- 🌙 **深色模式** - 支持明暗主题切换
- 🎯 **推荐系统** - 基于观看历史的个性化推荐

## 快速开始

### 方式一：使用预构建镜像（推荐）

1. 创建项目目录并下载配置文件：

```bash
mkdir emby-tracker && cd emby-tracker
curl -O https://raw.githubusercontent.com/GLH08/emby-tracker/main/docker-compose-ghcr.yml
curl -O https://raw.githubusercontent.com/GLH08/emby-tracker/main/.env.example
mv .env.example .env
```

2. 编辑 `.env` 文件，配置必要的环境变量：

```bash
nano .env
```

3. 启动服务：

```bash
docker compose -f docker-compose-ghcr.yml up -d
```

4. 访问 `http://localhost:3000`，使用配置的管理员账户登录。

### 方式二：本地构建

```bash
git clone https://github.com/GLH08/emby-tracker.git
cd emby-tracker
cp .env.example .env
nano .env  # 编辑配置
docker compose up -d --build
```

## 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `EMBY_URL` | ✅ | - | Emby 服务器地址，如 `http://192.168.1.100:8096` |
| `EMBY_API_KEY` | ✅ | - | Emby API 密钥 |
| `TMDB_API_KEY` | ✅ | - | TMDB API 密钥（用于发现、推荐、日历等功能） |
| `OMDB_API_KEYS` | ❌ | - | OMDb API 密钥，多个用逗号分隔（用于外部评分） |
| `ALLOWED_EMBY_USERS` | ❌ | 空（所有用户） | 允许访问的 Emby 用户，逗号分隔 |
| `SECRET_KEY` | ❌ | `change-this-secret-key` | JWT 密钥，生产环境请修改 |
| `ADMIN_USERNAME` | ❌ | `admin` | 管理员用户名 |
| `ADMIN_PASSWORD` | ❌ | `admin123` | 管理员密码 |
| `SYNC_INTERVAL_MINUTES` | ❌ | `30` | 自动同步间隔（分钟），设为 0 禁用 |
| `SYNC_ON_STARTUP` | ❌ | `true` | 启动时是否自动同步 |

## 获取 API 密钥

### Emby API Key

1. 登录 Emby 管理后台
2. 进入 **设置** → **API 密钥**
3. 点击 **新建 API 密钥**
4. 输入应用名称（如 `Emby Tracker`），保存
5. 复制生成的 API 密钥

### TMDB API Key

1. 访问 [TMDB](https://www.themoviedb.org/) 并注册账户
2. 进入 **设置** → **API**
3. 申请 API 密钥（选择 Developer）
4. 复制 **API Key (v3 auth)**

### OMDb API Key（可选，用于外部评分）

1. 访问 [OMDb API](https://www.omdbapi.com/apikey.aspx)
2. 选择免费计划（每天 1000 次请求）
3. 填写邮箱，验证后获取 API Key
4. 建议申请多个 Key 以增加配额，用逗号分隔配置

## 功能详解

### 外部评分（IMDB/烂番茄/Metacritic）

本项目集成了 OMDb API，可获取 IMDB、烂番茄、Metacritic 等外部评分。

**实现方式：**
- 后端服务 `services/omdb.py` 封装 OMDb API，支持多 Key 轮询
- 评分数据缓存到 SQLite 数据库，7天有效期
- 支持通过 IMDB ID 或标题+年份查询

**使用方式：**
1. 在 `.env` 中配置 `OMDB_API_KEYS`
2. 进入 **设置** 页面，点击 **同步外部评分**
3. 系统会扫描 Emby 媒体库，批量获取评分并缓存
4. 在影片详情页可查看 IMDB/烂番茄/Metacritic 评分
5. 可开启 **在影片列表显示 IMDB 评分** 开关，在所有卡片上显示评分

**注意事项：**
- 免费 API Key 每天限制 1000 次请求
- 建议申请 2-3 个 Key 以增加配额
- 已缓存的评分不会重复请求，除非强制刷新
- 评分可点击跳转到对应平台官网

### 日历视图

显示追剧更新时间表和即将上映的电影。

**实现方式：**
- 后端从 TMDB 获取剧集播出日期和电影上映日期
- 支持周视图/月视图切换
- 支持筛选：全部/剧集/电影/我的剧集

**使用方式：**
- 点击日历项可跳转到详情页
- 支持导出 iCal 格式，可导入到日历应用

### 剧集进度追踪

追踪剧集观看进度，显示完成百分比。

**实现方式：**
- 后端计算每部剧集的观看进度（已看集数/总集数）
- 支持按季展开查看详细进度
- 显示下一集提醒

**使用方式：**
- 进入 **进度** 页面查看所有正在追的剧集
- 点击剧集可展开查看每季进度
- 点击 **下一集** 可快速跳转

### 统计功能

提供丰富的观影数据可视化。

**包含内容：**
- 概览统计：电影/剧集数量、观看时长、完成进度
- 类型分布：饼图展示最爱的类型
- 评分分布：柱状图展示评分区间分布
- 观看趋势：30天每日观看数量折线图
- 热力图：类似 GitHub 的观看活跃度热力图
- 时段分布：早/中/晚/深夜观看习惯
- 星期分布：每周各天的观看数量
- 连续天数：当前和最长连续观看天数

### 年度回顾

类似 Spotify Wrapped 的年度观影总结。

**包含内容：**
- 年度总观看数量和时长
- 最爱的类型 Top 5
- 评分最高的电影/剧集
- 看得最多的剧集
- 月度观看分布图表
- 里程碑成就
- 第一部/最后一部观看
- 最忙的一天
- 最爱观看时段

### 自定义列表

创建多个列表管理影片。

**功能：**
- 创建/编辑/删除列表
- 添加/移除列表项
- 拖拽排序
- 设置列表封面和描述
- 公开分享链接

### 数据导入/导出

**导出格式：**
- 观看历史（JSON）
- 想看列表（JSON）
- 我的评分（JSON）
- 自定义列表（JSON）
- 完整备份（包含所有数据）

**导入支持：**
- 从 Trakt 导入历史（JSON 格式）
- 从备份恢复

## 技术架构

### 后端

- **框架**: Python FastAPI
- **数据库**: SQLite + SQLAlchemy（异步）
- **外部 API**: Emby API、TMDB API、OMDb API

### 前端

- **框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **样式**: TailwindCSS
- **路由**: Vue Router

### 数据模型

| 模型 | 说明 |
|------|------|
| `User` | 系统用户（管理员/访客） |
| `WatchHistory` | 观看历史记录 |
| `Watchlist` | 想看列表 |
| `MediaCache` | TMDB 数据缓存 |
| `HeroSlide` | 首页轮播配置 |
| `CustomList` | 自定义列表 |
| `CustomListItem` | 列表项 |
| `UserRating` | 用户评分 |
| `Checkin` | Check-in 记录 |
| `ExternalRating` | 外部评分缓存 |

### API 路由

| 路由前缀 | 说明 |
|----------|------|
| `/api/auth` | 认证相关 |
| `/api/emby` | Emby 数据代理 |
| `/api/tmdb` | TMDB 数据代理 |
| `/api/stats` | 统计数据 |
| `/api/history` | 观看历史 |
| `/api/watchlist` | 想看列表 |
| `/api/calendar` | 日历数据 |
| `/api/progress` | 剧集进度 |
| `/api/recommend` | 推荐系统 |
| `/api/lists` | 自定义列表 |
| `/api/ratings` | 用户评分 |
| `/api/checkin` | Check-in |
| `/api/export` | 导入/导出 |
| `/api/hero` | 轮播管理 |
| `/api/external-ratings` | 外部评分 |

## Nginx 反向代理

如需通过域名访问，请参考 `nginx.conf.example` 文件。

关键配置：
- 设置 `client_max_body_size 50M` 以支持数据导入
- API 路由设置较长超时（300s）以支持同步操作
- 启用 WebSocket 支持

> **重要**：`EMBY_URL` 环境变量需要设置为浏览器可访问的地址，因为前端需要直接加载 Emby 的图片资源。

## 注意事项

1. **EMBY_URL 配置**：必须是浏览器可访问的地址，不能是 Docker 内部地址
2. **API 配额**：OMDb 免费 Key 每天 1000 次，建议多申请几个
3. **数据同步**：首次使用建议手动触发一次同步
4. **外部评分**：需要先同步才能在详情页和卡片上显示
5. **日历数据**：依赖 TMDB API，需要正确配置 TMDB_API_KEY

## 常见问题

**Q: 图片无法加载？**
A: 检查 `EMBY_URL` 是否为浏览器可访问的地址。

**Q: 外部评分不显示？**
A: 1) 检查是否配置了 `OMDB_API_KEYS`；2) 在设置页面点击同步；3) 确认 API 配额未用尽。

**Q: 同步很慢？**
A: 首次同步需要获取所有媒体信息，后续同步会快很多。

**Q: 如何备份数据？**
A: 在设置页面点击"完整备份"下载 JSON 文件，或直接备份 `data/emby_tracker.db` 文件。

## License

MIT License
