# 全学段数学证明导师 APK 打包指南

本目录包含将 Web 前端封装为 Android APK 的完整方案。

## 方案一：使用 WebView Gold（推荐，无需编程）

### 步骤：
1. 下载 **WebView Gold** 应用（Google Play 或 APKPure）
2. 输入以下配置：
   - URL: `https://your-railway-app.up.railway.app`
   - App Name: `数学证明导师`
   - Icon: 选择一个数学相关的图标
3. 生成 APK

## 方案二：使用 Android Studio（自定义开发）

### 文件结构
```
android/
├── README.md
├── app/
│   └── src/
│       └── main/
│           ├── java/
│           │   └── com/
│           │       └── mathtutor/
│           │           └── MainActivity.java
│           ├── res/
│           │   ├── layout/
│           │   │   └── activity_main.xml
│           │   ├── values/
│           │   │   ├── colors.xml
│           │   │   ├── strings.xml
│           │   │   └── themes.xml
│           │   └── mipmap-*/
│           │       └── ic_launcher.png
│           └── AndroidManifest.xml
└── build.gradle
```

## 快速打包工具

### 方法1：使用 PWABuilder（推荐）

1. 访问 https://www.pwabuilder.com/
2. 输入你的网站 URL
3. 点击 "Package for stores"
4. 选择 "Android" -> "Generate Package"
5. 下载生成的 APK

### 方法2：使用 Bubblewrap

```bash
# 安装 bubblewrap
npm install -g @anthropic/bubblewrap

# 初始化项目
bubblewrap init --manifest https://your-app.com/manifest.json

# 构建 APK
bubblewrap build
```

### 方法3：使用 Apache Cordova

```bash
# 安装 Cordova
npm install -g cordova

# 创建项目
cordova create math-tutor com.mathtutor MathTutor

# 添加 Android 平台
cd math-tutor
cordova platform add android

# 配置 config.xml 中的 start URL
# 编辑 config.xml:
# <content src="https://your-railway-app.up.railway.app" />

# 构建 APK
cordova build android
```

## 发布到应用商店

### Google Play Store
1. 注册 Google Play 开发者账号（$25）
2. 准备应用截图和描述
3. 生成签名 APK/AAB
4. 提交审核

### 国内应用市场
- 华为应用市场
- 小米应用商店
- OPPO 软件商店
- Vivo 应用商店
- 腾讯应用宝

## 注意事项

1. **HTTPS 必须**：所有主流应用市场要求 HTTPS
2. **权限声明**：WebView 需要网络权限
3. **用户体验**：添加启动画面和加载指示器
4. **离线支持**：建议实现基本的离线缓存

## 获取帮助

- PWA Builder: https://www.pwabuilder.com/docs
- Cordova 文档: https://cordova.apache.org/docs/
- Android 开发: https://developer.android.com/
