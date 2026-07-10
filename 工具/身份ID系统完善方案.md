# 身份 ID 系统完善方案

> 2026-07-10 | 重构方案

---

## 〇、要解决的问题

当前系统中有**两套平行的身份读取逻辑**：

1. `getIdentity(user)`（line 2037）——已写好，返回完整的身份对象（角色判断、权限、UI 配置、统计数据、成就、徽章等）
2. 10 个老函数（`getUserTitle`、`getUserBadges`、`getAchievements`、`calcNtTotal` 等）——在 UI 层被各处直接调用

结果是：同一个人的信息，任务卡片的权限判断走 `hasRole` / `hasNTRole`，工作台个人信息卡走 `getUserTitle` / `getAchievements`。两套读的是同一份底层数据，路径不同，**逻辑耦合散落各处，改一处容易漏另一处**。

**目标**：全项目只有两个公开的身份/财务数据入口，其余路径全部关闭。

---

## 一、最终架构

```
全项目只有两个数据入口：

  入口 1：getIdentity(user)  →  "这个人是谁、能干嘛、该看什么"
  入口 2：calcNtTotal(name)   →  "这个人有多少 NT"（纯财务查询）
         calcNtByScope(name)
```

其余 8 个老函数（`hasRole`、`hasNTRole`、`getUserTitle`、`getUserBadges`、`getAchievements`、`userTabs`、`userCan`、`_getIdentityLabel`）的外部调用**全部清零**。它们继续存在，但只被 `getIdentity` 内部调用，等同于私有函数。

**为什么 `calcNtTotal` 单独保留**：它不是身份函数，是财务函数。`sendTip` 发打赏、排行榜排序、成员列表渲染只需要余额数字，不需要完整的身份对象。它独立存在不会造成混乱——两个入口职责完全不同（查身份 vs 查账）。

---

## 二、`getIdentity` 字段速查

| 字段 | 类型 | 含义 | 替代的老函数 |
|------|------|------|------|
| `id.uid` | string | 永久编号 | — |
| `id.name` | string | 用户名 | — |
| `id.title` | string | 称号（如"🧙 管理员"） | `getUserTitle(u)` |
| `id.badges` | array | 历期身份徽章 | `getUserBadges(u)` |
| `id.stats.achievements` | array | 成就列表 | `getAchievements(name)` |
| `id.stats.nt` | number | 总 NT | `calcNtTotal(name)` |
| `id.stats.ntCamp` | number | 营地 NT | `calcNtByScope(name).camp` |
| `id.stats.ntPersonal` | number | 个人 NT | `calcNtByScope(name).personal` |
| `id.stats.daysActive` | number | 活跃天数 | 手动 `daysSince` |
| `id.profile.skills` | array | 技能标签 | `mem.skills` |
| `id.isAdmin` | bool | 是否管理员 | `hasRole(u, 'admin')` |
| `id.isBuilder` | bool | 是否共建者 | `hasRole(u, 'builder')` |
| `id.isNPC` | bool | 是否在地伙伴 | `hasRole(u, 'npc')` |
| `id.isVisitor` | bool | 是否云村民 | `hasRole(u, 'visitor')` |
| `id.can.reviewTask` | bool | 可审核任务提交 | `hasRole + hasNTRole` |
| `id.can.manageNT` | bool | 可管理 NT | `hasRole + hasNTRole` |
| `id.can.isMember` | bool | 是否营队成员 | `userCan(u, 'isMember')` |
| `id.ui.tabs` | array | 可见标签页列表 | `userTabs(u)` |

---

## 三、逐函数清理：老函数外部调用全部清零

### 3.1 `getUserTitle(u)` —— 全部替换为 `id.title`

| 位置 | 当前 | 改为 |
|------|------|------|
| HUD 刷新（line 2252） | `getUserTitle(currentUser)` | `getIdentity(currentUser).title` |
| 村庄用户信息（line 2757） | `getUserTitle(user)` | `getIdentity(user).title` |
| 工作台个人信息卡（line 3913） | `getUserTitle(user)` | `profileId.title`（在改动 4 中统一处理） |

