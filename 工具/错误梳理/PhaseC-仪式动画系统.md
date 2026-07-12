# Phase C：仪式动画系统

> 2026-07-10 · 状态：已审查，待执行
> 所属方案：世界终端-完整数据与版本管理方案
> 本阶段定位：**纯前端动画层**。不涉及任何数据结构变化，不修改业务逻辑。
> 依赖：Phase B（Step ⓪ 和 Step ④-4c 的按钮会触发本阶段的入口函数）
> 被依赖：无

---

## 〇、背景：为什么要做这件事

### 仪式不是多余的装饰

社区型 DAO 的核心体验不是"效率工具"，而是"共同记忆"。创营和开营是两个最重要的仪式时刻——一个是"我决定创建"，一个是"我们一起开始"。如果这两个时刻只是表单按钮 + 一行 alert，体验和填一个 Excel 表格没区别。

本阶段给这两个时刻配上全屏动画。它有三个约束：

1. **必须可降级**：如果动画加载失败（低端设备、网络差、CSS 没加载），业务逻辑不能中断。Phase B 的按钮行为必须有一个"跳过仪式直接执行业务逻辑"的路径。
2. **不涉及数据层**：动画只读取 Phase A 的 `camp_info.current.identity`（显示营队名称和主题），不写入任何数据。
3. **自包含**：仪式相关代码应该集中在一个区域，方便未来维护或替换动画效果。

### 本阶段要达成什么

1. 实现 `openIgniteCeremony()` — 创营时的"点燃火种"全屏动画
2. 实现 `openLaunchCeremony()` — 开营时的"星光汇聚"全屏动画
3. 实现导航条中的火种指示器（根据步骤进度变化的小图标）

---

## 一、现有代码现状（执行前必须对照）

### 1.1 本阶段新增的代码全是独立文件或独立区块

因为全是 CSS 动画 + DOM 操作，本阶段不修改任何现有函数。所有新增代码放在以下位置：

- **动画 CSS**：在 `<style>` 标签末尾添加（约 line 315 附近，现有主题色定义之后）
- **仪式 HTML 覆盖层**：在 `</body>` 之前（约 line 11100 附近），添加两个全屏覆盖层 div
- **仪式 JS 函数**：在工具函数区域末尾（约 line 11000 附近），添加三个新函数

### 1.2 Phase B 预留的调用点

Phase B 在以下位置预留了对外接口——本阶段只需要实现这些函数，Phase B 会自动调用：

| 调用点 | 触发时机 | 调用的函数 | 回调 |
|--------|----------|-----------|------|
| Step ⓪ 保存后 | 管理员点击「点燃火种」 | `openIgniteCeremony(callback)` | `callback()` → 进入 Step ① |
| Step ④-4c | 管理员点击「开始开营仪式」 | `openLaunchCeremony(members, callback)` | `callback()` → 进入 4d |
| 导航条渲染 | `renderWizardNav()` 每次调用 | `getFlameState(step)` | 返回当前步骤对应的 emoji/class |

### 1.3 全局状态

仪式系统需要一个全局对象来跟踪开营就绪状态：

```
window._ceremonyState = {
  readyList: []  // 已就绪的成员名字数组
};
```

---

## 二、动画规格

### 2.1 创营仪式：点燃火种

**触发**：管理员在 Step ⓪ 点击「✨ 点燃火种」。

**动画流程**：

1. **暗场**（0ms）：全屏暗色覆盖层渐入（`opacity 0→1`，持续 500ms）。背景色约 `#0d0a06`，散布 15-30 颗极小白色星点，各自独立缓慢漂移。

2. **火种呼吸**（500ms-3500ms）：画面中央出现蜡烛火种（🕯️ emoji 或 CSS 绘制的火焰形状）。火种做一明一暗的呼吸动画（`scale(0.9) ↔ scale(1.1)`，周期约 2 秒）。周围有微弱的暖金色光晕（`box-shadow` 或 `radial-gradient`）。在其上方显示营队名称和主题文字，下方显示"砚仁 创建"。

3. **点燃瞬间**（用户点击「✨ 点燃火种」按钮后）：背景星点从各自位置加速飞向中央火种（`transition all 1.5s`）。星点到达火种位置的瞬间，火种从 🕯️ 变为 🔥（更大的火焰，更亮的光）。从火种中心发出 3-5 圈暖金色光圈，一圈圈向外扩散（`@keyframes ripple`，每圈半径递增、透明度递减，类似水面涟漪）。

4. **确认**（动画完成，约 1500ms 后）：火种稳定燃烧，画面底部显示"🌍 营队正式创立"和当前日期。出现「进入统筹 →」按钮。点击按钮 → 淡出覆盖层 → 调用 `callback()`。

**关键 CSS 动画**：
- 星点漂移：`@keyframes stardrift` — `translate` + `opacity`，随机延迟 0-8s，周期 8-12s
- 火种呼吸：`@keyframes flamebreathe` — `transform: scale(0.9, 1.1)`，周期 2s
- 光扩散：`@keyframes ripples` — `width` 从 0 到 300px，`opacity` 从 0.6 到 0，周期 1.5s
- 星点汇聚：CSS `transition` — `left` 和 `top` 从原始位置到中央，duration 1.5s，ease-in

