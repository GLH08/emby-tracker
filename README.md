# Emby Tracker

一个现代化的 Emby 媒体库管理和观影记录追踪应用。

## 功能特性

- 🎬 **媒体库浏览** - 浏览 Emby 服务器中的电影和剧集
- 📊 **观影统计** - 类型分布、评分分布、观看时长统计
- 📝 **观看历史** - 本地存储观看记录，支持自动同步
- 🔍 **发现内容** - 基于 TMDB 的热门趋势、即将上映等
- 📌 **想看列表** - 收藏想看的影视作品
- 🎨 **自定义轮播** - 自定义首页轮播海报
- 👥 **多用户支持** - 支持管理员和访客账户
- 🔄 **自动同步** - 启动时和定时自动同步观看记录

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
| `TMDB_API_KEY` | ✅ | - | TMDB API 密钥 |
| `ALLOWED_EMBY_USERS` | ❌ | 空（所有用户） | 允许访问的 Emby 用户，逗号分隔（支持用户名或用户ID） |
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

## Nginx 反向代理

如需通过域名访问，可参考以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 客户端请求体大小限制（用于数据导入）
    client_max_body_size 50M;

    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        
        # 基础代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如需实时功能）
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 禁用缓冲（用于流式响应）
        proxy_buffering off;
    }

    # API 路由（可选：单独配置更长超时）
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API 可能需要更长超时（如同步操作）
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

> **注意**：`EMBY_URL` 环境变量需要设置为浏览器可访问的地址，因为前端需要直接加载 Emby 的图片资源。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + TailwindCSS
- **部署**: Docker + Nginx

## 截图

（待添加）

## License

MIT License
