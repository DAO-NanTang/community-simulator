# Phase B+C 缺口清单与任务衔接指南

> 2026-07-10
> 说明：本文档列出执行版中未完成的内容，以及下次任务如何衔接。

---

## 一、执行版覆盖了哪些、没覆盖哪些

```
Round 1（仪式动画基础设施）  ████████████ ✅ 完整
Round 2（导航+工坊+火苗+⓪） ████████████ ✅ 完整
Round 3（快照+状态栏）       ██████░░░░░░ ⚠️ 基本完整，但缺一处
Round 4（角色升级修正）      ░░░░░░░░░░░░ 🔴 仅占位
Round 5（重写 Step ④）      ░░░░░░░░░░░░ 🔴 仅占位
数据同步（camp_info 回填）   ░░░░░░░░░░░░ 🔴 完全没有
旧函数编号修正               ░░░░░░░░░░░░ 🔴 完全没有
```

---

## 二、缺口详细清单

### 缺口 1 🔴：旧 saveStep 函数使用错误的 camp_progress 键名

**问题**：Round 2I 把 `data.camp_progress` 的初始化从键 `'1'~'5'` 改成了 `'0'~'4'`。但 `saveStep1/2/3/4` 和 `resetWizard` 仍然用旧的键名写入。

**影响**：导航条上的步骤状态显示错乱。比如 ⓪ 保存后，`steps['0']` 永远是 `'active'`（从未被更新），导航条一直以为 Step ⓪ 是当前步。

**需要修改的 4 个函数及行号**：

| 函数 | 行号 | 改动内容 |
|------|------|------|
| `saveStep1()` | 9911-9912 | `steps['1']='done'; steps['2']='active'` → `steps['0']='done'; steps['1']='active'` |
| `saveStep1()` | 9911 | 默认值 `{step:1,steps:{'1':'active',...}}` → `{step:0,steps:{'0':'active',...}}` |
| `saveStep2()` | 10087-10089 | `steps['2']='done'; steps['3']='active'` → `steps['1']='done'; steps['2']='active'` |
| `saveStep2()` | 10087 | 默认值同样需要改 |
| `saveStep3()` | 10395-10397 | `steps['3']='done'; steps['4']='active'` → `steps['2']='done'; steps['3']='active'` |
| `saveStep3()` | 10395 | 默认值同样需要改 |
| `saveStep4()` | 10603+ | `steps['4']='done'; steps['5']='active'` → 整个函数会在 Round 5 重写 |
| `resetWizard()` | 10953 | `{step:1,steps:{'1':'active',...}}` → `{step:0,steps:{'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'}}` |
| `resetWizard()` | 10957 | `switchStep(1)` → `switchStep(0)` |
| `switchStep()` 内部 | 9087 | 默认值 `{step:1,...}` → `{step:0,...}` |

**操作方式**：grep `steps.*'[1-5]'.*=.*'(done|active)'` 找到所有位置，逐个修正键名偏移（旧键 −1 = 新键）。

---

### 缺口 2 🔴：数据没有同步到 camp_info.current

**问题**：这是最大的设计漏洞。`saveStep1()` 写入 `data.budget`，`saveStep2()` 写入 `data.tasks`，`saveStep3()` 通过 `getStaffCards()` 管理 `data.staff_cards`。但 `camp_info.current.budget` / `camp_info.current.tasks` / `camp_info.current.team` 始终是空的。

这导致两个后果：
1. `checkStepFillLevel(1/2/3)` 永远返回 0，火苗永不增长
2. `camp_info` 只是一个空壳，Phase C 的后续功能（如版本对比）无数据可展示

**解决方案**：在每个 saveStep 函数的 `saveData()` 之前，加入数据同步逻辑。

`saveStep1()` 末尾加：
```javascript
// 同步到 camp_info
var b = data.budget || {};
data.camp_info.current.budget.nt_total_pool = 0; // Step ① 的旧 UI 没有 NT 总池字段，先留 0
data.camp_info.current.budget.rmb_budget = b.tuition || 0;
data.camp_info.current.budget.community_pool_total = b.community_pool_total || 500;
data.camp_info.current.budget.community_pool_daily = b.community_pool_daily || 10;
data.camp_info.current.calendar.start_date = (data.camp_dates && data.camp_dates.start) || '';
data.camp_info.current.calendar.duration_days = (data.camp_dates && data.camp_dates.duration_days) || 15;
data.camp_info.current.calendar.milestones = (data.camp_dates && data.camp_dates.milestones) || [];
```

