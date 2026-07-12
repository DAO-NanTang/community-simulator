# Phase B：创营向导 UI

> 2026-07-10 · 状态：已审查，待执行
> 所属方案：世界终端-完整数据与版本管理方案
> 本阶段定位：**UI + 逻辑层**。把现有五步向导扩展为完整的创营流程。
> 依赖：Phase A（`data.camp_info` 已存在，`createSnapshot` 函数可用）
> 被依赖：Phase C（仪式动画系统）

---

## 〇、背景：为什么要做这件事

### 当前向导做了什么、没做什么

dashboard.html 已有一套「创世终端」向导，步骤为 ①统筹 ②任务池 ③认领 ④填卡片 ⑤同步。它覆盖了营队筹备的核心流程，但有三个空缺：

1. **没有「创营」步骤**：管理员无法在系统里声明"我要创建第 X 期营队"。营队名称和期数硬编码在 UI 文字里（如"第四期南塘共创营"），不在数据层。
2. **没有审核/发包/启动流程**：向导结束后，数据直接生效，没有任何审核机制。共建者也看不到"你已被选中"的通知。
3. **保存不生成快照**：`saveStep1/2/3/4` 直接覆盖 `data` 字段，没有版本记录。改了什么、谁改的、什么时候改的，全无踪迹。

### 本阶段要达成什么

把现有向导从"五步筹备工具"升级为完整的"创营→审核→发包→启动"流程：

1. **新增 Step ⓪（创营）**：创建营队身份，写入 `camp_info.current.identity`
2. **重编号**：现有 ①②③④⑤ → 新 ⓪①②③④（Step ④ 合并原来 ④填卡片 + ⑤同步，再加审核/发包/启动）
3. **接入 Phase A 的快照系统**：每次保存生成版本快照
4. **共建者接收通知**：发包后共建者工作台能看到营队信息和自己的任务包

---

## 一、现有代码现状（执行前必须对照）

### 1.1 向导导航条

`renderWizardNav()`（约 line 9006）：根据 `data.camp_progress.steps` 渲染 5 个按钮。按钮样式由步骤状态决定：`active`（当前）、`done`（已完成）、`pending`（已解锁）、`locked`（锁定）。

**执行时需重写此函数**，将步骤数从 5 改为 5（编号从 ⓪ 开始），并增加火种指示器（Phase C 只读数据，本阶段预留 DOM 位置即可）。

### 1.2 步骤切换

`switchStep(n)`（约 line 9027）：隐藏所有步骤容器，显示编号为 `n` 的那个。参数 `n` 当前取值 1-5，需改为 0-4。

`unlockStep(n)`（约 line 9043）：将指定步骤的状态从 `locked` 改为 `pending`。参数和内部逻辑需适配新编号。

### 1.3 现有步骤渲染函数

| 函数 | 约行号 | 当前内容 | Phase B 改动 |
|------|--------|----------|-------------|
| `renderStep1()` | 9050 | 日历 + 预算表单 | 保留，增加「营队日历同步到 camp_info」的保存逻辑 |
| `renderStep2()` | 9874 | 任务池（模板导入 + 表格） | 保留，不改渲染逻辑 |
| `renderStep3()` | 10055 | 选将（任务认领 + 成员卡片编辑器） | 保留渲染，修改 `claimTasks` 逻辑（见下文 3.3） |
| `renderStep4()` | 10358 | 填卡片（成员卡片 + 角色信息） | **重写**：原 Step ④ 填卡片 + 原 Step ⑤ 同步，合并加审核/发包/启动 |
| `renderStep5()` | — | 同步到全部标签 | 合并入新 Step ④ |

### 1.4 需要修改的核心函数

| 函数 | 约行号 | 当前行为 | 改后行为 |
|------|--------|----------|----------|
| `renderWizardNav()` | 9006 | 渲染 ①-⑤ 按钮 | 渲染 ⓪-④ 按钮 + 火种占位 |
| `switchStep(n)` | 9027 | n 取值 1-5 | n 取值 0-4 |
| `unlockStep(n)` | 9043 | 内部编号适配 |
| `claimTasks()` | 9772 | 创建 staff card + 上周已修的 builder 升级逻辑 | 移除 builder 升级的兜底代码（`if (!upgradeResult.ok) { ... }` 那一段），改为：builder 升级统一在 Step ④ 发包时执行 |
| `changeUserRole()` | 2353 | builder 升级需"先有冒险者经历" | 增加 `opts.skipAdventurerCheck`，发包时管理员批量升级共建者可以跳过此检查 |

### 1.5 `claimTasks` 为什么要改

