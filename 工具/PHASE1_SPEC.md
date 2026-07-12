# 第一阶段实施规格书

> 版本：v3
> 目标：将 dashboard.html 从「单一面板管理工具」改造为「南塘世界·双面终端」
> 基线文件：dashboard.html（5,677 行）
> 备份：dashboard_archive_20260706.html
> 审查：已通过两轮 AI 审查，已知问题均已修正

---

## 〇、前置步骤：清理重复代码

### 现状

dashboard.html 中以下函数定义了**两次**（约第 900-1970 行为第一组，约第 2700-3510 行为第二组）：

- `renderMembers` / `renderPlayerDetail` / `renderPlayers`
- `renderTimeline` / `renderCalendar` / `switchScheduleView`
- `renderBudget` / `renderSettlementAll`
- `getStaffNames` / `recalcFinanceByPerson` / `aggregateMaterialBudgets`
- `showAvatarPicker` / `updateAvatarPreview` / `showAddMember`
- `esc` / `escAttr` / `avatarCircle`

### 哪组是对的

第一组中 `recalcFinanceByPerson`（第 2004 行）缺少一个闭合括号 `}`。这导致跟在其后的 `aggregateMaterialBudgets`、`isStaff2`、`renderMembers`、`renderPlayers`、`renderTimeline`、`renderBudget`、`renderSettlementAll` 等十几个函数被嵌套在它内部，变成了局部变量，外界调用不到。

第二组（~2700-3510 行）括号正确、功能完整。

### 清理步骤

1. **精确对比**：列出第一组和第二组中每一对同名函数，确认第二组完整
2. **检查独有函数**：`parseDate`（第 2737 行）只在第二组出现，必须保留
3. **操作**：删除第一组中与第二组重复的函数定义，保留第二组
4. **修复**：第一组中 `recalcFinanceByPerson` 如果被早期代码引用，检查是否依赖它的全局可见性——因为第二组中的版本是全局的，删掉第一组有 bug 的版本后反而不受影响
5. **验证**：git commit，打开 dashboard.html，确认所有标签页正常渲染

**注意**：不要用行号范围一刀切。逐个函数对比后再删。

---

## 一、改造策略

### 1.1 核心原则

- **不动数据结构**：`data` 对象的所有字段保持不变，导出/导入 JSON 格式不变
- **只加身份层**：在现有渲染层之上加登录、角色、权限三道过滤
- **一张网页两张脸**：共建者看到「世界终端」（深色），冒险者看到「副本游戏」（暖色）

### 1.2 安全边界（诚实标注）

本阶段的"认证"本质是**本地分身份使用**，不是真正的安全认证。

- 密码存储使用 `btoa(encodeURIComponent(...))` ——这是可逆编码，不是加密哈希。任何能看到 localStorage 的人都可以解码还原
- 登录态存储在 localStorage 的 `nt_session` 中，可以在浏览器控制台手动伪造
- **它解决的是**："多人共用一台电脑时，互相不误看对方的界面"
- **它不解决的是**："防止恶意访问"——真正的访问控制需要后端服务器

在代码中：
- 函数命名为 `encodePassword`，不是 `hashPassword`
- 函数上方加注释：`// 简单编码，防止路过式窥屏，不防恶意篡改`

### 1.3 现有 CSS 架构

- 有两套重复的 CSS 定义，第二套（行 59-79）覆盖第一套
- 第二套中大量硬编码颜色（`#e8d5b0`、`#d5c4a8` 等），不在 CSS 变量体系中
- 现有变量名是 `--card`（不是 `--card-bg`），新变量必须对齐

### 1.4 现有数据模型（不动）

```js
data = {
  tasks: [],           // 所有任务/委托
  decisions: [],       // 决策记录
  members: {},         // { name: { name, role, avatar_seed, gender, ... } }
  budget: {},          // 预算数据
  finance_cny: {},     // RMB 财务流水
  finance: [],         // NT 财务流水
  schedule: {},        // 日程安排
  camp_progress: {},   // 向导进度 { step: 1, steps: {...} }
  camp_dates: {},      // 营期时间 { start, end, duration_days, milestones }
  staff_cards: [],     // 共建者卡片（向导步骤③生成）
}
```

---

## 二、新增数据：用户系统

### 2.1 localStorage key 全集

| Key | 用途 | 说明 |
|-----|------|------|
| `camp_data` | 营地核心数据 | 现有，不动 |
| `camp_wizard_tasks` | 向导步骤②临时任务 | 现有，不动 |
| `camp_templates` | 任务/日程模板 | 现有（注意是单 key，不是 `camp_templates_tasks`） |
| **新增** `nt_users` | 用户账号表 | `{ "砚仁": { name, password, role, avatar_seed, created } }` |
| **新增** `nt_invite_codes` | 共建者邀请码 | `["NT-XXXX", ...]` |
| **新增** `nt_session` | 当前登录会话 | `{ name, role }` |
| **新增** `nt_remembered_user` | 记住我 | `{ name, role }`（仅用户勾选时写入） |

### 2.2 用户账号结构

```js
// nt_users 中每条记录：
{
  name: "砚仁",
  password: "YS43cHB...",   // encodePassword 的结果
  role: "builder",          // 'builder' | 'adventurer'
  avatar_seed: 12,
  created: "2026-07-06"
}
```

### 2.3 会话状态

```js
let currentUser = null;     // { name, role }  — 当前登录用户
let previewMode = false;    // 共建者正在预览冒险者视角时为 true
let pendingLoginName = null; // 用户列表中选中待登录的用户名
```

---

## 三、CSS 改造

### 3.1 CSS 变量体系

