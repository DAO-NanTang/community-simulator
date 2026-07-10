var fs = require("fs");
var lines = fs.readFileSync("dashboard.html", "utf8").split("\n");

// Find Step 1 area in HTML
var step1Start = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('<!-- Step 1: Framework -->') !== -1 && i < 2000) { step1Start = i; break; }
}
console.log("Step 1 HTML starts at line", step1Start + 1);

// The next line should be the wiz-step1 div
var step1Div = step1Start + 1;
console.log("wiz-step1 div at line", step1Div + 1, ":", lines[step1Div].substring(0, 60));

// Insert sub-navigation right after the wiz-step1 opening div
var subNav = [
'    <!-- Step 1 子导航 -->',
'    <div id="wizS1Nav" style="display:flex;gap:6px;justify-content:center;margin-bottom:14px;flex-wrap:wrap">',
'      <button class="btn pri" id="wizS1TabCal" onclick="wizS1Switch(\'cal\')" style="font-size:.8rem;padding:6px 16px">📅 日历</button>',
'      <button class="btn" id="wizS1TabFin" onclick="wizS1Switch(\'fin\')" style="font-size:.8rem;padding:6px 16px">💰 财政</button>',
'      <button class="btn" id="wizS1TabTeam" onclick="wizS1Switch(\'team\')" style="font-size:.8rem;padding:6px 16px">👥 团队</button>',
'    </div>',
'    <!-- 日历组 -->',
'    <div id="wizS1GroupCal">'
];
lines.splice(step1Div + 1, 0, ...subNav);
console.log("Inserted sub-nav after Step 1 div (" + subNav.length + " lines)");

// Now find the cards and wrap them in group divs
// After insertion, recount positions
// Card 1-4 are calendar group (营期时间, 每日安排, 日程编辑弹窗, 里程碑)
// Card 5-9 are finance group (收入, 支出, 鼓励池, 预测损益, 导出)
// Card 10 is team group (团队)

// Let me find the positions of the group boundaries by looking for specific markers
function findLineAfter(pattern, startLine) {
  for (var i = startLine; i < lines.length; i++) {
    if (pattern.test(lines[i])) return i;
  }
  return -1;
}

// For the calendar group end: find the closing </div> of the milestones card
// It's right before "<!-- ── 📥 收入参数 ── -->"
var incomeStart = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('📥 收入参数') !== -1 && i > step1Start && i < step1Start + 200) { incomeStart = i; break; }
}
console.log("Income section at line", incomeStart + 1);

// Close calendar group and open finance group before income
var groupClose = ['    </div>', '    <!-- 财政组 -->', '    <div id="wizS1GroupFin">'];
lines.splice(incomeStart, 0, ...groupClose);
console.log("Closed cal group, opened fin group");

// Find the end of finance group (before team card)
var teamStart = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('👥 团队') !== -1 && i > step1Start && i < step1Start + 300) { teamStart = i; break; }
}
console.log("Team section at line", teamStart + 1);

// Close finance group and open team group before team
var groupClose2 = ['    </div>', '    <!-- 团队组 -->', '    <div id="wizS1GroupTeam">'];
lines.splice(teamStart, 0, ...groupClose2);
console.log("Closed fin group, opened team group");

// Find the bottom buttons (save + next) and close team group before them
var saveBtn = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('saveStep1()') !== -1 && i > teamStart && i < teamStart + 60) { saveBtn = i; break; }
}
console.log("Save button at line", saveBtn + 1);

// The bottom buttons are in a div. Close team group before that div.
// Find the opening <div style="text-align:right... that contains the save button
var btnDiv = saveBtn;
while (btnDiv > teamStart && lines[btnDiv].indexOf('<div') === -1) btnDiv--;
console.log("Button container at line", btnDiv + 1, ":", lines[btnDiv].substring(0, 80));

lines.splice(btnDiv, 0, '    </div>');
console.log("Closed team group before buttons");

// Now add CSS for sub-nav active state and group visibility
// Find the workshop CSS section
var wsCssEnd = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('@keyframes wizCardIn') !== -1) { wsCssEnd = i; break; }
}
console.log("Workshop CSS ends at line", wsCssEnd + 1);

var s1css = [
'/* Step ① 子导航 */',
'#wizS1Nav button { transition: all .2s ease; }',
'#wizS1Nav button.active { background: var(--accent); color: #fff; }',
''
];
lines.splice(wsCssEnd + 2, 0, ...s1css);
console.log("Added Step 1 sub-nav CSS");

// Now add the JS function for sub-navigation toggling
// Find a good insertion point - after renderStep1 function definition
var renderS1Start = -1;
for (var i = 0; i < lines.length; i++) {
  if (lines[i].indexOf('// ── Step 1: Framework ──') !== -1 && i > 5000) { renderS1Start = i; break; }
}
console.log("renderStep1 JS at line", renderS1Start + 1);

// Insert before this line
var s1js = [
'// Step ① 子导航切换',
'var wizS1Tab = "cal";',
'function wizS1Switch(tab) {',
'  wizS1Tab = tab;',
'  var el;',
'  el = document.getElementById("wizS1GroupCal"); if (el) el.style.display = tab === "cal" ? "" : "none";',
'  el = document.getElementById("wizS1GroupFin"); if (el) el.style.display = tab === "fin" ? "" : "none";',
'  el = document.getElementById("wizS1GroupTeam"); if (el) el.style.display = tab === "team" ? "" : "none";',
'  // Update button styles',
'  ["Cal","Fin","Team"].forEach(function(t) {',
'    var btn = document.getElementById("wizS1Tab"+t);',
'    if (btn) { btn.classList.toggle("pri", tab === t.toLowerCase()); btn.classList.toggle("active", tab === t.toLowerCase()); }',
'  });',
'}',
''
];
lines.splice(renderS1Start, 0, ...s1js);
console.log("Added Step 1 sub-nav JS");

// Also need to call wizS1Switch at the end of renderStep1
// Find the end of renderStep1 function
var r1End = -1;
var braceCount = 0, started = false;
for (var i = renderS1Start + s1js.length + 1; i < lines.length; i++) {
  if (lines[i].indexOf('{') !== -1) { braceCount += (lines[i].match(/{/g) || []).length; started = true; }
  if (lines[i].indexOf('}') !== -1) { braceCount -= (lines[i].match(/}/g) || []).length; }
  if (started && braceCount === 0) { r1End = i; break; }
}
console.log("renderStep1 ends at line", r1End + 1, ":", lines[r1End]);

// Add wizS1Switch call before the closing }
lines.splice(r1End, 0, '  wizS1Switch(wizS1Tab || "cal");');
console.log("Added wizS1Switch call at end of renderStep1");

fs.writeFileSync("dashboard.html", lines.join("\n"));
console.log("\nDone. Lines:", lines.length);
