# AI 交接索引 — 南塘 DAO gNT 计算机制 · 工具

> 2026-07-10 | 给接手执行的 AI 阅读

---

## 一、项目是什么

这是一个**单文件 Web 应用**（`dashboard.html`，约 700KB），运行在浏览器中，数据存储在 `localStorage`。功能是共创营的任务管理、NT 经济系统、成员档案、社区互动。

- 入口文件：`dashboard.html`
- 无后端、无构建工具、无框架
- 纯 HTML + CSS + 原生 JavaScript
- 所有数据通过 `localStorage` 的 `camp_data` 键存取

---

## 二、最近做了什么（已完成，不需要再做）

### 函数统一化（已完成 ✅）

| 候选 | 做了什么 | 涉及方案文件 |
|------|------|------|
| 1 | 新增 `saveData()` 函数，收编 ~110 处散落的 `safeStorage.setItem('camp_data', ...)` | `函数统一化方案_2026-07-10.md` |
| 2 | 新增 `parseMD()` 统一日期解析，修复 2025/2026 年份硬编码 bug | 同上 |
| 3 | 删除死代码 `openHubSlide`/旧 `closeHubSlide`，重命名为 `closeHubSub` | 同上 |
| 4 | 新增 `daysBetween`/`daysSince`/`daysUntil`，收编 12 处魔术数字 `86400000` | 同上 |
| 5 | 新增 `hasRole(user, roles)` 函数，收编 ~14 处裸 `role === 'xxx'` 判断 | 同上 |
| 7 | 11 处 `var today = new Date().toISOString()` → `Clock.today()` | 同上 |

### 身份系统修复（已完成 ✅）

| 做了什么 | 涉及方案文件 |
|------|------|
| `data.members[name].role` 和 `data.members[name].title` 字段分离 | `修复方案_身份系统统一.md` |
| 新增 `ROLE_LABELS` 全局常量（含 `admin`），删除两处重复定义 | 同上 |
| 新增 `migrateMemberRoleToTitle()` 一次性数据迁移 | 同上 |
| 5 处写入点从 `role` 改为 `title` | 同上 |
| `getStaffNames()` 改用 `users[n].role` 判断 staff | 同上 |

### 社区窗口改造（已完成 ✅）

| 做了什么 | 涉及方案文件 |
|------|------|
| 删除旧版独立社区窗口（卡片 + Modal + `openCommunityWindow` 函数） | `社区窗口方案.md` |
| 嵌入社区副本 Modal 内，从右侧滑出二级面板 | 同上 |
| 垂直居中 `.village-modal` | 同上 |
| 双面板水平居中（`transform: translateX` + `getBoundingClientRect` 精确对齐） | 同上 |
| z-index 层级修复（picker 1010 > 二级 1002 > 遮罩 1001 > 一级 120） | 同上 |
| 多级关闭顺序（三级 → 二级 → 一级，逐级关闭） | 同上 |
| 打赏选人改为 `showReviewerPicker`（不再 `prompt` 手打名字） | 同上 |
| 打赏确认 + 结果反馈（`confirm` + `window._lastTipResult` + 面板顶部结果条） | 同上 |
| 社区池子已删除后又重建为社区公共基金（v3方案） | 同上 |
|「刚刚发生」→「💬 最近打赏」（只显示打赏，不混任务事件） | 同上 |
| 面板宽度比例反转（一级 380px，二级 ~440px） | 同上 |

---

## 三、待执行的方案（计划已写好，等执行）

### 🔴 信箱分类 + 打赏通知

**方案文件**：[信箱分类与打赏通知方案.md](信箱分类与打赏通知方案.md)

**要做什么**：
1. 在 `computeInboxMessages()` 中新增扫描 `data.tips`，为发给当前用户的打赏生成 `tip_received` 消息
2. 信箱 `renderInbox()` 加分类标签行（📋任务 / ✅审批 / 💬打赏 / 💰财务 / 📅活动），按分类过滤消息

**关键注意**：消息是 `computeInboxMessages()` **动态计算**的，不是持久存储。打赏通知在 `computeInboxMessages` 里生成，不在 `sendTip` 里生成。

### 🟡 任务时间精度 + 默认人数 + 发布确认 + 工作台增强

**方案文件**：[任务时间精度与默认人数方案.md](任务时间精度与默认人数方案.md)

**要做什么**：
1. `parseMD()` 加时间正则（`"M/D HH:MM"` 格式）
2. 表单 `type="date"` → `type="datetime-local"` ×3
3. 私人任务默认人数 1，营队任务默认人数 10
4. 发布确认卡片：`confirmPostTask`/`confirmCampTask` 拆两步
5. 工作台新增「我发布的任务」段落（复用 `renderQuestCard`）

