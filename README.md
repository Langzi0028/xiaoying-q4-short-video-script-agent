# 短视频脚本 Agent（Q4）

一个可运行、可审计的 CLI Agent：它根据主题、受众、目标时长、风格、产品事实和品牌规则，从安全的合成素材库生成可编辑短视频脚本。

## 快速开始

在本题目录运行：

```powershell
python -m pip install -r requirements.txt
python main.py run --topic "P01 字幕功能" --audience "短视频创作者" --target-seconds 30 --style "轻快" --material-id P01
python -m pytest -v
```

CLI 的 stdout 是单个机器可读 JSON；配置与 fallback 提示只输出至 stderr。

## 评审入口

- 需求与范围：`docs/01-requirements.md`
- Agent 闭环与安全边界：`docs/02-solution.md`
- 测试、结果和证据矩阵：`docs/03-evaluation.md`
- 实际运行证据：`examples/`

## 模型与安全

`.env` 是可选本地配置，环境变量优先。配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 和 `LLM_API_MODE=chat_completions` 后，程序会发起受限的在线动作选择并记录 `decision_source: live_llm`；缺失配置或调用异常时自动降级并标记 `fallback`。不要提交 API Key、私有网关 URL、数据库或运行日志；这些路径已在 `.gitignore` 中忽略。

## 已知限制

素材和规则均为可审计的合成数据，未连接真实素材库、视频生成、发布平台或生产品牌规则系统。fallback 证明工具边界和流程正确，但不代表在线模型的决策质量。
