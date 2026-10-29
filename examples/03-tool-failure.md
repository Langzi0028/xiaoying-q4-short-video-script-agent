# 03-tool-failure

## Input
```json
{
  "topic": "P01 字幕功能",
  "audience": "短视频创作者",
  "target_seconds": 30,
  "style": "轻快",
  "material_id": "P01",
  "product_facts": [],
  "brand_rules": []
}
```

## Actual Output
```json
{
  "run_id": "run_823e81069704",
  "status": "failed",
  "title": null,
  "shots": [],
  "total_estimated_seconds": 0,
  "material_source_ids": [],
  "risks": [],
  "message": "业务工具执行失败，未生成可交付脚本。",
  "decision_source": "fallback",
  "error_code": "TOOL_FAILURE"
}
```

## Actual Trace
```json
[
  {
    "node": "check_rules",
    "action": "check_rules",
    "parameters": {
      "topic": "P01 字幕功能",
      "brand_rule_count": 0
    },
    "result_summary": "品牌规则初检通过",
    "next_action": "search_materials",
    "decision_rationale": "未发现阻断规则，可以检索素材。"
  },
  {
    "node": "search_materials",
    "action": "search_materials",
    "parameters": {
      "query": "P01 字幕功能",
      "material_id": "P01"
    },
    "result_summary": "检索到 3 个素材",
    "next_action": "build_draft",
    "decision_rationale": "选择确定性安全动作。"
  },
  {
    "node": "build_draft",
    "action": "build_draft",
    "parameters": {
      "source_ids": [
        "P01-01",
        "P01-02",
        "P01-03"
      ]
    },
    "result_summary": "基于 3 个来源生成首稿",
    "next_action": "estimate_duration",
    "decision_rationale": "仅使用检索到的素材事实生成可编辑分镜。"
  }
]
```