### 3.2 `getUserBadges(u)` —— 全部替换为 `id.badges`

| 位置 | 当前 | 改为 |
|------|------|------|
| 工作台个人信息卡（line 3917） | `getUserBadges(user)` | `profileId.badges`（在改动 4 中统一处理） |

### 3.3 `getAchievements(name)` —— 全部替换为 `id.stats.achievements`

| 位置 | 当前 | 改为 |
|------|------|------|
| 工作台个人信息卡（line 3876） | `getAchievements(name)` | `profileId.stats.achievements`（在改动 4 中统一处理） |
| 个人档案（line 4248） | `getAchievements(name)` | `getIdentity(users[name]).stats.achievements` |

### 3.4 `hasRole(user, role)` —— 全部替换为内联判断或 `id.isXxx`

这个函数本身只有一行：`user.role === role`。调用它比内联还多一次函数调用开销。所有外部调用直接内联。

| 位置 | 当前 | 改为 |
|------|------|------|
| 村庄标签管理（line 2927） | `hasRole(currentUser, ['admin','npc'])` | `currentUser.role === 'admin' \|\| currentUser.role === 'npc'` |
| 工作台撤回审核区（line 3857） | `hasRole(currentUser, 'admin')` | `selfId.isAdmin` |
| 拍卖行 builder 可见（line 4826） | `hasRole(currentUser, ['admin','builder'])` | `currentUser.role === 'admin' \|\| currentUser.role === 'builder'` |
| 拍卖行参会人筛选（line 4873） | `hasRole(users[n], ['admin','builder'])` | `(users[n].role === 'admin' \|\| users[n].role === 'builder')` |
| 拍卖行主持人判断 ×2（line 4916, 4929） | `hasRole(currentUser, 'admin')` | `currentUser.role === 'admin'` |
| renderQuestCard 撤回审核（line 5465） | `hasRole(currentUser, 'admin')` | `id.isAdmin`（通过 `opts.identity` 传入） |
| renderQuestCard 标签管理（line 5515） | `hasRole(currentUser, ['admin','npc'])` | `id.isAdmin \|\| id.isNPC` |
| addCustomType（line 5897） | `hasRole(currentUser, 'visitor')` | `currentUser.role === 'visitor'` |
| switchTab 时间线视图（line 6707） | `hasRole(currentUser, ['npc','visitor'])` | `currentUser.role === 'npc' \|\| currentUser.role === 'visitor'` |
| 成员列表角色显示（line 7240） | `hasRole(user, 'admin')` | `user.role === 'admin'` |
| 玩家列表可见性（line 7810） | `hasRole(u, ['admin','builder'])` | `u.role === 'admin' \|\| u.role === 'builder'` |
| 时间线玩家过滤（line 8444） | `hasRole(u, ['visitor','npc'])` | `u.role === 'visitor' \|\| u.role === 'npc'` |

> `canUserSee`（line 2177）和 `canUserClaim`（line 2196）内部对 `hasRole` 的调用不动——它们本身就是权限中枢函数，`hasRole` 是它们的合理依赖。

### 3.5 `hasNTRole()` —— 全部替换为 `id.can.reviewTask` 或 `id.can.manageNT`

| 位置 | 当前 | 改为 |
|------|------|------|
| NT 管理页准入（line 5635） | `hasNTRole()` | `getIdentity(currentUser).can.manageNT` |
| 撤回审核（line 5848） | `hasNTRole()` | `getIdentity(currentUser).can.manageNT` |
| renderQuestCard 撤回审核（line 5465） | `hasNTRole()` | `id.can.reviewTask`（通过 `opts.identity` 传入） |

### 3.6 `userCan(user, cap)` —— 全部替换为 `id.can.*`

