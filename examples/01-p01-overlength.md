# 01-p01-overlength

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
  "run_id": "run_a75b294bb1fc",
  "status": "completed",
  "title": "支持字幕，让表达更清晰",
  "shots": [
    {
      "index": 1,
      "visual_description": "创作者在编辑页打开字幕开关，成片出现清晰字幕",
      "voiceover": "P01 支持字幕",
      "subtitle": "支持字幕",
      "estimated_seconds": 14,
      "material_source_ids": [
        "P01-01"
      ]
    },
    {
      "index": 2,
      "visual_description": "成片中字幕随旁白同步出现",
      "voiceover": "P01 支持字幕",
      "subtitle": "支持字幕",
      "estimated_seconds": 12,
      "material_source_ids": [
        "P01-02"
      ]
    },
    {
      "index": 3,
      "visual_description": "完成字幕编辑后预览短片",
      "voiceover": "P01 支持字幕",
      "subtitle": "支持字幕",
      "estimated_seconds": 4,
      "material_source_ids": [
        "P01-03"
      ]
    }
  ],
  "total_estimated_seconds": 30,
  "material_source_ids": [
    "P01-01",
    "P01-02",
    "P01-03"
  ],
  "risks": [],
  "message": "脚本已生成，可继续人工编辑。",
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
  },
  {
    "node": "estimate_duration",
    "action": "estimate_duration",
    "parameters": {
      "target_seconds": 30
    },
    "result_summary": "首稿预估 38 秒",
    "next_action": "compress_draft",
    "decision_rationale": "工具估算显示首稿超出目标时长，先压缩后复估。"
  },
  {
    "node": "compress_draft",
    "action": "compress_draft",
    "parameters": {
      "target_seconds": 30
    },
    "result_summary": "压缩镜头时长，不新增事实或素材",
    "next_action": "estimate_duration",
    "decision_rationale": "工具结果显示超时，选择先压缩后复估。"
  },
  {
    "node": "estimate_duration",
    "action": "estimate_duration",
    "parameters": {
      "target_seconds": 30
    },
    "result_summary": "压缩后预估 30 秒",
    "next_action": "finish",
    "decision_rationale": "当前工具结果已满足完成条件。"
  },
  {
    "node": "finish",
    "action": "finish",
    "parameters": {},
    "result_summary": "脚本可交付",
    "next_action": null,
    "decision_rationale": "素材、规则和时长均满足当前输入。"
  }
]
```
