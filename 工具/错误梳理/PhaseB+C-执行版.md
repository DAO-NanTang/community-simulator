# Phase B+C 执行版（完整版）

> 2026-07-10 · 六轮全覆盖，可直接交由 AI 执行
> 目标文件：`dashboard.html`
> 前置条件：Phase A 已完成

---

## ⚠️ 执行前必读（给 AI）

1. **文件很大（722KB，11559 行）**：用 `Grep` 定位，`Read offset/limit` 读片段，不要一次读全文件。
2. **行号会偏移**：每次编辑后行号变化。本文档行号基于 Phase A 之后的状态，**优先用 grep 模式定位**。
3. **缩进是空格不是 Tab**：用 `Read` 确认目标行的确切内容后再 `Edit`。
4. **Edit 要求完全匹配**：匹配失败时用 `Read` 重读，不要猜测。
5. **严格按顺序执行**：Rounds 1→2→3→4→5→6，不可跳。
6. **每轮结束验证**：控制台命令逐条确认。

---

## 执行地图（完整六轮）

```
Round 1 🟢 纯新增 ~400行   仪式 CSS + HTML + JS（openIgniteCeremony/openLaunchCeremony/getStepFlame）
Round 2 🟡 改+新 ~250行    导航重编号 + 沉浸工坊 + 火苗指示器 + Step ⓪
Round 3 🟡 改+新 ~100行    修正旧 saveStep 的键名 + 数据同步 camp_info + createSnapshot
Round 4 🟡 改 ~30行        角色升级逻辑修正（claimTasks + changeUserRole）
Round 5 🔴 新+删 ~200行    重写 Step ④（四阶段）+ 删除 Step ⑤
Round 6 🟢 清理 ~20行       resetWizard + saveWizDraft + 旧代码清理
```

---

# Round 1：Phase C 动画基础设施（纯新增）

## 操作 1A：追加仪式 CSS

**定位**：grep `</style>`，当前 line 394。

**操作**：在 `</style>` **之前**插入：

```css
/* ═══ Phase C: 仪式动画系统 ═══ */
.ceremony-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: #0d0a06;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  overscroll-behavior: contain;
  transition: opacity .5s ease;
  font-family: var(--font);
}
.ceremony-overlay.hidden { display: none; }
.ceremony-overlay.fade-out { opacity: 0; pointer-events: none; }

.ceremony-bg { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.ceremony-bg .star {
  position: absolute; width: 3px; height: 3px; background: #fff; border-radius: 50%;
  animation: stardrift var(--drift-dur, 10s) linear infinite;
  animation-delay: var(--drift-delay, 0s); opacity: 0;
}

.ceremony-flame { font-size: 64px; position: relative; z-index: 2; transition: all .5s ease; }
.ceremony-flame.breathing { animation: flamebreathe 2s ease-in-out infinite; }
.ceremony-flame.ignited { font-size: 80px; }
.ceremony-flame.roaring { font-size: 96px; }

.ceremony-title { color: #f0d080; font-size: 1.2rem; margin-top: 20px; z-index: 2; text-align: center; }
.ceremony-subtitle { color: rgba(240,208,128,.6); font-size: .85rem; margin-top: 6px; z-index: 2; }
.ceremony-btn {
  margin-top: 30px; padding: 14px 36px; font-size: 1.1rem; font-family: var(--font);
  background: linear-gradient(135deg, #f0a030, #e08020); color: #fff; border: none;
  border-radius: 12px; cursor: pointer; z-index: 2; transition: all .3s ease;
}
.ceremony-btn:hover { transform: scale(1.05); box-shadow: 0 0 30px rgba(240,160,48,.5); }
.ceremony-btn.done { background: #555; cursor: default; }
.ceremony-btn.done:hover { transform: none; box-shadow: none; }
.ceremony-done { text-align: center; z-index: 2; }
.ceremony-done .done-title { color: #f0d080; font-size: 1.4rem; margin-bottom: 8px; }
.ceremony-done .done-date { color: rgba(240,208,128,.5); font-size: .8rem; margin-bottom: 6px; }
.ceremony-skip {
  position: fixed; bottom: 20px; right: 24px; z-index: 10;
  color: rgba(255,255,255,.25); font-size: .7rem; cursor: pointer;
  opacity: 0; transition: opacity .5s 1.5s;
  background: none; border: none; font-family: var(--font);
}
.ceremony-skip.visible { opacity: 1; }
.ceremony-skip:hover { color: rgba(255,255,255,.5); }

.ceremony-stars { display: flex; gap: 60px; flex-wrap: wrap; justify-content: center; z-index: 2; margin: 30px 0; }
.ceremony-star-card { text-align: center; transition: all .5s ease; }
.ceremony-star-card .star-icon { font-size: 36px; display: block; transition: all .3s ease; }
.ceremony-star-card.ready .star-icon { color: #ffd700; filter: drop-shadow(0 0 8px rgba(255,215,0,.8)); transform: scale(1.2); }
.ceremony-star-card .star-name { color: rgba(240,208,128,.7); font-size: .85rem; margin-top: 4px; }
.ceremony-star-card .star-status { color: rgba(240,208,128,.4); font-size: .7rem; }
.ceremony-star-card.ready .star-status { color: #ffd700; }
.ceremony-status { color: rgba(240,208,128,.5); font-size: .8rem; z-index: 2; margin-top: 10px; }

.ceremony-ripple {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(255,180,50,.3);
  animation: ripple 1.5s ease-out forwards;
  pointer-events: none;
}

@keyframes stardrift {
  0%   { opacity: 0; transform: translate(0, 0) scale(.8); }
  10%  { opacity: .8; }
  90%  { opacity: .3; }
  100% { opacity: 0; transform: translate(var(--drift-x, 30px), var(--drift-y, -40px)) scale(1.2); }
}
@keyframes flamebreathe {
  0%, 100% { transform: scale(.9); filter: drop-shadow(0 0 8px rgba(255,150,30,.4)); }
  50%      { transform: scale(1.1); filter: drop-shadow(0 0 18px rgba(255,150,30,.8)); }
}
@keyframes ripple {
  0%   { width: 20px; height: 20px; opacity: .6; }
  100% { width: 350px; height: 350px; opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .ceremony-overlay { transition: none; }
  .ceremony-overlay * { animation: none !important; transition: none !important; }
}

/* ═══ 火苗指示器 ═══ */
.nav-flame { font-size: 1rem; display: block; text-align: center; line-height: 1; }
.nav-flame.editing  { animation: flameGlow 2s ease-in-out infinite; }
.nav-flame.just-lit { animation: flameIgnite .6s ease-out; }
.nav-flame.dim { opacity: .35; }
@keyframes flameGlow {
  0%, 100% { filter: drop-shadow(0 0 3px rgba(255,150,30,.5)); }
  50%      { filter: drop-shadow(0 0 8px rgba(255,150,30,1)); }
}
@keyframes flameIgnite {
  0%   { transform: scale(.6); opacity: .3; }
  100% { transform: scale(1); opacity: 1; }
}

/* ═══ 沉浸工坊 ═══ */
.workshop-mode .tabs { max-height: 0; opacity: 0; overflow: hidden; transition: max-height .3s ease, opacity .3s ease; }
.workshop-status-bar { text-align: center; font-size: .7rem; color: var(--muted); margin-top: 6px; padding: 4px 0; border-top: 1px solid var(--border); }
```

