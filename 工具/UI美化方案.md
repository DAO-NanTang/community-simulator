# UI 美化方案

> 目标：游戏感 + 紧凑布局 + 手机适配
> 2026-07-07

---

## 一、需要 AI 生成的图片（5张）

### 图1：登录页全屏背景（最重要）
- **用途**：登录页 + 身份选择页的背景
- **风格**：暗色调水墨水彩混合，中国乡村风景
- **内容**：南塘村的远景——青瓦白墙的民居群、远处有山、近处有菜地和画架、天空是暖黄色调的黄昏
- **构图**：横向画面，下半部分暗（放卡片），上半部分亮（天空）
- **色调**：深墨绿、暖黄、赭石色、留白
- **英文提示词**：
  > Watercolor and ink wash painting of a traditional Chinese village (Nantang) at dusk. White-walled houses with grey tile roofs nestled among green fields. Distant misty mountains. An easel and paintbrushes in the foreground hinting at an art commune. Warm golden hour light from the top, dark earthy shadows at the bottom. Cozy mysterious game-like atmosphere. Vertical composition with the lower third intentionally darker to overlay UI cards. 16:9 aspect ratio. Studio Ghibli inspired lighting.
- **中文提示词**：
  > 水墨水彩风格的中国南方村庄（南塘村）黄昏全景。青瓦白墙的民居，炊烟袅袅，远处有朦胧的山，近处是菜地和画架画具。暖金色天空光从上方洒落，下方地面自然暗下来。温馨神秘的游戏氛围。竖幅或16:9横幅，画面上半明亮下半暗沉，适合叠加UI卡片。吉卜力风格的温暖光线。

### 图2：管理者界面横幅背景
- **用途**：管理员/共建者登录后顶部 header 的水彩横幅
- **风格**：横向长条，浅绿色调水彩
- **内容**：南塘风景的横向切面——田野、画室、远山，从左到右自然过渡
- **色调**：浅绿色为主（builder-mode风格），温暖但不厚重
- **英文提示词**：
  > Wide horizontal watercolor banner of Nantang countryside. Rolling fields in light sage green, a white-walled art studio, distant blue mountains. Soft morning light. Very wide aspect ratio (approximately 4:1). Light and airy, translucent watercolor washes. Suitable for a website header banner.
- **中文提示词**：
  > 横向宽幅水彩画。南塘乡村风光——层层叠叠的浅绿色田野，白墙画室，远处蓝灰色山峦。柔和的晨光。超宽画幅（约4:1），轻透的水彩晕染。适合做网页顶部横幅。

### 图3：冒险者界面横幅背景
- **用途**：冒险者登录后顶部 header 的水彩横幅
- **风格**：蓝灰色调，神秘冒险氛围
- **内容**：同南塘景色但用更冷更神秘的色调
- **色调**：蓝灰、暗紫、暖棕点缀
- **英文提示词**：
  > Wide horizontal watercolor banner with mysterious adventure atmosphere. Same Nantang village but in cooler tones - slate blue, muted purple, warm brown accents. Mist rising from fields. A sense of quest and discovery. Very wide aspect ratio (approximately 4:1). Darker and more saturated than the builder version.
- **中文提示词**：
  > 横向宽幅水彩画。神秘冒险氛围的南塘村。蓝灰、暗紫色调，田间升起的薄雾，温暖棕色点缀。有探索和发现的感觉。超宽画幅（约4:1），比管理者版本更暗更浓。

### 图4：南塘村口实景照片
- **用途**：Phase 3 村口地图的底图（可以先用照片，以后手绘）
- **风格**：实景照片或写实水彩
- **内容**：南塘实景——素社、画室、菜地、展览厅、南塘村口的全景
- **英文提示词**：
  > Realistic watercolor illustration of Nantang art commune layout. Top-down or slightly isometric view showing: a white hostel building (素社), a large art studio (画室) with easels visible through windows, vegetable fields (菜地) with crops, an exhibition hall (展览厅), and the village entrance (村口). Each location labeled. Warm earthy colors. Map-like but painterly. Suitable for an interactive village map.
