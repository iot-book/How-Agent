package com.example.mobileagent;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private EditText etTask;
    private Button btnStart;
    private Button btnA11y;
    private TextView tvStatus;
    private ProgressBar progressBar;

    private final LlmClient llmClient = new MockLlmClient();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupListeners();
        checkA11yServiceStatus();
    }

    @Override
    protected void onResume() {
        super.onResume();
        checkA11yServiceStatus();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdownNow();
    }

    private void initViews() {
        etTask = findViewById(R.id.et_task);
        btnStart = findViewById(R.id.btn_start);
        btnA11y = findViewById(R.id.btn_a11y_settings);
        tvStatus = findViewById(R.id.tv_status);
        progressBar = findViewById(R.id.progress_bar);
    }

    private void setupListeners() {
        btnStart.setOnClickListener(v -> {
            String task = etTask.getText().toString().trim();
            if (task.isEmpty()) {
                showStatus("请先输入要执行的任务");
                return;
            }
            startAgentTask(task);
        });

        btnA11y.setOnClickListener(v -> {
            startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            showStatus("请在设置中找到「MobileAgentDemo」并开启");
        });
    }

    private void startAgentTask(String task) {
        AgentAccessibilityService a11yService = AgentAccessibilityService.getInstance();
        if (a11yService == null) {
            showStatus("❌ 无障碍服务未开启\n请点击下方按钮前往设置开启");
            btnA11y.setVisibility(View.VISIBLE);
            return;
        }

        setUiRunning(true);
        showStatus("⏳ 开始执行任务：" + task + "\n\n（使用模拟大模型，不调用真实 API）");

        executor.submit(() -> {
            TaskEngine engine = new TaskEngine(a11yService, llmClient);
            TaskEngine.TaskResult result;
            try {
                result = engine.executeTask(task);
            } catch (Exception e) {
                result = new TaskEngine.Failure("执行异常：" + e.getMessage());
            }

            TaskEngine.TaskResult finalResult = result;
            mainHandler.post(() -> {
                setUiRunning(false);
                if (finalResult instanceof TaskEngine.Success success) {
                    showStatus("✅ 任务完成！\n\n执行步数：" + success.steps + " 步\n结果：" + success.summary);
                } else if (finalResult instanceof TaskEngine.Failure failure) {
                    showStatus("❌ 任务失败\n\n原因：" + failure.reason);
                }
            });
        });
    }

    private void setUiRunning(boolean isRunning) {
        btnStart.setEnabled(!isRunning);
        progressBar.setVisibility(isRunning ? View.VISIBLE : View.GONE);
    }

    private void showStatus(String text) {
        tvStatus.setText(text);
    }

    private void checkA11yServiceStatus() {
        boolean isRunning = AgentAccessibilityService.getInstance() != null;
        if (isRunning) {
            btnA11y.setVisibility(View.GONE);
            showStatus("✅ 无障碍服务已开启，可以开始执行任务");
        } else {
            btnA11y.setVisibility(View.VISIBLE);
            showStatus("⚠️ 需要先开启无障碍服务\n点击下方按钮前往设置");
        }
    }
}