**验证**：grep `ceremony-overlay` 和 `@keyframes stardrift` 均出现在文件中。

---

## 操作 1B：追加仪式 HTML 覆盖层

**定位**：grep `</body>`，line 11553。

**操作**：在 `</body>` **之前**插入：

```html
<!-- ═══ Phase C: 仪式覆盖层 ═══ -->
<div id="ceremonyIgnite" class="ceremony-overlay hidden">
  <div id="ceremonyIgniteBg" class="ceremony-bg"></div>
  <div id="ceremonyIgniteFlame" class="ceremony-flame breathing">🕯️</div>
  <div id="ceremonyIgniteTitle" class="ceremony-title"></div>
  <div id="ceremonyIgniteSub" class="ceremony-subtitle"></div>
  <button class="ceremony-btn hidden" id="ceremonyIgniteBtn" onclick="window._ceremonyIgniteAction()">✨ 点燃火种 · 创建营队</button>
  <div id="ceremonyIgniteDone" class="ceremony-done hidden"></div>
  <button class="ceremony-skip" id="ceremonyIgniteSkip" onclick="window._ceremonySkip()">跳过仪式 →</button>
</div>

<div id="ceremonyLaunch" class="ceremony-overlay hidden">
  <div id="ceremonyLaunchBg" class="ceremony-bg"></div>
  <div id="ceremonyLaunchFlame" class="ceremony-flame breathing">🔥</div>
  <div class="ceremony-title" id="ceremonyLaunchTitle"></div>
  <div id="ceremonyLaunchStars" class="ceremony-stars"></div>
  <button class="ceremony-btn" id="ceremonyLaunchBtn" onclick="window._ceremonyLaunchAction()">🚀 开启共创</button>
  <div id="ceremonyLaunchStatus" class="ceremony-status"></div>
  <div id="ceremonyLaunchDone" class="ceremony-done hidden"></div>
  <button class="ceremony-skip" id="ceremonyLaunchSkip" onclick="window._ceremonySkip()">跳过仪式 →</button>
</div>

<!-- ═══ 版本历史面板容器 ═══ -->
<div id="changelogOverlay" class="modal-overlay hidden" style="display:flex;align-items:center;justify-content:center" onclick="if(event.target===this)closeChangelogPanel()">
  <div class="modal" style="max-width:500px;max-height:70vh;overflow-y:auto" id="changelogContent"></div>
</div>
```

**验证**：grep `ceremonyIgnite` 返回 3+ 处匹配。

---

## 操作 1C：追加仪式 JS 函数

**定位**：grep `</script>`，取第二个匹配（line 11552）。

**操作**：在 `</script>` **之前**插入：

