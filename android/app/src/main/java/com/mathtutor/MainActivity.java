package com.mathtutor;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.pm.ActivityInfo;
import android.graphics.Bitmap;
import android.net.http.SslError;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

/**
 * 全学段数学证明导师 - Android WebView 主界面
 * 将 Web 应用封装为原生 Android 应用
 */
public class MainActivity extends Activity {

    // TODO: 部署后替换为你的 Railway URL
    private static final String WEB_URL = "https://your-app-name.up.railway.app";
    
    private WebView webView;
    private ProgressBar progressBar;
    private View loadingView;
    private boolean isLoading = false;
    
    // 用于 JS 交互的接口名称
    private static final String JS_INTERFACE_NAME = "AndroidApp";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 全屏设置
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        
        setContentView(R.layout.activity_main);
        
        // 初始化视图
        initViews();
        
        // 配置 WebView
        configureWebView();
    }
    
    private void initViews() {
        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progress_bar);
        loadingView = findViewById(R.id.loading_view);
        
        // 显示加载动画
        showLoading();
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        
        // 启用 JavaScript
        settings.setJavaScriptEnabled(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        
        // 启用 DOM Storage
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        
        // 启用缓存
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAppCacheEnabled(true);
        
        // 支持缩放
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        
        // 支持视口
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        
        // 允许访问文件
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        
        // 混合内容模式
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }
        
        // 设置 WebViewClient
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                isLoading = true;
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                isLoading = false;
                hideLoading();
            }
            
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                // 处理加载错误
                if (request.isForMainFrame()) {
                    showErrorDialog("加载失败，请检查网络连接");
                }
            }
            
            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                // 对于开发环境，可以选择忽略 SSL 错误
                // 生产环境强烈建议使用有效证书
                handler.proceed();
            }
        });
        
        // 设置 WebChromeClient
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                super.onProgressChanged(view, newProgress);
                if (progressBar != null) {
                    progressBar.setProgress(newProgress);
                }
            }
        });
        
        // 添加 JavaScript 接口
        webView.addJavascriptInterface(new JSInterface(), JS_INTERFACE_NAME);
        
        // 加载网页
        webView.loadUrl(WEB_URL);
    }
    
    /**
     * JavaScript 接口类
     * 允许网页调用原生 Android 功能
     */
    private class JSInterface {
        
        @JavascriptInterface
        public void showToast(String message) {
            new Handler(Looper.getMainLooper()).post(() -> 
                Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show()
            );
        }
        
        @JavascriptInterface
        public String getAppVersion() {
            return "1.0.0";
        }
        
        @JavascriptInterface
        public void shareContent(String title, String content) {
            new Handler(Looper.getMainLooper()).post(() -> {
                android.content.Intent shareIntent = new android.content.Intent();
                shareIntent.setAction(android.content.Intent.ACTION_SEND);
                shareIntent.putExtra(android.content.Intent.EXTRA_TEXT, title + "\n" + content);
                shareIntent.setType("text/plain");
                startActivity(android.content.Intent.createChooser(shareIntent, "分享到"));
            });
        }
    }
    
    private void showLoading() {
        if (loadingView != null) {
            loadingView.setVisibility(View.VISIBLE);
        }
    }
    
    private void hideLoading() {
        if (loadingView != null) {
            loadingView.setVisibility(View.GONE);
        }
    }
    
    private void showErrorDialog(String message) {
        new AlertDialog.Builder(this)
            .setTitle("提示")
            .setMessage(message)
            .setPositiveButton("重试", (dialog, which) -> {
                webView.reload();
            })
            .setNegativeButton("取消", null)
            .show();
    }
    
    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
    
    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.onPause();
        }
    }
}