```css
/* 默认 = 冒险者暖色 */
:root {
  --bg: #f7f3ed;
  --card: #fffdf9;          /* 注意：沿用现有变量名 --card，不新建 --card-bg */
  --text: #3d3629;
  --muted: #9b9078;
  --accent: #c88740;
  --green: #5d9442;
  --red: #b84c38;
  --yellow: #c8892e;
  --border: #e5ddce;
  --font: system-ui, -apple-system, 'Segoe UI', 'Noto Sans SC', sans-serif;
  --pixel: 'Courier New', monospace;
  --tab-bg: #d5c4a8;
  --tab-hover: #e0d0b8;
  --tab-active-bg: #fffdf9;
  --btn-bg: #e8d5b0;
  --btn-hover: #f0e0c0;
  --btn-border: #8b7355;
  --header-start: #fdfaf5;
  --header-end: #f8f2e8;

  /* 卡牌颜色（两个主题共用） */
  --card-gold: #c8a030;
  --card-green: #5d9442;
  --card-brown: #8b7355;
  --card-purple: #8b5a9e;
  --card-blue: #5b8cb8;
}

/* 建造者模式 = 深色终端 */
body.builder-mode {
  --bg: #1a1410;
  --card: #241e18;
  --text: #d4c8b0;
  --muted: #8a7a5e;
  --accent: #c8a860;
  --green: #6b9b4e;
  --red: #c4553d;
  --yellow: #d4a840;
  --border: #3a3028;
  --tab-bg: #2a2218;
  --tab-hover: #3a3028;
  --tab-active-bg: #241e18;
  --btn-bg: #3a3028;
  --btn-hover: #4a3a2a;
  --btn-border: #6a5a3e;
  --header-start: #1a1410;
  --header-end: #241e18;
}
```

### 3.2 CSS 重构步骤

1. 以第二套 CSS（行 59-79）为基底，逐个把硬编码颜色替换为 `var(--xxx)`：
   - `#f7f3ed` → `var(--bg)`
   - `#fffdf9` → `var(--card)`
   - `#3d3629` → `var(--text)`
   - `#9b9078` → `var(--muted)`
   - `#c88740` → `var(--accent)`
   - `#e5ddce` → `var(--border)`
   - `#e8d5b0` → `var(--btn-bg)`
   - `#f0e0c0` → `var(--btn-hover)`
   - `#d5c4a8` → `var(--tab-bg)`
   - `#8b7355` → `var(--btn-border)`
   - 等等
2. 删除第一套已被覆盖的 CSS 规则
3. 每改几个值就刷新浏览器确认样式未变
4. Header 背景图片 `ai_expand_image1783014990973.png` 不动

### 3.3 新增组件样式

```css
/* 世界状态条 */
.world-hud {
  display: flex; gap: 24px; align-items: center; padding: 8px 24px;
  background: var(--card); border-bottom: 1px solid var(--border);
  font-size: .82rem; flex-wrap: wrap;
}

/* 模式切换栏 */
.mode-bar {
  display: flex; gap: 4px; align-items: center; padding: 6px 24px;
  background: var(--card); border-bottom: 1px solid var(--border);
}
.mode-btn {
  padding: 5px 14px; border: 1px solid var(--border); border-radius: 4px;
  cursor: pointer; font-size: .82rem; background: var(--btn-bg); color: var(--text);
}
.mode-btn.active { background: var(--accent); color: #fff; }

/* 委托卡片网格 */
.quest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
@media (max-width: 640px) { .quest-grid { grid-template-columns: 1fr; } }

/* 委托卡片 */
.quest-card {
  background: var(--card); border: 2px solid var(--border);
  border-radius: 10px; padding: 16px; position: relative;
  cursor: pointer; transition: .15s; overflow: hidden;
}
.quest-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }
.quest-card.gold  { border-color: var(--card-gold); }
.quest-card.green { border-color: var(--card-green); }
.quest-card.brown { border-color: var(--card-brown); }
.quest-card.purple { border-color: var(--card-purple); }
.quest-card.blue  { border-color: var(--card-blue); }

/* 完成印章 */
.quest-card.done { opacity: .75; }
.quest-card.done::after {
  content: '✅ 已完成'; position: absolute; top: 50%; left: 50%;
  transform: translate(-50%,-50%) rotate(-15deg);
  font-size: 2rem; font-weight: 900; color: var(--green);
  opacity: .35; pointer-events: none; white-space: nowrap;
}

/* 卡片内部 */
.quest-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.quest-card-badge {
  display: inline-block; padding: 2px 8px; border-radius: 3px;
  font-size: .7rem; font-weight: 800; background: var(--accent); color: #fff;
}
.quest-card-type { font-size: .75rem; color: var(--muted); }
.quest-card-title { font-size: .95rem; font-weight: 700; margin-bottom: 10px; color: var(--text); }
.quest-card-meta { display: flex; gap: 12px; font-size: .78rem; color: var(--muted); margin-bottom: 8px; }
.quest-card-reward { font-size: 1.3rem; font-weight: 800; color: var(--card-gold); text-align: right; }

/* 登录页 */
.login-page {
  position: fixed; inset: 0; z-index: 1000; display: flex;
  align-items: center; justify-content: center;
  background: radial-gradient(ellipse at 50% 30%, rgba(160,140,100,.15), transparent 60%),
              linear-gradient(180deg, #e8f0e0, #f2efe4, #f7f3ed);
}
body.builder-mode .login-page {
  background: radial-gradient(ellipse at 50% 30%, rgba(200,168,96,.1), transparent 60%),
              linear-gradient(180deg, #1a1410, #241e18);
}

/* 头像网格 */
.avatar-grid { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
.avatar-chip {
  cursor: pointer; text-align: center; padding: 8px; border-radius: 10px;
  border: 2px solid transparent; transition: .15s;
}
.avatar-chip:hover { border-color: var(--accent); background: rgba(200,135,64,.08); }
```

### 3.4 保留不动的现有样式

- 表格样式、日历样式（`.cal-table`）、时间线样式（`.timeline-wrap`）
- 模态框样式（`.modal-overlay`、`.modal`）、进度条样式（`.completeness`）
- Header 背景图片、DiceBear 头像、统计卡片（`.stats`、`.stat`）

---

## 四、HTML 改造

### 4.1 新增：登录页

放在 `<main>` 之前，默认显示，登录成功后隐藏。