```javascript
// ═══ Phase C: 仪式系统 ═══
window._ceremonyActive = false;
window._ceremonyCallback = null;
window._ceremonyState = { readyList: [] };

function _canAnimate() {
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  return !prefersReduced && CSS.supports('animation', 'name: test');
}

function _renderCeremonyStars(bgEl, count) {
  bgEl.innerHTML = '';
  for (var i = 0; i < (count || 20); i++) {
    var star = document.createElement('div');
    star.className = 'star';
    star.style.left = (Math.random() * 100) + '%';
    star.style.top = (Math.random() * 100) + '%';
    star.style.setProperty('--drift-dur', (8 + Math.random() * 6) + 's');
    star.style.setProperty('--drift-delay', (Math.random() * 8) + 's');
    star.style.setProperty('--drift-x', ((Math.random() - .5) * 60) + 'px');
    star.style.setProperty('--drift-y', ((Math.random() - .5) * 80) + 'px');
    star.style.width = (2 + Math.random() * 3) + 'px';
    star.style.height = star.style.width;
    bgEl.appendChild(star);
  }
}

function _spawnRipples(overlay, count) {
  var flame = overlay.querySelector('.ceremony-flame');
  var rect = flame.getBoundingClientRect();
  var cx = rect.left + rect.width / 2;
  var cy = rect.top + rect.height / 2;
  for (var i = 0; i < (count || 4); i++) {
    var ripple = document.createElement('div');
    ripple.className = 'ceremony-ripple';
    ripple.style.left = (cx - 10) + 'px';
    ripple.style.top = (cy - 10) + 'px';
    ripple.style.animationDelay = (i * .3) + 's';
    overlay.appendChild(ripple);
  }
  setTimeout(function() {
    overlay.querySelectorAll('.ceremony-ripple').forEach(function(r) { r.remove(); });
  }, 2000);
}

window._ceremonySkip = function() {
  if (!window._ceremonyActive) return;
  var overlay = document.querySelector('.ceremony-overlay:not(.hidden)');
  if (overlay) {
    clearCeremonyListeners();
    overlay.classList.add('fade-out');
    setTimeout(function() {
      overlay.classList.add('hidden');
      overlay.classList.remove('fade-out');
      window._ceremonyActive = false;
      if (window._ceremonyCallback) { var cb = window._ceremonyCallback; window._ceremonyCallback = null; cb(); }
    }, 400);
  }
};

var _ceremonyKeyHandler = null;
function setupCeremonyKeyHandler() {
  if (_ceremonyKeyHandler) document.removeEventListener('keydown', _ceremonyKeyHandler);
  _ceremonyKeyHandler = function(e) {
    if (e.key === 'Escape' && window._ceremonyActive) { window._ceremonySkip(); }
  };
  document.addEventListener('keydown', _ceremonyKeyHandler);
}
function clearCeremonyListeners() {
  if (_ceremonyKeyHandler) { document.removeEventListener('keydown', _ceremonyKeyHandler); _ceremonyKeyHandler = null; }
}

// ═══ 创营仪式 ═══
function openIgniteCeremony(callback) {
  if (!_canAnimate()) { callback(); return; }
  window._ceremonyActive = true;
  window._ceremonyCallback = callback;
  setupCeremonyKeyHandler();

  var identity = (data.camp_info && data.camp_info.current && data.camp_info.current.identity) || {};
  var campName = identity.name || '未命名营队';
  var campTheme = identity.description || '';
  var creator = identity.created_by || (currentUser && currentUser.name) || '';

  var overlay = document.getElementById('ceremonyIgnite');
  var bg = document.getElementById('ceremonyIgniteBg');
  var flame = document.getElementById('ceremonyIgniteFlame');
  var title = document.getElementById('ceremonyIgniteTitle');
  var sub = document.getElementById('ceremonyIgniteSub');
  var btn = document.getElementById('ceremonyIgniteBtn');
  var done = document.getElementById('ceremonyIgniteDone');
  var skip = document.getElementById('ceremonyIgniteSkip');

  overlay.classList.remove('hidden', 'fade-out');
  flame.textContent = '🕯️'; flame.className = 'ceremony-flame breathing';
  btn.classList.add('hidden'); btn.classList.remove('done');
  done.classList.add('hidden');
  skip.classList.remove('visible');

  title.textContent = campName;
  sub.textContent = (campTheme ? '「' + campTheme + '」' : '') + (creator ? '  ·  ' + creator + ' 创建' : '');
  _renderCeremonyStars(bg, 20);

  setTimeout(function() { btn.classList.remove('hidden'); skip.classList.add('visible'); }, 1500);

  window._ceremonyIgniteAction = function() {
    if (btn.classList.contains('done')) return;
    btn.classList.add('done');
    skip.classList.remove('visible');
    bg.querySelectorAll('.star').forEach(function(s) {
      s.style.transition = 'all 1.5s ease-in';
      s.style.left = '50%'; s.style.top = '50%'; s.style.opacity = '0';
    });
    setTimeout(function() {
      flame.textContent = '🔥'; flame.className = 'ceremony-flame ignited';
      _spawnRipples(overlay, 4);
    }, 1200);
    setTimeout(function() {
      done.innerHTML = '<div class="done-title">🌍 营队正式创立</div>' +
        '<div class="done-date">' + Clock.today() + ' · ' + creator + ' 创建</div>' +
        '<div style="margin-top:16px;color:rgba(240,208,128,.6);font-size:.85rem">五步搭建，即将开始 ——</div>' +
        '<button class="ceremony-btn" style="margin-top:16px" onclick="window._ceremonySkip()">进入统筹 →</button>';
      done.classList.remove('hidden');
      btn.classList.add('hidden');
    }, 2200);
  };
}

// ═══ 开营仪式 ═══
function openLaunchCeremony(members, callback) {
  if (!_canAnimate()) { callback(); return; }
  window._ceremonyActive = true;
  window._ceremonyCallback = callback;
  window._ceremonyState.readyList = [];
  setupCeremonyKeyHandler();

  var identity = (data.camp_info && data.camp_info.current && data.camp_info.current.identity) || {};
  var campName = identity.name || '未命名营队';

  var overlay = document.getElementById('ceremonyLaunch');
  var bg = document.getElementById('ceremonyLaunchBg');
  var stars = document.getElementById('ceremonyLaunchStars');
  var btn = document.getElementById('ceremonyLaunchBtn');
  var status = document.getElementById('ceremonyLaunchStatus');
  var done = document.getElementById('ceremonyLaunchDone');
  var skip = document.getElementById('ceremonyLaunchSkip');
  var title = document.getElementById('ceremonyLaunchTitle');

  overlay.classList.remove('hidden', 'fade-out');
  document.getElementById('ceremonyLaunchFlame').className = 'ceremony-flame breathing';
  title.textContent = campName;
  btn.classList.remove('done');
  done.classList.add('hidden');
  skip.classList.remove('visible');
  _renderCeremonyStars(bg, 25);

  var mList = members || [];
  stars.innerHTML = mList.map(function(m, i) {
    return '<div class="ceremony-star-card" id="launchStar' + i + '">' +
      '<span class="star-icon">☆</span>' +
      '<span class="star-name">' + (typeof escHtml === 'function' ? escHtml(m.name) : m.name) + '</span>' +
      '<span class="star-status">等待中…</span></div>';
  }).join('');
  status.textContent = '等待所有人就绪 · 0/' + mList.length;

  setTimeout(function() { skip.classList.add('visible'); }, 1500);

  window._ceremonyLaunchAction = function() {
    if (btn.classList.contains('done')) return;
    var who = currentUser && currentUser.name;
    if (!who) return;
    if (window._ceremonyState.readyList.indexOf(who) === -1) {
      window._ceremonyState.readyList.push(who);
    }
    btn.classList.add('done');
    mList.forEach(function(m, i) {
      if (m.name === who) {
        var card = document.getElementById('launchStar' + i);
        if (card) { card.classList.add('ready'); card.querySelector('.star-icon').textContent = '✨'; card.querySelector('.star-status').textContent = '已就绪！'; }
      }
    });
    var ready = window._ceremonyState.readyList.length;
    var total = mList.length;
    status.textContent = '你已就绪 · ' + ready + '/' + total + (ready < total ? ' · 等待其他人…' : '');

    if (ready >= total) {
      skip.classList.remove('visible');
      status.textContent = '全员就绪！星光汇聚…';
      document.getElementById('ceremonyLaunchFlame').textContent = '🔥🔥';
      document.getElementById('ceremonyLaunchFlame').className = 'ceremony-flame roaring';
      _spawnRipples(overlay, 5);
      stars.querySelectorAll('.ceremony-star-card').forEach(function(c) { c.querySelector('.star-icon').textContent = '★'; });
      setTimeout(function() {
        done.innerHTML = '<div class="done-title">🏁 正式启动！</div>' +
          '<div class="done-date">' + Clock.today() + '</div>' +
          mList.map(function(m) { return '<div style="color:#f0d080;font-size:.8rem;margin:2px">✨ ' + (typeof escHtml === 'function' ? escHtml(m.name) : m.name) + ' · ' + (m.taskCount||0) + '项 · ' + (m.nt||0) + ' NT</div>'; }).join('') +
          '<button class="ceremony-btn" style="margin-top:16px" onclick="window._ceremonySkip()">进入我的工作台 →</button>';
        done.classList.remove('hidden');
        btn.classList.add('hidden');
        stars.innerHTML = '';
      }, 2000);
    }
  };
}

// ═══ 火苗指示器 ═══
function getStepFlame(n) {
  var ci = data.camp_info;
  if (!ci) return { emoji: '🕯️', cls: 'dim', label: '待点燃' };

  var isCurrent = data.camp_progress && data.camp_progress.step === n;
  var level = checkStepFillLevel(n);

  if (n === 0) {
    var campCreated = ci.current && ci.current.identity && ci.current.identity.name;
    if (!campCreated && !isCurrent) return { emoji: '🕯️', cls: 'dim', label: '待点燃' };
    if (isCurrent && !campCreated) return { emoji: '🕯️', cls: 'editing', label: '编辑中' };
    if (campCreated && !isCurrent) return { emoji: '🔥', cls: '', label: '已点燃' };
    return { emoji: '🔥', cls: 'editing', label: '编辑中' };
  }

  if (isCurrent) {
    if (level === 2) return { emoji: '🔥🔥', cls: 'editing', label: '编辑中' };
    return { emoji: '🔥', cls: 'editing', label: '编辑中' };
  }

  if (level === 0) return { emoji: '🕯️', cls: 'dim', label: '待填写' };
  if (level === 1) return { emoji: '🔥', cls: '', label: '初燃' };
  return { emoji: '🔥+', cls: '', label: '已完整' };
}

function checkStepFillLevel(n) {
  var ci = data.camp_info;
  if (!ci || !ci.current) return 0;
  var c = ci.current;

  if (n === 0) {
    var id = c.identity || {};
    if (id.name && id.period) return 2;
    if (id.name || id.period) return 1;
    return 0;
  }
  if (n === 1) {
    var b = c.budget || {};
    var cal = c.calendar || {};
    if (b.nt_total_pool > 0 && cal.start_date) return 2;
    if (b.nt_total_pool > 0 || cal.start_date) return 1;
    return 0;
  }
  if (n === 2) {
    return (c.tasks && c.tasks.pool && c.tasks.pool.length > 0) ? 2 : 0;
  }
  if (n === 3) {
    return (c.team && c.team.staff_cards && c.team.staff_cards.length > 0) ? 2 : 0;
  }
  if (n === 4) {
    return (c.identity && c.identity.status === 'active') ? 2 : 0;
  }
  return 0;
}
```

