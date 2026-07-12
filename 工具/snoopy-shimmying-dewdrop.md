# 南塘云村 (cloud-village.html) 实施方案

## 上下文

**为什么做**：当前 dashboard.html 中的村口占位页过于简陋（一段文字 + 退出按钮），远程/云上参与者没有一个属于自己的入口空间。需要做一个独立的静态页面「南塘云村」，给游客和在地伙伴使用。

**核心理念**：
- 独立单文件（`cloud-village.html`），将来拼入主应用
- 与 dashboard.html 共享同一套 localStorage key，数据互通
- 专注做游客/NPC 的注册和云村体验，不涉及管理员/共建者/冒险者功能
- 所有数据接口预留清晰，后续扩展不改地基

---

## 页面结构（三视图切换）

```
┌─────────────────────────────────────────┐
│  View 1: 着陆页                         │
│  ☁️ 南塘云村 · 云上空间                  │
│  [注册成为云村民]  [我是老村民]           │
│  （自动检测 nt_session，已登录直接进入）   │
├─────────────────────────────────────────┤
│  View 2a: 注册表单                      │
│  头像选择 → 名字 → 密码 → 云上访客/在地伙伴│
│  [注册并进入]                           │
├─────────────────────────────────────────┤
│  View 2b: 简易登录                      │
│  名字 → 密码 → [进入云村]               │
├─────────────────────────────────────────┤
│  View 3: 云村主界面                     │
│  ┌──────────┐ ┌──────────────────┐     │
│  │ 个人资料  │ │ 📢 云村公告       │     │
│  │ 头像/名字 │ │ （预留：动态公告）  │     │
│  │ 身份/日期 │ │                  │     │
│  └──────────┘ └──────────────────┘     │
│  ┌──────────────────────────────┐     │
│  │ 🔓 升级身份（世界码/NPC邀请码）│     │
│  └──────────────────────────────┘     │
│  ~~ 预留扩展区（任务板/地图/排行榜）~~   │
└─────────────────────────────────────────┘
```

---

## 数据接口（与 dashboard.html 共享的 localStorage key）

### 写入 + 读取（云村和主界面都写）

| Key | 结构 | 云村写入时机 |
|-----|------|------------|
| `nt_users` | `{ "name": { name, role, password, avatar_seed, created, world_id } }` | 注册时（role=visitor/npc，world_id=null） |
| `nt_session` | `{ name, role }` | 登录/登出时 |
| `nt_invite_codes` | `["NT-XXXXXXXX", ...]` | NPC邀请码被消耗时（filter移除） |

### 只读（云村只读，主界面写入）

| Key | 用途 |
|-----|------|
| `nt_world_codes` | doUpgrade 检查世界码 |
| `camp_data` | 注册时同步 member 记录（可选） |

### 预留（当前不读写，为未来扩展定义）

| Key | 用途 |
|-----|------|
| `nt_village_news` | 云村公告 `[{ id, title, content, posted_by, posted_at }]` |
| `nt_village_tasks` | 云村日常委托 `[{ id, title, description, points, status }]` |

---

## 复用清单（从 dashboard.html 字节级复制）

| 内容 | dashboard.html 行号 | 说明 |
|------|-------------------|------|
| `:root` CSS 变量 | 8-19 | 完整复制，保证视觉一致 |
| `.card` / `.btn` / `.btn.pri` 样式 | 83-101 | 复用按钮卡片系统 |
| `CHARACTER_SEEDS` | 1198 | 60个头像种子 |
| `AVATAR_STYLE = 'avataaars'` | 1207 | DiceBear 风格 |
| `encodePassword()` | 1237 | btoa+encodeURIComponent |
| `getUsers()` / `saveUsers()` | 1233-1234 | 用户读写 |
| `getWorldCodes()` | 1369 | 世界码读取 |
| `getInviteCodes()` / `saveInviteCodes()` | 1367-1368 | NPC邀请码读写 |
| `esc()` / `escAttr()` | dashboard | HTML转义 |
| `avatarCircle()` | 3359 | DiceBear头像渲染 |
| `doUpgrade()` 逻辑 | 1494-1524 | 升级逻辑（适配云村） |

**原则**：这些函数一个字不改地复制，保证两个文件的密码编码、数据读写完全一致。

---

## 新增内容（云村独有）

### 视觉
- 天空/云朵主题（`--village-sky: #d6e8f5`），区别于 dashboard 的羊皮纸暖色
- `.village-header` 云朵横幅（CSS 渐变 + border-radius 模拟云朵）
- `.village-grid` 双列布局（768px 断点变单列）

### 逻辑
- `detectSession()` — 自动检测 `nt_session`，实现「来过就直接进」
- `registerUser()` — 简化版，游客/NPC 不需要邀请码
- `loginUser()` — 简化版，只做密码比对 + session 写入
- 升级为冒险者后 `location.href = 'dashboard.html'` 跳转到主界面

---

## 关键设计决策

1. **不复制 dashboard 的用户网格 + 密码弹窗登录**：云村用简单的名字+密码表单，符合「少即是多」。
2. **升级为冒险者后跳转到 dashboard.html**：冒险者的任务/排行等功能在主界面，云村只负责注册和初步体验。
3. **`renderVillage()` 从 `nt_users` 重读角色**：防止 `nt_session` 中的角色信息过时。
4. **预留扩展点**：`#villageExtensions` div + 预留 localStorage key，后续加功能只需在这里追加渲染函数。

---

## 实施步骤（约 6-8 小时）

### Step 1：文件骨架 + CSS（~2h）
- 创建 `cloud-village.html`
- 复制 `:root` 变量、`.card`、`.btn` 样式
- 添加云村主题色和 `.village-header`、`.village-grid` 样式
- 搭建三视图 HTML 结构

### Step 2：数据层 + 认证层（~2h）
- 复制所有工具函数（encodePassword, getUsers, avatarCircle 等）
- 实现 `detectSession`、`registerUser`、`loginUser`、`logoutUser`
- 实现 `doUpgrade`（适配云村，升级后跳转 dashboard）

### Step 3：UI 层（~2h）
- 视图切换逻辑（showLanding / showRegister / showLogin / showVillage）
- 注册表单 UI（头像选择器、身份选择、验证）
- 简易登录表单 UI
- 云村主视图（renderProfileCard、renderVillageStatus、renderUpgradeSection）

### Step 4：CSS 打磨 + 响应式（~1h）
- 移动端适配（768px 断点）
- 视觉一致性检查

### Step 5：集成测试（~30min）
- 云村注册游客 → dashboard 能看到
- dashboard 改角色 → 云村刷新后反映
- NPC 邀请码消耗 → 两边数据一致
- session 互认 → 一边登录另一边自动识别

---

## 验收标准

- [ ] 游客/NPC 能注册并进入云村主界面
- [ ] 老用户能被自动检测并直接进入
- [ ] 简易登录（名字+密码）可用
- [ ] 升级：世界码 → 冒险者（跳转 dashboard）
- [ ] 升级：NPC邀请码 → NPC（消耗码，留在云村）
- [ ] `nt_users` 中注册的用户在 dashboard 登录页可见
- [ ] 云村视觉有独立的「天空/云朵」感觉
- [ ] 文件约 800 行，不冗余