```html
<div id="loginPage" class="login-page">
  <!-- 入口 -->
  <div id="loginEntry" style="text-align:center;max-width:520px;padding:40px">
    <div style="font-size:4rem;margin-bottom:8px">🏰</div>
    <h1 style="font-size:1.6rem;margin:0 0 4px">🌍 南塘·第四期</h1>
    <p style="font-size:.9rem;color:var(--muted);margin:0 0 4px">「寻找」—— 艺术共创生活副本</p>
    <p id="loginDateRange" style="font-size:.8rem;color:var(--muted);margin:0 0 32px">—</p>
    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
      <button class="btn pri" onclick="showRegister('adventurer')" style="font-size:.9rem;padding:12px 24px">⚔️ 我是新来的冒险者</button>
      <button class="btn" onclick="showRegister('builder')" style="font-size:.9rem;padding:12px 24px">🧙 我是世界建造者</button>
      <button class="btn" onclick="showUserList()" style="font-size:.9rem;padding:12px 24px">📋 我上次来过</button>
    </div>
  </div>

  <!-- 注册表单 -->
  <div id="registerForm" class="hidden" style="text-align:center;max-width:420px;padding:32px">
    <h2 id="registerTitle"></h2>
    <div style="margin:16px 0;cursor:pointer" id="regAvatarPreview"></div>
    <button class="btn" onclick="cycleRegAvatar()" style="font-size:.7rem">🎨 换头像</button>
    <input type="text" id="regName" placeholder="你的名字" style="display:block;width:100%;margin:12px 0;padding:10px;border:2px solid var(--border);border-radius:8px;font-size:.9rem;text-align:center">
    <input type="password" id="regPassword" placeholder="设置密码（至少2位）" style="display:block;width:100%;margin:12px 0;padding:10px;border:2px solid var(--border);border-radius:8px;font-size:.9rem;text-align:center">
    <div id="regInviteRow" class="hidden">
      <input type="text" id="regInviteCode" placeholder="建造者邀请码" style="display:block;width:100%;margin:12px 0;padding:10px;border:2px solid var(--border);border-radius:8px;font-size:.9rem;text-align:center">
    </div>
    <div id="regError" style="color:var(--red);font-size:.82rem;margin:8px 0"></div>
    <div style="display:flex;gap:8px;justify-content:center;margin-top:16px">
      <button class="btn" onclick="showLoginEntry()">← 返回</button>
      <button class="btn pri" onclick="doRegister()">确认注册 →</button>
    </div>
  </div>

  <!-- 用户列表 -->
  <div id="userListPanel" class="hidden" style="text-align:center;max-width:600px;padding:32px">
    <h2 style="margin-bottom:16px">选择你的身份</h2>
    <div style="margin-bottom:20px">
      <div style="font-size:.85rem;font-weight:600;color:var(--accent);margin-bottom:8px">🧙 共建者</div>
      <div class="avatar-grid" id="builderUserGrid"></div>
    </div>
    <div style="margin-bottom:20px">
      <div style="font-size:.85rem;font-weight:600;color:#5b8cb8;margin-bottom:8px">⚔️ 冒险者</div>
      <div class="avatar-grid" id="adventurerUserGrid"></div>
    </div>
    <button class="btn" onclick="showLoginEntry()" style="margin-top:16px">← 返回入口</button>
  </div>

  <!-- 密码弹窗 -->
  <div id="passwordModal" class="modal-overlay">
    <div class="modal" style="text-align:center">
      <h2>输入密码</h2>
      <div id="pwdModalAvatar" style="margin:12px 0"></div>
      <div id="pwdModalName" style="font-weight:700;margin-bottom:12px"></div>
      <input type="password" id="pwdModalInput" placeholder="密码" style="width:100%;padding:10px;border:2px solid var(--border);border-radius:8px;font-size:.9rem;text-align:center">
      <label style="font-size:.78rem;cursor:pointer;display:block;margin:8px 0">
        <input type="checkbox" id="pwdRememberMe"> 记住我（下次自动登录）
      </label>
      <div id="pwdModalError" style="color:var(--red);font-size:.82rem;margin:8px 0"></div>
      <div class="actions" style="justify-content:center">
        <button class="btn" onclick="closePasswordModal()">取消</button>
        <button class="btn pri" onclick="doLogin()">进入世界 →</button>
      </div>
    </div>
  </div>
</div>
```

**日期动态化**：`loginDateRange` 从 `data.camp_dates` 读取，不硬编码。

### 4.2 删除：原欢迎页

删除现有 `defaultView`（行 297-321）。登录页完全替代。

### 4.3 新增：世界状态条

放在 header 下方：

```html
<div id="worldHUD" class="world-hud hidden">
  <span>🌍 <b id="hudWorldName">南塘·第四期</b></span>
  <span>⏳ 距启动 <b id="hudDaysLeft">—</b> 天</span>
  <span>👥 冒险者 <b id="hudAdventurers">—</b></span>
  <span>💰 ¥<b id="hudRMB">—</b></span>
  <span>💎 NT <b id="hudNT">—</b></span>
  <span style="margin-left:auto;font-size:.75rem;color:var(--muted)" id="hudCurrentUser"></span>
  <button class="btn" onclick="logoutUser()" style="font-size:.7rem;padding:3px 10px">🚪 退出</button>
</div>
```

### 4.4 改造：Tab 栏 → 两套面板

**删除**原单行 tab（行 282-291），**替换为**：

```html
<!-- 共建者面板 -->
<div id="builderTabs" class="tabs hidden">
  <button class="tab" data-tab="settings">🌍 创世终端</button>
  <button class="tab" data-tab="members">👥 冒险者档案</button>
  <button class="tab" data-tab="taskhall">📋 猎人公会</button>
  <button class="tab" data-tab="timeline">📅 世界时间线</button>
  <button class="tab" data-tab="budget">💰 资源金库</button>
  <button class="tab" data-tab="settlement">🧾 通关结算</button>
</div>

<!-- 冒险者面板 -->
<div id="adventurerTabs" class="tabs hidden">
  <button class="tab" data-tab="taskhall">📋 我的委托</button>
  <button class="tab" data-tab="map">🗺️ 冒险任务</button>
  <button class="tab" data-tab="timeline">📅 世界时间线</button>
  <button class="tab" data-tab="budget">💰 资源金库</button>
  <button class="tab" data-tab="settlement">🧾 通关结算</button>
</div>
```

### 4.5 新增：共建者模式切换栏

```html
<div id="builderModeBar" class="mode-bar hidden">
  <button class="mode-btn active" data-mode="genesis">创世</button>
  <button class="mode-btn" data-mode="oversee">监察</button>
  <span style="margin-left:auto">
    <button class="btn" onclick="switchToAdventurerPreview()">⚔️ 切到冒险者视角</button>
  </span>
  <button class="btn" onclick="showInviteManager()" style="font-size:.72rem" title="管理邀请码">🔑</button>
</div>
```