**验收**：
```javascript
typeof openIgniteCeremony   // 'function'
typeof openLaunchCeremony   // 'function'
typeof getStepFlame         // 'function'
getStepFlame(0)             // { emoji:'🕯️', cls:'dim', label:'待点燃' }
```

---

# Round 2：导航重编号 + 沉浸工坊 + Step ⓪

## 操作 2A：重写 renderWizardNav()

**定位**：grep `function renderWizardNav()`，line 9064。整个函数从 line 9064 到 9083。

**操作**：整体替换为：

```javascript
function renderWizardNav() {
  var steps = [
    { num:0, label:'创营', key:'0' },
    { num:1, label:'统筹', key:'1' },
    { num:2, label:'任务池', key:'2' },
    { num:3, label:'选将', key:'3' },
    { num:4, label:'启动', key:'4' },
  ];
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  var cp = data.camp_progress;
  var campCreated = data.camp_info && data.camp_info.current && data.camp_info.current.identity && data.camp_info.current.identity.name;

  var html = '<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:center">';
  steps.forEach(function(s, i) {
    var flame = getStepFlame(s.num);
    var isActive = cp.step === s.num;
    var canClick = (s.num === 0) || campCreated;
    var isDone = (cp.steps[s.key] === 'done');

    var badge = isActive ? '⚠' : (isDone ? '✅' : '');
    var cls = isActive ? 'btn pri' : 'btn';
    var op = canClick ? '' : 'opacity:.35;pointer-events:none';
    var title = canClick ? '' : 'title="请先完成 Step ⓪ 创营"';

    html += '<div style="text-align:center">' +
      '<button class="' + cls + '" onclick="switchStep(' + s.num + ')" style="font-size:.78rem;padding:6px 12px;' + op + '" ' + title + '>' +
      badge + ' ' + s.num + '. ' + s.label + '</button>' +
      '<span class="nav-flame' + (flame.cls ? ' ' + flame.cls : '') + '" title="' + flame.label + '">' + flame.emoji + '</span></div>';
    if (i < 4) html += '<span style="color:var(--border);font-size:1rem">→</span>';
  });
  html += '</div>';

  // 状态栏
  var ci = data.camp_info;
  var campName = (ci && ci.current && ci.current.identity && ci.current.identity.name) || '未创建';
  var ver = (ci && ci.current && ci.current.version) || 0;
  var who = (ci && ci.current && ci.current.updated_by) || '';
  html += '<div class="workshop-status-bar">' +
    '<span>当前营队：' + campName + ' · v' + ver + (who ? ' · ' + who : '') + '</span>' +
    '<button class="btn" onclick="showChangelogPanel()" style="font-size:.65rem;padding:2px 8px;margin-left:8px">📋 版本历史</button>' +
    '<button class="btn" onclick="exitWorkshop()" style="font-size:.65rem;padding:2px 8px;margin-left:4px">← 退出工坊</button>' +
    '</div>';

  document.getElementById('wizardNav').innerHTML = html;
}
```

## 操作 2B：修改 switchStep(n)

**定位**：grep `function switchStep(n)`，line 9085。函数到 line 9099。

**操作**：替换为：

```javascript
function switchStep(n) {
  wizardStep = n;
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  data.camp_progress.step = n;
  for (var i = 0; i <= 4; i++) {
    var el = document.getElementById('wiz-step' + i);
    if (el) el.classList.toggle('hidden', i !== n);
  }
  renderWizardNav();
  if (n === 0) renderStep0();
  if (n === 1) renderStep1();
  if (n === 2) { refreshWizTemplateSelect(); renderStep2(); }
  if (n === 3) renderStep3();
  if (n === 4) renderStep4();
  saveData();
}
```

## 操作 2C：废弃 unlockStep(n)

**定位**：grep `function unlockStep(n)`，line 9101。

**操作**：替换为：

```javascript
function unlockStep(n) {
  // Phase B 修订：不再手动解锁。步骤可访问性由 ⓪ 是否完成决定，
  // 步骤状态由 checkStepFillLevel() 数据驱动。保留函数以兼容旧调用。
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  var key = String(n);
  if (data.camp_progress.steps[key] === 'locked') data.camp_progress.steps[key] = 'pending';
}
```

## 操作 2D：新增 enterWorkshop() / exitWorkshop()

**定位**：grep `// ── Wizard State (5-step flow) ──`，line 9047。在它**之前**插入。

**操作**：插入：

```javascript
// ═══ 沉浸式工坊模式 ═══
var _workshopActive = false;

function enterWorkshop() {
  if (_workshopActive) return;
  _workshopActive = true;
  // 给 body 加 class 触发 CSS 收起标签栏
  document.body.classList.add('workshop-mode');
  var hudGenesis = document.getElementById('hudGenesisBtn');
  if (hudGenesis) hudGenesis.classList.add('hidden');
  renderWizardNav();
  switchStep(data.camp_progress.step || 0);
}

function exitWorkshop() {
  if (!_workshopActive) return;
  _workshopActive = false;
  document.body.classList.remove('workshop-mode');
  var hudGenesis = document.getElementById('hudGenesisBtn');
  if (hudGenesis) hudGenesis.classList.remove('hidden');
  saveData();
  switchTab('workspace');
}
```

## 操作 2E：修改 switchTab 中 settings 的进入逻辑

**定位**：grep `name === 'settings'.*renderWizardNav`，line 7158。

**操作**：将：
```javascript
if (name === 'settings') { renderWizardNav(); switchStep(data.camp_progress.step || 1); }
```
替换为：
```javascript
if (name === 'settings') { enterWorkshop(); }
```

## 操作 2F：新增 Step ⓪ HTML

**定位**：grep `id="wiz-step1"`，line 784。

**操作**：在 `<!-- Step 1: Framework -->` 之前插入：

