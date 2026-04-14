package com.example.mobileagent;

import android.graphics.Rect;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public abstract class AgentAction {

    public enum Direction {
        UP,
        DOWN,
        LEFT,
        RIGHT
    }

    public static final class Click extends AgentAction {
        public final String nodeId;
        public final int x;
        public final int y;

        public Click(String nodeId, int x, int y) {
            this.nodeId = nodeId;
            this.x = x;
            this.y = y;
        }
    }

    public static final class Type extends AgentAction {
        public final String nodeId;
        public final String text;

        public Type(String nodeId, String text) {
            this.nodeId = nodeId;
            this.text = text;
        }
    }

    public static final class Scroll extends AgentAction {
        public final Direction direction;

        public Scroll(Direction direction) {
            this.direction = direction;
        }
    }

    public static final class SystemIntent extends AgentAction {
        public final String action;
        public final Map<String, Object> extras;

        public SystemIntent(String action, Map<String, Object> extras) {
            this.action = action;
            this.extras = extras;
        }
    }

    public static final class Wait extends AgentAction {
    }

    public static final class Done extends AgentAction {
        public final String summary;

        public Done(String summary) {
            this.summary = summary;
        }
    }
}

class UiNode {
    public final String id;
    public final String className;
    public final String text;
    public final String contentDescription;
    public final Rect bounds;
    public final boolean isClickable;
    public final boolean isScrollable;
    public final boolean isEditable;
    public final List<UiNode> children;

    UiNode(
            String id,
            String className,
            String text,
            String contentDescription,
            Rect bounds,
            boolean isClickable,
            boolean isScrollable,
            boolean isEditable,
            List<UiNode> children
    ) {
        this.id = id;
        this.className = className;
        this.text = text;
        this.contentDescription = contentDescription;
        this.bounds = bounds;
        this.isClickable = isClickable;
        this.isScrollable = isScrollable;
        this.isEditable = isEditable;
        this.children = children == null ? new ArrayList<>() : children;
    }
}

class ScreenState {
    public final String packageName;
    public final String activityName;
    public final String uiTreeText;
    public final long timestamp;

    ScreenState(String packageName, String activityName, String uiTreeText) {
        this(packageName, activityName, uiTreeText, System.currentTimeMillis());
    }

    ScreenState(String packageName, String activityName, String uiTreeText, long timestamp) {
        this.packageName = packageName;
        this.activityName = activityName;
        this.uiTreeText = uiTreeText;
        this.timestamp = timestamp;
    }

    public String summary() {
        StringBuilder sb = new StringBuilder();
        sb.append("package=").append(packageName == null ? "" : packageName).append("\n");
        sb.append("activity=").append(activityName == null ? "" : activityName).append("\n");
        sb.append(uiTreeText == null ? "" : uiTreeText);
        return sb.toString();
    }

    public static ScreenState fromScreenshot(String base64Image) {
        return new ScreenState("", "", "[screenshot] " + base64Image);
    }
}
