# 身份 ID 系统碎片化：问题分析与解决方案

> 日期：2026-07-10
> 涉及文件：`dashboard.html`（本项目唯一运行时文件）
> 备份：`存档/dashboard_20260710_身份ID系统重构前.html`

---

## 一、问题证据

### 1.1 两套平行的身份读取系统并存

**证据 A：`getIdentity` 函数已存在且功能完整**

`getIdentity(user)`（line 2037-2167）返回一个包含身份全貌的对象，覆盖 7 个层级：

| 层级 | 字段举例 | 数据来源 |
|------|------|------|
| 固定层 | `uid`、`name`、`created` | `getUsers()`、用户对象 |
| 变化层 | `role`、`title`、`season` | `ROLE_TITLES`、用户对象 |
| 履历 | `badges`、`history` | `season_history` |
| 权限 | `can.isMember`、`can.reviewTask`、`can.manageNT` 等 8 个字段 | `ROLE_CAPABILITIES` |
| 界面配置 | `ui.tabs`、`ui.mode`、`ui.showQuestBoard` 等 6 个字段 | `ROLE_CAPABILITIES` |
| 个人资料 | `profile.avatar`、`profile.bio`、`profile.skills` 等 8 个字段 | `data.members`、用户对象 |
| 实时数据 | `stats.nt`、`stats.daysActive`、`stats.achievements` 等 8 个字段 | `calcNtByScope`、任务遍历计算 |

`getIdentity` 内部已经调用了多个老函数来计算这些数据：
- line 2045：调用 `calcNtByScope(name)` 计算 NT 余额
- line 2116-2117：调用 `hasNTRole()` 设置权限字段
- line 2153：调用 `daysSince(u.created)` 计算活跃天数

**证据 B：10 个老函数在 UI 层被直接调用**

以下函数在 `getIdentity` 之外，被 UI 渲染代码直接调用（行号为重构前）：

| 老函数 | 功能 | UI 层调用次数 | 典型调用位置 |
|------|------|:--:|------|
| `hasRole(user, role)` | 判断角色是否匹配 | 13 处 | `renderQuestCard`（line 5465, 5515）、`switchTab`（line 6707）、拍卖行（line 4826, 4873, 4916, 4929）、成员列表（line 7241, 7812, 8446）、村庄标签管理（line 2927）、`addCustomType`（line 5897） |
| `hasNTRole()` | 判断是否有 NT 管理角色 | 3 处 | `renderQuestCard`（line 5465）、NT 管理页准入（line 5635）、撤回审核（line 5848） |
| `getUserTitle(u)` | 返回角色称号 | 3 处 | 工作台个人信息卡（line 3913）、HUD 刷新（line 2252）、村庄用户信息（line 2757） |
| `getUserBadges(u)` | 返回历期身份徽章 | 1 处 | 工作台个人信息卡（line 3917） |
| `getAchievements(name)` | 计算成就列表 | 2 处 | 工作台个人信息卡（line 3876）、个人档案（line 4248） |
| `userCan(user, cap)` | 检查单项权限 | 4 处 | 村庄 isMember 判断（line 2887, 3070）、工作台准入（line 3760） |
| `userTabs(user)` | 返回可见标签页列表 | 2 处 | `switchTab`（line 6688） |
| `_getIdentityLabel(...)` | 拼接身份标签字符串 | 1 处 | 工作台设置面板（line 3961） |
| `calcNtTotal(name)` | 计算总 NT | 约 15 处 | UI 显示（line 4246）、业务检查（`sendTip`、发帖、拍卖、排行榜） |
| `calcNtByScope(name)` | 分营地/个人计算 NT | 2 处 | 工作台（line 3831）、`updateWorldHUD`（line 3106） |

### 1.2 同一函数内调用多个老函数的证据

以 `renderWorkspace()`（工作台渲染函数）为例，重构前在同一个函数内为**同一个用户**调用了 5 个不同的老函数：