```html
<!-- Step 0: Camp Creation (Phase B 新增) -->
<div id="wiz-step0" class="wiz-step">
  <div class="card" style="max-width:600px;margin:0 auto">
    <h3 style="text-align:center;margin:0 0 4px">🌍 创营 · 创建营队</h3>
    <p style="text-align:center;color:var(--muted);font-size:.82rem;margin:0 0 20px">填入营队的基本信息，点燃属于你们的共创火种。</p>

    <div style="margin-bottom:16px">
      <label style="font-size:.85rem;font-weight:600">营队名称</label>
      <input type="text" id="wizCampName" placeholder="例：第四期南塘共创营" style="width:100%;padding:8px 12px;border:2px solid var(--border);border-radius:8px;font-family:var(--font);font-size:.9rem;margin-top:4px;box-sizing:border-box">
    </div>

    <div style="margin-bottom:16px">
      <label style="font-size:.85rem;font-weight:600">期数</label>
      <select id="wizCampPeriod" style="width:100%;padding:8px 12px;border:2px solid var(--border);border-radius:8px;font-family:var(--font);font-size:.9rem;margin-top:4px;box-sizing:border-box">
        <option value="">-- 选择期数 --</option>
        <option value="第一期">第一期</option><option value="第二期">第二期</option><option value="第三期">第三期</option>
        <option value="第四期">第四期</option><option value="第五期">第五期</option><option value="第六期">第六期</option>
        <option value="第七期">第七期</option><option value="第八期">第八期</option>
        <option value="特别期">特别期</option>
      </select>
    </div>

    <div style="margin-bottom:16px">
      <label style="font-size:.85rem;font-weight:600">类型</label>
      <div style="display:flex;gap:16px;margin-top:6px">
        <label style="font-size:.85rem;cursor:pointer"><input type="radio" name="wizCampType" value="regular" checked onchange="document.getElementById('wizCampTypeVal').value=this.value"> 常规共创营</label>
        <label style="font-size:.85rem;cursor:pointer"><input type="radio" name="wizCampType" value="special" onchange="document.getElementById('wizCampTypeVal').value=this.value"> 特别活动营</label>
      </div>
      <input type="hidden" id="wizCampTypeVal" value="regular">
    </div>

    <div style="margin-bottom:16px">
      <label style="font-size:.85rem;font-weight:600">一句话主题</label>
      <input type="text" id="wizCampTheme" placeholder="例：南塘有风，共创有光" style="width:100%;padding:8px 12px;border:2px solid var(--border);border-radius:8px;font-family:var(--font);font-size:.9rem;margin-top:4px;box-sizing:border-box">
    </div>

    <div style="margin-bottom:20px">
      <label style="font-size:.85rem;font-weight:600">描述 <span style="color:var(--muted);font-weight:400">（可选）</span></label>
      <textarea id="wizCampDesc" rows="3" placeholder="更详细的说明…" style="width:100%;padding:8px 12px;border:2px solid var(--border);border-radius:8px;font-family:var(--font);font-size:.9rem;margin-top:4px;resize:vertical;box-sizing:border-box"></textarea>
    </div>

    <div style="margin-bottom:16px">
      <label style="font-size:.82rem;cursor:pointer;display:flex;align-items:center;gap:6px">
        <input type="checkbox" id="wizCampTestMode" style="width:16px;height:16px">
        🧪 测试模式（测试营队可删除）
      </label>
    </div>

    <div style="text-align:center">
      <button class="btn pri" onclick="saveStep0()" style="font-size:1rem;padding:12px 32px">✨ 点燃火种 · 创建营队</button>
    </div>
  </div>
</div>
```

## 操作 2G：新增 renderStep0() / saveStep0()

**定位**：grep `// ── Wizard State ──`（第二次出现），line 9057。在它**之前**插入。

**操作**：插入：

```javascript
// ═══ Step ⓪：创营 ═══
function renderStep0() {
  var id = (data.camp_info && data.camp_info.current && data.camp_info.current.identity) || {};
  var el;
  el = document.getElementById('wizCampName'); if (el) el.value = id.name || '';
  el = document.getElementById('wizCampPeriod'); if (el) el.value = id.period || '';
  el = document.getElementById('wizCampTheme'); if (el) el.value = id.description || '';
  el = document.getElementById('wizCampDesc'); if (el) el.value = '';
  el = document.getElementById('wizCampTestMode'); if (el) el.checked = !!(id.test_mode);
  var typeRadios = document.getElementsByName('wizCampType');
  for (var i = 0; i < typeRadios.length; i++) {
    typeRadios[i].checked = (typeRadios[i].value === (id.type || 'regular'));
  }
  document.getElementById('wizCampTypeVal').value = id.type || 'regular';
}

function saveStep0() {
  var name = document.getElementById('wizCampName').value.trim();
  var period = document.getElementById('wizCampPeriod').value;
  var type = document.getElementById('wizCampTypeVal').value;
  var theme = document.getElementById('wizCampTheme').value.trim();
  var testMode = document.getElementById('wizCampTestMode').checked;

  if (!name) { alert('请输入营队名称'); return; }
  if (!period) { alert('请选择期数'); return; }

  var ci = data.camp_info;
  ci.current.identity.name = name;
  ci.current.identity.period = period;
  ci.current.identity.type = type;
  ci.current.identity.description = theme;
  ci.current.identity.status = 'preparing';
  ci.current.identity.created_at = Clock.iso();
  ci.current.identity.created_by = (currentUser && currentUser.name) || '系统';
  ci.current.identity.test_mode = !!(testMode);
  ci.current.updated_at = Clock.iso();
  ci.current.updated_by = (currentUser && currentUser.name) || '系统';

  createSnapshot('创营原档', '创建营队：' + name);
  data.camp_progress.steps['0'] = 'done';
  saveData();

  openIgniteCeremony(function() { switchStep(1); });
}
```

## 操作 2H：更新 camp_progress 默认值（4 处）

用 grep 找到**所有**包含 `{step:1,steps:{'1':'active','2':'locked','3':'locked','4':'locked','5':'locked'}}` 的位置，逐个替换为：
```
{step:0,steps:{'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'}}
```

涉及位置（至少 5 处）：
- line 1738：`let data = {...}` 初始化
- line ~1936：corrupted-data 重置对象
- line ~1944：`if (!data.camp_progress)` 兼容检查
- line 9087：`switchStep()` 内部默认值
- line 9102：`unlockStep()` 内部默认值

**验证**：清空 localStorage 刷新后，`data.camp_progress` 为 `{step:0, steps:{'0':'active',...}}`。

---

# Round 3：修正旧函数 + 数据同步 + createSnapshot

> ⚠️ 这是最关键的一轮。旧 saveStep 函数有三个问题：
> 1. camp_progress 用了旧的键名 `'1'~'5'`
> 2. 数据写在 `data.budget/tasks/staff_cards`，没同步到 `camp_info.current`
> 3. 没有调用 `createSnapshot`

## 操作 3A：修正 saveStep1()

**定位**：grep `function saveStep1()`，line 9884。

**操作**：找到函数末尾（`}` 之前），确保最终代码如下：

