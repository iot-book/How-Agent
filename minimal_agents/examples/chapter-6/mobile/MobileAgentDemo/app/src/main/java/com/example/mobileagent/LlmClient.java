package com.example.mobileagent;

import java.util.ArrayList;
import java.util.List;

public interface LlmClient {
    String chat(List<Message> messages) throws Exception;
}

class Message {
    public final String role;
    public final String content;

    Message(String role, String content) {
        this.role = role;
        this.content = content;
    }
}

class MockLlmClient implements LlmClient {
    private final List<String> mockResponses = new ArrayList<>();
    private int currentStep = 0;

    MockLlmClient() {
        mockResponses.add("""
            {
              \"thought\": \"当前在主屏幕，需要先打开地图 App\",
              \"action\": {
                \"type\": \"system_intent\",
                \"intent_action\": \"android.intent.action.MAIN\",
                \"package\": \"com.autonavi.minimap\"
              }
            }
            """);

        mockResponses.add("""
            {
              \"thought\": \"看到搜索框，点击进入\",
              \"action\": {
                \"type\": \"click\",
                \"node_id\": \"n1\"
              }
            }
            """);

        mockResponses.add("""
            {
              \"thought\": \"输入关键词\",
              \"action\": {
                \"type\": \"type\",
                \"node_id\": \"n1\",
                \"text\": \"咖啡店\"
              }
            }
            """);

        mockResponses.add("""
            {
              \"thought\": \"任务完成\",
              \"action\": {
                \"type\": \"done\",
                \"summary\": \"已搜索附近咖啡店\"
              }
            }
            """);
    }

    @Override
    public synchronized String chat(List<Message> messages) throws Exception {
        Thread.sleep(500);
        if (currentStep < mockResponses.size()) {
            return mockResponses.get(currentStep++);
        }
        return "{\"thought\":\"任务已完成\",\"action\":{\"type\":\"done\",\"summary\":\"所有步骤已执行完毕\"}}";
    }

    public synchronized void reset() {
        currentStep = 0;
    }
}
