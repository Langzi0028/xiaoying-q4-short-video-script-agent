# 03 Evaluation

## 预期验证

| 验收点 | 自动化测试 | 实际证据 |
| --- | --- | --- |
| P01 首稿超时后压缩并复估 | `tests/test_workflow.py::test_p01_overlength_draft_is_compressed_and_reestimated` | `examples/01-p01-overlength.md` |
| 无素材改写后请求补充 | `tests/test_workflow.py::test_no_search_results_rewrites_once_then_requests_information` | `examples/02-no-material.md` |
| 无素材时直接请求补充 | `tests/test_decisions.py::test_no_result_decision_can_request_more_information_without_a_rewrite` | 自动化动作选择回归测试 |
| 工具失败不会伪造成功 | `tests/test_guards.py::test_tool_failure_never_reports_success` | `examples/03-tool-failure.md` |
| 执行上限明确未完成 | `tests/test_guards.py::test_execution_limit_returns_explicit_incomplete_status` | `examples/04-execution-limit.md` |
| 规则阻断、Trace 和 CLI JSON 边界 | `tests/test_guards.py`、`tests/test_cli.py` | `examples/01-p01-overlength.md` |
| 受限在线动作选择的标记边界 | `tests/test_decisions.py::test_live_decision_source_is_recorded_after_a_legal_online_choice` | `examples/05-live-llm-decision.json`（仅在本地配置真实模型后生成） |
| 在线模型异常的安全降级 | `tests/test_llm_failure.py::test_live_llm_failure_prints_only_exception_type_then_falls_back` | 自动化 CLI 回归测试 |

## 实际结果

在最终交付前从题目根目录运行 `python -m pytest -v` 和代表性 `python main.py ...` 命令。详见终端验证输出；未配置在线模型时，所有证据都明确标记 `fallback`。

## 失败行为

- 规则风险：`blocked`，不生成分镜。
- 无素材：`needs_info`，不返回素材 ID。
- 工具异常：`failed` / `TOOL_FAILURE`。
- 超过步数：`incomplete` / `EXECUTION_LIMIT_REACHED`。

## 限制

没有真实 LLM 证据、真实素材库或人工品牌审核，本题不对这些内容作完成声明。