| 位置 | 当前 | 改为 |
|------|------|------|
| 村庄 isMember（line 2887） | `userCan(currentUser, 'isMember')` | `getIdentity(currentUser).can.isMember` |
| 村庄 isMember（line 3070） | 同上 | 同上 |
| 工作台 isMember（line 3760） | `userCan(currentUser, 'isMember')` | `selfId.can.isMember` |

### 3.7 `userTabs(user)` —— 替换为 `id.ui.tabs`

| 位置 | 当前 | 改为 |
|------|------|------|
| switchTab（line 6688） | `userTabs(currentUser)` | `getIdentity(currentUser).ui.tabs` |

### 3.8 `_getIdentityLabel(user, mi)` —— 替换为 `id.title`

| 位置 | 当前 | 改为 |
|------|------|------|
| 工作台设置面板（line 3961） | `_getIdentityLabel(user, memInfo)` | `profileId.title` |

---

## 四、集中改动：renderWorkspace 个人信息卡

这是老函数调用的最大聚集点——一个函数内调了 5 个老函数。单独拿出来做集中替换。

**新增变量**（约 line 3825，`selfId` 之后）：

```js
var profileId = getIdentity(user);
```

> `user` 已有（`users[name]`）。看自己看别人都有值。

**逐行替换**：

删除以下独立计算行（数据由 `profileId` 统一提供）：

| 行 | 删除内容 |
|------|------|
| ~3831-3832 | `var balance = calcNtByScope(name); var campNT = ..., personalNT = ..., totalNT = ...;` |
| ~3876 | `var achievements = getAchievements(name);` |
| ~3879 | `var _ds = user.created ? daysSince(user.created) : 0;` |

替换渲染行：

| 行 | 当前 | 改为 |
|------|------|------|
| ~3912 名字下方 | （不存在） | **新增** `UID: ${profileId.uid}` |
| ~3913 | `getUserTitle(user)` | `profileId.title` |
| ~3914-3916 | `achievements.map(...)` | `profileId.stats.achievements.map(...)` |
| ~3917-3922 | `var badges = getUserBadges(user); if (badges...)` | `if (profileId.badges.length > 0)` |
| ~3924 | `totalNT.toLocaleString()` | `profileId.stats.nt.toLocaleString()` |
| ~3925 | `campNT.toLocaleString()` | `profileId.stats.ntCamp.toLocaleString()` |
| ~3926 | `personalNT.toLocaleString()` | `profileId.stats.ntPersonal.toLocaleString()` |
| ~3927 | `_ds + ' 天'` | `profileId.stats.daysActive + ' 天'` |
| ~3961 | `_getIdentityLabel(user, memInfo)` | `profileId.title` |

额外替换（line 3760、3857）：在 renderWorkspace 作用域内，`selfId` 已有：

| 行 | 当前 | 改为 |
|------|------|------|
| ~3760 | `userCan(currentUser, 'isMember')` | `selfId.can.isMember` |
| ~3857 | `hasRole(currentUser, 'admin') \|\| hasNTRole()` | `selfId.isAdmin \|\| selfId.can.reviewTask` |

---

## 五、renderQuestCard：通过 opts 传入 identity

`renderQuestCard` 不在 workspace 作用域内。需要扩展参数，让调用方把 identity 传进来。

**Step 1**：在 `renderQuestCard` 的 opts 读取处（约 line 5384）新增：

```js
var id = opts.identity || null;
```

**Step 2**：替换卡片内的角色判断：

| 行 | 当前 | 改为 |
|------|------|------|
| ~5465 | `hasRole(currentUser, 'admin') \|\| hasNTRole()` | `id && (id.isAdmin \|\| id.can.reviewTask)` |
| ~5515 | `hasRole(currentUser, ['admin','npc'])` | `id && (id.isAdmin \|\| id.isNPC)` |

**Step 3**：所有调用 `renderQuestCard` 的地方，传入 `identity:` 字段：