```javascript
function saveStep1() {
  // Save camp dates
  if (!data.camp_dates) data.camp_dates = {};
  data.camp_dates.start = document.getElementById('wizStartDate').value;
  data.camp_dates.duration_days = parseInt(document.getElementById('wizDuration').value) || 15;
  // Save budget parameters
  if (!data.budget) data.budget = {};
  var staffCount = parseInt(document.getElementById('wizStaffCount2').value) || 0;
  var pCount = parseInt(document.getElementById('wizParticipantBudget').value) || 10;
  var days = data.camp_dates.duration_days || 15;
  data.budget.staff_count = staffCount;
  data.budget.participant_budget = pCount;
  var el;
  el = document.getElementById('wizEarlyBird'); if (el) data.budget.early_bird_price = parseInt(el.value) || 499;
  el = document.getElementById('wizEarlyBirdPct'); if (el) data.budget.early_bird_pct = parseInt(el.value) || 60;
  el = document.getElementById('wizFullPrice'); if (el) data.budget.full_price = parseInt(el.value) || 599;
  el = document.getElementById('wizLodgingRMB'); if (el) data.budget.lodging_rmb = parseInt(el.value) || 30;
  el = document.getElementById('wizLodgingNT'); if (el) data.budget.lodging_nt = parseInt(el.value) || 40;
  el = document.getElementById('wizMealRMB'); if (el) data.budget.meal_rmb = parseInt(el.value) || 8;
  el = document.getElementById('wizMealNT'); if (el) data.budget.meal_nt = parseInt(el.value) || 10;
  // Computed
  data.budget.tuition = (Math.round(pCount * (data.budget.early_bird_pct||60) / 100)) * (data.budget.early_bird_price||499) + (pCount - Math.round(pCount * (data.budget.early_bird_pct||60) / 100)) * (data.budget.full_price||599);
  data.budget.food_lodging_rmb = pCount * days * ((data.budget.lodging_rmb||30) + (data.budget.meal_rmb||8));
  data.budget.food_lodging_nt = pCount * days * ((data.budget.lodging_nt||40) + (data.budget.meal_nt||10));
  if (!data.stats) data.stats = {};
  data.stats.participant_count = pCount;

  // 🆕 修正：使用新的 camp_progress 键名（'1'→'0', '2'→'1'）
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  data.camp_progress.steps['0'] = 'done';
  data.camp_progress.steps['1'] = 'active';
  data.camp_progress.step = 1;

  // 🆕 同步到 camp_info.current
  var b = data.budget || {};
  var cd = data.camp_dates || {};
  data.camp_info.current.budget.nt_total_pool = b.nt_total_pool || 0;
  data.camp_info.current.budget.rmb_budget = b.tuition || 0;
  data.camp_info.current.budget.community_pool_total = b.community_pool_total || 500;
  data.camp_info.current.budget.community_pool_daily = b.community_pool_daily || 10;
  data.camp_info.current.calendar.start_date = cd.start || '';
  data.camp_info.current.calendar.duration_days = cd.duration_days || 15;
  data.camp_info.current.calendar.milestones = cd.milestones || [];
  data.camp_info.current.updated_at = Clock.iso();
  data.camp_info.current.updated_by = (currentUser && currentUser.name) || '系统';

  // 🆕 生成快照
  createSnapshot('统筹完成', '日历和预算设定');

  saveData();
  updateAll();
  switchStep(1);
  setStatus('步骤①已保存 → 进入②任务池');
}
```

**关键改动**：
1. `steps['1']='done'` → `steps['0']='done'`（键名偏移）
2. `steps['2']='active'` → `steps['1']='active'`
3. `data.camp_progress.step = 2` → `= 1`（因为 Step ① = 编号 1）
4. 新增 camp_info 同步代码段
5. 新增 `createSnapshot(...)` 调用
6. `switchStep(2)` → `switchStep(1)`

## 操作 3B：修正 saveStep2()

**定位**：grep `function saveStep2()`，line 10083。

**操作**：替换为：

```javascript
function saveStep2() {
  mergeWizardToData(wizardTasks);
  wizardDirty = false;

  // 🆕 修正键名
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  data.camp_progress.steps['1'] = 'done';
  data.camp_progress.steps['2'] = 'active';
  data.camp_progress.step = 2;

  // 🆕 同步到 camp_info
  data.camp_info.current.tasks.pool = JSON.parse(JSON.stringify(wizardTasks));
  data.camp_info.current.updated_at = Clock.iso();
  data.camp_info.current.updated_by = (currentUser && currentUser.name) || '系统';

  // 🆕 生成快照
  createSnapshot('任务池完成', '共 ' + wizardTasks.length + ' 项任务');

  saveData();
  updateAll();
  switchStep(2);
  setStatus('步骤②已保存 → 进入③选将');
}
```

**关键改动**：
1. `steps['2']='done'` → `steps['1']='done'`
2. `steps['3']='active'` → `steps['2']='active'`
3. `step = 3` → `step = 2`
4. 默认值更新
5. 新增 camp_info 同步 + createSnapshot
6. `switchStep(3)` → `switchStep(2)`

## 操作 3C：修正 saveStep3()

**定位**：grep `function saveStep3()`，line 10394。

**操作**：替换为：

```javascript
function saveStep3() {
  // 🆕 修正键名
  if (!data.camp_progress) data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  data.camp_progress.steps['2'] = 'done';
  data.camp_progress.steps['3'] = 'active';
  data.camp_progress.step = 3;

  // 🆕 同步到 camp_info
  data.camp_info.current.team.staff_cards = JSON.parse(JSON.stringify(getStaffCards()));
  data.camp_info.current.updated_at = Clock.iso();
  data.camp_info.current.updated_by = (currentUser && currentUser.name) || '系统';

  // 🆕 生成快照
  createSnapshot('选将完成', getStaffCards().length + ' 位共建者');

  saveData();
  switchStep(3);
  setStatus('步骤③已保存 → 进入④启动');
}
```

**关键改动**：
1. `steps['3']='done'` → `steps['2']='done'`
2. `steps['4']='active'` → `steps['3']='active'`
3. `step = 4` → `step = 3`
4. 默认值更新
5. 新增 camp_info 同步 + createSnapshot
6. `switchStep(4)` → `switchStep(3)`

## 操作 3D：旧 saveStep4() 暂不改

**原因**：`saveStep4()` 会在 Round 5 整体重写。当前它仍然能工作（写入键 `'4'` 和 `'5'`），但导航条不会显示 Step ⑤。先不管，Round 5 一起解决。

---

# Round 4：角色升级逻辑修正

## 操作 4A：claimTasks 删除 builder 升级兜底代码

**定位**：grep `upgradeResult`，找到该变量出现的区域。

**操作**：Read 周围 30 行，找到类似如下的代码段并删除：

```javascript
// 同步更新系统角色（兜底逻辑）
// ... 约 10 行，包含 if (!upgradeResult.ok) { ... } 的 builder 直接赋值 ...
```

**确认删除后**：`claimTasks` 应该只做：
1. 创建 staff card
2. 更新 `data.members[name].title`
3. 调用 `saveData()` + `renderStep3()`

**注意**：如果 grep `upgradeResult` 找不到，可能是变量名不同。改为 grep `builder.*升级` 或搜索 `users\[name\]\.role = 'builder'` 来定位。

## 操作 4B：changeUserRole 加 skipAdventurerCheck

