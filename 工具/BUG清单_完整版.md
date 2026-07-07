# BUG 清单 · 完整版

> 三组探员深度审计结论汇总 | 逐函数逐行审查
> dashboard.html ~6500 行 | 2026-07-07

---

## 🔴 P0 — 严重（数据丢失/破坏/安全）

| # | 行号 | 问题 | 影响 |
|---|------|------|------|
| 1 | 5000, 5811, 5863 | **saveStep2 / executeSync / saveWizDraft 完全替换 data.tasks**。wizardTasks 不走 NT 系统，替换后 scope、visibility、reviewer、min_season、claimants、max_slots 全部丢失 | 创世终端操作后，之前所有任务设置被清空 |
| 2 | 1312 | **seedAdminAccount() 每次页面加载重置 admin 密码为 '1500'**。改了密码，刷新页面就还原 | admin 无法真正改密码 |
| 3 | 3787, 3847 | **结算页读 `members[name].nt_actual` 而不读 `data.finance`**。`nt_actual` 只在手动编辑成员时填入，reviewTask 不会更新它 | 结算页永远看不到任务奖励 NT |
| 4 | 1219-1229 | **loadData() 任务 normalize 丢弃 materials/subtasks/outputs/steps**。导入 JSON → 材料预算、子任务、产出物全丢 | 导入导出数据循环会损失数据 |
| 5 | 1170 | **损坏的 JSON 静默失败** `try { data = JSON.parse(saved); } catch(e) {}` — 空 catch | localStorage 数据损坏时用户毫无知觉，数据丢失 |

## 🔴 P1 — 高（数据覆盖/丢失）

| # | 行号 | 问题 | 影响 |
|---|------|------|------|
| 6 | 3130-3149 | **saveTask 丢失 max_slots**：编辑保留合并没写 `task.max_slots = existing.max_slots`；新建没设默认值 | 编辑/新建任务后 max_slots 变 undefined |
| 7 | 1911 | **saveMember 覆盖 data.members[name]**：新建对象替代旧对象，wallet、actual_materials、_staff_removed 全丢 | 编辑成员后钱包地址和材料记录消失 |
| 8 | 3157-3165 | **deleteTask 只 splice 任务**：不清理 data.finance、staff_cards、wizardTasks 中的引用 | 幽灵引用，统计数不准 |
| 9 | 1923-1933 | **deleteMember 漏清理**：不清理 data.finance（NT流水）、staff_cards（成员卡片）、wizardTasks | 同上 |

## 🟡 P2 — 中（功能缺陷/刷新缺失）

| # | 行号 | 问题 | 影响 |
|---|------|------|------|
| 10 | 1567-1715 | **信箱单时间戳判定**：`inbox_lastOpened` 一个值判全部，打开即全消。应逐条核销 | 管理员错过重要提醒 |
| 11 | 2189 | **reviewTask 只刷新 NT管理**：不刷工作台、个人资料、排行榜、结算页 | 审核后其他 tab 显示过期数据 |
| 12 | 4054 | **向导中修改成员角色不持久化**：onchange 改 `data.members[...].role`，没有 `localStorage.setItem` | 刷新页面角色修改丢失 |
| 13 | 2475-2619 | **renderDailyView 多处 getElementById 无 null 检查**（taskhallDate, mapDate, *Milestones, *TaskCount, *AvatarList, *DailyTasks） | 元素缺失时 crash |
| 14 | 1950 | **renderWorkspace 的 camp 只查 claimants**：不查 `t.assignee === name`，创世分配的任务看不到 | 活动任务页空白 |
| 15 | 2276-2287 | **updateAll() 不包含 renderWorkspace、renderMyProfile、renderLeaderboard、renderNTAdmin** | saveTask/deleteTask 后这些 tab 不刷新 |
| 16 | 4840-4843 | **wizardTasks 不参与页面加载恢复**：DOMContentLoaded 不读 camp_wizard_tasks。依赖 data.tasks 不为空才回填 | 刷新页面后向导中未同步的进度全丢 |
| 17 | 4769-4770 | **废弃 budget key 只在向导中清理**：非向导路径下残留旧字段 | 预算数据膨胀 |

## 🟢 P3 — 低（代码质量/体验）

| # | 行号 | 问题 | 影响 |
|---|------|------|------|
| 18 | 1447-1449 | **promptPassword 重复定义**：第一个被第二个覆盖，死代码 | 混淆 |
| 19 | 3273-3276 | **isStaff2 重复定义**：两份完全相同的代码 | 死代码 |
| 20 | 4535-4536 | **colDrop() 重复的条件检查和变量声明** | 死代码 |
| 21 | 2376-2394 | **getMilestones() 有副作用**：伪装成 getter，实际修改 data.mapMilestones | 反模式，渲染触发数据变更 |
| 22 | 4565 | **BUDGET_ITEM_ID 计数器页面刷新后重置为 0** | 仅在 initDefaultBudgetItems 中恢复 |
| 23 | 2082-2085 | **工作台设置 onchange 写 localStorage 但不刷新 UI** | 用户必须手动切 tab 才能看到 |
| 24 | ~30 处 | **getElementById().innerHTML/textContent 无 null 检查** | tab 切换时元素缺失会 crash |
| 25 | 1537 | **HUD updateWorldHUD 不区分 scope**：营队NT和个人NT混在一起显示 | 用户分不清余额来源 |
| 26 | 1121-1170 | **data 初始化是覆盖不是 merge**：localStorage 有旧格式缺少新字段时没有默认值 | 版本升级不兼容 |

---

## 严重性分布

```
🔴 P0: 5 个 — 数据永久丢失、安全破坏
🔴 P1: 4 个 — 数据覆盖/删除不完整
🟡 P2: 8 个 — 功能缺陷/刷新缺失
🟢 P3: 9 个 — 代码质量/体验
────────────────
合计: 26 个
```

---

## 按修复领域分组

**数据完整性** (1, 2, 4, 5, 6, 7, 8, 9, 12, 14, 17) — 11 个
**刷新/同步** (11, 13, 15, 23, 24) — 5 个  
**NT 余额** (3, 25, 26) — 3 个
**导入导出** (4, 5) — 2 个
**死代码/重复** (18, 19, 20, 21, 22) — 5 个

---

*按 P0→P1→P2→P3 顺序修复。每个修完验证后再修下一个。*
