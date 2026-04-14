// ============================================================
// build.gradle.kts  —  App 模块的构建配置
//
// 这个文件告诉 Android 构建工具（Gradle）：
//   - 使用哪个版本的 Android SDK
//   - 依赖哪些第三方库
//   - 如何编译打包这个 App
// ============================================================

plugins {
    id("com.android.application")
}

android {
    namespace = "com.example.mobileagent"

    compileSdk = 35  // 使用的 Android SDK 编译版本（使用最新稳定版）

    defaultConfig {
        applicationId = "com.example.mobileagent"
        minSdk = 26          // 最低支持 Android 8.0（API 26）——手势分发 API 需要此版本
        targetSdk = 35       // 目标 Android 版本
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    // AndroidX 基础库
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.constraintlayout:constraintlayout:2.2.0")

    // ── 可选依赖（接入真实大模型时取消注释） ──────────────────────────

    // OkHttp：HTTP 客户端，用于调用云端 LLM API
    // implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Gson：JSON 解析库，替换 TaskEngine 中的简化字符串解析
    // implementation("com.google.code.gson:gson:2.11.0")

    // ── 可选：接入端侧推理引擎 ──────────────────────────────────────
    // 以下库需要从各自项目的 Release 页面下载 AAR 文件手动集成

    // MediaPipe LLM Inference（Google，最简单的端侧推理方案）
    // implementation("com.google.mediapipe:tasks-genai:0.10.14")

    // MLC-LLM（CMU，支持更多模型架构）
    // 需从 https://llm.mlc.ai/docs/ 下载对应的 AAR 文件
}