**注意**：当前阶段只开放「创世」和「监察」两个模式。预测、整理、结算三个模式 UI 暂不显示，等对应功能就绪后再放出来。

### 4.6 Tab 内容区

所有 `id="tab-xxx"` 的 div 保留。`tab-settings` 仅在共建者创世模式可见，`tab-map` 仅在冒险者模式可见。权限门禁在 JS 层实现。

### 4.7 Wizard 步骤改名

| 旧 | 新 |
|----|----|
| ①统筹定框架 | ①创世设定 |
| ②统一任务池 | ②任务之书 |
| ③打包认领 | ③委托分配 |
| ④角色卡片填写 | ④封印指定 |
| ⑤同步展示 | ⑤世界启动 |

---

## 五、JS 实现

### 5.1 认证模块

```js
// ═══════════════════════════════════════════════
// 认证模块
// 注意：密码使用 btoa(encodeURIComponent(...)) 做简单编码
// 这是「防止路过式窥屏」，不是「加密」。
// 任何能看到 localStorage 的人都可以解码还原密码，
// 也可以手动伪造 nt_session 绕过登录。
// 本阶段解决的是"多人共用一台电脑时互不看错界面"，
// 真正的访问控制需要后端服务器。
// ═══════════════════════════════════════════════

const NT_USERS_KEY = 'nt_users';
const NT_INVITE_KEY = 'nt_invite_codes';
const NT_SESSION_KEY = 'nt_session';

let currentUser = null;
let previewMode = false;
let pendingLoginName = null;

// ── 密码编码 ──
function encodePassword(password, username) {
  return btoa(encodeURIComponent(password + ':' + username));
}

// ── 用户 CRUD ──
function getUsers() {
  try { return JSON.parse(localStorage.getItem(NT_USERS_KEY)) || {}; }
  catch(e) { return {}; }
}

function saveUsers(users) {
  localStorage.setItem(NT_USERS_KEY, JSON.stringify(users));
}

// ── 成员迁移（每次初始化都跑，只补不覆盖）──
function migrateExistingMembers() {
  var users = getUsers();
  var staffNames = getStaffNames();

  // 迁移共建者
  (data.staff_cards || []).forEach(function(c) {
    if (!users[c.name]) {
      users[c.name] = {
        name: c.name, role: 'builder',
        password: null,  // null = 首次登录时设密码
        avatar_seed: c.avatar_seed || 0,
        created: new Date().toISOString().slice(0, 10)
      };
    }
  });

  // 迁移冒险者（排除共建者）
  Object.values(data.members || {}).forEach(function(m) {
    var isStaff = staffNames.some(function(s) {
      return m.name === s;  // 精确匹配，不用 indexOf
    });
    if (!isStaff && !users[m.name]) {
      users[m.name] = {
        name: m.name, role: 'adventurer',
        password: null,
        avatar_seed: m.avatar_seed || 0,
        created: new Date().toISOString().slice(0, 10)
      };
    }
  });

  saveUsers(users);
}

// ── 注册 ──
var regRole = 'adventurer';
var regAvatarSeed = Math.floor(Math.random() * 60);

function showRegister(role) {
  regRole = role;
  regAvatarSeed = Math.floor(Math.random() * 60);
  document.getElementById('loginEntry').classList.add('hidden');
  document.getElementById('userListPanel').classList.add('hidden');
  document.getElementById('registerForm').classList.remove('hidden');
  document.getElementById('registerTitle').textContent =
    role === 'builder' ? '🧙 注册为世界建造者' : '⚔️ 注册为冒险者';
  document.getElementById('regInviteRow').classList.toggle('hidden', role !== 'builder');
  document.getElementById('regName').value = '';
  document.getElementById('regPassword').value = '';
  document.getElementById('regInviteCode').value = '';
  document.getElementById('regError').textContent = '';
  updateRegAvatarPreview();
}

function cycleRegAvatar() {
  regAvatarSeed = (regAvatarSeed + 1) % 60;
  updateRegAvatarPreview();
}

function updateRegAvatarPreview() {
  document.getElementById('regAvatarPreview').innerHTML = avatarCircle(regAvatarSeed, 64, 0);
}

function doRegister() {
  var name = document.getElementById('regName').value.trim();
  var password = document.getElementById('regPassword').value;
  var inviteCode = document.getElementById('regInviteCode').value.trim();
  var errEl = document.getElementById('regError');

  if (!name) { errEl.textContent = '请输入名字'; return; }
  if (!password || password.length < 2) { errEl.textContent = '密码至少 2 位'; return; }

  var result = registerUser(name, password, regRole, regAvatarSeed, inviteCode);
  if (!result.ok) { errEl.textContent = result.error; return; }

  loginUser(name, password, false);
}

function registerUser(name, password, role, avatarSeed, inviteCode) {
  var users = getUsers();
  if (users[name]) return { ok: false, error: '这个名字已经被注册了' };

  if (role === 'builder') {
    var codes = getInviteCodes();
    if (!inviteCode) return { ok: false, error: '建造者需要邀请码' };
    if (!codes.includes(inviteCode)) return { ok: false, error: '邀请码无效' };
    saveInviteCodes(codes.filter(function(c) { return c !== inviteCode; }));
  }

  users[name] = {
    name: name, role: role,
    password: encodePassword(password, name),
    avatar_seed: avatarSeed,
    created: new Date().toISOString().slice(0, 10)
  };
  saveUsers(users);

  // 同步到 data.members
  if (!data.members) data.members = {};
  if (!data.members[name]) {
    data.members[name] = { name: name, role: '', avatar_seed: avatarSeed, gender: '' };
    localStorage.setItem('camp_data', JSON.stringify(data));
  }

  return { ok: true };
}

// ── 登录 ──
function loginUser(name, password, rememberMe) {
  var users = getUsers();
  var user = users[name];
  if (!user) return { ok: false, error: '用户不存在' };

  if (user.password === null) {
    // 迁移用户首次登录 → 用输入作为新密码
    if (!password || password.length < 2) {
      return { ok: false, error: '请设置你的密码（至少 2 位）' };
    }
    user.password = encodePassword(password, name);
    saveUsers(users);
  } else if (user.password !== encodePassword(password, name)) {
    return { ok: false, error: '密码错误' };
  }

  currentUser = { name: user.name, role: user.role };
  previewMode = false;
  localStorage.setItem(NT_SESSION_KEY, JSON.stringify(currentUser));

  if (rememberMe) {
    localStorage.setItem('nt_remembered_user', JSON.stringify(currentUser));
  }

  enterWorld(currentUser);
  return { ok: true };
}

// ── 登出 ──
function logoutUser() {
  currentUser = null;
  previewMode = false;
  localStorage.removeItem(NT_SESSION_KEY);

  ['worldHUD','builderTabs','adventurerTabs','builderModeBar'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });

  var banner = document.getElementById('previewBanner');
  if (banner) banner.style.display = 'none';

  document.body.classList.remove('builder-mode', 'adventurer-mode');
  hideAllTabs();
  document.getElementById('loginPage').style.display = 'flex';
  showLoginEntry();
}

// ── 登录页导航 ──
function showLoginEntry() {
  document.getElementById('loginEntry').classList.remove('hidden');
  document.getElementById('registerForm').classList.add('hidden');
  document.getElementById('userListPanel').classList.add('hidden');
  updateLoginDateRange();
}

function showUserList() {
  document.getElementById('loginEntry').classList.add('hidden');
  document.getElementById('registerForm').classList.add('hidden');
  document.getElementById('userListPanel').classList.remove('hidden');
  renderUserGrids();
}

function updateLoginDateRange() {
  var start = data.camp_dates && data.camp_dates.start ? data.camp_dates.start : '';
  var duration = (data.camp_dates && data.camp_dates.duration_days) || 15;
  var el = document.getElementById('loginDateRange');
  if (start) {
    var end = new Date(start);
    end.setDate(end.getDate() + duration);
    el.textContent = start + ' — ' + end.toISOString().slice(0, 10);
  } else {
    el.textContent = '营期未设定';
  }
}

// ── 用户列表 ──
function renderUserGrids() {
  var users = getUsers();
  var builderHTML = '', adventurerHTML = '';

  Object.values(users).forEach(function(u) {
    var av = avatarCircle(u.avatar_seed || 0, 48, 0);
    var chip = '<div class="avatar-chip" onclick="promptPassword(\'' +
      escAttr(u.name) + '\')" title="' + escAttr(u.name) + '">' +
      av + '<div style="font-size:.75rem;margin-top:2px">' + esc(u.name) + '</div></div>';
    if (u.role === 'builder') builderHTML += chip;
    else adventurerHTML += chip;
  });

  document.getElementById('builderUserGrid').innerHTML =
    builderHTML || '<div style="color:var(--muted);font-size:.8rem">暂无共建者</div>';
  document.getElementById('adventurerUserGrid').innerHTML =
    adventurerHTML || '<div style="color:var(--muted);font-size:.8rem">暂无冒险者</div>';
}

function promptPassword(name) {
  pendingLoginName = name;
  var users = getUsers();
  var user = users[name];
  var isNew = user && user.password === null;

  document.getElementById('pwdModalAvatar').innerHTML =
    avatarCircle(user ? user.avatar_seed : 0, 64, 0);
  document.getElementById('pwdModalName').textContent = name;
  document.getElementById('pwdModalInput').value = '';
  document.getElementById('pwdModalInput').placeholder =
    isNew ? '首次登录，请设置密码' : '输入密码';
  document.getElementById('pwdModalError').textContent = '';
  document.getElementById('passwordModal').classList.add('show');
  document.getElementById('pwdModalInput').focus();
}

function closePasswordModal() {
  document.getElementById('passwordModal').classList.remove('show');
  pendingLoginName = null;
}

function doLogin() {
  var password = document.getElementById('pwdModalInput').value;
  var rememberMe = document.getElementById('pwdRememberMe').checked;
  var result = loginUser(pendingLoginName, password, rememberMe);
  if (!result.ok) {
    document.getElementById('pwdModalError').textContent = result.error;
    return;
  }
  document.getElementById('passwordModal').classList.remove('show');
}

// ── 邀请码 ──
function getInviteCodes() {
  try { return JSON.parse(localStorage.getItem(NT_INVITE_KEY)) || []; }
  catch(e) { return []; }
}

function saveInviteCodes(codes) {
  localStorage.setItem(NT_INVITE_KEY, JSON.stringify(codes));
}

function generateInviteCode() {
  var arr = new Uint8Array(4);
  crypto.getRandomValues(arr);
  var code = 'NT-' + Array.from(arr).map(function(b) {
    return b.toString(36).toUpperCase().padStart(2, '0');
  }).join('');
  return code;
}

function showInviteManager() {
  var codes = getInviteCodes();
  var listHTML = codes.length > 0
    ? codes.map(function(c) { return '<div style="padding:3px 0">📋 <code>' + c + '</code></div>'; }).join('')
    : '<div style="color:var(--muted)">暂无可用邀请码</div>';

  var msg = '🔑 邀请码管理\n\n现有邀请码：\n' +
    (codes.length > 0 ? codes.join('\n') : '（无）') +
    '\n\n点击「确定」生成新的邀请码，或「取消」关闭。';

  if (confirm(msg)) {
    var newCode = generateInviteCode();
    codes.push(newCode);
    saveInviteCodes(codes);
    alert('✅ 已生成新邀请码：\n\n' + newCode + '\n\n请复制分享给新共建者。');
  }
}
```

