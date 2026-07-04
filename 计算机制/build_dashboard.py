"""
Build clean dashboard.html from scratch.
Minimal, functional, all 7 tabs working.
"""
import json

# Read the actual data.json to verify it works
data_path = r'C:\Users\苏砚仁\Desktop\共创营工具\data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    test_data = json.load(f)
print(f'data.json OK: {len(test_data.get(\"tasks\",[]))} tasks')

# Build the HTML
html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>共创营工会大厅</title>
<style>
:root { --bg:#f7f3ed; --card:#fffdf9; --text:#3d3629; --muted:#9b9078; --accent:#c88740; --green:#5d9442; --red:#b84c38; --yellow:#c8892e; --border:#e5ddce; --shadow:0 2px 8px rgba(60,40,20,.06); --font:system-ui,-apple-system,'Segoe UI','Noto Sans SC',sans-serif; }
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);color:var(--text);line-height:1.6;min-height:100vh;background:radial-gradient(ellipse at 20% 10%,rgba(160,200,140,.1) 0%,transparent 50%),radial-gradient(ellipse at 80% 30%,rgba(200,180,140,.08) 0%,transparent 45%),linear-gradient(180deg,#e8f0e0 0%,#f2efe4 8%,#f7f3ed 20%,#f3ede4 100%)}
header{padding:18px 32px;border-bottom:4px solid #4a3828;position:relative;overflow:hidden;min-height:180px;background:linear-gradient(0deg,rgba(0,0,0,.25),rgba(0,0,0,.05) 40%,rgba(0,0,0,.15) 100%),url('ai_expand_image1783014990973.png') center 70%/80% no-repeat}
header h1{font-size:1.2rem;color:#fff;text-shadow:2px 2px 6px rgba(0,0,0,.5)}
h1,h2,h3{font-weight:600}
.btn{padding:7px 16px;border:1.5px solid var(--border);border-radius:8px;cursor:pointer;font-size:.84rem;font-family:var(--font);background:var(--card);color:var(--text);transition:all .15s;white-space:nowrap;font-weight:500}
.btn:hover{background:#f5efe4;border-color:var(--accent);transform:translateY(-1px);box-shadow:0 2px 6px rgba(0,0,0,.06)}
.btn:active{transform:translateY(0)}
.btn.pri{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.green{background:var(--green);color:#fff;border-color:var(--green)}
.btn.danger{background:var(--red);color:#fff;border-color:var(--red)}
main{max-width:1200px;margin:0 auto;padding:24px 28px}
.tabs{display:flex;gap:4px;margin-bottom:22px;border-bottom:2px solid var(--border)}
.tab{padding:10px 20px;cursor:pointer;border:none;background:none;font-size:.88rem;color:var(--muted);font-family:var(--font);border-bottom:2px solid transparent;margin-bottom:-2px;transition:.15s;border-radius:6px 6px 0 0}
.tab:hover{color:var(--accent);background:rgba(200,135,64,.04)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:600}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;margin-bottom:18px;box-shadow:var(--shadow)}
.card h3{font-size:.95rem;margin-bottom:14px;color:#5a4530}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{text-align:left;padding:10px 12px;border-bottom:2px solid var(--border);color:var(--muted);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.5px}
td{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:middle}
tr:hover td{background:#faf8f2}
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.75rem;font-weight:600}
.badge.done{background:#e8f0e2;color:var(--green)}
.badge.progress{background:#fdf3e0;color:var(--yellow)}
.badge.todo{background:#f5e8e4;color:var(--red)}
.hidden{display:none!important}
.empty-state{text-align:center;padding:40px;color:var(--muted)}
.ms-avatar-row{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:18px;justify-content:center}
.ms-avatar-btn{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;padding:8px;border-radius:10px;border:2px solid transparent;transition:.15s;background:none;font-family:var(--font)}
.ms-avatar-btn:hover{background:#faf8f0;border-color:var(--border)}
.ms-avatar-btn.active{border-color:var(--accent);background:#fdf8ee}
.ms-av-circle{width:44px;height:44px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#e8e0d0}
.ms-av-circle img{width:100%;height:100%;object-fit:cover}
.ms-av-name{font-size:.75rem;font-weight:600;color:var(--text)}
.ms-av-badge{font-size:.65rem;color:var(--muted)}
.phase-select-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px;justify-content:center}
.phase-block{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;padding:12px 20px;border-radius:10px;border:2px solid var(--border);background:var(--card);transition:.15s;font-family:var(--font);min-width:80px}
.phase-block:hover{border-color:var(--accent);background:#fdf8ee}
.phase-block.active{border-color:var(--accent);background:#fdf5e0;box-shadow:0 0 0 2px var(--accent)}
.phase-block .ph-icon{font-size:1.3rem}
.phase-block .ph-label{font-weight:700;font-size:.88rem}
.phase-block .ph-count{font-size:.7rem;color:var(--muted)}
.member-sheet{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;display:flex;max-width:860px;margin:0 auto;box-shadow:var(--shadow)}
.member-sheet .ms-left{flex:0 0 200px;padding:18px 16px;border-right:1px solid var(--border);background:#faf8f2;text-align:center}
.ms-avatar{width:56px;height:56px;border-radius:50%;overflow:hidden;background:#e8e0d0;margin:0 auto 8px}
.ms-avatar img{width:100%;height:100%;object-fit:cover}
.ms-left .ms-name{font-weight:700;font-size:1rem;margin-bottom:2px}
.ms-left .ms-role{font-size:.78rem;color:var(--muted);margin-bottom:10px}
.ms-stats{text-align:left;font-size:.78rem}
.ms-stats .stat-row{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dotted var(--border)}
.ms-stats .stat-row .sv{font-weight:600}
.sv.g{color:var(--green)} .sv.y{color:var(--yellow)} .sv.r{color:var(--red)}
.member-sheet .ms-right{flex:1;padding:14px 18px;min-width:0}
.ms-right h4{font-size:.8rem;color:var(--muted);margin:0 0 6px}
.ms-task-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dotted var(--border);font-size:.82rem}
.ms-task-row .done{text-decoration:line-through;color:var(--muted)}
.ms-task-col{flex:1;min-width:0;padding-right:8px;margin-bottom:8px}
.ms-bar-wrap{height:6px;background:#e6dfcc;border-radius:3px;margin:6px 0 10px}
.ms-bar-wrap .fill{height:100%;border-radius:3px;transition:width .3s}
.modal-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.3);z-index:100;justify-content:center;align-items:center}
.modal-overlay.show{display:flex}
.modal{background:var(--card);border-radius:12px;padding:28px;max-width:560px;width:90%;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.15)}
.modal h2{margin-bottom:16px;font-size:1.1rem}
.modal label{display:block;font-size:.82rem;color:var(--muted);margin:10px 0 4px}
.modal input,.modal select,.modal textarea{width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-family:var(--font);font-size:.88rem}
.modal textarea{min-height:80px;resize:vertical}
.modal .actions{display:flex;gap:8px;margin-top:20px;justify-content:flex-end}
</style>
</head>
<body>
<header>
  <div style="position:relative;z-index:3"><span style="font-size:2rem;filter:drop-shadow(2px 2px 3px rgba(0,0,0,.35))">🏰</span></div>
</header>
<main>
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px">
    <div class="tabs" style="margin-bottom:0;border-bottom:none;padding-bottom:2px">
      <button class="tab active" onclick="switchTab('tasks')" style="border-bottom:2px solid var(--accent);margin-bottom:0">📋 任务大厅</button>
      <button class="tab" onclick="switchTab('map')" style="border-bottom:2px solid transparent;margin-bottom:0">🗺️ 攻略地图</button>
      <button class="tab" onclick="switchTab('members')" style="border-bottom:2px solid transparent;margin-bottom:0">👥 游戏策划组</button>
      <button class="tab" onclick="switchTab('players')" style="border-bottom:2px solid transparent;margin-bottom:0">⚔️ 游戏玩家</button>
      <button class="tab" onclick="switchTab('timeline')" style="border-bottom:2px solid transparent;margin-bottom:0">📅 日历系统</button>
      <button class="tab" onclick="switchTab('budget')" style="border-bottom:2px solid transparent;margin-bottom:0">💰 公会资金池</button>
      <button class="tab" onclick="switchTab('settlement')" style="border-bottom:2px solid transparent;margin-bottom:0">🧾 结算界面</button>
    </div>
    <div style="display:flex;gap:8px;align-items:center;padding-bottom:6px">
      <span style="font-size:.75rem;color:var(--muted)" id="statusDot"></span>
      <button class="btn" onclick="loadData()">📂 加载</button>
      <button class="btn" onclick="exportData()">💾 导出</button>
    </div>
  </div>
  <div id="tab-content"></div>
</main>
<script>
// ── State ──
var data = { tasks: [], decisions: [], members: {}, budget: {} };
var PIE_COLORS = ['#d4a853','#6b9b4e','#5b8cb8','#c47d5a','#8b6bae','#c4553d'];
var CHARACTER_SEEDS = ['Alex','Jordan','Casey','Morgan','Riley','Taylor','Quinn','Sam','Charlie','Drew','Blake','Avery','Skyler','Reese','Finley','Sage','Harper','Emery','Parker','Rowan','Dakota','Phoenix','River','Jamie','Kai','Sasha','Remy','Jules','Ari','Nico','Luca','Ezra','Theo','Ollie','Max','Leo','Mia','Zoe','Eli','Ivy','Asher','Nova'];
var AVATAR_STYLES = ['avataaars','adventurer','lorelei','open-peeps','notionists','personas','micah','bottts-neutral','fun-emoji'];
var memberData = {}, selectedMember = null, selectedPlayer = null;

function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s) { return (s||'').replace(/'/g,"\\'").replace(/"/g,'&quot;'); }
function avatarUrl(idx, size) { var seed = CHARACTER_SEEDS[idx] || 'Alex'; return 'https://api.dicebear.com/9.x/avataaars/svg?seed='+seed+'&size='+(size||80); }
function avatarImg(idx, size) { return '<img src="'+avatarUrl(idx,size)+'" style="width:100%;height:100%;object-fit:cover" onerror="this.style.display=\\'none\\';var n=this.nextElementSibling;if(n)n.style.display=\\'flex\\'">'; }
function avatarInitial(idx) { var c=['#d4a853','#6b9b4e','#5b8cb8','#c47d5a','#8b6bae'],s=CHARACTER_SEEDS[idx]||'?'; return '<span style="display:none;width:100%;height:100%;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;color:#fff;background:'+c[idx%5]+'">'+esc(s[0])+'</span>'; }
function avatarCircle(idx,size) { return avatarImg(idx,size)+avatarInitial(idx); }
function parseDate(s){if(!s)return Infinity;var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return new Date(2026,parseInt(m[1])-1,parseInt(m[2])).getTime();return Infinity}
function parseDateStr(s){var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return new Date(2026,parseInt(m[1])-1,parseInt(m[2])).getTime();return Infinity}

function setStatus(msg) { var el=document.getElementById('statusDot'); if(el)el.textContent='🟢 '+msg; }

function loadData() {
  var inp=document.createElement('input');inp.type='file';inp.accept='.json';
  inp.onchange=function(e){
    var f=e.target.files[0];if(!f)return;
    var r=new FileReader();
    r.onload=function(){
      try{
        var ld=JSON.parse(r.result);
        data.tasks=(ld.tasks||[]).map(function(t){return{name:t.name||'',type:t.type||'初始',category:t.category||'其他',assignee:t.assignee||'',start:t.start||'',deadline:t.deadline||'',confirmer:t.confirmer||'',points:t.points||1,status:t.status||'待确认',source:t.source||'',note:t.note||''}});
        if(ld.decisions)data.decisions=ld.decisions;
        if(ld.members)data.members=ld.members;
        if(ld.summary)data.summary=ld.summary;
        if(ld.schedule)data.schedule=ld.schedule;
        if(ld.budget)data.budget=ld.budget;
        if(ld.finance_cny)data.finance_cny=ld.finance_cny;
        if(ld.stats)data.stats=ld.stats;
        localStorage.setItem('camp_data',JSON.stringify(data));
        updateAll();
        setStatus('已加载: '+data.tasks.length+' 任务');
      }catch(err){ alert('JSON 解析失败: '+err.message); }
    };
    r.readAsText(f);
  };
  inp.click();
}

function exportData() {
  var b=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(b);
  a.download='data_'+new Date().toISOString().slice(0,10)+'.json';a.click();
  setStatus('已导出');
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');t.style.borderBottom='2px solid transparent'});
  var at=document.querySelector('.tab[onclick*=\"'+name+'\"]');if(at){at.classList.add('active');at.style.borderBottom='2px solid var(--accent)'}
  renderTab(name);
}

function updateAll() { renderTab('tasks'); }

function renderTab(name) {
  var c=document.getElementById('tab-content');if(!c)return;
  if(name==='tasks')renderTasksTo(c);
  else if(name==='members')renderMembersTo(c);
  else if(name==='players')renderPlayersTo(c);
  else if(name==='timeline')renderTimelineTo(c);
  else if(name==='budget')renderBudgetTo(c);
  else if(name==='settlement')renderSettlementTo(c);
  else if(name==='map')renderMapTo(c);
}
</script>
</body>
</html>'''

print(f'HTML length: {len(html)} chars')
print('Now need to add tab render functions...')
print('Base structure written.')