- **中文提示词**：
  > 写实水彩风格的南塘艺术公社布局图。俯视或微等距视角。显示：白色民宿楼（素社）、大画室（透过窗户可见画架）、菜地（有各种作物）、展览厅、村口。各地点标注名称。温暖的土色调。像地图但有手绘感觉。适合做互动村落地图。

### 图5：卡片纹理背景
- **用途**：作为 UI 卡片的细微纹理
- **风格**：宣纸纹理
- **内容**：纯纹理，无明显画面内容
- **英文提示词**：
  > Seamless rice paper texture. Subtle fiber patterns, slightly aged warm white/cream color. Very light and understated, suitable for UI card backgrounds. Tileable. Minimalist.
- **中文提示词**：
  > 无缝宣纸纹理。细微的纤维纹理，微微泛黄的暖白/奶油色。非常淡雅低调，适合做UI卡片背景。可平铺。极简。

---

## 二、布局优化方案

### 2.1 顶部工具栏 → 紧凑化 + 二级菜单

**现状**：worldHUD、builderModeBar、builderTabs、adminToolbar 各占一行，共4行。

**优化后**：

```
┌─ 🧙 砚仁（管理员）  💎 12,500  [⚙️ 工具 ▼] [🚪] ─────────────┐  ← worldHUD (1行)
│  [🌍创世] [📊监察] [👁️预览]                                     │  ← modeBar (可选)
│  [🌍创世终端] [📋成员档案] [📋猎人公会] [🎯NT管理] [📅时间线] ...│  ← tabs (1行)
│                                            📂 💾 🔑            │  ← 合并到 ⚙️ 工具 下拉
└────────────────────────────────────────────────────────────────┘
```

- worldHUD 右侧的按钮（退出、邀请码）合并到「⚙️」下拉菜单
- 加载/导出按钮从独立工具栏移入「⚙️」下拉
- 「⚙️ 工具」菜单内容：📂 加载 / 💾 导出 / 🔑 邀请码 / 🖼️ 切换背景

### 2.2 二级菜单实现

```html
<div class="dropdown">
  <button class="btn" onclick="toggleDropdown('toolsMenu')">⚙️</button>
  <div id="toolsMenu" class="dropdown-menu hidden">
    <button onclick="loadData()">📂 加载数据</button>
    <button onclick="exportData()">💾 导出数据</button>
    <button onclick="showInviteManager()">🔑 邀请码</button>
  </div>
</div>
```

### 2.3 Tab 栏：图标优先 + 文字可选

**桌面端**：显示完整文字（当前状态）

**手机端**（<768px）：只显示图标，文字变 tooltip

```
桌面：[🌍 创世终端] [📋 成员档案] [📋 猎人公会] [🎯 NT管理] ...
手机：[🌍] [📋] [📋] [🎯] ...    ← hover/long-press 显示全名
```

### 2.4 冒险者 Tab 同样优化

冒险者只有4个 tab，手机端可以更宽松：
```
[📋 公告栏] [⚔️ 资料] [📅 时间线] [🏆 排行]
```

---

## 三、配色方案

### 3.1 登录页（暗色主题）

```
背景：水彩图片 + 深色渐变遮罩
卡片：半透明深色卡片，金色边框
文字：暖金色
按钮：暗金底色
```

```css
.login-page {
  background: url('bg_login.jpg') center/cover;
}
.login-page::after {
  background: linear-gradient(180deg,
    rgba(20,15,8,.75), rgba(30,20,10,.8), rgba(15,10,5,.85));
}
.login-card {
  background: rgba(30,25,18,.85);
  border: 1px solid rgba(200,160,80,.3);
  box-shadow: 0 8px 40px rgba(0,0,0,.5), 0 0 80px rgba(200,150,50,.1);
  color: #e0d0b0;
}
```

### 3.2 管理者界面（绿色调，已有 builder-mode）

当前绿色调不错，微调：
- 背景色稍微再浅一点
- 卡片加细微阴影

### 3.3 冒险者界面（暖棕色调）

冒险者应该有不同的视觉感受——暖棕色/羊皮纸调：

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

---

## 四、手机适配

### 4.1 响应式断点