### 2.2 开营仪式：星光汇聚

**触发**：管理员在 Step ④-4c 点击「🎊 开始开营仪式」。

**参与者**：所有共建者（从 `data.camp_info.current.team.staff_cards` 获取名字列表）。

**动画流程**：

1. **暗场 + 星辰面板**（0ms）：全屏暗色覆盖层渐入。中央显示营队火种（🔥，比创营时更亮）。周围均匀分布 N 颗暗淡星辰（☆），每颗下面标注成员名字和「等待中…」。

2. **就绪阶段**（交互阶段，无固定时长）：页面底部显示「🚀 开启共创」按钮和就绪计数「等待所有人就绪 · 0/N」。每个参与者点击自己的按钮后：

   - 该参与者的星 ☆ → ✨（白色金光，有光晕，微微旋转）
   - 按钮变灰显示「✓ 已就绪」
   - 底部文案更新为「你已就绪，等待其他人…（X/N）」
   - 其他人看到「张三 已就绪，等待你…（X/N）」
   - 火种火焰稍微变亮一点

3. **汇聚**（N/N 就绪后）：全部星光从各自位置加速飞向中央火种（1.5s）。火种 🔥 → 🔥🔥（大火，火星粒子飞溅）。光扩散涟漪（同创营仪式）。

4. **完成**：「🏁 正式启动！」文字 + 日期 + 各成员名字及任务数。出现「进入我的工作台 →」按钮。点击 → 淡出 → 调用 `callback()`。

**就绪状态同步**：
- 纯前端实现：通过 `window._ceremonyState.readyList` 数组管理
- 每个人点击后名字加入数组，更新 DOM（所有共建者通常在同一设备上操作，如果是远程协作则需额外同步机制——本阶段先做单设备版本）

### 2.3 降级模式

两个函数都必须实现降级逻辑：

```
function openIgniteCeremony(callback) {
  // 检测浏览器能力：支持 CSS animation 且非缩减动画偏好
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced || !CSS.supports('animation', 'name: test')) {
    // 降级：跳过动画，直接执行回调
    callback();
    return;
  }
  // 正常动画流程...
}
```

### 2.4 火种指示器

`getFlameState(step)` 返回当前步骤对应的火种状态：

| 步骤 | 状态 | 返回 |
|:--:|------|------|
| ⓪ 未开始 | 未燃 | `{ emoji: '🕯️', class: 'unlit', label: '待点燃' }` |
| ⓪ 已提交 → ① | 初燃 | `{ emoji: '🔥', class: 'ignited', label: '已点燃' }` |
| ① 完成后 | 初燃 | 同前 |
| ② 完成后 | 渐亮 | `{ emoji: '🔥', class: 'brighter', label: '火焰渐亮' }` |
| ③ 完成后 | 添柴 | `{ emoji: '🔥', class: 'adding', label: '添柴' }` |
| ④ 发包/启动后 | 旺盛 | `{ emoji: '🔥🔥', class: 'roaring', label: '旺盛' }` |

Phase B 的 `renderWizardNav()` 调用此函数，把结果渲染在导航条的步骤按钮旁边。

### 2.5 视觉参数速查表

| 元素 | 属性 | 值 |
|------|------|------|
| 覆盖层背景 | `background` | `#0d0a06` |
| 覆盖层 z-index | `z-index` | `9999` |
| 背景星点数量 | 随机 | 15-30 个 |
| 星点大小 | `width/height` | 2-4px |
| 火种（未燃）尺寸 | `font-size` | 48px |
| 火种（初燃）尺寸 | `font-size` | 64px |
| 火种（旺盛）尺寸 | `font-size` | 80px |
| 光扩散圈数 | | 3-5 圈 |
| 光扩散颜色 | | `rgba(255, 180, 50, var(--opacity))` |
| 仪式文字颜色 | `color` | `#f0d080`（暖金色） |
| 仪式文字字体大小 | `font-size` | 标题 1.2rem，正文 0.85rem |
| 降级检测 | | `prefers-reduced-motion` + `CSS.supports('animation', ...)` |

---

## 三、具体操作（按顺序执行）

### 操作 1：添加仪式覆盖层 HTML

在 `</body>` 之前（约 line 11100）添加两个 div：

```html
<div id="ceremonyIgnite" class="ceremony-overlay hidden">
  <div id="ceremonyIgniteBg" class="ceremony-bg"></div>
  <div id="ceremonyIgniteFlame" class="ceremony-flame">🕯️</div>
  <div id="ceremonyIgniteTitle" class="ceremony-title"></div>
  <div id="ceremonyIgniteBtn" class="ceremony-btn hidden">✨ 点燃火种 · 创建营队</div>
  <div id="ceremonyIgniteDone" class="ceremony-done hidden"></div>
</div>

<div id="ceremonyLaunch" class="ceremony-overlay hidden">
  <div id="ceremonyLaunchBg" class="ceremony-bg"></div>
  <div id="ceremonyLaunchFlame" class="ceremony-flame">🔥</div>
  <div id="ceremonyLaunchStars" class="ceremony-stars"></div>
  <div id="ceremonyLaunchBtn" class="ceremony-btn">🚀 开启共创</div>
  <div id="ceremonyLaunchStatus" class="ceremony-status"></div>
  <div id="ceremonyLaunchDone" class="ceremony-done hidden"></div>
</div>
```