### 5.2 初始化流程

```js
document.addEventListener('DOMContentLoaded', function() {
  // 0. 加载营地数据
  var saved = localStorage.getItem('camp_data');
  if (saved) {
    try { data = JSON.parse(saved); } catch(e) {}
  }
  updateAll();
  loadTemplates();
  refreshTemplateSelects();

  // 1. 成员迁移（每次启动都跑，只补不覆盖）
  migrateExistingMembers();

  // 2. 检查已登录会话
  var session = localStorage.getItem(NT_SESSION_KEY);
  if (session) {
    try {
      currentUser = JSON.parse(session);
      // 验证用户仍然存在
      var users = getUsers();
      if (users[currentUser.name]) {
        enterWorld(currentUser);
        return;
      }
    } catch(e) {}
    // 会话无效 → 清理
    localStorage.removeItem(NT_SESSION_KEY);
  }

  // 3. 检查"记住我"
  var remembered = localStorage.getItem('nt_remembered_user');
  if (remembered) {
    try {
      currentUser = JSON.parse(remembered);
      var users = getUsers();
      if (users[currentUser.name]) {
        enterWorld(currentUser);
        return;
      }
    } catch(e) {}
    localStorage.removeItem('nt_remembered_user');
  }

  // 4. 显示登录页
  document.getElementById('loginPage').style.display = 'flex';
  hideAllTabs();
  updateLoginDateRange();
});

function hideAllTabs() {
  ['members','players','timeline','budget','settlement','map','taskhall','settings'].forEach(function(n) {
    var el = document.getElementById('tab-' + n);
    if (el) el.classList.add('hidden');
  });
}

function enterWorld(user) {
  document.getElementById('loginPage').style.display = 'none';
  document.getElementById('worldHUD').classList.remove('hidden');
  document.getElementById('hudCurrentUser').textContent =
    user.name + ' (' + (user.role === 'builder' ? '🧙共建者' : '⚔️冒险者') + ')';
  updateWorldHUD();

  if (user.role === 'builder') {
    document.body.classList.add('builder-mode');
    document.body.classList.remove('adventurer-mode');
    document.getElementById('builderTabs').classList.remove('hidden');
    document.getElementById('builderModeBar').classList.remove('hidden');
    document.getElementById('adventurerTabs').classList.add('hidden');
    switchBuilderMode('genesis');
  } else {
    document.body.classList.add('adventurer-mode');
    document.body.classList.remove('builder-mode');
    document.getElementById('adventurerTabs').classList.remove('hidden');
    document.getElementById('builderTabs').classList.add('hidden');
    document.getElementById('builderModeBar').classList.add('hidden');
    switchTab('taskhall');
  }
}
```