**定位**：grep `function changeUserRole`，line ~2353。

**操作**：找到 builder 升级的检查条件（约 line 2365-2370），在条件开头加入 `!opts.skipAdventurerCheck &&`。

改前（大致）：
```javascript
if (!wasAdventurer && oldRole !== 'adventurer') {
  return { ok: false, reason: '共建者需先有冒险者经历' };
}
```

改后：
```javascript
if (!opts.skipAdventurerCheck && !wasAdventurer && oldRole !== 'adventurer') {
  return { ok: false, reason: '共建者需先有冒险者经历' };
}
```

**注意**：变量名 `wasAdventurer` 和 `oldRole` 可能不同，需要 Read 确认实际代码。

---

# Round 5：重写 Step ④ + 删除 Step ⑤

## 操作 5A：注释旧 HTML + 新增四阶段 HTML

**定位**：grep `id="wiz-step4"`，找到旧 Step ④ 的 div。同样处理 `id="wiz-step5"`。

**操作**：
1. 在 `<!-- Step 4:` 前面加 `<!-- [Phase B: 已废弃]`
2. 在 Step ⑤ 末尾 `</div>` 后面加 `-->` 闭合注释
3. 在注释之后、Step ① 之前（或 Settings tab 末尾），插入新的 Step ④ HTML

**插入的新 HTML**：

```html
<!-- Step 4: Launch (Phase B 重写) -->
<div id="wiz-step4" class="wiz-step hidden">
  <!-- 4a: 审核 -->
  <div id="wiz4a-review" class="card" style="max-width:650px;margin:0 auto">
    <h3>🔍 审核 · 发包前确认</h3>
    <div id="wiz4aSummary" style="font-size:.85rem;line-height:1.8;margin:12px 0"></div>
    <div style="margin:12px 0">
      <label style="font-size:.85rem">审核人：
        <select id="wiz4aReviewer" style="padding:6px 10px;border:1px solid var(--border);border-radius:6px"></select>
      </label>
    </div>
    <div style="text-align:right">
      <button class="btn" onclick="switchStep(3)">← ③选将</button>
      <button class="btn pri" onclick="wizSubmitReview()">提交审核 →</button>
    </div>
  </div>

  <!-- 4b: 发包 -->
  <div id="wiz4b-deploy" class="card hidden" style="max-width:650px;margin:0 auto">
    <h3>📦 发包 · 推送到工作台</h3>
    <div id="wiz4bConfirm" style="font-size:.85rem;margin:12px 0;line-height:1.8"></div>
    <div style="text-align:right">
      <button class="btn" onclick="wizStep4Phase='review';renderStep4()">← 返回审核</button>
      <button class="btn pri" onclick="wizDeploy()">📦 确认发包</button>
    </div>
  </div>

  <!-- 4c: 开营仪式 -->
  <div id="wiz4c-ceremony" class="card hidden" style="max-width:650px;margin:0 auto;text-align:center">
    <h3>🎊 开营仪式</h3>
    <p style="color:var(--muted);font-size:.85rem">所有共建者将进入星光汇聚仪式</p>
    <button class="btn pri" onclick="wizStartCeremony()" style="font-size:1rem;padding:12px 32px;margin:16px 0">🎊 开始开营仪式</button>
  </div>

  <!-- 4d: 启动确认 -->
  <div id="wiz4d-launch" class="card hidden" style="max-width:650px;margin:0 auto;text-align:center">
    <h3>🏁 营队正式启动</h3>
    <div id="wiz4dConfirm" style="font-size:.85rem;margin:12px 0;line-height:1.8"></div>
    <button class="btn pri" onclick="wizLaunch()" style="font-size:1rem;padding:12px 32px">🏁 正式启动营队</button>
  </div>
</div>
```

## 操作 5B：重写 renderStep4()

**定位**：grep `function renderStep4()`，line ~10407。

**操作**：整体替换旧函数为：

```javascript
// ═══ Step ④：审核→发包→开营→启动 ═══
var wizStep4Phase = 'review'; // 'review' | 'deploy' | 'ceremony' | 'launch'

function renderStep4() {
  // 显示/隐藏四个子面板
  document.getElementById('wiz4a-review').classList.toggle('hidden', wizStep4Phase !== 'review');
  document.getElementById('wiz4b-deploy').classList.toggle('hidden', wizStep4Phase !== 'deploy');
  document.getElementById('wiz4c-ceremony').classList.toggle('hidden', wizStep4Phase !== 'ceremony');
  document.getElementById('wiz4d-launch').classList.toggle('hidden', wizStep4Phase !== 'launch');

  if (wizStep4Phase === 'review') {
    // 渲染审核摘要
    var cards = getStaffCards();
    var tasks = data.tasks || [];
    var ci = data.camp_info.current;
    var html = '<b>NT 总池：</b>' + (ci.budget.nt_total_pool || 0) + ' NT<br>' +
      '<b>预算：</b>' + (ci.budget.rmb_budget || 0) + ' 元<br>' +
      '<b>营期：</b>' + (ci.calendar.start_date || '未设') + ' · ' + (ci.calendar.duration_days || 0) + ' 天<br>' +
      '<b>任务：</b>' + (ci.tasks.pool.length || tasks.length) + ' 项<br>' +
      '<b>共建者：</b>' + cards.length + ' 人<br>';
    document.getElementById('wiz4aSummary').innerHTML = html;

    // 审核人下拉（排除创建人自己）
    var reviewer = document.getElementById('wiz4aReviewer');
    var users = getUsers();
    var creator = ci.identity.created_by;
    reviewer.innerHTML = '<option value="">-- 选择审核人 --</option>';
    Object.keys(users).forEach(function(name) {
      if (name !== creator && users[name]) {
        reviewer.innerHTML += '<option value="' + name + '">' + name + '</option>';
      }
    });
  }

  if (wizStep4Phase === 'deploy') {
    var cards2 = getStaffCards();
    var html2 = '<b>即将执行：</b><br>' +
      '✅ 审核已通过<br>' +
      '• ' + cards2.length + ' 位共建者 → 角色升级为共建者<br>' +
      '• 任务包推送到个人工作台<br>';
    cards2.forEach(function(c) {
      html2 += '• ' + c.name + '：' + (c.title || '未指定') + '<br>';
    });
    document.getElementById('wiz4bConfirm').innerHTML = html2;
  }

  if (wizStep4Phase === 'launch') {
    document.getElementById('wiz4dConfirm').innerHTML =
      '🎊 开营仪式完成<br>🔥🔥 火种已旺盛<br>' +
      '⚠️ 启动后原档锁定，后续修改需提交审核<br>' +
      '所有任务从草稿转为进行中';
  }
}
```

## 操作 5C：实现四个阶段的处理函数

**定位**：在 `renderStep4()` 之后插入。

**操作**：插入：

