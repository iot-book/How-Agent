package com.example.mobileagent;

import android.content.Intent;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TaskEngine {

    public abstract static class TaskResult {
        private TaskResult() {
        }
    }

    public static final class Success extends TaskResult {
        public final String summary;
        public final int steps;

        public Success(String summary, int steps) {
            this.summary = summary;
            this.steps = steps;
        }
    }

    public static final class Failure extends TaskResult {
        public final String reason;

        public Failure(String reason) {
            this.reason = reason;
        }
    }

    private final AgentAccessibilityService a11yService;
    private final LlmClient llmClient;
    private final List<Message> conversationHistory = new ArrayList<>();
    private final int maxSteps = 20;

    public TaskEngine(AgentAccessibilityService a11yService, LlmClient llmClient) {
        this.a11yService = a11yService;
        this.llmClient = llmClient;
    }

    public TaskResult executeTask(String userInstruction) throws Exception {
        conversationHistory.clear();
        conversationHistory.add(new Message("system", buildSystemPrompt()));
        conversationHistory.add(new Message("user", "用户任务：" + userInstruction));

        for (int step = 1; step <= maxSteps; step++) {
            ScreenState screenState = a11yService.getCurrentScreenState();
            conversationHistory.add(new Message("user", buildObservationText(screenState)));

            String llmResponse = llmClient.chat(conversationHistory);
            conversationHistory.add(new Message("assistant", llmResponse));

            AgentAction action = parseAction(llmResponse);
            if (action == null) {
                continue;
            }

            if (action instanceof AgentAction.Done done) {
                return new Success(done.summary, step);
            }

            if (action instanceof AgentAction.Click click) {
                if (click.nodeId != null && !click.nodeId.isBlank()) {
                    a11yService.clickByNodeId(click.nodeId);
                } else {
                    a11yService.clickByCoordinate(click.x, click.y);
                }
            } else if (action instanceof AgentAction.Type type) {
                if (type.nodeId != null && !type.nodeId.isBlank()) {
                    a11yService.inputText(type.nodeId, type.text);
                }
            } else if (action instanceof AgentAction.Scroll scroll) {
                a11yService.scroll(scroll.direction);
            } else if (action instanceof AgentAction.SystemIntent systemIntent) {
                executeSystemIntent(systemIntent);
            } else if (action instanceof AgentAction.Wait) {
                Thread.sleep(1500);
            }

            Thread.sleep(800);
        }

        return new Failure("超过最大步数限制（" + maxSteps + " 步），任务未完成");
    }

    private String buildSystemPrompt() {
        return """
            你是一个 Android 手机操作助手。你会收到 UI 元素树。
            你必须输出 JSON 动作，type 仅可为 click/type/scroll/system_intent/wait/done。
            规则：每次只输出一个动作，优先使用 node_id。
            """;
    }

    private String buildObservationText(ScreenState state) {
        StringBuilder sb = new StringBuilder();
        sb.append("=== 当前屏幕状态 ===\n");
        if (state.packageName != null && !state.packageName.isEmpty()) {
            sb.append("当前 App：").append(state.packageName).append("\n");
        }
        sb.append("UI 元素树：\n");
        sb.append(state.uiTreeText == null ? "（空白屏幕）" : state.uiTreeText).append("\n");
        sb.append("请根据以上状态，决定下一步操作。\n");
        return sb.toString();
    }

    private AgentAction parseAction(String json) {
        try {
            String type = extractJsonField(json, "type");
            if (type == null) {
                return null;
            }

            switch (type) {
                case "click": {
                    String nodeId = extractJsonField(json, "node_id");
                    String xStr = extractJsonNumber(json, "x");
                    String yStr = extractJsonNumber(json, "y");
                    int x = xStr == null ? 0 : Integer.parseInt(xStr);
                    int y = yStr == null ? 0 : Integer.parseInt(yStr);
                    return new AgentAction.Click(nodeId, x, y);
                }
                case "type": {
                    String nodeId = extractJsonField(json, "node_id");
                    String text = extractJsonField(json, "text");
                    return new AgentAction.Type(nodeId, text == null ? "" : text);
                }
                case "scroll": {
                    String directionRaw = extractJsonField(json, "direction");
                    AgentAction.Direction direction;
                    if ("up".equals(directionRaw)) {
                        direction = AgentAction.Direction.UP;
                    } else if ("left".equals(directionRaw)) {
                        direction = AgentAction.Direction.LEFT;
                    } else if ("right".equals(directionRaw)) {
                        direction = AgentAction.Direction.RIGHT;
                    } else {
                        direction = AgentAction.Direction.DOWN;
                    }
                    return new AgentAction.Scroll(direction);
                }
                case "system_intent": {
                    String intentAction = extractJsonField(json, "intent_action");
                    String pkg = extractJsonField(json, "package");
                    Map<String, Object> extras = new HashMap<>();
                    if (pkg != null) {
                        extras.put("package", pkg);
                    }
                    return new AgentAction.SystemIntent(intentAction == null ? "" : intentAction, extras);
                }
                case "wait":
                    return new AgentAction.Wait();
                case "done": {
                    String summary = extractJsonField(json, "summary");
                    return new AgentAction.Done(summary == null ? "任务完成" : summary);
                }
                default:
                    return null;
            }
        } catch (Exception e) {
            return null;
        }
    }

    private String extractJsonField(String json, String key) {
        Pattern pattern = Pattern.compile("\\\"" + key + "\\\"\\s*:\\s*\\\"([^\\\"]*?)\\\"");
        Matcher matcher = pattern.matcher(json);
        return matcher.find() ? matcher.group(1) : null;
    }

    private String extractJsonNumber(String json, String key) {
        Pattern pattern = Pattern.compile("\\\"" + key + "\\\"\\s*:\\s*([0-9]+)");
        Matcher matcher = pattern.matcher(json);
        return matcher.find() ? matcher.group(1) : null;
    }

    private void executeSystemIntent(AgentAction.SystemIntent action) {
        Intent intent = new Intent(action.action);
        Object pkg = action.extras.get("package");
        if (pkg instanceof String) {
            intent.setPackage((String) pkg);
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            a11yService.startActivity(intent);
        } catch (Exception ignored) {
        }
    }
}