### 5.3 Tab 切换（含事件委托 + 权限门禁 + 双面板高亮）

```js
// 绑定事件委托（在 init 或 DOMContentLoaded 末尾调用一次）
function bindTabEvents() {
  document.querySelectorAll('.tabs').forEach(function(tabBar) {
    tabBar.addEventListener('click', function(e) {
      var tab = e.target.closest('.tab');
      if (!tab) return;
      var tabName = tab.dataset.tab;
      if (tabName) switchTab(tabName);
    });
  });
}

function switchTab(name) {
  // ── 冒险者权限门禁 ──
  if (currentUser && currentUser.role === 'adventurer' && !previewMode) {
    if (name === 'settings' || name === 'members' || name === 'players') {
      return; // 无权访问
    }
  }

  // ── 隐藏所有 tab 内容 ──
  ['members','players','timeline','budget','settlement','map','taskhall','settings'].forEach(function(n) {
    var el = document.getElementById('tab-' + n);
    if (el) el.classList.toggle('hidden', n !== name);
  });

  // ── 高亮当前可见面板中的 active tab ──
  document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
  var activeBar = document.getElementById('builderTabs');
  if (activeBar.classList.contains('hidden')) {
    activeBar = document.getElementById('adventurerTabs');
  }
  if (!activeBar.classList.contains('hidden')) {
    var activeTab = activeBar.querySelector('.tab[data-tab="' + name + '"]');
    if (activeTab) activeTab.classList.add('active');
  }

  // ── 渲染内容 ──
  if (name === 'members') { memViewType = 'members'; renderMembers(); }
  if (name === 'players') { memViewType = 'players'; renderPlayers(); }
  if (name === 'timeline') { renderTimeline(); renderCalendar(); switchScheduleView('calendar'); }
  if (name === 'budget') renderBudget();
  if (name === 'settlement') renderSettlementAll();
  if (name === 'map') renderDailyView('player');
  if (name === 'taskhall') {
    if (currentUser && currentUser.role === 'builder' && !previewMode) {
      renderDailyView('staff'); renderTasks(); renderCompleteness();
    } else {
      renderDailyView('player');
    }
  }
  if (name === 'settings') { renderWizardNav(); switchStep(data.camp_progress.step || 1); }
}
```

### 5.4 权限系统（集中判断 + 全覆盖）

```js
// ── 统一权限判断 ──
function isAdventurerView() {
  if (!currentUser) return false;
  return currentUser.role === 'adventurer' || previewMode;
}

// ── assignee 精确匹配（避免 "红" 误匹配 "小红"）──
function isCurrentUserAssignee(assignee) {
  if (!currentUser) return false;
  if (!assignee) return false;
  return (assignee || '').split(/[,，、]/).map(function(s) {
    return s.trim();
  }).includes(currentUser.name);
}

// ── 需要加权限过滤的函数清单 ──
//
// renderDailyView(role):
//   如果 isAdventurerView() → tasks 只保留 isCurrentUserAssignee 为 true 的项
//
// renderTasks():
//   同上，按 assignee 精确过滤
//
// renderBudget():
//   如果 isAdventurerView() → 只显示 NT 余额，隐藏 RMB 详情和工资明细
//
// renderSettlementAll():
//   如果 isAdventurerView() → 只渲染当前用户的结算卡片
//
// renderMembers() / renderPlayers():
//   通过 switchTab 门禁阻止访问（冒险者看不到这两个 tab 按钮）
//
// renderCalendar():
//   如果 isAdventurerView() → 保留日历但隐藏里程碑编辑按钮
//
// dailyCheckTask(idx, role):
//   如果 isAdventurerView() → 只允许操作自己的任务（检查 isCurrentUserAssignee）
//   否则 alert("你只能管理自己的委托")
//
// showAddTask() / showAddMember():
//   如果 isAdventurerView() → 直接 return
//
// 财务编辑 (editTx / deleteTx):
//   如果 isAdventurerView() → 直接 return
```

### 5.5 共建者模式切换（仅开放创世 + 监察）