| 行号（重构前） | 调用 | 计算内容 |
|------|------|------|
| 3831 | `calcNtByScope(name)` | NT 余额（营地 + 个人） |
| 3874 | `daysSince(user.created)` | 活跃天数 |
| 3876 | `getAchievements(name)` | 成就列表 |
| 3913 | `getUserTitle(user)` | 称号 |
| 3917 | `getUserBadges(user)` | 历期徽章 |
| 3961 | `_getIdentityLabel(user, memInfo)` | 身份标签 |

这些调用的输入数据全部来自同一个 `user` 对象和同一个 `name` 变量，但每个调用走的是独立的函数路径，没有一个统一的入口。

### 1.3 外部资源加载失败的证据

**Phosphor Icons 图标字体**：

| 证据 | 内容 |
|------|------|
| 加载位置 | line 396：`<script src="https://unpkg.com/@phosphor-icons/web@2.1.1" defer></script>` |
| CDN 域名 | `unpkg.com` |
| 国内访问状态 | 该域名在中国大陆被墙，脚本加载失败 |
| 影响范围 | 共使用 7 种图标、11 处 HTML 标签 |
| 最严重的影响 | 齿轮按钮（line 516, 544）只有 `<i class="ph-duotone ph-gear">` 没有文字，图标加载失败后按钮为空元素，不可见、不可点击 |
| 下拉菜单按钮有文字 | 其余 9 处（加载数据、导出数据、邀请码、内测世界、回南塘村口、退出）同时包含图标和文字，图标损坏后文字仍可交互 |

---

## 二、逻辑链

### 2.1 问题定义

系统存在一个身份数据读取入口（`getIdentity`），但 UI 层没有使用它。UI 层通过 10 个相互独立的老函数分别获取身份信息。这导致了以下事实状态：

1. **同一个人的身份信息，存在两条完全不同的获取路径**。一条路径是 `getIdentity(user)`，另一条路径是逐个调用老函数。
2. **工作台个人信息卡在渲染同一个用户的身份时，调用了 5 个互不感知的老函数**。每个老函数独立从数据源取值，没有共享已计算的结果。
3. **任务卡片中的权限判断使用 `hasRole` 和 `hasNTRole`**，而同一个用户的权限信息在 `getIdentity` 返回值的 `can.*` 字段中已经计算完毕，但未被使用。
4. **`getIdentity` 已经内部调用了多个老函数**，说明老函数是 `getIdentity` 的底层依赖，但老函数同时也在外部被直接调用，形成了"底层组件被上层和中间层同时调用"的结构。

### 2.2 根因

不是缺少功能——`getIdentity` 在重构之前就已经写好了全部 30+ 个字段。根因是：

**UI 层的身份数据获取没有统一的入口约束。任何渲染函数可以自由选择：走 `getIdentity` 统一获取，还是直接调某个老函数获取单个值。**

这个自由选择导致了事实上的碎片化——如果一个渲染函数只需要"称号"这一个值，开发者自然倾向于调 `getUserTitle(user)` 而不是 `getIdentity(user).title`。每多一个这样的选择，系统就多一条独立的数据获取路径。

### 2.3 解决方案

**关闭老函数的所有外部调用路径。全项目只保留两个公开入口：**

- 入口 1：`getIdentity(user)`——获取身份全貌（角色、权限、UI 配置、个人资料、统计数据、成就、徽章）
- 入口 2：`calcNtTotal(name)` / `calcNtByScope(name)`——纯财务查询（只汇总 NT 余额）

其余 8 个老函数（`hasRole`、`hasNTRole`、`getUserTitle`、`getUserBadges`、`getAchievements`、`userCan`、`userTabs`、`_getIdentityLabel`）的外部调用全部清零。它们继续存在，但只被 `getIdentity` 内部调用，等同于私有函数。

**具体执行**：

