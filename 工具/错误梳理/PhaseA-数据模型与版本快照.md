# Phase A：数据模型与版本快照

> 2026-07-10 · 状态：已审查，待执行
> 所属方案：世界终端-完整数据与版本管理方案
> 本阶段定位：**纯数据层**。不涉及任何 UI 变化，不涉及动画。
> 依赖：无（可独立执行）
> 被依赖：Phase B（创营向导 UI）、Phase C（仪式动画系统）

---

## 〇、背景：为什么要做这件事

### 当前系统的数据是散装的

dashboard.html 里跟"营队"相关的数据分散在多个地方，各自独立维护，没有统一的容器：

| 数据 | 当前位置 | 存储方式 |
|------|----------|----------|
| 营队名称/期数 | 无（硬编码在 UI 里，如"第四期"） | 不存在于数据层 |
| 预算 | `data.budget` | 独立对象 |
| 日历 | `data.camp_dates` + `data.schedule` | 独立对象 |
| 成员 | `data.members` + `data.staff_cards` | 独立数组/对象 |
| 任务 | `data.tasks` | 独立数组 |
| 治理 | `data.decisions` | 独立数组 |
| 步骤进度 | `data.camp_progress` | 独立对象 |
| 完结快照 | `data.archived_periods` | 独立对象（只写不读） |

问题：
- 没有"营队"这个概念的数据结构，系统根本不知道当前是第几期
- 更改营队数据时，不知道改了什么、谁改的、什么时候改的
- `closePeriod()` 创建了 `archived_periods` 快照，但没有版本追踪
- 如果未来支持多期共存（如同时查看第四期和第五期），当前数据结构完全无法支撑

### 本阶段要达成什么

建立 `data.camp_info` 作为营队的**唯一数据容器**：

1. **六维数据模型**：把散装数据收纳到一个结构化的对象里
2. **版本快照**：每次正式保存生成一个只读快照，记录谁、什么时候、改了什么
3. **原档锁定**：创营时的 v1 快照永久不可修改
4. **变更日志**：轻量索引，快速浏览版本历史

**本阶段不做 UI 变化**。现有功能继续用旧的数据字段（`data.tasks`、`data.budget` 等），新结构先建好，Phase B 再逐步迁移 UI。

---

## 一、现有代码现状（执行前必须对照）

### 1.1 数据初始化

`loadData()` 约 line 1738：`data` 对象的初始结构。执行时需要在这里增加 `camp_info` 的初始化。

### 1.2 现有向导步骤

`data.camp_progress`（约 line 1738）记录向导进度：
```
{ step: 1, steps: {'1':'active','2':'locked','3':'locked','4':'locked','5':'locked'} }
```
步骤编号 1-5，状态为 `active` / `locked` / `pending` / `done`。

`switchStep(n)`（约 line 9027）切换步骤，`unlockStep(n)`（约 line 9043）解锁下一步。

Phase A **不改**这些函数，只在 `data.camp_info` 中存储步骤信息作为快照的一部分。

### 1.3 完结快照

`closePeriod()`（约 line 2561）将当前期的 tasks/members/finance/tips 存入 `data.archived_periods`。Phase A 的版本快照机制**不是替代**这个功能——`closePeriod` 是「营期完结」时的一次性操作，`camp_info.snapshots` 是「每次重要修改」时生成的版本记录。两者共存，维度不同。

### 1.4 需要修改的现有函数

| 函数 | 约行号 | 修改内容 |
|------|--------|----------|
| `loadData()` | 1738 | 初始化 `data.camp_info` 默认值 |
| 数据加载逻辑 | 1936 | 从 localStorage 恢复时兼容旧数据（没有 `camp_info` 时自动创建） |
| — | — | 本阶段不改 UI 函数 |

---

## 二、要新增的数据结构

### 2.1 顶级容器：`data.camp_info`

放在 `data` 对象中，与 `tasks`、`members`、`budget` 平级。它是一个独立的对象，不替代任何现有字段（Phase B 才会逐步迁移）。

### 2.2 六维数据模型：`camp_info.current`

当前营队的六类数据，收纳在一个对象中。各类字段详见原方案第一节（第 22-81 行），此处不重复列举。

关键设计点：
- 六类数据在 `current` 中各自独立，修改某一类不影响其他类的快照版本号
- `current.version` 是全局版本号，每次**任何一类**生成正式快照时递增
- `current.updated_at` 和 `updated_by` 记录最后一次修改
- 在 Phase A，`current` 中的数据**不与**现有 `data.tasks`、`data.budget` 等自动同步——Phase B 会做同步逻辑。本阶段只建容器。

### 2.3 版本快照：`camp_info.snapshots`

一个数组，每个元素代表一次正式保存时的完整数据副本。

每个快照包含：
- `version`：版本号（从 1 开始递增）
- `created_at`：快照创建时间（ISO 格式）
- `created_by`：创建人
- `label`：人类可读的标签（如"创营原档""调整预算"）
- `frozen`：布尔值，`true` 表示此版本已锁定不可修改
- `change_summary`：一句话描述变更内容
- `data`：该版本的六维数据完整副本

