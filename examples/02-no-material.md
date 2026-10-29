# 02-no-material

## Input
```json
{
  "topic": "量子护肤配方",
  "audience": "短视频创作者",
  "target_seconds": 30,
  "style": "专业",
  "material_id": null,
  "product_facts": [],
  "brand_rules": []
}
```

## Actual Output
```json
{
  "run_id": "run_49fa0e194d98",
  "status": "needs_info",
  "title": null,
  "shots": [],
  "total_estimated_seconds": 0,
  "material_source_ids": [],
  "risks": [],
  "message": "未找到可用素材，请补充产品事实、素材 ID 或更具体主题。",
  "decision_source": "fallback",
  "error_code": null
}
```

## Actual Trace
```json
[
  {
    "node": "check_rules",
    "action": "check_rules",
    "parameters": {
      "topic": "量子护肤配方",
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
      "query": "量子护肤配方",
      "material_id": ""
    },
    "result_summary": "检索到 0 个素材",
    "next_action": "rewrite_search",
    "decision_rationale": "选择确定性安全动作。"
  },
  {
    "node": "rewrite_search",
    "action": "rewrite_search",
    "parameters": {
      "original_query": "量子护肤配方",
      "rewritten_query": "护肤配方"
    },
    "result_summary": "将检索词改写为更短的描述",
    "next_action": "search_materials",
    "decision_rationale": "第一次检索无结果时，先安全地降低检索词的限定。"
  },
  {
    "node": "search_materials",
    "action": "search_materials",
    "parameters": {
      "query": "护肤配方",
      "material_id": ""
    },
    "result_summary": "改写检索后得到 0 个素材",
    "next_action": "request_more_info",
    "decision_rationale": "选择确定性安全动作。"
  },
  {
    "node": "request_more_info",
    "action": "request_more_info",
    "parameters": {},
    "result_summary": "没有可用素材",
    "next_action": null,
    "decision_rationale": "缺少可追溯素材时，向用户索要产品事实或素材线索。"
  }
]
```