1. `renderWorkspace()` 个人信息卡——新增 `profileId = getIdentity(user)` 作为统一数据源，所有称号、徽章、成就、NT、活跃天数的渲染全部改为读取 `profileId.*` 字段。同时新增 UID 显示。
2. `renderQuestCard()`——通过 `opts.identity` 参数接收调用方已计算好的 identity 对象，卡片内的角色判断从 `hasRole` + `hasNTRole` 改为读取 `id.isAdmin`、`id.can.reviewTask`、`id.isNPC`。
3. 所有 `renderQuestCard` 的调用方——在调用前计算一次 `getIdentity(currentUser)`，通过 `identity:` 字段传入。
4. `hasRole` 的 13 处外部调用——全部内联为 `user.role === 'xxx'`（该函数本质上就是一行字符串比较，内联比调用更直接）。
5. `hasNTRole` 的 3 处外部调用——改为 `getIdentity(currentUser).can.reviewTask` 或 `.can.manageNT`。
6. `userCan` 的 4 处外部调用——改为 `getIdentity(currentUser).can.isMember`。
7. `userTabs` 的 2 处外部调用——改为 `getIdentity(currentUser).ui.tabs`。
8. `getUserTitle`、`getUserBadges`、`getAchievements`、`_getIdentityLabel` 的外部调用——全部改为读取 `getIdentity` 返回值的对应字段。

**同时解决的独立问题**：

9. Phosphor Icons 图标库——从 unpkg CDN 下载改为本地嵌入。将 `@phosphor-icons/web@2.1.1` 的 CSS 和 woff2 字体文件放入项目目录，HTML 引用从 `<script src="https://unpkg.com/...">` 改为 `<link rel="stylesheet" href="phosphor-icons.css">`。

### 2.4 不改的范围

| 不碰 | 原因 |
|------|------|
| 10 个老函数的函数体 | `getIdentity` 内部继续调用它们，函数本身没有错误 |
| `getIdentity` 函数体 | 逻辑正确，不需要改 |
| `canUserSee` / `canUserClaim` 内部的 `hasRole` 调用 | 它们本身是权限中枢函数，`hasRole` 是它们合理的内部依赖 |
| `calcNtTotal` / `calcNtByScope` 的调用 | 财务计算函数，非身份展示函数。排行榜排序、成员列表、`sendTip` 余额检查等场景只需要一个数字，调用完整 `getIdentity` 会浪费计算 |
| CSS `.tabs` / `.tab` | 与身份系统无关 |
| customTitle 显示 | 功能新增，不在此重构范围 |
| DiceBear 头像 | 外部 API 问题，需要单独评估处理方案 |

### 2.5 保留 `calcNtTotal` 作为独立入口的原因

`calcNtTotal` 和 `getIdentity` 不构成"两套平行逻辑"，因为它们的底层数据源是同一个：`calcNtByScope`（遍历 `data.finance` 汇总 NT）。

`getIdentity` 内部调用 `calcNtByScope` 来填充 `stats.nt`。`calcNtTotal` 也是 `calcNtByScope` 的薄封装。两条路径最终读取的是同一份 `data.finance`，计算的是同一个结果。

之所以保留 `calcNtTotal` 作为独立入口，是因为以下场景只需要 NT 余额这一个数字：

- `sendTip` 发打赏前检查余额是否够 5 NT
- 排行榜对 50 个成员按 NT 排序（排序比较器会被调用 O(n log n) 次）
- 成员列表每个成员显示 NT 余额

这些场景调用 `getIdentity` 会额外遍历全部 tasks 计算成就、遍历 season_history 计算徽章——只为获取一个余额数字，浪费 95% 以上的计算量。

---

## 三、解决方案效果说明（含代码逻辑）

### 3.1 数据流变化

**改前**：