| 调用位置 | 传参 |
|------|------|
| `renderWorkspace` 任务卡片 | `identity: selfId` |
| 任务大厅 `renderQuestBoard` | 函数顶部 `var id = getIdentity(currentUser);`，传 `identity: id` |
| 村庄任务 `renderVillageQuestHall` | 同上 |
| Hub 任务 `openHubQuestHall` | 同上 |
| 集市任务列表 | 同上 |

---

## 六、Phosphor Icons 图标库本地化

**问题**：[line 396](dashboard.html#L396) 从 unpkg CDN 加载 Phosphor Icons。`unpkg.com` 在国内经常被墙，导致图标字体加载失败。齿轮按钮（line 516 / 544）只有图标没有文字，加载失败后按钮完全不可见。

**影响**：共 7 种图标、11 处使用。

**修复**：

1. 下载 `@phosphor-icons/web@2.1.1`，提取两个文件放到 `工具/` 目录：
   - `phosphor-icons.css`
   - `phosphor-icons.woff2`（约 80KB）

   来源：`https://github.com/phosphor-icons/web/releases` 或 `npm install @phosphor-icons/web`

2. 改 line 396：

   **改前**：`<script src="https://unpkg.com/@phosphor-icons/web@2.1.1" defer></script>`

   **改后**：`<link rel="stylesheet" href="phosphor-icons.css">`

3. 所有 `<i class="ph-duotone ph-xxx">` 标签不动——CSS 类名不变，路径变本地后自动生效。

---

## 七、不改的范围

| 不碰 | 原因 |
|------|------|
| 8 个老函数本身 | 保留不动，`getIdentity` 内部继续调用它们 |
| `getIdentity` 函数 | 已经写好，不需要改 |
| `canUserSee` / `canUserClaim` 内部的 `hasRole` | 它们本身是权限中枢，`hasRole` 是合理依赖 |
| `calcNtTotal` / `calcNtByScope` | 财务函数，非身份函数。`sendTip`、排行榜、成员列表保留使用 |
| CSS `.tabs` / `.tab` | 与身份系统无关 |
| customTitle 显示 | 功能新增，不在此重构范围 |

---

## 八、执行顺序

```
Step 1：Phosphor Icons 本地化（§六）
  — 下载 2 个文件，改 1 行
  — 所有角色立即看到图标恢复

Step 2：renderWorkspace 个人信息卡（§四）
  — 集中在一个函数内，改完立即见效
  — 含 UID 新增显示

Step 3：renderQuestCard 传入 identity（§五）
  — 改函数签名 + 所有调用点（5 处）

Step 4：逐函数清理（§三）
  — 按 3.1→3.8 逐项替换
  — 每个点位 1-2 行，可批量执行

Step 5：验收
```

---

## 九、验收清单

| # | 验证动作 | 预期 |
|:--:|------|------|
| 1 | 所有角色 → 打开工作台 | 个人信息卡：UID、称号、成就、徽章、NT、活跃天数与改动前数据一致 |
| 2 | 管理员 → 查看其他成员的工作台 | 显示该成员的数据，非当前登录者的数据 |
| 3 | 齿轮按钮（管理员+冒险者顶栏） | 图标可见、可点击、下拉菜单正常 |
| 4 | 下拉菜单所有图标 | 全部可见（加载/导出/邀请码/内测/回村口/退出） |
| 5 | 任务卡片撤回审核按钮 | 仅管理员/NT管理可见，功能不变 |
| 6 | 任务卡片自定义标签按钮 | 仅管理员/在地伙伴可见，功能不变 |
| 7 | 标签栏切换 | 各角色看到的标签与改动前一致 |
| 8 | 村庄广场 / HUD / 个人档案 | 称号、NT 显示一致 |
| 9 | 拍卖行 | 主持人判断、builder 可见性、参会人筛选功能不变 |
| 10 | sendTip 发打赏 | NT 余额检查正常 |
| 11 | NT 管理页 | 准入判断正常 |
| 12 | 成员列表 / 排行榜 | 排序、NT 显示与改动前一致 |
