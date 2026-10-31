# RailMind API 契约

所有接口使用 `/api/v1` 前缀。下列结构是框架阶段的稳定方向；字段可以新增，已有字段应保持向后兼容。

## 通用对象

### TravelRequest

```json
{
  "origin": "上海",
  "destination": "杭州",
  "travel_date": null,
  "departure_window": {
    "start": "08:00",
    "end": "12:00"
  },
  "max_price": 120,
  "max_duration_minutes": 150,
  "seat_classes": ["second"],
  "weights": {
    "price": 0.30,
    "duration": 0.35,
    "comfort": 0.20,
    "schedule": 0.15
  }
}
```

权重总和必须为 `1`，误差范围 `0.001`。`seat_classes` 首版使用：`second`、`first`、`hard_seat`、`hard_sleeper`、`soft_sleeper`。

### Recommendation

```json
{
  "journey": {},
  "score": 87.4,
  "dimension_scores": {
    "price": 92.1,
    "duration": 84.0,
    "comfort": 78.5,
    "schedule": 95.0
  },
  "reasons": [
    "票价低于当前候选平均水平",
    "整体耗时较短"
  ],
  "tradeoffs": [
    "出发车站距离市中心可能较远"
  ],
  "confidence": 0.82
}
```

## `GET /health`

返回服务状态、样例数据版本和算法版本。

```json
{
  "status": "ok",
  "data_version": "sh_to_hz.sample",
  "algorithm_version": "weighted-v1"
}
```

## `POST /api/v1/assistant/parse`

将自然语言转换为需求草稿。解析器可以返回缺失字段和追问，不直接执行查询。

请求：

```json
{
  "text": "明天上午去杭州，最好 10 点前到，预算 100 元，想坐高铁"
}
```

响应：

```json
{
  "request_draft": {
    "origin": "上海",
    "destination": "杭州",
    "travel_date": "2026-10-31",
    "departure_window": null,
    "max_price": 100,
    "max_duration_minutes": null,
    "seat_classes": ["second"],
    "weights": {
      "price": 0.30,
      "duration": 0.35,
      "comfort": 0.20,
      "schedule": 0.15
    }
  },
  "missing_fields": [],
  "clarifications": [
    "你说的是 10 点前到达，我已记录为到达时间目标"
  ],
  "parser": "rule-based"
}
```

## `POST /api/v1/journeys/search`

查询过滤后的候选车次，不做多目标推荐排序。

```json
{
  "request": {},
  "page": 1,
  "page_size": 20
}
```

## `POST /api/v1/recommendations`

应用硬过滤和多目标评分，返回排序后的方案。

```json
{
  "request": {},
  "limit": 3,
  "include_candidates": false
}
```

响应：

```json
{
  "recommendations": [],
  "candidate_count": 52,
  "filtered_count": 8,
  "relaxation_suggestions": [],
  "algorithm_version": "weighted-v1",
  "data_version": "sh_to_hz.sample"
}
```

当 `filtered_count` 为 0 时，`relaxation_suggestions` 应指出哪一项条件最值得放宽，例如：

```json
[
  {
    "field": "max_price",
    "suggested_value": 140,
    "reason": "预算提高 20 元后可增加 9 趟候选车次"
  }
]
```

## `POST /api/v1/recommendations/explain`

为已展示的方案生成或刷新解释。首版由结构化规则生成；接入 LLM 时只允许润色，不允许编造事实。

## 错误格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "权重总和必须为 1",
    "details": {
      "fields": ["weights"]
    }
  }
}
```

错误码统一使用大写蛇形字符串。前端根据 `code` 做恢复动作，不依赖中文错误文案。