```
renderWorkspace()
  ├── getUserTitle(user)        → 读 ROLE_TITLES
  ├── getUserBadges(user)       → 读 season_history
  ├── getAchievements(name)     → 遍历 tasks，计算成就
  ├── calcNtByScope(name)       → 遍历 finance，汇总 NT
  └── daysSince(user.created)   → 计算活跃天数

renderQuestCard(t, opts)
  ├── hasRole(currentUser, 'admin')   → 读 currentUser.role
  └── hasNTRole()                     → 读 staff_cards

switchTab(name)
  ├── userTabs(currentUser)           → 读 ROLE_CAPABILITIES
  └── hasRole(currentUser, ...)       → 读 currentUser.role
```

**改后**：

```
renderWorkspace()
  ├── profileId = getIdentity(user)     ← 一次性获取身份全貌
  │     ├── profileId.title             → 替代 getUserTitle
  │     ├── profileId.badges            → 替代 getUserBadges
  │     ├── profileId.stats.achievements → 替代 getAchievements
  │     ├── profileId.stats.nt          → 替代 calcNtByScope
  │     └── profileId.stats.daysActive  → 替代 daysSince
  └── selfId = getIdentity(currentUser) ← 用于权限判断
        ├── selfId.isAdmin             → 替代 hasRole(currentUser, 'admin')
        ├── selfId.can.reviewTask      → 替代 hasNTRole()
        └── selfId.can.isMember        → 替代 userCan(currentUser, 'isMember')

renderQuestCard(t, opts)
  └── id = opts.identity               ← 由调用方传入
        ├── id.isAdmin                 → 替代 hasRole
        ├── id.isNPC                   → 替代 hasRole
        └── id.can.reviewTask          → 替代 hasNTRole

switchTab(name)
  └── getIdentity(currentUser).ui.tabs → 替代 userTabs
```

### 3.2 调用次数变化

| 场景 | 改前 | 改后 |
|------|------|------|
| 工作台个人信息卡渲染 | 5 次老函数调用（独立计算，无共享） | 1 次 `getIdentity(user)` + 字段读取 |
| 工作台任务卡片权限判断 | 每次 `renderQuestCard` 内调 `hasRole` + `hasNTRole` | 调用方传 `selfId`，卡片内无函数调用 |
| 村庄任务卡片权限判断 | 每次 `renderQuestCard` 内调 `hasRole` + `hasNTRole` | 调用方计算一次 `getIdentity`，传入 `opts.identity` |
| `switchTab` 标签过滤 | 调 `userTabs(currentUser)` | 调 `getIdentity(currentUser).ui.tabs` |
| 13 处 `hasRole` 调用 | 每次函数调用 `hasRole(user, roles)` | 内联 `user.role === 'xxx'`（零函数调用开销） |

### 3.3 格式兼容性

`getIdentity` 返回值的结构在重构前后完全一致（没有新增或删除字段）。UID 显示是 UI 层新增的渲染行，不改变 `getIdentity` 的返回结构。

所有老函数的函数体保留不动。`getIdentity` 内部对这些函数的调用路径不变。重构只关闭了外部调用路径，没有修改任何函数内部逻辑。

---

## 四、解决方案效果说明（纯自然语言 / 功能性语言）

### 4.1 改前状态

系统里有一个完整的身份信息查询入口，叫 `getIdentity`。你给它一个用户对象，它返回这个人的全部身份信息——编号、名字、角色、称号、权限、能看到哪些界面标签、个人资料、NT 余额、成就徽章。这些信息覆盖了七个维度，全部字段加起来超过三十个。

但是这个查询入口在重构之前几乎没有被 UI 层使用。UI 层走的是另一条路：每次需要知道一个身份信息，就单独去调一个专门的小函数。需要知道称号，就调"取称号"函数。需要知道徽章，就调"取徽章"函数。需要知道 NT 余额，就调"算余额"函数。需要知道用户是不是管理员，就调"判断角色"函数。

这些小函数本身没有错。但问题在于，同一个页面渲染同一个用户的信息时，这些小函数会被反复调用，每个都独立从数据源取值，互不知道彼此的存在。以工作台个人信息卡为例，渲染一个人的完整名片需要调五个不同的小函数——实际上这些信息都在同一个查询入口里已经算好了，只是没有人用。

