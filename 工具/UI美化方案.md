# UI 美化方案

> 目标：游戏感 + 紧凑布局 + 手机适配 + 统一图标
> 2026-07-07 · 更新：集成 Phosphor Duotone 图标系统

---

## 一、图标系统（已确认：Phosphor Duotone）

### 1.1 引入方式

一行 CDN，放在 `<head>` 最后：

```html
<script src="https://unpkg.com/@phosphor-icons/web@2.1.1"></script>
```

### 1.2 一键切换图标风格

在 localStorage 存一个 `nt_icon_style` 值，页面加载时读取，全局生效。

```js
// 图标风格配置（存 localStorage key: nt_icon_style）
// 可选值: 'duotone' | 'fill' | 'regular' | 'bold'
const ICON_STYLES = {
  duotone: { prefix: 'ph-duotone', label: '双色调' },
  fill:     { prefix: 'ph-fill',    label: '实心' },
  regular:  { prefix: 'ph',         label: '常规' },
  bold:     { prefix: 'ph-bold',    label: '加粗' },
};

let iconStyle = localStorage.getItem('nt_icon_style') || 'duotone';

function setIconStyle(style) {
  iconStyle = style;
  localStorage.setItem('nt_icon_style', style);
  // 刷新所有图标
  document.querySelectorAll('[data-icon]').forEach(el => {
    el.className = ICON_STYLES[style].prefix + ' ' + el.getAttribute('data-icon');
  });
}

// 渲染图标辅助函数
function icon(name, size) {
  var s = size ? 'font-size:' + size : '';
  return '<i class="' + ICON_STYLES[iconStyle].prefix + ' ' + name + '" style="' + s + '"></i>';
}
```

**切换入口**：在「⚙️ 工具」下拉菜单里加一个「🎨 图标风格」子菜单，点击即切换。

### 1.3 图标使用规范

所有图标统一用 `data-icon` 属性标记，便于一键切换：

```html
<!-- 正确写法 -->
<button><i data-icon="ph ph-planet"></i> 创世终端</button>

<!-- JS 动态生成 -->
html += icon('ph-sword', '1.2rem') + ' 冒险者';
```

### 1.4 6类图标完整映射（Duotone 优先）

#### 第1类：身份/角色（5个）

| 用途 | 图标 class | 颜色 |
|------|----------|------|
| 管理员 | `ph-duotone ph-crown` | `#c8a040` 金 |
| 共建者 | `ph-duotone ph-hammer` | `#5a8a3c` 绿 |
| 冒险者 | `ph-duotone ph-sword` | `#5b8cb8` 蓝 |
| 南塘NPC | `ph-duotone ph-storefront` | `#8b7355` 棕 |
| 游客 | `ph-duotone ph-campfire` | `#9b9078` 灰 |

#### 第2类：Tab导航（11个）

| Tab | 图标 class |
|-----|----------|
| 创世终端 | `ph-duotone ph-planet` |
| 成员档案 | `ph-duotone ph-identification-card` |
| 猎人公会 | `ph-duotone ph-buildings` |
| NT管理 | `ph-duotone ph-target` |
| 世界时间线 | `ph-duotone ph-calendar` |
| 资源金库 | `ph-duotone ph-vault` |
| 通关结算 | `ph-duotone ph-scroll` |
| 任务公告栏 | `ph-duotone ph-signpost` |
| 我的资料 | `ph-duotone ph-user-circle` |
| 排行榜 | `ph-duotone ph-trophy` |
| 预览冒险者 | `ph-duotone ph-eye` |

#### 第3类：操作按钮（12个）

| 操作 | 图标 class |
|------|----------|
| 新增 | `ph-duotone ph-plus-circle` |
| 编辑 | `ph-duotone ph-pencil` |
| 保存 | `ph-duotone ph-floppy-disk` |
| 删除 | `ph-duotone ph-trash` |
| 领取委托 | `ph-duotone ph-hand-fist` |
| 提交完成 | `ph-duotone ph-check-circle` |
| 放弃 | `ph-duotone ph-flag-banner` |
| 确认通过 | `ph-duotone ph-check-fat` |
| 退回修改 | `ph-duotone ph-x-circle` |
| 触发隐藏 | `ph-duotone ph-key` |
| 发布任务 | `ph-duotone ph-plus-square` |
| 退出 | `ph-duotone ph-sign-out` |

#### 第4类：工具栏（6个）

| 工具 | 图标 class |
|------|----------|
| 工具菜单 | `ph-duotone ph-gear` |
| 加载数据 | `ph-duotone ph-folder-open` |
| 导出数据 | `ph-duotone ph-download` |
| 邀请码 | `ph-duotone ph-keyhole` |
| 换头像 | `ph-duotone ph-paint-brush` |
| 返回 | `ph-duotone ph-arrow-left` |

#### 第5类：任务状态（8个）

| 状态 | 图标 class |
|------|----------|
| 可领取 | `ph-duotone ph-circle` |
| 已领取 | `ph-duotone ph-check-circle` |
| 进行中 | `ph-duotone ph-circle-dashed` |
| 审核中 | `ph-duotone ph-hourglass` |
| 已完成 | `ph-fill ph-check-circle` |
| 已退回 | `ph-duotone ph-arrow-u-up-left` |
| 主线标记 | `ph-fill ph-star` |
| 支线标记 | `ph-duotone ph-compass` |

#### 第6类：装饰（5个）

| 用途 | 图标 class |
|------|----------|
| NT货币 | `ph-duotone ph-coin` |
| 成就勋章 | `ph-duotone ph-medal` |
| 空状态 | `ph-duotone ph-ghost` |
| 加载中 | `ph-duotone ph-spinner` |
| 公告 | `ph-duotone ph-megaphone` |

---

## 二、布局优化