上周修复共建者不升级的 bug 时，在 `claimTasks` 里加了一段"如果 `changeUserRole` 被拒就兜底直接写 `users[name].role = 'builder'`"的逻辑。这是当时为了快速修复而做的妥协——选将和角色升级耦合在了同一个函数里。

正确的设计是：**选将只是认领任务，角色升级在发包时统一执行**。所以本阶段把 `claimTasks` 中的 builder 升级代码移除（兜底那段删掉），改为在 Step ④ 发包逻辑中统一调用 `changeUserRole`。

`changeUserRole` 的 builder 升级检查（"共建者需先有冒险者经历"）在发包场景下是不必要的——因为被选为共建者的人可能直接就是新加入的成员，没有正式的冒险者履历。`skipAdventurerCheck` 参数就是为这个场景准备的。

---

## 二、步骤重编号对照表

| 旧编号 | 旧名称 | 新编号 | 新名称 | 改动类型 |
|:--:|------|:--:|------|:--:|
| — | — | ⓪ | 创营 | **新增** |
| ① | 统筹 | ① | 统筹 | 保留，保存逻辑增加快照 |
| ② | 任务池 | ② | 任务池 | 保留，保存逻辑增加快照 |
| ③ | 认领 | ③ | 选将 | 保留渲染，`claimTasks` 逻辑调整 |
| ④ | 填卡片 | ④ | 启动 | **重写**：合并原④⑤ + 新增审核/发包/开营/启动 |
| ⑤ | 同步 | — | — | 合并入新④ |

---

## 三、具体操作（按顺序执行）

### 操作 1：重编号基础函数

**`switchStep(n)`**：参数范围从 1-5 改为 0-4。内部 `for` 循环从 `i=0; i<=4`。

**`unlockStep(n)`**：参数范围从 1-5 改为 0-4。`data.camp_progress.steps` 的 key 从 `'1'`~`'5'` 改为 `'0'`~`'4'`。

**`renderWizardNav()`**：步骤标签数组改为 `['⓪ 创营', '① 统筹', '② 任务池', '③ 选将', '④ 启动']`。为 Phase C 的火种指示器预留一个 `<span>` 位置（本阶段设为空或默认图标）。

**`data.camp_progress` 初始化**：默认值从 `{ step: 1, steps: {'1':'active', '2':'locked', ...} }` 改为 `{ step: 0, steps: {'0':'active', '1':'locked', ...} }`。需同时更新 `loadData()` 初始化和兼容逻辑（约 line 1738 和 1944）。

### 操作 2：新增 Step ⓪（创营）

新增 `renderStep0()` 函数：

渲染一个表单，包含：
- 营队名称（文本输入）
- 期数（下拉选择或文本输入）
- 类型（单选：常规共创营 / 特别活动营）
- 一句话主题（文本输入）
- 详细描述（文本区域，可选）
- 测试模式（复选框，勾选后创建为测试营队）

保存按钮文字为「✨ 点燃火种 · 创建营队」。

新增 `saveStep0()` 函数：

功能描述（自然语言）：
1. 读取表单中的营队名称、期数、类型、主题、描述
2. 写入 `data.camp_info.current.identity`
3. 设置 `identity.status = 'preparing'`（筹备中）
4. 设置 `identity.created_at` 为当前时间，`created_by` 为当前用户名
5. 如果勾选了测试模式，设置 `identity.test_mode = true`
6. 调用 Phase A 的 `createSnapshot('创营原档', '创建营队：' + 营队名称)` → 这会生成 v1 原档
7. 调用 `unlockStep(1)` → 解锁 Step ①
8. 调用 `switchStep(1)` → 进入下一步

### 操作 3：修改现有步骤的保存逻辑

**`saveStep1()`**（统筹保存）：
- 保存后调用 `createSnapshot('统筹完成', '日历和预算设定')`

**`saveStep2()`**（任务池保存）：
- 保存后调用 `createSnapshot('任务池完成', '共 N 项任务')`

**`saveStep3()`**（选将确认，对应的旧 `saveStep3`）：
- 保存后调用 `createSnapshot('选将完成', 'N 位共建者')`
- 同时写入 `data.camp_info.current.team.staff_cards`（从 `getStaffCards()` 读取）

### 操作 4：重写 Step ④（启动）

删除旧的 `renderStep4()` 和 `renderStep5()`，新建一个统一的 `renderStep4()`。它包含四个子阶段，通过状态变量 `wizStep4Phase` 控制（取值 `'review'` / `'deploy'` / `'ceremony'` / `'launch'`）：

