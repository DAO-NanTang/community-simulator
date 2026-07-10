# Hub 档案室统合方案

> 2026-07-10 · 将归档任务 + 往期营期并入 Hub 档案室

---

## 〇、当前状态

Hub 档案室（`renderArchiveHub`，行 6686）有两个层级：

```
📚 档案室
  ├── 📂 在地成员（X人）
  │     └── 点击成员 → 个人案卷（打赏/财务/审核/拍卖记录）
  ├── 📂 共建者（X人）
  ├── 📂 冒险者（X人）
  └── 📂 云村民（X人）
```

**缺失**：
- 归档任务：已完成的任务去哪了？现在散落在任务大厅「📦 已归档」和村庄「📦 往期」
- 往期营期：完结的营期快照去哪了？`data.archived_periods` 有数据但 Hub 档案室没有入口

---

## 一、统合后 UI

```
📚 档案室
  ┌─────────────────────────────────────────┐
  │ [📂成员] [📋归档任务] [📦往期营期]        │  ← 三个标签
  └─────────────────────────────────────────┘

标签「📂成员」→ 当前成员目录 + 点击进个人案卷
标签「📋归档任务」→ 已完成的归档任务列表（从任务大厅搬来）
标签「📦往期营期」→ 已完结营期快照浏览（从村庄搬来）
```

三个标签共享同一个 `hubSlideBody`，切换标签时重新渲染。

---

## 二、实施

### 改 1：`renderArchiveHub` 加标签切换

在函数开头加三个标签按钮：

```
[📂 成员] [📋 归档任务] [📦 往期营期]
```

默认显示「📂 成员」。点击标签切换 `window._archiveTab`，重新渲染。

### 改 2：归档任务标签

复用已有的 `getTaskDoneDate` + `ARCHIVE_DAYS` + `renderArchiveList`：

```
收集逻辑：遍历 data.tasks，找 doneDate = getTaskDoneDate(t, null)
         筛选 daysSince(doneDate) > ARCHIVE_DAYS
渲染：renderArchiveList('hubArchiveTaskList', archiveTasks, 'week', 'hub')
```

### 改 3：往期营期标签

复用村庄往期的渲染逻辑（已实现在 `renderVillageQuestHall` 的 archive 分支）：

```
读取 data.archived_periods → 营期卡片列表 → 点击展开 renderArchiveList
```

### 改 4：个人案卷补全归档任务

`getMemberRecords` 已收集打赏/财务/审核/拍卖，但在 `renderMemberDossier` 中缺少该成员的已完成任务列表。在案卷最后加一段「📋 已完成任务」，复用 `renderArchiveList`。

---

## 三、不改的

- 任务大厅「📦 已归档」按钮 — 保留（作为任务大厅内的快捷入口，数据源和 Hub 档案室共用 getTaskDoneDate + renderArchiveList）
- 村庄「📦 往期」按钮 — 保留（村庄内的快捷入口）
- 个人案卷的打赏/财务/审核/拍卖记录 — 已正确

---

## 四、执行顺序

```
A：renderArchiveHub 加标签切换
B：归档任务标签（复制 questboard 的收集+渲染逻辑）
C：往期营期标签（复制 village archive 的渲染逻辑）
D：个人案卷加已完成任务
```

---

## 五、自查

- **少即是多**：三个标签，不新增函数（全部复用已有 renderArchiveList）
- **复用优先**：归档任务和往期营期的渲染逻辑直接复用已实现的代码
- **需求对齐**：你说了「所有答案都应该在档案室」——归档任务和往期营期搬进去
- **全局最优**：Hub 档案室成为唯一的归档信息中枢，任务大厅和村庄的归档按钮保留为快捷入口
- **长期主义**：加第四个标签只需在 renderArchiveHub 加一个按钮 + 一个渲染分支