这就好比办公楼有一个正门，门内所有楼层都通。但每层楼又在外面单独开了一个侧门，人们习惯了走侧门，正门一直开着但没人走。

另一个独立的问题是图标字体。页面从 unpkg.com 这个国外 CDN 加载图标字体库，这个域名在国内被墙。结果所有纯图标的按钮都变成了空白——因为没有文字标签，图标加载失败后按钮就是一个零尺寸的空元素，用户根本不知道那里有一个按钮。

### 4.2 改后状态

所有 UI 代码如果需要知道"这个人是谁"，统一走 `getIdentity` 查询。老函数的侧门全部关闭——它们继续存在，但只作为 `getIdentity` 内部的支撑组件，不再对外暴露。

工作台个人信息卡现在只做一次身份查询，然后直接从查询结果里读取称号、徽章、成就、NT 余额、活跃天数——不再分别调用五个小函数。同时新增了永久编号的显示，让每个成员的身份信息更完整。

任务卡片的权限判断也不再直接调用"判断角色"和"判断 NT 管理权"这两个老函数。调用方在渲染卡片之前计算好当前用户的身份对象，通过参数传给卡片渲染函数。卡片内部只读字段值，不做函数调用。

所有"判断角色"的调用点都直接内联为角色值的字符串比较——因为这个判断本质上就是看一个人的角色字段是不是等于某个值，不需要通过函数包装。

图标字体库从国外 CDN 搬到了项目本地——下载了两个文件放到项目目录里，页面直接加载本地文件，不再依赖任何外部域名。所有图标恢复显示，齿轮按钮重新可见可点。

### 4.3 全局效果

改完后，全项目只有两个公开入口可以获取身份和财务数据：身份查询（`getIdentity`）和余额查询（`calcNtTotal`）。这两个入口分别服务于不同类型的需求——前者用于需要全面了解一个人的场景（个人名片、权限判断、界面配置），后者用于只需要一个余额数字的场景（检查打赏前余额够不够、排行榜排序）。

新加入项目的开发者不需要在"我该调哪个函数"之间做选择：需要知道这个人是谁，调身份查询；只需要知道余额，调余额查询。没有其他选项。

---

## 五、改动量统计

| 类别 | 改动处数 | 涉及函数 |
|------|:--:|------|
| 老函数外部调用清零 | 约 30 处 | `renderWorkspace`、`renderQuestCard`、`switchTab`、`updateWorldHUD`、`showPlazaPlaceholder`、`renderMyProfile`、`renderMemberDetailFor`、`renderDailyView`、`renderVillageQuestHall`、`renderQuestBoard`、`refreshUserHUD`、`renderVillageActivityList`、拍卖行函数、`addCustomType`、成员列表、时间线过滤 |
| 工作台个人信息卡新增 UID | 1 处 | `renderWorkspace` |
| renderQuestCard 参数扩展 | 1 处（函数签名）+ 5 处（调用方传参） | `renderQuestCard` + 5 个调用方 |
| Phosphor Icons 本地化 | 1 行 HTML + 2 个新增文件 | line 396 |
| **总计** | **约 40 处** | **16 个函数** |

所有改动均为 1-2 行的局部替换。没有新增函数，没有修改函数签名（`renderQuestCard` 的 `opts` 参数是已有的扩展点，增加一个字段不破坏现有调用），没有修改任何老函数的内部逻辑。

---

## 六、相关文件

| 文件 | 说明 |
|------|------|
| `dashboard.html` | 本项目唯一运行时文件，所有改动在此文件中 |
| `phosphor-icons.css` | 新增，Phosphor Icons Duotone 样式文件（231KB） |
| `Phosphor-Duotone.woff2` | 新增，Phosphor Icons Duotone 字体文件（164KB） |
| `存档/dashboard_20260710_身份ID系统重构前.html` | 重构前备份 |
| `身份ID系统完善方案.md` | 重构方案文档 |