`saveStep2()` 末尾加：
```javascript
// 同步到 camp_info
data.camp_info.current.tasks.pool = JSON.parse(JSON.stringify(wizardTasks));
```

`saveStep3()` 末尾加：
```javascript
// 同步到 camp_info
data.camp_info.current.team.staff_cards = JSON.parse(JSON.stringify(getStaffCards()));
```

**⚠️ 注意**：这些同步代码必须放在 `createSnapshot()` 调用**之前**，否则快照里的数据是空的。

---

### 缺口 3 🔴：Round 3A 的 createSnapshot 位置需要调整

**问题**：执行版 Round 3A 说「在 `saveData()` 之后、`}` 之前加 `createSnapshot(...)`」。但根据缺口 2，同步逻辑必须先于 `createSnapshot` 执行。正确的顺序是：

```
saveStep1() {
  // ... 原有保存逻辑 ...
  // 🆕 同步到 camp_info（缺口 2）
  // 🆕 createSnapshot(...)（Round 3A）
  saveData();
}
```

`createSnapshot` 必须在 `saveData` **之前**调用（因为 `createSnapshot` 内部会调 `saveData`）。

---

### 缺口 4 🔴：Round 4 缺精确执行细节

**问题**：执行版 Round 4 只有方向性描述，没有精确代码。

**需要做的事**：

**4A：claimTasks 删除 builder 升级兜底代码**

定位方式：grep `upgradeResult` 或 grep `builder.*升级`

需要精确找到并删除约 10 行代码（从 `// 同步更新系统角色` 到 `saveUsers(users)`）。

建议执行步骤：
1. grep `upgradeResult` 找到具体行号
2. Read 周围 30 行，定位要删除的代码段
3. 确认这段代码的功能（builder 升级兜底）
4. 删除之

**4B：changeUserRole 加 skipAdventurerCheck**

定位方式：grep `function changeUserRole`

在 builder 升级的检查处（约 line 2365-2370），原来的条件是类似：
```javascript
if (!wasAdventurer && oldRole !== 'adventurer') { return { ok: false, reason: '...' }; }
```

改为：
```javascript
if (!opts.skipAdventurerCheck && !wasAdventurer && oldRole !== 'adventurer') { return { ok: false, reason: '...' }; }
```

---

### 缺口 5 🔴：Round 5 完全未指定

Round 5 是工作量最大的部分（约 150 行新代码），包括：
- 注释旧 `renderStep4()` 和 `renderStep5()`
- 注释旧 HTML `wiz-step4` 和 `wiz-step5`
- 新增四阶段 Step ④ HTML
- 新增 `renderStep4()` 四阶段版
- 新增 `wizStep4Phase` 状态管理
- 发包逻辑（调用 `changeUserRole` with `skipAdventurerCheck`）
- 启动确认逻辑（`identity.status = 'active'`，生成最终快照）

**细化为 5 个子任务**：

| 子任务 | 内容 |
|:--:|------|
| 5A | 注释旧 `wiz-step4` 和 `wiz-step5` HTML div，新增四阶段 HTML |
| 5B | 重写 `renderStep4()`：四个子阶段的渲染 |
| 5C | 实现 4a（审核）和 4b（发包）逻辑 |
| 5D | 实现 4c（开营仪式 → 调用 `openLaunchCeremony`） |
| 5E | 实现 4d（启动确认：锁定原档、draft→active、最终快照） |

---

### 缺口 6 🟡：saveWizDraft() 需要知道 camp_info

**问题**：`saveWizDraft()`（line 10961）只处理 `wizardStep === 2` 的情况。现在有了 Step ⓪，暂存也应该覆盖 Step ⓪ 的表单数据。

**修改**：在 `saveWizDraft()` 中增加 `wizardStep === 0` 的情况，暂存 Step ⓪ 表单到 `camp_info.current.identity`。

---

### 缺口 7 🟡：saveStep1 缺少 NT 总池输入框

**问题**：旧 Step ① 的 UI 没有 NT 总池（`nt_total_pool`）的输入框。Phase B 方案提到 NT 总池是六维数据模型的核心字段，但旧 UI 里不存在。

