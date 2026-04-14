package com.example.mobileagent;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.os.Build;
import android.os.Bundle;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

public class AgentAccessibilityService extends AccessibilityService {

    public interface ScreenChangedListener {
        void onScreenChanged(ScreenState state);
    }

    private static volatile AgentAccessibilityService instance;
    private ScreenChangedListener onScreenChanged;

    public static AgentAccessibilityService getInstance() {
        return instance;
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        instance = null;
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        int type = event.getEventType();
        boolean isWindowChange = type == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED;
        boolean isContentChange = type == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED;
        if (!isWindowChange && !isContentChange) {
            return;
        }
        if (onScreenChanged != null) {
            onScreenChanged.onScreenChanged(getCurrentScreenState());
        }
    }

    public void setOnScreenChanged(ScreenChangedListener onScreenChanged) {
        this.onScreenChanged = onScreenChanged;
    }

    public ScreenState getCurrentScreenState() {
        AccessibilityNodeInfo rootNode = getRootInActiveWindow();
        if (rootNode == null) {
            return new ScreenState("", "", "（无法获取屏幕内容，请确认无障碍服务已开启）");
        }

        String uiTreeText = serializeUiTree(rootNode, 6);
        String packageName = rootNode.getPackageName() == null ? "" : rootNode.getPackageName().toString();
        return new ScreenState(packageName, "", uiTreeText);
    }

    private String serializeUiTree(AccessibilityNodeInfo root, int maxDepth) {
        StringBuilder sb = new StringBuilder();
        int[] counter = new int[]{0};
        serializeNode(root, 0, maxDepth, sb, counter);
        return sb.toString();
    }

    private void serializeNode(AccessibilityNodeInfo node, int depth, int maxDepth, StringBuilder sb, int[] counter) {
        if (node == null || depth > maxDepth) {
            return;
        }

        String id = "n" + counter[0]++;
        String indent = "  ".repeat(Math.max(0, depth));
        String className = node.getClassName() == null ? "View" : node.getClassName().toString();
        String shortClass = className.substring(className.lastIndexOf('.') + 1);

        StringBuilder attrs = new StringBuilder();
        CharSequence text = node.getText();
        CharSequence desc = node.getContentDescription();
        if (text != null && text.length() > 0) {
            attrs.append("text=\"").append(text).append("\" ");
        }
        if (desc != null && desc.length() > 0) {
            attrs.append("desc=\"").append(desc).append("\" ");
        }
        if (node.isClickable()) attrs.append("clickable ");
        if (node.isScrollable()) attrs.append("scrollable ");
        if (node.isEditable()) attrs.append("editable ");

        if (attrs.length() > 0 || node.getChildCount() > 0) {
            sb.append(indent)
                    .append("[").append(id).append("] ")
                    .append(shortClass)
                    .append(" ")
                    .append(attrs.toString().trim())
                    .append("\n");
        }

        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                serializeNode(child, depth + 1, maxDepth, sb, counter);
            }
        }
    }

    public AccessibilityNodeInfo findNodeById(String nodeId) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) {
            return null;
        }
        int[] counter = new int[]{0};
        return findNodeRecursive(root, nodeId, counter);
    }

    private AccessibilityNodeInfo findNodeRecursive(AccessibilityNodeInfo node, String targetId, int[] counter) {
        String currentId = "n" + counter[0]++;
        if (currentId.equals(targetId)) {
            return node;
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                AccessibilityNodeInfo found = findNodeRecursive(child, targetId, counter);
                if (found != null) {
                    return found;
                }
            }
        }
        return null;
    }

    public boolean clickByNodeId(String nodeId) {
        AccessibilityNodeInfo node = findNodeById(nodeId);
        return node != null && node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
    }

    public void clickByCoordinate(float x, float y) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) {
            return;
        }
        Path path = new Path();
        path.moveTo(x, y);
        GestureDescription gesture = new GestureDescription.Builder()
                .addStroke(new GestureDescription.StrokeDescription(path, 0, 50))
                .build();
        dispatchGesture(gesture, null, null);
    }

    public boolean inputText(String nodeId, String text) {
        AccessibilityNodeInfo node = findNodeById(nodeId);
        if (node == null) {
            return false;
        }
        Bundle args = new Bundle();
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text);
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
    }

    public void swipe(float startX, float startY, float endX, float endY, long durationMs) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) {
            return;
        }
        Path path = new Path();
        path.moveTo(startX, startY);
        path.lineTo(endX, endY);
        GestureDescription gesture = new GestureDescription.Builder()
                .addStroke(new GestureDescription.StrokeDescription(path, 0, durationMs))
                .build();
        dispatchGesture(gesture, null, null);
    }

    public void scroll(AgentAction.Direction direction) {
        float sx;
        float sy;
        float ex;
        float ey;

        switch (direction) {
            case UP:
                sx = 540f;
                sy = 1600f;
                ex = 540f;
                ey = 800f;
                break;
            case DOWN:
                sx = 540f;
                sy = 800f;
                ex = 540f;
                ey = 1600f;
                break;
            case LEFT:
                sx = 900f;
                sy = 1200f;
                ex = 180f;
                ey = 1200f;
                break;
            case RIGHT:
            default:
                sx = 180f;
                sy = 1200f;
                ex = 900f;
                ey = 1200f;
                break;
        }
        swipe(sx, sy, ex, ey, 300);
    }

    public boolean goBack() {
        return performGlobalAction(GLOBAL_ACTION_BACK);
    }

    public boolean goHome() {
        return performGlobalAction(GLOBAL_ACTION_HOME);
    }

    @Override
    public void onInterrupt() {
    }
}
