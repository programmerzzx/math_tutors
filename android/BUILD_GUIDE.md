# APK 打包配置说明

## 构建步骤

### 1. 使用 Android Studio

1. 打开 Android Studio
2. 选择 "Open an Existing Project"
3. 选择 `android` 目录
4. 等待 Gradle 同步完成
5. 连接 Android 设备或启动模拟器
6. 点击 Run 按钮

### 2. 使用命令行构建 APK

```bash
cd android

# 确保已安装 Android SDK
export ANDROID_HOME=/path/to/android/sdk

# 构建 Debug APK
./gradlew assembleDebug

# 构建 Release APK (需要签名)
./gradlew assembleRelease
```

### 3. APK 输出位置

- Debug APK: `app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `app/build/outputs/apk/release/app-release.apk`

## 配置说明

### 修改 Web URL

编辑 `MainActivity.java`，修改 `WEB_URL` 常量：

```java
private static final String WEB_URL = "https://your-actual-railway-url.up.railway.app";
```

### 应用签名（发布时需要）

1. 生成签名密钥：
```bash
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

2. 在 `app/build.gradle` 中配置签名：
```gradle
android {
    signingConfigs {
        release {
            storeFile file('my-release-key.jks')
            storePassword 'your_password'
            keyAlias 'my-key-alias'
            keyPassword 'your_password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

## 常见问题

### Q: 构建失败提示 SDK 版本问题
A: 确保已安装对应版本的 Android SDK，并在 Android Studio 中配置正确的 SDK 路径。

### Q: WebView 无法加载 HTTPS 页面
A: 在 `MainActivity.java` 中，`onReceivedSslError` 方法已配置为忽略 SSL 错误。生产环境请使用有效证书。

### Q: 如何获取设备日志
```bash
adb logcat | grep "com.mathtutor"
```