**解决方案**（三种选一）：
- A. 在 Step ① 加一个 NT 总池输入框（改动最小）
- B. 在 Step ⓪ 加 NT 总池字段
- C. 先设默认值 0，启动前可以手动改 `data.camp_info.current.budget.nt_total_pool`

建议选 A，在 Step ① 的「💬 社区鼓励池」card 上面加一个「🎯 NT 总池」card。

---

## 三、任务衔接流程

### 当前状态（执行完 Rounds 1-3 后）

```
能用的：                        不能用的 / 有问题的：
├── 仪式动画 ✅                  ├── 火苗指示器不增长（数据没同步）🔴
├── Step ⓪ 表单 ✅              ├── 旧 saveStep 用错 camp_progress 键 🔴
├── 沉浸工坊（标签栏收起）✅      ├── 数据在 data.* 和 camp_info.* 之间分裂 🔴
├── 自由导航 ✅                  ├── Step ④ 还是旧的内容（角色填卡）🔴
├── 版本历史面板 ✅              ├── Step ⑤ 仍然存在但导航条不显示 🔴
├── 火苗图标渲染 ✅              ├── claimTasks 有旧兜底代码 🔴
└── 仪式降级机制 ✅              ├── changeUserRole 没有 skipAdventurerCheck 🔴
                                └── resetWizard 使用旧编号 🔴
```

### 下次任务的执行顺序

```
任务 0（前置检查）：
  └── 确认 Rounds 1-3 已执行完毕，验收清单通过

任务 1（修正 camp_progress 键名）：
  └── 改 saveStep1/2/3/4、resetWizard、switchStep 内部默认值
     把 '1'~'5' 键名改为 '0'~'4'

任务 2（数据同步）：
  └── 在 saveStep1/2/3 中加 camp_info.current 同步逻辑
     必须先于 createSnapshot 执行

任务 3（调整 createSnapshot 顺序）：
  └── 确保顺序：同步数据 → createSnapshot → saveData

任务 4（Round 4：角色升级）：
  ├── 4A：删除 claimTasks 兜底代码
  └── 4B：changeUserRole 加 skipAdventurerCheck

任务 5（Round 5：Step ④ 重写）：
  ├── 5A：注释旧 HTML，新增四阶段 HTML
  ├── 5B：重写 renderStep4()
  ├── 5C：实现审核 + 发包
  ├── 5D：实现开营仪式对接
  └── 5E：实现启动确认

任务 6（收尾）：
  ├── 更新 resetWizard()
  ├── 更新 saveWizDraft()
  └── 删除旧 Step ⑤ 的残留代码
```

---

## 四、给下次 AI 的交接说明

### 执行前提
- Phase A ✅ 已完成（`data.camp_info` 存在，`createSnapshot/getSnapshot/getChangelog` 可用）
- Phase B+C Rounds 1-3 ✅ 已执行（仪式动画、工坊模式、火苗系统、Step ⓪、快照调用、版本面板）

### 当前文件状态
- 文件：`dashboard.html`（约 11,900 行，~730KB）
- 新增了约 600 行代码（仪式 CSS/HTML/JS + 工坊模式 + Step ⓪ + 导航重编号）

### 已知的活跃 bug（需要修复）
1. 火苗指示器始终显示 🕯️（因为 `checkStepFillLevel` 检查的是空白的 `camp_info.current.*`）
2. 导航条步骤状态可能与实际不一致（旧 saveStep 写入错误的 camp_progress 键）
3. `resetWizard()` 不会清除 camp_info 数据

### 建议的启动命令
在浏览器控制台执行以下命令确认前置条件：
```javascript
// 1. 确认 Phase A 完成
typeof createSnapshot          // → 'function'
typeof getSnapshot             // → 'function'
typeof getChangelog            // → 'function'
data.camp_info                 // → 非 undefined

// 2. 确认 Rounds 1-3 完成
typeof openIgniteCeremony      // → 'function'
typeof openLaunchCeremony      // → 'function'
typeof getStepFlame            // → 'function'
typeof enterWorkshop           // → 'function'
typeof exitWorkshop            // → 'function'
typeof checkStepFillLevel      // → 'function'
data.camp_progress.step        // → 0（新默认值）
```