### 2.1 紧凑化原则

```
现在（4行）:                  优化后（2行+下拉）:
┌─ worldHUD ──────────────┐   ┌─ 🧙砚仁 💎12,500 [⚙️▼] [🚪] ──┐
├─ builderModeBar ────────┤   ├─ [🌍创世][📊监察][👁️预览] ──────┤
├─ builderTabs ───────────┤   ├─ [🌍终端][📋档案][📋公会][🎯NT]..┤  ← 图标+文字
├─ adminToolbar ──────────┤   └──────────────────────────────────┘
└─────────────────────────┘   加载/导出/邀请码 → 收到 ⚙️ 下拉里
```

### 2.2 ⚙️ 工具下拉菜单

```html
<div class="dropdown" style="position:relative">
  <button class="btn" onclick="toggleDropdown('toolsMenu')">
    <i class="ph-duotone ph-gear"></i>
  </button>
  <div id="toolsMenu" class="dropdown-menu hidden"
       style="position:absolute;right:0;top:100%;z-index:50;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:4px;min-width:160px;box-shadow:0 4px 16px rgba(0,0,0,.15)">
    <button onclick="loadData()"><i class="ph-duotone ph-folder-open"></i> 加载数据</button>
    <button onclick="exportData()"><i class="ph-duotone ph-download"></i> 导出数据</button>
    <button onclick="showInviteManager()"><i class="ph-duotone ph-keyhole"></i> 邀请码</button>
    <hr style="border-color:var(--border);margin:2px 0">
    <button onclick="setIconStyle('duotone')"><i class="ph-duotone ph-paint-brush"></i> 图标：双色调</button>
    <button onclick="setIconStyle('fill')"><i class="ph-fill ph-paint-brush"></i> 图标：实心</button>
    <button onclick="setIconStyle('regular')"><i class="ph ph-paint-brush"></i> 图标：常规</button>
  </div>
</div>
```

### 2.3 手机端 Tab 图标模式

```css
@media (max-width: 768px) {
  .tab { font-size: 0; }            /* 隐藏文字 */
  .tab i { font-size: 1.25rem; }     /* 只显示图标 */
  .tab::after { content: none; }
}
```

---

## 三、配色方案

### 3.1 登录页（暗色主题）

```css
.login-page {
  background: url('ai_expand_image1783014990973.png') center/cover;
}
.login-page::after {
  background: linear-gradient(180deg,
    rgba(20,15,8,.8), rgba(25,18,10,.85), rgba(15,10,5,.9));
}
.login-card {
  background: rgba(28,22,14,.88);
  border: 1px solid rgba(200,160,80,.25);
  box-shadow: 0 8px 40px rgba(0,0,0,.5), 0 0 100px rgba(200,150,50,.06);
  color: #e0d0b0;
}
.login-card h1, .login-card h2 { color: #d4c8b0; }
.login-card p { color: #8a7a5e; }
.login-card input {
  background: rgba(0,0,0,.3); border-color: rgba(200,160,80,.2); color: #e0d0b0;
}
.login-card input:focus { border-color: var(--accent); }
```

### 3.2 冒险者界面（暖棕/羊皮纸调）

```css
body.adventurer-mode {
  --bg: #f5efe0;
  --card: #fdfaf3;
  --text: #3d3025;
  --muted: #8a7560;
  --accent: #b8703a;
  --green: #6b8e4a;
  --red: #c05040;
  --yellow: #c08530;
  --border: #d8c8b0;
}
```

### 3.3 管理者界面（浅绿调，已有 builder-mode）

当前 builder-mode 配色保持，微调卡片加细微阴影。

---

## 四、手机响应式

```css
@media (max-width: 768px) {
  main { padding: 12px 8px; }
  .tabs { gap: 2px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .tab { padding: 8px 10px; font-size: 0; }
  .tab i { font-size: 1.25rem; }
  .card { padding: 12px 10px; }
  .modal { max-width: 100%; width: 100%; max-height: 100vh; border-radius: 0; }
  .ms-av-circle { width: 40px; height: 40px; }
  .quest-grid { grid-template-columns: 1fr; }
  header { min-height: 80px; max-height: 120px; }
  .login-card { padding: 24px 16px; }
  #memberSubNav .btn { font-size: .7rem; padding: 4px 6px; }
  .dropdown-menu { right: auto; left: 0; min-width: 140px; }
}

@media (max-width: 480px) {
  main { padding: 8px 4px; }
  .tab { padding: 6px 8px; }
  .btn { padding: 6px 10px; font-size: .78rem; }
}
```

---

## 五、Header 横幅优化

```css
header {
  position: relative;
  height: 15vh;
  min-height: 100px;
  max-height: 180px;
  overflow: hidden;
}
header img {
  width: 100%; height: 100%; object-fit: cover; object-position: center 60%;
}
/* 手机端降低高度 */
@media (max-width: 768px) {
  header { height: 12vh; min-height: 70px; max-height: 120px; }
}
```

---

## 六、实施步骤

| 步 | 内容 | 影响 |
|----|------|------|
| 1 | `<head>` 加 Phosphor CDN script | 一行 |
| 2 | 加 `icon()` 辅助函数 + `setIconStyle()` + ICON_STYLES 配置 | ~20行 JS |
| 3 | 加 `#iconStyleMenu` 下拉切换 + CSS | ~15行 HTML/CSS |
| 4 | 替换所有 emoji → Duotone 图标 | 批量替换 |
| 5 | 登录页暗色主题 CSS | ~30行 |
| 6 | 手机响应式 @media | ~40行 |
| 7 | 工具栏二级菜单（⚙️ 下拉） | ~20行 HTML/CSS |
| 8 | 冒险者暖棕配色 | ~10行 |

---

*确认后按步骤施工。*