设计规则：
- `snapshots[0]`（v1）是创营原档，`frozen` 永远为 `true`，任何代码不得修改它
- 后续快照（v2, v3, ...）也是只读的，但可以通过「恢复此版本」操作将其内容复制为新的 `current`
- 快照不删除，只追加
- **正式营队快照不可删除，测试营队快照可随营队一起删除**

### 2.4 变更日志：`camp_info.changelog`

轻量索引，不包含完整数据，只记录每次版本变更的摘要。用于快速展示版本历史时间线（不需要加载完整快照数据）。

每条日志包含：
- `version`：对应的版本号
- `at`：时间
- `by`：操作人
- `action`：`'create'` / `'update'` / `'revert'`
- `summary`：一句话描述

---

## 三、具体操作（按顺序执行）

### 操作 1：初始化 `data.camp_info`

在 `loadData()` 的 `data` 初始对象中（约 line 1738），添加 `camp_info` 字段：

```
camp_info: {
  current: {
    version: 0,
    updated_at: '',
    updated_by: '',
    identity: { name: '', period: '', description: '', type: 'regular', status: 'draft', created_at: '', created_by: '' },
    budget: { nt_total_pool: 0, nt_allocated: 0, nt_remaining: 0, rmb_budget: 0, rmb_items: [], community_pool_total: 0, community_pool_daily: 0, allocation_rules: {} },
    calendar: { start_date: '', end_date: '', duration_days: 15, daily_schedule: [], milestones: [], key_dates: [] },
    team: { admin: '', staff_cards: [], members: {} },
    tasks: { pool: [], assignments: {}, templates: [] },
    governance: { council_meetings: [], decisions: [], rules: {} }
  },
  snapshots: [],
  changelog: []
}
```

### 操作 2：兼容旧数据

在数据加载逻辑中（约 line 1936，从 localStorage 读取 data 之后），添加兼容处理：

```
if (!data.camp_info) {
  data.camp_info = { /* 同上的默认结构 */ };
}
```

这样已有用户的 localStorage 数据不会报错。

### 操作 3：新增快照生成函数

新增全局函数 `createSnapshot(label, changeSummary)`：

功能描述（用自然语言，不用代码）：
1. 读取 `data.camp_info.current` 当前数据
2. `version` 递增 1
3. 将当前数据深拷贝为快照对象
4. 推入 `snapshots` 数组
5. 添加一条 `changelog` 记录
6. 如果 `version === 1`，设置 `frozen: true`（原档锁定）
7. 更新 `current.updated_at` 和 `current.version`
8. 调用 `saveData()` 写入 localStorage

位置：放在约 line 2561（`closePeriod` 函数附近），因为它们都是数据快照相关逻辑。

### 操作 4：新增版本查看函数

新增全局函数 `getSnapshot(version)`：

功能：从 `snapshots` 数组中查找指定版本号的快照，返回深拷贝（防止调用方意外修改只读快照）。如果版本号不存在，返回 `null`。

新增全局函数 `getChangelog()`：

功能：返回 `changelog` 数组的浅拷贝，按版本号倒序排列。

---

## 四、不改的范围（明确排除）

| 不碰 | 原因 |
|------|------|
| 现有 UI（向导、工作台、任务大厅） | Phase B 才做 |
| `data.tasks`、`data.budget` 等现有字段 | 暂不同步，Phase B 会迁移 |
| `data.camp_progress` | 继续使用，不在本阶段修改 |
| `closePeriod()` | 逻辑正确，不改 |
| `data.archived_periods` | 和 `camp_info.snapshots` 是不同维度，共存 |
| `changeUserRole` / `claimTasks` | Phase B 改 |

---

## 五、与其他 Phase 的关系

```
Phase A（本阶段）
  │
  │  产出：data.camp_info 数据结构 + createSnapshot/getSnapshot/getChangelog 函数
  │
  ├──→ Phase B（创营向导 UI）
  │      依赖：data.camp_info 已存在
  │      改动：向导表单读写 camp_info.current；保存时调用 createSnapshot
  │
  └──→ Phase C（仪式动画系统）
         依赖：data.camp_info + Phase B 的向导 UI
         改动：纯前端 CSS 动画，不涉及数据层
```

---

## 六、验收清单

| # | 验证动作 | 预期 |
|:--:|------|------|
| 1 | 页面加载 → 打开浏览器控制台 → 输入 `data.camp_info` | 返回对象，结构符合 2.2 节定义 |
| 2 | 没有 `camp_info` 的旧数据加载 | 自动创建默认 `camp_info`，不报错 |
| 3 | 控制台调用 `createSnapshot('测试快照', '验证快照功能')` | `data.camp_info.snapshots` 新增一条记录 |
| 4 | 同上 | `data.camp_info.current.version` 递增 1 |
| 5 | 同上 | `data.camp_info.changelog` 新增一条记录 |
| 6 | 第一次调用 `createSnapshot` | 生成的 v1 快照 `frozen: true` |
| 7 | `getSnapshot(1)` | 返回 v1 快照的深拷贝 |
| 8 | 修改返回的深拷贝 | 不影响 `snapshots[0]` 中的原始数据 |
| 9 | `getChangelog()` | 返回按版本倒序的日志数组 |
| 10 | 页面刷新后 `data.camp_info` | 数据持久化，不丢失 |