```js
var currentBuilderMode = 'genesis';

var modeDefaultTab = {
  genesis: 'settings',
  oversee: 'taskhall'
};

function switchBuilderMode(mode) {
  currentBuilderMode = mode;

  document.querySelectorAll('.mode-btn').forEach(function(b) { b.classList.remove('active'); });
  var btn = document.querySelector('.mode-btn[data-mode="' + mode + '"]');
  if (btn) btn.classList.add('active');

  // 隐藏模式专属面板
  ['overseePanel'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });

  if (mode === 'genesis') {
    switchTab('settings');
  } else if (mode === 'oversee') {
    showOverseePanel();
  }
}
```

### 5.6 冒险者预览

```js
function switchToAdventurerPreview() {
  previewMode = true;

  document.body.classList.remove('builder-mode');
  document.body.classList.add('adventurer-mode');
  document.getElementById('builderTabs').classList.add('hidden');
  document.getElementById('builderModeBar').classList.add('hidden');
  document.getElementById('adventurerTabs').classList.remove('hidden');

  showPreviewBanner();
  switchTab('taskhall');
}

function showPreviewBanner() {
  var banner = document.getElementById('previewBanner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'previewBanner';
    banner.style.cssText = 'background:#c8a860;color:#1a1410;text-align:center;padding:8px;font-weight:600;font-size:.85rem';
    banner.innerHTML = '👁️ 你正在以冒险者视角预览 · <button onclick="exitPreview()" style="background:#1a1410;color:#c8a860;border:none;padding:4px 12px;border-radius:4px;cursor:pointer;font-weight:600;margin-left:12px">返回世界终端</button>';
    document.getElementById('worldHUD').after(banner);
  }
  banner.style.display = 'block';
}

function exitPreview() {
  previewMode = false;

  var banner = document.getElementById('previewBanner');
  if (banner) banner.style.display = 'none';

  document.body.classList.add('builder-mode');
  document.body.classList.remove('adventurer-mode');
  document.getElementById('builderTabs').classList.remove('hidden');
  document.getElementById('builderModeBar').classList.remove('hidden');
  document.getElementById('adventurerTabs').classList.add('hidden');

  switchBuilderMode(currentBuilderMode);
}
```

### 5.7 世界状态条

```js
function updateWorldHUD() {
  // 距启动天数
  var startDate = (data.camp_dates && data.camp_dates.start) || '';
  if (startDate) {
    var start = new Date(startDate);
    var now = new Date();
    var daysLeft = Math.ceil((start - now) / (1000 * 60 * 60 * 24));
    document.getElementById('hudDaysLeft').textContent = Math.max(0, daysLeft);
  }

  // 冒险者人数（精确匹配，不用 indexOf）
  var staffNames = getStaffNames();
  var adventurerCount = Object.values(data.members || {}).filter(function(m) {
    return !staffNames.some(function(s) { return m.name === s; });
  }).length;
  var expected = (data.camp_dates && data.camp_dates.expected_players) || 10;
  document.getElementById('hudAdventurers').textContent = adventurerCount + '/' + expected;

  // RMB（从 budget 已有字段读取）
  var budget = data.budget || {};
  var totalRMB = (budget.sponsor_needed || 0) + (budget.tuition_total || 0);
  if (!totalRMB && budget.salary_total) {
    totalRMB = budget.salary_total + (budget.lodging_cost || 0) + (budget.rmb_pool || 0);
  }
  document.getElementById('hudRMB').textContent = totalRMB ? totalRMB.toLocaleString() : '—';

  // NT
  var totalNT = budget.nt_total_pool || budget.nt_pool || 0;
  document.getElementById('hudNT').textContent = totalNT ? totalNT.toLocaleString() : '—';
}
```

### 5.8 按钮/标签文案替换

| 旧 | 新 |
|----|----|
| `'新增任务'` | `'发布委托'` |
| `'激励点'` | `'NT 奖励'` |
| `'任务总览'` | `'委托总览'` |
| `'任务名称'` | `'委托名称'` |
| `'任务大厅'` | `'猎人公会'` |
| `'公会资金池'` | `'资源金库'` |
| `'提交到任务大厅'` | `'发布到猎人公会'` |

### 5.9 startGame() 废弃

原有 `startGame(role)` 函数保留但不再被调用。登录流程由 `enterWorld()` 接管。

---

## 六、任务卡片化

### 6.1 卡片模板

```js
function renderQuestCard(task, index) {
  var catColors = {
    '宣传': 'gold', '课程': 'green', '生活': 'brown',
    '财务': 'purple', '管理': 'blue', '结项': 'blue', '其他': 'brown'
  };
  var catNames = {
    '宣传': '传令卡', '课程': '修行卡', '生活': '生活卡',
    '财务': '财富卡', '管理': '秩序卡', '结项': '秩序卡', '其他': '生活卡'
  };
  var typeBadges = {
    '主线': 'M', '支线': 'S', '共创': 'C', '隐藏': 'H',
    '初始': 'M', '新增': 'S', '变更': 'C'
  };

  var color = catColors[task.category] || 'brown';
  var catName = catNames[task.category] || '委托';
  var badge = typeBadges[task.type] || 'M';
  var done = task.status === '已完成' || task.status === '已确认';
  // 使用 isAdventurerView() 来判断点击时的身份
  var viewRole = isAdventurerView() ? 'player' : 'staff';

  return '<div class="quest-card ' + color + (done ? ' done' : '') +
    '" onclick="dailyCheckTask(' + index + ', \'' + viewRole + '\')">' +
    '<div class="quest-card-header">' +
      '<span class="quest-card-badge">' + badge + '</span>' +
      '<span class="quest-card-type">' + catName + '</span>' +
    '</div>' +
    '<div class="quest-card-title">' + esc(task.name) + '</div>' +
    '<div class="quest-card-meta">' +
      '<span>🧙 ' + esc(task.assignee || '未分配') + '</span>' +
      '<span>📅 ' + esc(task.deadline || '—') + '</span>' +
    '</div>' +
    '<div class="quest-card-reward">💎 ' + (task.points || 0) + ' NT</div>' +
  '</div>';
}
```

**点击行为**：单击卡片 = 切换任务状态。在 `dailyCheckTask` 中由 `isAdventurerView()` 门禁保护——冒险者只能操作自己的委托。

### 6.2 应用范围

