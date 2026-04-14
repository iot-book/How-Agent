## Demo

一个运行在 Android 手机上的 AI 智能体框架，包含以下核心组件：

```
用户输入任务
    ↓
TaskEngine（PDA 循环）
    ↓           ↓           ↓
  感知层       决策层       行动层
AgentA11y   LlmClient   执行点击
Service     （大模型）    输入文字
（读屏幕）               滑动屏幕
```

**PDA 循环**（感知 → 决策 → 行动）每步的工作：
1. **感知**：通过 Android 无障碍服务读取当前屏幕上所有 UI 元素
2. **决策**：把 UI 信息发给大模型，让它决定"下一步点哪里"
3. **行动**：执行大模型给出的操作（点击、输入、滑动等）

---

## 文件结构说明

```
MobileAgentDemo/
├── app/src/main/
│   ├── java/com/example/mobileagent/
│   │   ├── AgentAction.java               ← 智能体动作 + 屏幕状态的数据类定义
│   │   ├── LlmClient.java                 ← 大模型接口 + 模拟实现（无需 API Key）
│   │   ├── AgentAccessibilityService.java ← 感知层：读屏幕 + 模拟操作
│   │   ├── TaskEngine.java                ← 核心：PDA 主循环调度器
│   │   └── MainActivity.java              ← 用户界面（极简）
│   │
│   ├── res/
│   │   ├── layout/activity_main.xml       ← 主界面布局
│   │   ├── xml/agent_accessibility_config.xml ← 无障碍服务配置
│   │   └── values/strings.xml             ← 文字资源
│   │
│   └── AndroidManifest.xml               ← App 配置 + 权限声明
│
├── app/build.gradle.kts                   ← App 依赖配置
├── build.gradle.kts                       ← 根项目配置
└── settings.gradle.kts                    ← 项目设置
```

---

## 快速上手

### 第一步：环境准备

1. 安装 [Android Studio](https://developer.android.com/studio)（推荐最新稳定版）
2. 用 Android Studio 打开 `MobileAgentDemo/` 目录（File → Open → 选择此文件夹）
3. 等待 Gradle 同步完成

### 第二步：运行 Demo（无需真实大模型）

Demo 内置了 `MockLlmClient`（模拟大模型），**不需要配置任何 API Key**，可以直接运行来查看完整流程。

1. 连接 Android 手机或启动模拟器（建议 Android 8.0 及以上）
2. 点击 Android Studio 的 ▶️ Run 按钮，将 App 安装到设备
3. 在手机上打开 App，点击「开启无障碍服务」按钮
4. 在手机设置中找到「MobileAgentDemo」并开启无障碍服务
5. 返回 App，输入任意任务描述，点击「开始执行任务」

> 使用模拟大模型时，智能体会按预设的脚本执行"搜索咖啡店"的步骤，
> 并不会真正操作手机，只是演示 PDA 循环的运转流程。

### 第三步：接入真实大模型（可选）

在 `LlmClient.java` 中实现真实的 LLM 客户端。
以 OpenAI 为例，实现 `LlmClient` 接口：

```java
public final class OpenAiClient implements LlmClient {
    private final String apiKey;

    public OpenAiClient(String apiKey) {
        this.apiKey = apiKey;
    }

    @Override
    public String chat(List<Message> messages) throws Exception {
        // 调用 OpenAI Chat Completions API
        // POST https://api.openai.com/v1/chat/completions
        // 详见官方文档：https://platform.openai.com/docs/api-reference/chat
        throw new UnsupportedOperationException("在这里实现 API 调用");
    }
}
```

然后在 `MainActivity.java` 中替换：
```java
// 把这行：
private final LlmClient llmClient = new MockLlmClient();

// 换成：
private final LlmClient llmClient = new OpenAiClient("sk-你的API密钥");
```

---

## 核心概念对应关系

| 示例代码 | 教程中的概念 |
|---|---|
| `AgentAccessibilityService` | 感知层（Perception）+ 行动层（Action）|
| `LlmClient` | 决策层（Decision）|
| `TaskEngine.executeTask()` | PDA 循环 |
| `AgentAction.Done` | 任务终止条件 |
| `serializeUiTree()` | A11y 树文字序列化 |
| `MockLlmClient` | 用于演示流程的桩代码（Stub）|

---