# Write complete working dashboard.html
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>共创营工会大厅</title>
<style>
:root{--bg:#f7f3ed;--card:#fffdf9;--text:#3d3629;--muted:#9b9078;--accent:#c88740;--green:#5d9442;--red:#b84c38;--yellow:#c8892e;--border:#e5ddce;--shadow:0 2px 8px rgba(60,40,20,.06);--font:system-ui,-apple-system,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);color:var(--text);line-height:1.6;min-height:100vh;background:linear-gradient(180deg,#e8f0e0 0%,#f2efe4 8%,#f7f3ed 20%,#f3ede4 100%)}
header{padding:18px 32px;border-bottom:4px solid #4a3828;position:relative;overflow:hidden;min-height:180px;background:linear-gradient(0deg,rgba(0,0,0,.25),rgba(0,0,0,.05) 40%,rgba(0,0,0,.15)),url('ai_expand_image1783014990973.png') center 70%/80% no-repeat}
.btn{padding:7px 16px;border:1.5px solid var(--border);border-radius:8px;cursor:pointer;font-size:.84rem;font-family:var(--font);background:var(--card);color:var(--text);transition:.15s;white-space:nowrap;font-weight:500}
.btn:hover{background:#f5efe4;border-color:var(--accent)}
.btn.pri{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.green{background:var(--green);color:#fff;border-color:var(--green)}
main{max-width:1200px;margin:0 auto;padding:24px 28px}
.tabs{display:flex;gap:4px;margin-bottom:22px;border-bottom:2px solid var(--border)}
.tab{padding:10px 20px;cursor:pointer;border:none;background:none;font-size:.88rem;color:var(--muted);font-family:var(--font);border-bottom:2px solid transparent;margin-bottom:-2px;transition:.15s}
.tab:hover{color:var(--accent)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:600}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;margin-bottom:18px;box-shadow:var(--shadow)}
.card h3{font-size:.95rem;margin-bottom:14px;color:#5a4530}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{text-align:left;padding:10px 12px;border-bottom:2px solid var(--border);color:var(--muted);font-weight:600;font-size:.78rem}
td{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:middle}
tr:hover td{background:#faf8f2}
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.75rem;font-weight:600}
.badge.done{background:#e8f0e2;color:var(--green)}.badge.progress{background:#fdf3e0;color:var(--yellow)}.badge.todo{background:#f5e8e4;color:var(--red)}
.hidden{display:none!important}
.empty-state{text-align:center;padding:40px;color:var(--muted)}
.ms-avatar-row{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:18px;justify-content:center}
.ms-avatar-btn{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;padding:8px;border-radius:10px;border:2px solid transparent;transition:.15s;background:none}
.ms-avatar-btn:hover{background:#faf8f0;border-color:var(--border)}.ms-avatar-btn.active{border-color:var(--accent);background:#fdf8ee}
.ms-av-circle{width:44px;height:44px;border-radius:50%;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#e8e0d0}
.ms-av-circle img{width:100%;height:100%;object-fit:cover}
.ms-av-name{font-size:.75rem;font-weight:600}.ms-av-badge{font-size:.65rem;color:var(--muted)}
.phase-select-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px;justify-content:center}
.phase-block{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;padding:12px 20px;border-radius:10px;border:2px solid var(--border);background:var(--card);transition:.15s;min-width:80px}
.phase-block:hover{border-color:var(--accent)}.phase-block.active{border-color:var(--accent);background:#fdf5e0}
.phase-block .ph-icon{font-size:1.3rem}.phase-block .ph-label{font-weight:700;font-size:.88rem}.phase-block .ph-count{font-size:.7rem;color:var(--muted)}
</style></head>
<body>
<header><div style="position:relative;z-index:3;font-size:2rem">🏰</div></header>
<main>
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px">
<div class="tabs" style="margin-bottom:0;border-bottom:none;padding-bottom:2px">
<button class="tab active" id="btn-tasks" onclick="switchTab('tasks')">📋 任务大厅</button>
<button class="tab" id="btn-map" onclick="switchTab('map')">🗺️ 攻略地图</button>
<button class="tab" id="btn-members" onclick="switchTab('members')">👥 游戏策划组</button>
<button class="tab" id="btn-players" onclick="switchTab('players')">⚔️ 游戏玩家</button>
<button class="tab" id="btn-timeline" onclick="switchTab('timeline')">📅 日历系统</button>
<button class="tab" id="btn-budget" onclick="switchTab('budget')">💰 公会资金池</button>
<button class="tab" id="btn-settlement" onclick="switchTab('settlement')">🧾 结算界面</button>
</div>
<div style="display:flex;gap:8px;align-items:center">
<span style="font-size:.75rem;color:var(--muted)" id="statusDot"></span>
<button class="btn" onclick="loadData()">📂 加载</button>
<button class="btn" onclick="exportData()">💾 导出</button>
</div>
</div>
<input type="file" id="fileInput" accept=".json" style="display:none" onchange="handleFileSelect(event)">
<div id="view"><div class="empty-state">📂 请先加载 data.json</div></div>
</main>
<script>
var D={tasks:[],members:{},budget:{},finance_cny:{},schedule:{}};
function esc(s){return(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
function escAttr(s){return(s||"").replace(/'/g,"\\'").replace(/"/g,"&quot;")}
function parseDate(s){if(!s)return Infinity;var m=s.match(/(\\d+)\\D+(\\d+)/);if(m)return new Date(2026,parseInt(m[1])-1,parseInt(m[2])).getTime();return Infinity}
var AVSEEDS=["Alex","Jordan","Casey","Morgan","Riley","Taylor","Quinn","Sam","Charlie","Drew","Blake","Avery","Skyler","Reese","Finley","Sage","Harper","Emery","Parker","Rowan"];
function avUrl(i,sz){return"https://api.dicebear.com/9.x/avataaars/svg?seed="+(AVSEEDS[i]||"Alex")+"&size="+(sz||80)}
function avImg(i,sz){return'<img src="'+avUrl(i,sz)+'" style="width:100%;height:100%;object-fit:cover" onerror="this.style.display=\\'none\\';var n=this.nextElementSibling;if(n)n.style.display=\\'flex\\'">'}
var AVC=["#d4a853","#6b9b4e","#5b8cb8","#c47d5a","#8b6bae"];
function avInit(i){var s=AVSEEDS[i]||"?";return'<span style="display:none;width:100%;height:100%;align-items:center;justify-content:center;font-size:1.2rem;font-weight:700;color:#fff;background:'+AVC[i%5]+'">'+esc(s[0])+'</span>'}
function avCircle(i,sz){return avImg(i,sz)+avInit(i)}
function setStatus(m){var e=document.getElementById("statusDot");if(e)e.textContent="🟢 "+m}
function loadOrCached(){var s=localStorage.getItem("camp_data");if(s){try{D=JSON.parse(s);switchTab("tasks");setStatus("已加载缓存 "+D.tasks.length+" 任务")}catch(e){}}}

function loadData(){document.getElementById("fileInput").click()}
function handleFileSelect(e){
 var f=e.target.files[0];if(!f)return;
 var r=new FileReader();
 r.onload=function(ev){
  try{
   var ld=JSON.parse(ev.target.result);
   D.tasks=(ld.tasks||[]).map(function(t){return{name:t.name||"",type:t.type||"",category:t.category||"",assignee:t.assignee||"",start:t.start||"",deadline:t.deadline||"",confirmer:t.confirmer||"",points:t.points||1,status:t.status||"待确认",source:t.source||"",note:t.note||""}});
   if(ld.members)D.members=ld.members;
   if(ld.budget)D.budget=ld.budget;
   if(ld.finance_cny)D.finance_cny=ld.finance_cny;
   if(ld.schedule)D.schedule=ld.schedule;
   if(ld.summary)D.summary=ld.summary;
   if(ld.stats)D.stats=ld.stats;
   localStorage.setItem("camp_data",JSON.stringify(D));
   switchTab("tasks");setStatus("已加载 "+D.tasks.length+" 任务");
  }catch(err){alert("JSON解析失败: "+err.message)}
 };
 r.readAsText(f);
}
function exportData(){
 var b=new Blob([JSON.stringify(D,null,2)],{type:"application/json"});
 var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="data.json";a.click();setStatus("已导出")
}
function switchTab(name){
 ["tasks","map","members","players","timeline","budget","settlement"].forEach(function(n){
  var b=document.getElementById("btn-"+n);if(b){b.classList.toggle("active",n===name);b.style.borderBottom=n===name?"2px solid var(--accent)":"2px solid transparent"}
 });
 var v=document.getElementById("view");if(!v)return;
 if(name==="tasks")renderTasks(v);
 else if(name==="members")renderMembers(v);
 else if(name==="players")renderPlayers(v);
 else if(name==="timeline")renderTimeline(v);
 else if(name==="budget")renderBudget(v);
 else if(name==="settlement")renderSettlement(v);
 else if(name==="map")renderMap(v);
}

/* ====== TASKS ====== */
function renderTasks(v){
 var tasks=D.tasks||[];
 var ph={筹备期:[],营期:[],营后:[],改进项:[]};
 tasks.forEach(function(t){
  var n=(t.name||"")+(t.note||"");var p="营期";
  if(/改进|缺失/.test(n))p="改进项";
  else if(/结项|结算|复盘|报告/.test(n))p="营后";
  else if(/筹备|预算|资助|提案|分工|合伙人|里程碑|规则|动员会/.test(n))p="筹备期";
  ph[p].push(t)
 });
 var h='<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><h3 style="margin:0">任务清单</h3><button class="btn green" onclick="addTask()">＋ 新增</button></div>';
 var phases=["筹备期","营期","营后","改进项"],icons={筹备期:"📝",营期:"🎨",营后:"📊",改进项:"💡"};
 h+='<div class="phase-select-row">';
 phases.forEach(function(p){h+='<button class="phase-block active" onclick="filterPhase(\''+p+'\')"><span class="ph-icon">'+icons[p]+'</span><span class="ph-label">'+p+'</span><span class="ph-count">'+ph[p].length+'项</span></button>'});
 h+='</div><div style="overflow-x:auto"><table><thead><tr><th>任务</th><th>负责人</th><th>截止</th><th>状态</th><th></th></tr></thead><tbody>';
 var all=ph["筹备期"].concat(ph["营期"]).concat(ph["营后"]).concat(ph["改进项"]);
 all.forEach(function(t,i){
  var idx=D.tasks.indexOf(t);
  var sc=t.status==="已完成"||t.status==="已确认"?"done":(t.status==="进行中"?"progress":"todo");
  var sl=t.status==="已确定"?"已确定":t.status;
  h+='<tr><td><strong>'+esc(t.name)+'</strong></td><td>'+esc(t.assignee)+'</td><td>'+esc(t.deadline)+'</td><td><span class="badge '+sc+'">'+sl+'</span></td><td><button class="btn" style="padding:2px 6px;font-size:.7rem" onclick="editTask('+idx+')">✎</button></td></tr>'
 });
 h+='</tbody></table></div></div>';
 v.innerHTML=h
}
function addTask(){
 var n=prompt("任务名称:");if(!n)return;
 var a=prompt("负责人:")||"";
 D.tasks.push({name:n,type:"初始",category:"其他",assignee:a,start:"",deadline:"",confirmer:"",points:1,status:"待开始",source:"",note:""});
 localStorage.setItem("camp_data",JSON.stringify(D));switchTab("tasks")
}
function editTask(i){
 var t=D.tasks[i];if(!t)return;
 t.name=prompt("名称:",t.name)||t.name;
 t.assignee=prompt("负责人:",t.assignee)||t.assignee;
 t.deadline=prompt("截止:",t.deadline)||t.deadline;
 t.status=prompt("状态(待开始/进行中/已完成/已确认):",t.status)||t.status;
 localStorage.setItem("camp_data",JSON.stringify(D));switchTab("tasks")
}
function filterPhase(p){switchTab("tasks")}

/* ====== MEMBERS ====== */
function renderMembers(v){
 var staff=["砚仁","朝林","小红","若曦","淑惠","跳大爷"];
 var md={};
 (D.tasks||[]).forEach(function(t){var n=t.assignee||"";if(!staff.some(function(s){return n.includes(s)}))return;if(!md[n])md[n]={tsk:[],pts:0,done:0,act:0,td:0};md[n].tsk.push(t);md[n].pts+=t.points||1;if(t.status==="已完成"||t.status==="已确认")md[n].done++;else if(t.status==="进行中")md[n].act++;else md[n].td++});
 var sd=Object.entries(md).sort(function(a,b){return b[1].tsk.length-a[1].tsk.length});
 var h='<div class="card"><h3>🧙 游戏策划组</h3><div class="ms-avatar-row">';
 sd.forEach(function(e){var n=e[0],m=e[1],mi=D.members[n]||{},si=mi.avatar_seed!==undefined?mi.avatar_seed:0;
  h+='<div class="ms-avatar-btn" onclick="showMDetail(\''+escAttr(n)+'\')"><div class="ms-av-circle">'+avCircle(si,64)+'</div><div class="ms-av-name">'+esc(n)+'</div><div class="ms-av-badge">'+m.tsk.length+'任务</div></div>'});
 h+='</div><div id="memberDetail"></div></div>';v.innerHTML=h
}
function showMDetail(name){
 var ts=D.tasks.filter(function(t){return t.assignee===name});
 var dn=ts.filter(function(t){return t.status==="已完成"||t.status==="已确认"});
 var ac=ts.filter(function(t){return t.status==="进行中"});
 var td=ts.filter(function(t){return t.status!=="已完成"&&t.status!=="已确认"&&t.status!=="进行中"});
 var dd=document.getElementById("memberDetail");if(!dd)return;
 var mi=D.members[name]||{},si=mi.avatar_seed!==undefined?mi.avatar_seed:0,pc=ts.length>0?Math.round(dn.length/ts.length*100):0;
 dd.innerHTML='<div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;display:flex;gap:20px;max-width:700px;margin:0 auto"><div style="text-align:center;min-width:140px"><div class="ms-av-circle" style="width:56px;height:56px;margin:0 auto 6px">'+avCircle(si,100)+'</div><div style="font-weight:700">'+esc(name)+'</div><div style="font-size:.8rem">✅'+dn.length+' 🔄'+ac.length+' ⬜'+td.length+'</div><div style="height:4px;background:#e6dfcc;border-radius:2px;margin:6px 0"><div style="height:100%;width:'+pc+'%;background:var(--green);border-radius:2px"></div></div><div style="font-size:.7rem;color:var(--muted)">'+pc+'%</div></div><div style="flex:1">'+
  (td.length?'<div style="margin-bottom:8px"><strong>⬜ 待开始 ('+td.length+')</strong>'+td.map(function(t){return'<div style="font-size:.8rem;padding:2px 0">'+esc(t.name)+'</div>'}).join("")+'</div>':'')+
  (ac.length?'<div style="margin-bottom:8px"><strong>🔄 进行中 ('+ac.length+')</strong>'+ac.map(function(t){return'<div style="font-size:.8rem;padding:2px 0">'+esc(t.name)+'</div>'}).join("")+'</div>':'')+
  (dn.length?'<div><strong>✅ 已完成 ('+dn.length+')</strong>'+dn.map(function(t){return'<div style="font-size:.8rem;padding:2px 0;text-decoration:line-through;color:var(--muted)">'+esc(t.name)+'</div>'}).join("")+'</div>':'')+
  '</div></div>'
}

/* ====== PLAYERS ====== */
function renderPlayers(v){
 var staff=["砚仁","朝林","小红","若曦","淑惠","跳大爷"];
 var md={};
 (D.tasks||[]).forEach(function(t){var n=t.assignee||"";if(staff.some(function(s){return n.includes(s)}))return;if(!md[n])md[n]={tsk:[],pts:0,done:0};md[n].tsk.push(t);md[n].pts+=t.points||1;if(t.status==="已完成"||t.status==="已确认")md[n].done++});
 var sd=Object.entries(md).sort(function(a,b){return b[1].tsk.length-a[1].tsk.length});
 var h='<div class="card"><h3>⚔️ 游戏玩家</h3><div class="ms-avatar-row">';
 sd.forEach(function(e){var n=e[0],m=e[1],mi=D.members[n]||{},si=mi.avatar_seed!==undefined?mi.avatar_seed:Math.floor(Math.random()*20);
  h+='<div class="ms-avatar-btn" onclick="showPDetail(\''+escAttr(n)+'\')"><div class="ms-av-circle">'+avCircle(si,64)+'</div><div class="ms-av-name">'+esc(n)+'</div><div class="ms-av-badge">'+m.tsk.length+'任务</div></div>'});
 h+='</div><div id="playerDetail"></div></div>';v.innerHTML=h
}
function showPDetail(name){
 var ts=D.tasks.filter(function(t){return t.assignee===name});
 var dn=ts.filter(function(t){return t.status==="已完成"||t.status==="已确认"});
 var dd=document.getElementById("playerDetail");if(!dd)return;
 var mi=D.members[name]||{},si=mi.avatar_seed!==undefined?mi.avatar_seed:0,pc=ts.length>0?Math.round(dn.length/ts.length*100):0;
 dd.innerHTML='<div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;max-width:500px;margin:0 auto;text-align:center"><div class="ms-av-circle" style="width:56px;height:56px;margin:0 auto 8px">'+avCircle(si,100)+'</div><div style="font-weight:700">'+esc(name)+'</div><div style="margin:8px 0">'+dn.length+'/'+ts.length+' 完成 ('+pc+'%)</div><div style="height:6px;background:#e6dfcc;border-radius:3px"><div style="height:100%;width:'+pc+'%;background:var(--green);border-radius:3px"></div></div></div>'
}

/* ====== MAP ====== */
function renderMap(v){
 var tasks=D.tasks||[],today=new Date().toISOString().slice(5,10).replace("-","/");
 var active=tasks.filter(function(t){if(!t.deadline)return false;var d=parseDate(t.deadline);return d>=parseDate(today)||/每日/.test(t.deadline)});
 var h='<div class="card"><h3>🗺️ 攻略地图 · '+today+'</h3>';
 h+='<div style="margin-bottom:12px;display:flex;flex-wrap:wrap;gap:8px">';
 [{d:"06/06",n:"开营日",i:"🏕️"},{d:"06/09",n:"动员会",i:"📢"},{d:"06/22",n:"村展",i:"🎨"},{d:"06/24",n:"城市展",i:"🏙️"},{d:"06/26",n:"结项",i:"🏁"}].forEach(function(m){
  var isT=m.d===today,isP=parseDate(m.d)<parseDate(today);
  h+='<span style="padding:3px 8px;border-radius:6px;font-size:.75rem;background:'+(isT?"#fdf5e0":isP?"#e8f0e2":"#f8f6f0")+';border:1px solid '+(isT?"var(--accent)":"var(--border)")+';opacity:'+(isP&&!isT?".5":"1")+'">'+m.i+' '+m.n+(isT?" 📍":"")+'</span>'});
 h+='</div><div style="font-size:.8rem;color:var(--muted);margin-bottom:8px">今日 '+active.length+' 项任务</div>';
 active.slice(0,15).forEach(function(t){
  var done=t.status==="已完成"||t.status==="已确认";
  var bg=done?"#e8f0e2":(t.status==="进行中"?"#fef9ee":"#fafaf7");
  var bc=done?"var(--green)":(t.status==="进行中"?"var(--yellow)":"var(--border)");
  h+='<div style="background:'+bg+';border:2px solid '+bc+';border-radius:8px;padding:10px 14px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;cursor:pointer" onclick="var s=t.status;toggleTaskStatus('+D.tasks.indexOf(t)+');return false" title="点击切换状态">';
  h+='<div><strong>'+esc(t.name)+'</strong><br><span style="font-size:.75rem;color:var(--muted)">'+esc(t.assignee)+' · '+esc(t.deadline)+'</span></div>';
  h+='<span class="badge '+(done?"done":t.status==="进行中"?"progress":"todo")+'">'+(done?"✅":t.status==="进行中"?"🔄":"⬜")+'</span></div>'});
 h+='</div>';v.innerHTML=h
}

/* ====== TIMELINE ====== */
function toggleTaskStatus(i){var t=D.tasks[i];if(!t)return;if(t.status==='已完成'||t.status==='已确认')t.status='待开始';else if(t.status==='进行中')t.status='已完成';else t.status='进行中';localStorage.setItem('camp_data',JSON.stringify(D));switchTab('map')}

function renderTimeline(v){v.innerHTML='<div class="card"><h3>📅 日历系统</h3><div class="empty-state">加载日程数据后显示</div></div>'}

/* ====== BUDGET ====== */
function renderBudget(v){
 var fc=D.finance_cny||{},txs=fc.transactions||[];
 var h='<div class="card" style="text-align:center"><h3>🏦 公会资金池</h3>';
 h+='<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">';
 h+='<div style="flex:1;min-width:200px;max-width:280px;background:#eaf4e2;border:2px solid #6a9a4a;border-radius:12px;padding:14px"><div style="font-size:1.5rem">💰</div><div style="font-weight:700;margin-bottom:8px">人民币金库</div><div><span style="font-size:1.3rem;font-weight:700">'+ (fc.summary?fc.summary.rmb_spent.toFixed(0):"--") +'</span><br><span style="font-size:.7rem;color:var(--muted)">已支出</span></div></div>';
 h+='<div style="flex:1;min-width:200px;max-width:280px;background:#fef8e8;border:2px solid #c8a040;border-radius:12px;padding:14px"><div style="font-size:1.5rem">💎</div><div style="font-weight:700;margin-bottom:8px">NT 金库</div><div><span style="font-size:1.3rem;font-weight:700">'+ (fc.summary?fc.summary.nt_spent.toFixed(0):"--") +'</span><br><span style="font-size:.7rem;color:var(--muted)">已支出</span></div></div>';
 h+='</div>';
 if(txs.length)h+='<div style="margin-top:14px;text-align:left;max-height:300px;overflow-y:auto"><table><thead><tr><th>事由</th><th>RMB</th><th>NT</th></tr></thead><tbody>'+txs.map(function(t){return'<tr><td>'+esc(t.desc)+'</td><td style="color:var(--red)">'+(t.rmb?t.rmb.toFixed(2):"")+'</td><td style="color:var(--accent)">'+(t.nt?t.nt.toFixed(0):"")+'</td></tr>'}).join("")+'</tbody></table></div>';
 h+='</div>';v.innerHTML=h
}

/* ====== SETTLEMENT ====== */
function renderSettlement(v){
 var tasks=D.tasks||[],stats={};
 tasks.forEach(function(t){var n=t.assignee||"未分配";if(!stats[n])stats[n]={pts:0,done:0,total:0};stats[n].total++;stats[n].pts+=t.points||1;if(t.status==="已完成"||t.status==="已确认")stats[n].done++});
 var sorted=Object.entries(stats).sort(function(a,b){return b[1].pts-a[1].pts}),total=sorted.reduce(function(s,e){return s+e[1].pts},0);
 var svg="",cx=90,cy=90,r=80,angle=0,PC=["#d4a853","#6b9b4e","#5b8cb8","#c47d5a","#8b6bae","#c4553d"];
 sorted.forEach(function(e,i){if(!e[1].pts)return;var a=e[1].pts/total*360,s=angle;angle+=a;var x1=cx+r*Math.cos((s-90)*Math.PI/180),y1=cy+r*Math.sin((s-90)*Math.PI/180),x2=cx+r*Math.cos((angle-90)*Math.PI/180),y2=cy+r*Math.sin((angle-90)*Math.PI/180);svg+='<path d="M'+cx+','+cy+' L'+x1+','+y1+' A'+r+','+r+' 0 '+(a>180?1:0)+',1 '+x2+','+y2+' Z" fill="'+PC[i%6]+'"/>'});
 var h='<div class="card"><h3>📊 激励分布</h3><div style="display:flex;align-items:center;gap:20px;justify-content:center;flex-wrap:wrap">';
 h+='<svg width="180" height="180" viewBox="0 0 180 180">'+svg+'</svg>';
 h+='<div style="font-size:.8rem">'+sorted.map(function(e,i){return'<div style="display:flex;align-items:center;gap:6px;padding:2px 0"><span style="width:12px;height:12px;border-radius:3px;background:'+PC[i%6]+'"></span>'+esc(e[0])+' · '+e[1].pts+'点</div>'}).join("")+'</div>';
 h+='</div><div style="margin-top:12px">';
 sorted.forEach(function(e){var n=e[0],m=e[1],pc=m.total>0?Math.round(m.done/m.total*100):0;h+='<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px dotted var(--border)"><span style="font-weight:600;width:80px">'+esc(n)+'</span><div style="flex:1;height:18px;background:#e6dfcc;border-radius:9px;overflow:hidden"><div style="height:100%;width:'+pc+'%;background:'+(pc>=80?"var(--green)":pc>=40?"var(--yellow)":"var(--red)")+';border-radius:9px;display:flex;align-items:center;padding-left:8px;font-size:.7rem;color:#fff;font-weight:700">'+m.pts+'点</div></div><span style="font-size:.75rem;color:var(--muted)">✅'+m.done+'/'+m.total+'</span></div>'});
 h+='</div></div>';v.innerHTML=h
}

window.onload=function(){alert("JS运行正常！请点确定后点加载按钮");try{loadOrCached()}catch(e){alert("缓存错误:"+e.message)}};
</script></body></html>"""

import sys
if len(sys.argv) > 1:
    output = sys.argv[1]
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written! {len(html)} bytes')
    print(output)
else:
    print(html)