- 冒险者「我的委托」→ 卡片视图
- 共建者「猎人公会」→ 卡片视图
- 冒险者「冒险任务」→ 卡片视图（附带空间地图）
- 共建者「创世终端」→ **保持表格**（wizard 需要表格编辑）

---

## 七、监察模式面板

```js
function showOverseePanel() {
  hideAllTabs();
  var panel = document.getElementById('overseePanel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'overseePanel';
    document.querySelector('main').appendChild(panel);
  }
  panel.innerHTML =
    '<div class="card"><h3>📊 冒险者状态总览</h3>' + renderAdventurerProgressBars() + '</div>' +
    '<div class="card"><h3>🔔 今日焦点</h3>' + renderDailyFocus() + '</div>' +
    '<div class="card"><h3>📋 需要协调</h3>' + renderCoordinationNeeds() + '</div>';
  panel.classList.remove('hidden');
}

function renderAdventurerProgressBars() {
  var tasks = data.tasks || [];
  var staffNames = getStaffNames();
  var advData = {};

  tasks.forEach(function(t) {
    var name = t.assignee || '(未分配)';
    if (staffNames.some(function(s) { return name === s; })) return;
    if (!advData[name]) advData[name] = { total: 0, done: 0 };
    advData[name].total++;
    if (t.status === '已完成' || t.status === '已确认') advData[name].done++;
  });

  var html = '';
  Object.entries(advData).forEach(function(e) {
    var name = e[0], d = e[1];
    var pct = d.total > 0 ? Math.round(d.done / d.total * 100) : 0;
    var barColor = pct >= 80 ? 'var(--green)' : pct >= 40 ? 'var(--yellow)' : 'var(--red)';
    html += '<div style="display:flex;align-items:center;gap:8px;margin:6px 0">' +
      '<span style="width:80px;font-size:.85rem;font-weight:600">' + esc(name) + '</span>' +
      '<div style="flex:1;height:8px;background:var(--border);border-radius:4px;overflow:hidden">' +
        '<div style="height:100%;width:' + pct + '%;background:' + barColor + ';border-radius:4px"></div>' +
      '</div>' +
      '<span style="font-size:.78rem;color:var(--muted);width:80px;text-align:right">' +
        d.done + '/' + d.total + ' (' + pct + '%)</span>' +
    '</div>';
  });

  return html || '<div style="color:var(--muted)">暂无冒险者数据</div>';
}

function renderDailyFocus() {
  var today = new Date().toISOString().slice(0, 10);
  var tasks = data.tasks || [];
  var items = [];

  tasks.forEach(function(t) {
    if (t.deadline && t.deadline < today && t.status !== '已完成' && t.status !== '已确认') {
      items.push({ level: '🔴', text: esc(t.assignee || '?') + '·' + esc(t.name) + ' 已逾期' });
    } else if (t.deadline === today && t.status !== '已完成' && t.status !== '已确认') {
      items.push({ level: '🟡', text: esc(t.assignee || '?') + '·' + esc(t.name) + ' 今天到期' });
    }
  });

  if (items.length === 0) {
    return '<div style="color:var(--green)">🟢 今日无异常，世界运转良好</div>';
  }
  return items.map(function(i) {
    return '<div style="padding:2px 0">' + i.level + ' ' + i.text + '</div>';
  }).join('');
}

function renderCoordinationNeeds() {
  var tasks = data.tasks || [];
  var noAssignee = tasks.filter(function(t) {
    return !t.assignee && t.status !== '已完成' && t.status !== '已确认';
  });
  if (noAssignee.length > 0) {
    return '<div style="padding:2px 0">⚠️ ' + noAssignee.length + ' 项委托缺少负责人</div>';
  }
  return '<div style="color:var(--green)">✅ 无需协调的事项</div>';
}
```

---

## 八、实施步骤

| 步骤 | 内容 | 时间 |
|------|------|------|
| 0 | **清理重复代码**：删第一组（有 bug），保留第二组（正确）；保留独有函数如 `parseDate` | 30min |
| 1 | **重构 CSS**：硬编码颜色 → `var(--xxx)`，添加 `.builder-mode` 主题，添加新组件样式 | 45min |
| 2 | **添加登录页 HTML**：删除 `defaultView`，添加入口 + 注册表单 + 用户列表 + 密码弹窗 | 45min |
| 3 | **添加 HUD + 面板 HTML**：替换旧 tab 栏为两套面板，添加 HUD 和模式切换栏 | 30min |
| 4 | **实现认证 JS**：注册/登录/登出/迁移/邀请码完整逻辑 | 60min |
| 5 | **改造初始化 + switchTab + 权限**：事件委托、门禁过滤、双面板高亮 | 45min |
| 6 | **模式切换 + 预览**：创世/监察两模式，预览模式 + `previewMode` 标志 | 30min |
| 7 | **任务卡片化**：`renderQuestCard`，替换表格为卡片网格，印章效果 | 60min |
| 8 | **文案替换 + wizard 改名**：全局搜索替换 7 处文案 | 30min |
| 9 | **测试**：注册→登录→创世→监察→预览→退出预览→登出→重新登录 | 60min |

**总计：约 7 小时**

---

## 九、风险清单

| 风险 | 应对 |
|------|------|
| 第一组函数因为括号 bug 导致部分函数局部化 | 删第一组前先做函数交叉对比，确认第二组完整 |
| CSS 硬编码颜色替换后有遗漏 | 逐行替换，每改几个值就刷新验证 |
| `parseDate` 等独有函数被误删 | 清理前先 grep 检查哪些函数只出现一次 |
| 密码编码可被解码还原 | 文档已诚实标注，函数命名为 `encodePassword` |
| 登录态可被控制台伪造 | 文档已诚实标注——这是本地分身份使用，不防篡改 |
| 手机端卡片太挤 | 响应式 grid，640px 以下单列 |
| 忘记密码无法找回 | 共建者可通过控制台手动重置：`localStorage.removeItem('nt_users')` 后重新注册 |

---

## 十、不做的事（后续阶段）

- 南塘实景地图、排行榜、通关证书个性化（第二阶段）
- 交易市场、同伴动态、成长记录（第三阶段）
- 预测/整理/结算模式完整实现（第三阶段）
- 后端认证系统（第三阶段）
- 密码找回功能

---

*规格书 v3 完成。*