# 04-execution-limit

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
  "run_id": "run_c9554cdee7d8",
  "status": "incomplete",
  "title": null,
  "shots": [],
  "total_estimated_seconds": 0,
  "material_source_ids": [],
  "risks": [],
  "message": "达到执行步数上限，任务未完成。",
  "decision_source": "fallback",
  "error_code": "EXECUTION_LIMIT_REACHED"
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
  }
]
```
