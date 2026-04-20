# 全学段数学证明导师 - Railway 部署指南

## 目录

- [快速部署](#快速部署)
- [详细配置](#详细配置)
- [环境变量](#环境变量)
- [自定义域名](#自定义域名)
- [监控与日志](#监控与日志)
- [故障排查](#故障排查)

## 快速部署

### 方法一：使用 Railway CLI

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 初始化项目
cd 全学段数学证明导师
railway init

# 4. 部署
railway up

# 5. 设置环境变量
railway variables set DEEPSEEK_API_KEY=your_api_key_here
```

### 方法二：使用 GitHub 部署

1. 将项目推送到 GitHub 仓库
2. 访问 [Railway](https://railway.app)
3. 点击 "New Project" -> "Deploy from GitHub repo"
4. 选择你的仓库
5. 添加环境变量

## 详细配置

### 1. 创建 `.env` 文件

```bash
cd 全学段数学证明导师
cp .env.example .env
```

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
FLASK_DEBUG=False
PORT=5000
```

### 2. Railway 环境变量

在 Railway Dashboard 中设置以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| DEEPSEEK_API_KEY | 你的API Key | DeepSeek API 密钥 |
| DEEPSEEK_BASE_URL | https://api.deepseek.com | API 地址 |
| DEEPSEEK_MODEL | deepseek-chat | 模型名称 |
| FLASK_DEBUG | false | 调试模式 |

### 3. 获取 DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com)
2. 注册并登录
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制并保存（只显示一次）

## Railway 免费版限制

| 资源 | 免费额度 |
|------|----------|
| 项目数 | 3 个 |
| 内存 | 512 MB |
| CPU | 共享 |
| 磁盘 | 1 GB |
| 带宽 | 100 GB/月 |
| 睡眠策略 | 500小时后休眠 |

### 避免休眠

Railway 免费版在 500 小时无请求后会休眠。保持活跃的方法：

1. 使用 UptimeRobot 或类似服务监控
2. 设置定期健康检查
3. 升级到付费版本

## 自定义域名

1. 在 Railway 项目设置中点击 "Settings"
2. 找到 "Networking" -> "Public Networking"
3. 添加自定义域名
4. 在你的 DNS 服务商处添加 CNAME 记录
5. 等待 SSL 证书自动配置

## 监控与日志

### 查看日志

```bash
railway logs
```

### 实时日志

```bash
railway logs -f
```

### 部署历史

在 Railway Dashboard 的 "Deployments" 标签页查看。

## 故障排查

### 常见问题

#### 1. 部署失败

检查：
- `requirements_simple.txt` 格式是否正确
- Python 版本是否兼容
- 环境变量是否设置

#### 2. API 调用失败

检查：
- DEEPSEEK_API_KEY 是否正确
- API Key 是否有额度
- 网络连接是否正常

#### 3. 内存超限

Railway 免费版限制 512MB。精简依赖：

```bash
# 检查内存使用
railway status
```

### 获取帮助

- Railway 文档: https://docs.railway.app
- GitHub Issues: https://github.com/railwayapp/railway/issues