```css
/* 平板及以下 (≤768px) */
@media (max-width: 768px) {
  /* Tab 文字隐藏，只显示图标 */
  .tab { font-size: 0; }
  .tab::before { font-size: 1rem; }
  /* 卡片全宽 */
  .card { padding: 12px; }
  /* 弹出窗口全屏 */
  .modal { max-width: 100%; width: 100%; max-height: 100vh; border-radius: 0; }
  /* 头像缩小 */
  .ms-av-circle { width: 40px; height: 40px; }
  /* 二级导航按钮缩小 */
  #memberSubNav .btn { font-size: .7rem; padding: 4px 8px; }
}

/* 手机 (≤480px) */
@media (max-width: 480px) {
  main { padding: 8px; }
  .tabs { gap: 0; overflow-x: auto; }
  /* 登录卡片 */
  .login-card { padding: 20px 16px; }
  /* 任务卡片单列 */
  .quest-grid { grid-template-columns: 1fr; }
}
```

### 4.2 移动端特有优化

- Tab 栏可横向滑动（`overflow-x: auto`）
- 成员档案头像行可横向滑动
- 弹窗在手机上全屏显示
- 按钮最小触摸区域 44×44px
- 输入框字体不小于 16px（防止 iOS 缩放）

---

## 五、Header 横幅优化

### 5.1 当前问题

- 图片 `object-fit:cover` 但 header 高度固定 `min-height:180px`
- 图片可能被裁切得不理想
- 登录后 header 显得太空

### 5.2 优化方案

```css
header {
  position: relative;
  height: 15vh;           /* 相对视口高度 */
  min-height: 120px;
  max-height: 200px;
  overflow: hidden;
}
header img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 60%;
}
```

- 手机端减小高度：`height: 12vh; min-height: 80px; max-height: 140px;`
- 登录后 header 叠加用户信息（当前已通过 worldHUD 实现）
- 不登录时 header 可以显示大幅欢迎图

---

## 六、登录页整体改造

### 6.1 当前问题
- 登录页没有背景图，只有纯色渐变
- 没有「南塘世界」的氛围感

### 6.2 改造方案

```
┌─────────────────────────────────────────────────┐
│                                                 │
│         [全屏水彩背景图+暗色渐变遮罩]              │
│                                                 │
│         ┌──────────────────────┐                │
│         │    🏰                │                │
│         │  🌍 南塘·第四期      │                │
│         │  「寻找」             │                │
│         │                      │                │
│         │  [✨ 我是新来的]      │                │
│         │  [📋 我有账号]        │                │
│         └──────────────────────┘                │
│                                                 │
└─────────────────────────────────────────────────┘
```

- 背景图用图1（水彩南塘黄昏）
- 卡片半透明暗色，金色边框
- 按钮圆角更大，有微光效果
- 整体暗色调，金色点缀

---

## 七、实施优先级

| 优先级 | 改动 | 效果 |
|--------|------|------|
| 🔴 P0 | 登录页暗色主题 + 背景图支撑 | 第一印象质变 |
| 🔴 P0 | 手机响应式 (@media) | 手机可用 |
| 🟡 P1 | 顶部工具栏二级菜单 | 界面更干净 |
| 🟡 P1 | 冒险者暖棕配色 | 身份视觉区分 |
| 🟢 P2 | Header 横幅图片更新 | 更美观 |
| 🟢 P2 | 卡片纹理背景 | 质感提升 |

---

## 八、给 AI 的第一批图片提示词（立即可跑）

如果你想先跑几张图看看效果：

**最急（现在就需要）**：
> **图1中文版**：水墨水彩，中国南方古村黄昏，青瓦白墙，炊烟，远山，画架，暖金色光，下方暗上方亮，吉卜力光线风格，16:9横幅

**次急（Phase 2用）**：
> **图2中文版**：横向宽幅水彩，南塘田野，浅绿色调，白墙画室，晨光，轻透水彩，超宽画幅4:1

> **图3中文版**：横向宽幅水彩，南塘村庄，蓝灰紫调，薄雾，神秘冒险感，比浅绿色更暗更浓，超宽画幅4:1

---

*执行顺序：先把图1跑出来 → 登录页改造 → 响应式 → 二级菜单 → 其他细节*