**阶段 4a · 审核**：
- 显示数据摘要（NT 总池、预算、天数、任务数、共建者人数）
- 选择审核人（下拉选择，排除创建人自己）
- 「提交审核」按钮 → 写入审核状态到 `camp_info.current.governance`，通知审核人

**阶段 4b · 发包**（审核通过后显示）：
- 显示发包确认面板（列出所有共建者及其任务数/NT 数）
- 「确认发包」按钮 → 触发以下操作：
  - 遍历所有 `staff_cards` 中的共建者，调用 `changeUserRole(name, 'builder', { skipAdventurerCheck: true })`
  - 将 `camp_info.current.team` 数据推送到各共建者的工作台视图
  - 调用 `createSnapshot('发包确认', 'N位共建者已就绪')`

**阶段 4c · 开营仪式**（发包后显示）：
- 本阶段只渲染一个按钮「🎊 开始开营仪式」→ 触发 Phase C 的全屏仪式
- 如果 Phase C 尚未实现，按钮行为降级为直接跳到 4d
- 仪式结束后的回调进入 4d

**阶段 4d · 启动确认**：
- 显示启动确认面板（原档锁定提示）
- 「🏁 正式启动营队」按钮 → 触发以下操作：
  - `data.camp_info.current.identity.status = 'active'`
  - 所有草稿任务 → 转为 `active`
  - 调用 `createSnapshot('营队启动', '🏁 正式启动')`
  - 向导结束，跳转回工作台

新增 `saveStep4()` 或通过各阶段按钮分别处理。

### 操作 5：修改 `claimTasks` 和 `changeUserRole`

**`claimTasks()`**（约 line 9772）：
- 删除上周添加的 builder 升级兜底代码（约 line 9873-9882，即 `// 同步更新系统角色` 注释到 `saveUsers(users)` 那一段）
- 保留 staff card 创建和 `data.members` 更新的逻辑
- 保留 `data.members[personName].title = role`（自由文本标签仍然需要）

**`changeUserRole()`**（约 line 2353）：
- 在 `opts` 中新增可选字段 `skipAdventurerCheck`，默认 `false`
- 在 builder 升级的检查逻辑（约 line 2365-2370）中，增加条件：`if (!opts.skipAdventurerCheck && !wasAdventurer && oldRole !== 'adventurer')`

---

## 四、不改的范围（明确排除）

| 不碰 | 原因 |
|------|------|
| Phase A 的数据结构 | 只读不写（除 `createSnapshot` 在保存时调用） |
| 现有任务大厅 / 村庄 / 工作台渲染 | 发包后的"共建者看到任务包"通过现有 `renderWorkspace` 实现，不需要新渲染函数 |
| Phase C 的动画代码 | 只预留调用点（4c 的按钮），不实现动画 |
| `data.archived_periods` | 独立于 `camp_info.snapshots`，不修改 |

---

## 五、与 Phase A / C 的关系

```
Phase A（数据层）
  │  data.camp_info.current  ← Phase B 读写
  │  createSnapshot()        ← Phase B 保存时调用
  │
Phase B（本阶段）
  │  向导 UI 读写 camp_info.current
  │  保存时调用 createSnapshot
  │  Step ④-4c 触发 openCeremony()
  │
  └──→ Phase C（动画层）
          openCeremony() 实现全屏动画
          ceremony.onComplete → Phase B 的 4d 继续
```

---

## 六、验收清单

| # | 验证动作 | 预期 |
|:--:|------|------|
| 1 | 管理员进入创世终端 | 导航条显示 ⓪①②③④，当前步骤为 ⓪ |
| 2 | Step ⓪ 填写营队信息 → 点击「点燃火种」 | 解锁 Step ①，自动跳转 |
| 3 | 同上 | `data.camp_info.current.identity` 已填入表单数据 |
| 4 | 同上 | `data.camp_info.snapshots` 产生 v1（`frozen: true`） |
| 5 | 依次完成 Step ①②③ | 每次保存生成新快照 |
| 6 | Step ③ 认领任务 → 成员被加入 staff_cards | `data.members[name].title` 有自由文本标签 |
| 7 | Step ③ 认领后 | 共建者的系统角色**未**立即变为 builder（延后到发包） |
| 8 | Step ④-4a 选择审核人 → 提交 | 审核状态写入 `camp_info.current.governance` |
| 9 | Step ④-4b 发包 | 共建者系统角色变为 builder |
| 10 | Step ④-4d 启动 | 任务状态从 draft → active；生成启动快照 |
| 11 | 无 Phase C 时点「开始开营仪式」 | 直接跳到 4d，不报错 |
| 12 | 测试营队勾选 | `identity.test_mode = true`，后续可删除 |
