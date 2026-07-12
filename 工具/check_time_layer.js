#!/usr/bin/env node
/**
 * 时间层护栏：检查 dashboard.html 是否有"裸"时间调用绕过 Clock。
 * 规则：
 *   - 业务代码禁止裸 new Date() / Date.now()（带参 new Date('...') 允许）。
 *   - Clock 模块内部允许（它就是唯一时间源）。
 * 用法：node 工具/check_time_layer.js  [文件路径]
 * 退出码：0=通过，1=发现违规（供 pre-commit 钩子拦截提交）。
 */
var fs = require('fs');
var path = process.argv[2] || '工具/dashboard.html';

var src;
try { src = fs.readFileSync(path, 'utf8'); }
catch (e) { console.error('[时间层护栏] 读不到文件: ' + path); process.exit(1); }

// 1) Clock 模块必须存在（旧副本覆盖会导致它消失 → 直接失败）
if (src.indexOf('var Clock = (function') === -1) {
  console.error('[时间层护栏] ❌ 未找到 Clock 模块！很可能被旧副本覆盖了。');
  process.exit(1);
}

// 2) 抠掉 Clock 模块本身（其内部 Date.now/new Date 是合法的唯一时间源）
var clean = src.replace(/var Clock = \(function \(\) \{[\s\S]*?\}\)\(\);/, '');
// 3) 去掉注释，避免注释里的字样误报
clean = clean.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');

// 4) 统计裸调用并定位行号
var offenders = [];
var lines = clean.split('\n');
for (var i = 0; i < lines.length; i++) {
  var ln = lines[i];
  if (/new Date\(\)/.test(ln) || /Date\.now\(\)/.test(ln)) {
    offenders.push((i + 1) + ': ' + ln.trim().slice(0, 80));
  }
}

if (offenders.length === 0) {
  console.log('[时间层护栏] ✅ 通过：无裸 new Date()/Date.now()，时间读取全部走 Clock。');
  process.exit(0);
} else {
  console.error('[时间层护栏] ❌ 发现 ' + offenders.length + ' 处裸时间调用（应改用 Clock.today()/iso()/hour()/ms() 等）：');
  offenders.slice(0, 30).forEach(function (o) { console.error('   ' + o); });
  if (offenders.length > 30) console.error('   … 还有 ' + (offenders.length - 30) + ' 处');
  console.error('修复：把无参 new Date()/Date.now() 换成 Clock.*；带参 new Date(\'...\') 不用动。');
  process.exit(1);
}