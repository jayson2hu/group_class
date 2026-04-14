# 拼课课程系统 Batch 1 字段映射与契约冻结文档

Date: 2026-04-12
Status: Frozen for prototype
Owner: Hermes
Scope: 当前仓库 `apps/group_class_backend/` 原型实现唯一标准源

---

## 1. 冻结范围

本文件冻结当前原型的：
1. 后台课程接口路径
2. 统一响应结构
3. 关键错误码
4. Batch 1 必需字段映射
5. 动作集合与版本并发语义

---

## 2. 接口冻结

1. `GET /api/v1/admin/classes`
2. `GET /api/v1/admin/classes/{classId}`
3. `POST /api/v1/admin/classes`
4. `PUT /api/v1/admin/classes/{classId}`

当前原型允许以 Python 函数模拟上述接口，但返回结构必须与本文件一致。

---

## 3. 统一响应结构

### 3.1 成功响应

```json
{
  "requestId": "req-001",
  "code": "OK",
  "data": {}
}
```

### 3.2 错误响应

```json
{
  "requestId": "req-001",
  "code": "VALIDATION_INVALID_ARGUMENT",
  "details": [
    {
      "field": "minStudents",
      "message": "minStudents must be greater than 0"
    }
  ]
}
```

规则：
1. `requestId` 必返
2. 成功只返 `data`
3. 错误只返 `details`
4. 字段名统一 camelCase

---

## 4. 错误码冻结

1. `OK`
2. `VALIDATION_INVALID_ARGUMENT`
3. `VALIDATION_REQUIRED_FIELD_MISSING`
4. `CLASS_NOT_FOUND`
5. `CLASS_VERSION_CONFLICT`
6. `PERMISSION_DENIED`
7. `SYSTEM_INTERNAL_ERROR`

---

## 5. 后台课程字段冻结

### 5.1 创建 / 编辑 / 详情字段

| API 字段 | 类型 | 说明 |
|---|---|---|
| `classId` | string | 课程 ID |
| `version` | integer | 乐观锁版本 |
| `className` | string \| null | 课程名称 |
| `templateId` | string \| null | 模板 ID |
| `status` | string | 默认 `DRAFT` |
| `classType` | string \| null | 课程类型 |
| `priceAmount` | number \| null | 正价 |
| `depositAmount` | number \| null | 订金 |
| `minStudents` | integer \| null | 最小成班人数 |
| `maxStudents` | integer \| null | 最大人数 |
| `currentStudents` | integer | 当前人数，默认 0 |
| `waitlistCount` | integer | 候补人数，默认 0 |
| `startDate` | string \| null | ISO 8601 |
| `endDate` | string \| null | ISO 8601 |
| `signupDeadline` | string \| null | ISO 8601 |
| `actions` | string[] | Batch 1 固定返回动作集合子集 |
| `createdAt` | string | ISO 8601 |
| `updatedAt` | string | ISO 8601 |

### 5.2 列表字段

列表项必须至少包含：
- `classId`
- `className`
- `status`
- `classType`
- `startDate`
- `endDate`
- `signupDeadline`
- `currentStudents`
- `minStudents`
- `maxStudents`
- `actions`
- `updatedAt`

---

## 6. 动作集合冻结

Batch 1 最小动作集合：
- `view`
- `edit`
- `submit_review`

`DRAFT` 默认返回全部三项动作。

---

## 7. 关键校验冻结

1. 草稿保存至少满足 `className` 或 `templateId` 之一
2. `minStudents > 0`
3. `maxStudents >= minStudents`
4. `endDate >= startDate`
5. `signupDeadline <= startDate`
6. `depositAmount <= priceAmount`
7. 草稿允许部分字段为空，不触发发布级必填校验

---

## 8. 版本语义冻结

1. 创建成功后 `version = 1`
2. 更新时必须提交当前 `version`
3. 版本不匹配返回 `CLASS_VERSION_CONFLICT`
4. 更新成功后版本递增 1