### 操作 2：添加仪式 CSS

在 `<style>` 标签末尾（约 line 315 附近）添加所有仪式相关的 CSS 类：
- `.ceremony-overlay` — 全屏覆盖层基础样式
- `.ceremony-bg` — 星空背景（`radial-gradient` + 星点伪元素）
- `.ceremony-flame` — 火种呼吸动画
- 光扩散涟漪的 `@keyframes ripples`
- 星点漂移的 `@keyframes stardrift`
- 降级检测无关的样式（`@media (prefers-reduced-motion) { ... }`）

### 操作 3：实现 JS 函数

**`openIgniteCeremony(callback)`**：
1. 降级检测 → 是则 `callback()` 返回
2. 读取 `data.camp_info.current.identity`（营队名称、主题、创建人）
3. 显示 `#ceremonyIgnite`，隐藏 `#ceremonyIgniteDone` 和 `#ceremonyIgniteBtn`
4. 启动暗场 + 火种呼吸动画（CSS class 切换）
5. 1.5s 后显示「✨ 点燃火种」按钮
6. 按钮点击 → 执行点燃动画（星点汇聚 + 光扩散）→ 显示完成面板 → 点击「进入统筹」→ 淡出 → `callback()`

**`openLaunchCeremony(members, callback)`**：
1. 降级检测 → 是则 `callback()` 返回
2. `members` 数组：`[{name, taskCount, nt}]`，从 staff_cards 传入
3. 在 `#ceremonyLaunchStars` 中为每个成员渲染一颗星（位置随机但均匀分布在火种周围）
4. 显示就绪计数「0/N」
5. 按钮点击 → 当前用户就绪 → 更新星状态 → 更新计数
6. N/N → 星光汇聚动画 → 火种变旺盛 → 光扩散 → 显示完成面板 → `callback()`

**`getFlameState(step)`**：
根据 `data.camp_progress` 的步骤状态返回火种状态对象。

### 操作 4：在 Phase B 的调用点接入

确认 `saveStep0()` 在调用 `createSnapshot` 之后、`switchStep(1)` 之前，调用 `openIgniteCeremony(function() { switchStep(1); })`。

确认 Step ④-4c 的「开始开营仪式」按钮调用 `openLaunchCeremony(members, function() { /* 进入 4d */ })`。

---

## 四、不改的范围（明确排除）

| 不碰 | 原因 |
|------|------|
| Phase A 数据结构 | 只读 `camp_info.current.identity` |
| Phase B 业务逻辑 | 只通过 callback 衔接 |
| 音效 | 本阶段不做（可选增强） |
| 远程同步 | 单设备版本，多人远程就绪同步以后做 |
| 现有 CSS 类名 | 所有仪式类名以 `ceremony-` 前缀，避免冲突 |

---

## 五、与其他 Phase 的关系

```
Phase B（向导 UI）
  │  saveStep0() → openIgniteCeremony(callback)
  │  Step ④-4c  → openLaunchCeremony(members, callback)
  │  renderWizardNav() → getFlameState(step)
  │
Phase C（本阶段）
  │  实现上述三个函数
  │  纯 CSS + DOM 操作
  │  通过 callback 与 Phase B 解耦
  │
  └── 无下游依赖
```

---

## 六、验收清单

| # | 验证动作 | 预期 |
|:--:|------|------|
| 1 | Step ⓪ 点击「点燃火种」 | 全屏暗色覆盖层出现，火种呼吸动画可见 |
| 2 | 覆盖层中点击「✨ 点燃火种」 | 星点汇聚动画 + 光扩散涟漪 |
| 3 | 动画完成后点击「进入统筹」 | 覆盖层淡出，自动跳转 Step ① |
| 4 | 系统设置 `prefers-reduced-motion: reduce` | 跳过动画，直接执行回调，无报错 |
| 5 | 导航条中火种指示器 | Step ⓪ 显示 🕯️，Step ①-④ 显示 🔥 或 🔥🔥 |
| 6 | Step ④-4c 点击「开始开营仪式」 | 全屏暗色 + 星辰面板 + 就绪计数 |
| 7 | 点击「🚀 开启共创」 | 自己的星 ☆→✨ 亮起，计数更新 |
| 8 | 所有共建者就绪（N/N） | 星光汇聚动画 → 火种旺盛 → 光扩散 |
| 9 | 动画完成 | 显示完成面板，点击按钮进入 4d |
| 10 | 所有仪式 CSS 类 | 以 `ceremony-` 前缀，不与现有类名冲突 |