```javascript
function wizSubmitReview() {
  var reviewer = document.getElementById('wiz4aReviewer').value;
  if (!reviewer) { alert('请选择审核人'); return; }
  // 记录审核状态
  data.camp_info.current.governance.decisions.push({
    title: '发包审核', date: Clock.iso(), reviewer: reviewer, status: 'approved'
  });
  createSnapshot('审核通过', '审核人：' + reviewer);
  wizStep4Phase = 'deploy';
  renderStep4();
  setStatus('审核已提交 → ' + reviewer);
}

function wizDeploy() {
  if (!confirm('确认发包？共建者将收到任务通知。')) return;
  var cards = getStaffCards();
  // 批量升级共建者角色
  cards.forEach(function(c) {
    var result = changeUserRole(c.name, 'builder', { skipAdventurerCheck: true });
    // 即使返回非 ok 也继续（可能已经是 builder）
  });
  createSnapshot('发包确认', cards.length + '位共建者已就绪');
  saveData();
  wizStep4Phase = 'ceremony';
  renderStep4();
  setStatus('发包完成 · 等待开营仪式');
}

function wizStartCeremony() {
  var cards = getStaffCards();
  var members = cards.map(function(c) {
    var ntTotal = 0, taskCount = 0;
    if (c.task_names) { taskCount = c.task_names.length; }
    (data.tasks || []).forEach(function(t) {
      if (c.task_names && c.task_names.indexOf(t.name) !== -1) ntTotal += (t.points || 1);
    });
    return { name: c.name, taskCount: taskCount, nt: ntTotal };
  });

  openLaunchCeremony(members, function() {
    wizStep4Phase = 'launch';
    renderStep4();
  });
}

function wizLaunch() {
  if (!confirm('🏁 正式启动营队？\n\n启动后原档 v1 永久锁定，后续修改需审核。')) return;
  data.camp_info.current.identity.status = 'active';
  // 所有草稿任务 → active
  (data.tasks || []).forEach(function(t) {
    if (!t.status || t.status === '待认领' || t.status === 'draft') t.status = 'active';
  });
  data.camp_progress.steps['3'] = 'done';
  data.camp_progress.steps['4'] = 'done';
  data.camp_progress.step = 4;
  createSnapshot('营队启动', '🏁 正式启动');
  saveData();
  updateAll();
  alert('🎉 营队正式启动！\n\n所有任务已进入执行阶段。');
  exitWorkshop();
}
```

---

# Round 6：收尾清理

## 操作 6A：修正 resetWizard()

**定位**：grep `function resetWizard()`，line 10951。

**操作**：替换为：

```javascript
function resetWizard() {
  if (!confirm('重置向导将清除所有步骤进度。任务数据不会被删除。确定继续？')) return;
  data.camp_progress = { step: 0, steps: {'0':'active','1':'locked','2':'locked','3':'locked','4':'locked'} };
  wizardTasks = [];
  wizardDirty = false;
  wizStep4Phase = 'review';
  saveData();
  switchStep(0);
  setStatus('向导已重置');
}
```

## 操作 6B：更新 saveWizDraft() 支持 Step ⓪

**定位**：grep `function saveWizDraft()`，line 10961。

**操作**：在函数体中增加 Step ⓪ 的处理：

```javascript
function saveWizDraft() {
  if (wizardStep === 0) {
    // 暂存 Step ⓪ 表单数据
    var id = data.camp_info.current.identity;
    var el;
    el = document.getElementById('wizCampName'); if (el) id.name = el.value.trim();
    el = document.getElementById('wizCampPeriod'); if (el) id.period = el.value;
    el = document.getElementById('wizCampTheme'); if (el) id.description = el.value.trim();
    el = document.getElementById('wizCampTypeVal'); if (el) id.type = el.value;
  }
  if (wizardStep === 2) {
    mergeWizardToData(wizardTasks);
  }
  saveData();
  setStatus('已暂存步骤' + wizardStep);
}
```

## 操作 6C：删除旧 Step ⑤ 残留

**操作**：
1. grep `wiz-step5` 找到旧 HTML div，确认已经在 Round 5A 中被注释
2. grep `renderStep5` 和 `saveStep5` 和 `executeSync`，确认不再被调用
3. 如果导航或其他代码仍引用这些函数，替换为 no-op 或删除

---

# 附录 A：验收总清单

## Round 1
```javascript
typeof openIgniteCeremony   // 'function'
typeof openLaunchCeremony   // 'function'
typeof getStepFlame         // 'function'
document.getElementById('ceremonyIgnite')  // 非 null
```

## Round 2
```javascript
data.camp_progress.step     // 0
// 导航条显示 ⓪~④ + 火苗图标
// ⓪ 未完成时 ①~④ 灰色不可点
// 标签栏在进入 Settings 时收起
```

## Round 3
```javascript
// 完成 ⓪ → 保存 → 检查：
data.camp_info.current.identity.name  // 非空
data.camp_info.snapshots.length       // 1（v1 原档）

// 完成 ① → 保存 → 检查：
data.camp_info.current.budget.nt_total_pool  // 同步了
data.camp_info.current.calendar.start_date   // 同步了
data.camp_info.snapshots.length              // 2

// 火苗指示器应有变化（🕯️→🔥）

// 完成 ② ③ 同样验证
```

## Round 4
```javascript
// Step ③ 认领后：
getStaffCards()[0].name     // 成员名
getUsers()['成员名'].role  // 应≠'builder'（未立即升级）
```

## Round 5
```javascript
// Step ④ 四个子阶段依次展示：审核→发包→开营→启动
// 发包后：getUsers()['成员名'].role  // 'builder'
// 启动后：data.camp_info.current.identity.status  // 'active'
```

## Round 6
```javascript
resetWizard();              // 重置到 Step ⓪，不报错
saveWizDraft();             // 暂存不报错
```

---

# 附录 B：给下次 AI 的启动命令

```javascript
// 粘贴到浏览器控制台，确认前置条件全部通过
var checks = [
  ['Phase A: createSnapshot', typeof createSnapshot === 'function'],
  ['Phase A: getSnapshot', typeof getSnapshot === 'function'],
  ['Phase A: getChangelog', typeof getChangelog === 'function'],
  ['Phase A: camp_info', !!data.camp_info],
  ['R1: openIgniteCeremony', typeof openIgniteCeremony === 'function'],
  ['R1: openLaunchCeremony', typeof openLaunchCeremony === 'function'],
  ['R1: getStepFlame', typeof getStepFlame === 'function'],
  ['R2: enterWorkshop', typeof enterWorkshop === 'function'],
  ['R2: exitWorkshop', typeof exitWorkshop === 'function'],
  ['R2: camp_progress.step', data.camp_progress && data.camp_progress.step === 0],
  ['R3: checkStepFillLevel', typeof checkStepFillLevel === 'function'],
  ['R5: wizStep4Phase', typeof wizStep4Phase !== 'undefined'],
  ['R6: resetWizard', typeof resetWizard === 'function'],
];
var pass = 0, fail = 0;
checks.forEach(function(c) { if (c[1]) { pass++; console.log('✅', c[0]); } else { fail++; console.log('❌', c[0]); } });
console.log((pass + fail) + ' checks: ' + pass + ' pass, ' + fail + ' fail');
```