### 🟢 多人部署方案

**方案文件**：[多人部署方案.md](多人部署方案.md)

**要做什么**：SQLite + Node.js Express + SSE 后端，把 localStorage → 服务器 API。改动量大（~800 行新代码），建议先执行上面两个再动这个。

### ⚪ 图标统一方案（低优先级）

**方案文件**：[图标统一方案.md](图标统一方案.md)

**要做什么**：emoji → Phosphor Icons SVG。纯视觉改动，不影响功能。

---

## 四、关键技术约定（执行时遵守）

### 4.1 函数入口

| 功能 | 函数 | 位置 |
|------|------|------|
| 数据持久化 | `saveData()` | 唯一入口，不要直接写 `localStorage` |
| 日期解析 | `parseMD(s)` | 唯一入口，返回 `Date \| null`，年份从 `Clock` 获取 |
| 天数差 | `daysBetween(a,b)` / `daysSince(x)` / `daysUntil(x)` | 统一按 UTC+8 日历日 |
| 角色判断 | `hasRole(user, roles)` | `roles` 是字符串或数组 |
| 系统身份标签 | `ROLE_TITLES`（带 emoji）/ `ROLE_LABELS`（纯中文） | 全局常量 |
| 营地身份标签 | `data.members[name].title` | 自由文本，可空 |
| 系统角色 | `users[name].role` | `admin`/`builder`/`adventurer`/`npc`/`visitor` |
| 今日日期 | `Clock.today()` | 不要用 `new Date().toISOString()` |
| 用户权限 | `userCan(user, cap)` / `hasRole(user, roles)` | 不用裸 `role === 'admin'` |

### 4.2 命名规范

- 新函数用 `camelCase`
- 全局变量用 `camelCase`（如 `roleLabels` → `ROLE_LABELS` 全局常量）
- 不要新建 `var roleLabels = {...}` 局部定义——用全局 `ROLE_LABELS`
- CSS 类名用 `kebab-case`

### 4.3 执行纪律

- 每次改动前先存档：`cp dashboard.html archive/dashboard_$(date +%Y%m%d_%H%M%S).html`
- 改完做语法检查：`node -e "new Function(js)"`
- grep 确认旧代码残留为 0
- 不要顺手优化——只改方案里列的内容

### 4.4 关键 z-index 层级

```
1010  .picker-dropdown（选人面板）
1002  #activityCommunitySlide（二级社区面板）
1001  #activityBackdrop（二级遮罩）
 120  .village-modal（一级 Modal）
  52  .hub-sub-panel（南塘云村子面板）
  50  .dropdown-menu（下拉菜单）
```

### 4.5 多级窗口关闭顺序

```
点遮罩/✕ → 检查 #pickerDropdown 可见 → 关之 → return
          → 检查 #activityCommunitySlide 可见 → 关之 → return
          → 关一级 Modal
```

---

## 五、重要文件速查

| 文件 | 性质 | 说明 |
|------|:--:|------|
| `dashboard.html` | 🔴 主代码 | 唯一的工作文件 |
| `archive/` | 📦 备份 | 每次改动前的快照，用于回退 |
| `社区窗口方案.md` | 📋 已执行方案 | 社区窗口改造全记录 |
| `函数统一化方案_2026-07-10.md` | 📋 已执行方案 | 函数统一化全记录 |
| `修复方案_身份系统统一.md` | 📋 已执行方案 | 身份系统修复 |
| `信箱分类与打赏通知方案.md` | ⏳ 待执行方案 | 信箱改造 |
| `任务时间精度与默认人数方案.md` | ⏳ 待执行方案 | 时间精度 + 工作台增强 |
| `多人部署方案.md` | ⏳ 待执行方案 | 单人 → 多人迁移 |
| `图标统一方案.md` | ⏳ 待执行方案 | 图标统一（低优） |
| `错误梳理/社区窗口问题梳理与修复报告.md` | 📖 参考 | 7 个问题的完整证据链 |
| `错误梳理/身份ID系统碎片化问题分析与解决方案.md` | 📖 参考 | 身份系统碎片化分析 |

---

## 六、开始执行前

1. 阅读对应方案文件的全部内容
2. 阅读 `错误梳理/` 下的报告了解历史问题
3. 理解「四、关键技术约定」中的所有入口函数
4. 存档 → 改代码 → grep 验证 → 语法检查
5. 不要动方案里没写的代码
