"""Inject missing functions into desktop dashboard.html"""
path = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The 5 missing functions to inject before </script>
inject = r'''
// ── Budget (公会资金池) ──
let financeFilter = '全部'; // 全部

function selectFinanceType(type) { financeFilter = type; renderBudget(); }

function renderBudget() {
  const b = data.budget || {};
  const fc = data.finance_cny || {};
  if (fc.summary) {
    const rmbTotal = fc.summary.rmb_total_budget || 0, rmbSpent = fc.summary.rmb_spent || 0, rmbRemain = fc.summary.rmb_remaining || 0;
    const ntIncome = fc.summary.nt_income_total || 0, ntSpent = fc.summary.nt_spent || 0, ntRemain = fc.summary.nt_remaining || 0;
    document.getElementById('bmRMBTotal').textContent = rmbTotal.toFixed(0);
    document.getElementById('bmRMBSpent').textContent = rmbSpent.toFixed(0);
    document.getElementById('bmRMBRemain').textContent = rmbRemain.toFixed(0);
    document.getElementById('bmNTIncome').textContent = ntIncome.toFixed(0);
    document.getElementById('bmNTSpent').textContent = ntSpent.toFixed(0);
    document.getElementById('bmNTRemain').textContent = ntRemain.toFixed(0);
    var rmbBar = document.getElementById('bmRMBBar'); if(rmbBar) rmbBar.style.width = rmbTotal>0 ? (rmbSpent/rmbTotal*100)+'%' : '0%';
    var ntBar = document.getElementById('bmNTBar'); if(ntBar) ntBar.style.width = ntIncome>0 ? (ntSpent/ntIncome*100)+'%' : '0%';
  }
  var txs = fc.transactions || [];
  var allTypes = [...new Set(txs.map(function(t){return t.type}).filter(Boolean))];
  var tb = document.getElementById('financeTypeBlocks');
  if(tb) tb.innerHTML = '<button class="phase-block'+(financeFilter==='\\u5168\\u90e8'?' active':'')+'" onclick="selectFinanceType(\\'\\u5168\\u90e8\\')"><span class="ph-icon">\\ud83d\\udcca</span><span class="ph-label">\\u603b\\u89c8</span><span class="ph-count">'+txs.length+'\\u7b14</span></button>' + allTypes.map(function(ty){var cnt=txs.filter(function(t){return t.type===ty}).length;return '<button class="phase-block'+(financeFilter===ty?' active':'')+'" onclick="selectFinanceType(\\''+escAttr(ty)+'\\')"><span class="ph-icon">\\ud83d\\udcb0</span><span class="ph-label">'+esc(ty)+'</span><span class="ph-count">'+cnt+'\\u7b14</span></button>';}).join('');
  var shown = financeFilter==='\\u5168\\u90e8' ? txs : txs.filter(function(t){return t.type===financeFilter});
  var txBody = document.querySelector('#txTable tbody');
  if(txBody) txBody.innerHTML = shown.length>0 ? shown.map(function(t,i){return '<tr><td>'+esc(t.type)+'</td><td>'+esc(t.person)+'</td><td style="font-size:.82rem">'+esc(t.desc)+'</td><td style="color:var(--red);text-align:right">'+(t.rmb?t.rmb.toFixed(2):'')+'</td><td style="color:var(--accent);text-align:right">'+(t.nt?t.nt.toFixed(0):'')+'</td><td><button class="btn" style="padding:2px 6px;font-size:.7rem" onclick="editTx('+txs.indexOf(t)+')">\\u270e</button></td></tr>';}).join('') : '<tr><td colspan="6" style="text-align:center;color:var(--muted)">\\u65e0\\u5339\\u914d\\u6d41\\u6c34</td></tr>';
  var byPerson = {}; shown.forEach(function(t){var p=t.person||'\\u672a\\u77e5';if(!byPerson[p])byPerson[p]={rmb:0,nt:0,count:0};byPerson[p].rmb+=Math.abs(t.rmb||0);byPerson[p].nt+=Math.abs(t.nt||0);byPerson[p].count++;});
  var pfBody = document.querySelector('#personFinanceTable tbody');
  if(pfBody) pfBody.innerHTML = Object.entries(byPerson).sort(function(a,b){return b[1].rmb-a[1].rmb}).map(function(e){return '<tr><td><strong>'+esc(e[0])+'</strong></td><td style="color:var(--red);text-align:right">'+(e[1].rmb>0?e[1].rmb.toFixed(2):'')+'</td><td style="color:var(--accent);text-align:right">'+(e[1].nt>0?e[1].nt.toFixed(0):'')+'</td><td>'+e[1].count+'</td></tr>';}).join('');
}

function showAddTx() {
  var type=prompt('流水类型：',''); if(!type)return;
  var person=prompt('出纳人：',''), desc=prompt('事由：',''); if(!desc)return;
  var rmb=prompt('RMB金额：','0'), nt=prompt('NT金额：','0');
  if(!data.finance_cny)data.finance_cny={transactions:[]};
  if(!data.finance_cny.transactions)data.finance_cny.transactions=[];
  data.finance_cny.transactions.push({type:type,person:person||'',desc:desc,rmb:parseFloat(rmb)||null,nt:parseFloat(nt)||null});
  localStorage.setItem('camp_data',JSON.stringify(data)); renderBudget();
}

function editTx(idx){var txs=data.finance_cny.transactions||[],t=txs[idx];if(!t)return;t.type=prompt('类型：',t.type||'')||t.type;t.person=prompt('出纳人：',t.person||'')||t.person;t.desc=prompt('事由：',t.desc||'')||t.desc;var r=prompt('RMB：',t.rmb||'0');t.rmb=r?parseFloat(r)||null:t.rmb;var n=prompt('NT：',t.nt||'0');t.nt=n?parseFloat(n)||null:t.nt;localStorage.setItem('camp_data',JSON.stringify(data));renderBudget();}

// ── Timeline + Calendar ──
var currentScheduleView = 'calendar';
function switchScheduleView(view) {
  currentScheduleView = view;
  var bcv = document.getElementById('btnCalendarView'); if(bcv) bcv.className = view==='calendar' ? 'btn pri' : 'btn';
  var btv = document.getElementById('btnTimelineView'); if(btv) btv.className = view==='timeline' ? 'btn pri' : 'btn';
  var cv = document.getElementById('calendarView'); if(cv) cv.classList.toggle('hidden',view!=='calendar');
  var tvc = document.getElementById('timelineViewCard'); if(tvc) tvc.classList.toggle('hidden',view!=='timeline');
  if(view==='calendar') renderCalendar();
  if(view==='timeline') renderTimeline();
}

function renderCalendar() {
  var sched = data.schedule;
  var grid = document.getElementById('calendarGrid');
  if (!sched || !sched.dates || sched.dates.length===0) {
    if(grid) grid.innerHTML = '<div class="empty-state">\\ud83d\\udcc5 \\u6682\\u65e0\\u65e5\\u7a0b\\u6570\\u636e</div>';
    return;
  }
  var dates=sched.dates, weekdays=sched.weekdays||[], slots=sched.slots||[];
  var html='<table class="cal-table"><thead><tr><th class="time-col">\\u65f6\\u95f4</th>';
  for(var i=0;i<dates.length;i++) html+='<th class="day-col">'+esc(dates[i])+'<br><span style="font-size:.68rem;color:var(--muted)">'+esc(weekdays[i]||'')+'</span></th>';
  html+='</tr></thead><tbody>';
  for(var j=0;j<slots.length;j++) {
    var slot=slots[j];
    html+='<tr><td class="time-cell">'+esc(slot.time)+'</td>';
    for(var k=0;k<dates.length;k++) {
      var act=(slot.activities&&slot.activities[k])?slot.activities[k]:'';
      html+='<td class="'+(act?'has-activity':'')+'">'+esc(act)+'</td>';
    }
    html+='</tr>';
  }
  html+='</tbody></table>';
  if(grid) grid.innerHTML=html;
}

function renderTimeline() {
  var sched=data.schedule, tasks=data.tasks||[], view=document.getElementById('timelineView');
  if(!view)return;
  var items=[];
  if(sched&&sched.dates){for(var i=0;i<(sched.slots||[]).length;i++){var slot=sched.slots[i];for(var j=0;j<sched.dates.length;j++){var act=(slot.activities&&slot.activities[j])?slot.activities[j]:'';if(act&&act.length>1)items.push({date:sched.dates[j],text:act,time:slot.time,source:'schedule'});}}}
  for(var k=0;k<tasks.length;k++){var t=tasks[k];if(t.deadline&&t.deadline.length>1){var dl=t.deadline,m2=dl.match(/(\\d+)\\D+(\\d+)/);if(m2)dl=m2[1].padStart(2,'0')+'/'+m2[2].padStart(2,'0');items.push({date:dl,text:t.name,assignee:t.assignee,status:t.status,source:'task',category:t.category});}}
  if(items.length===0){view.innerHTML='';return;}
  items.sort(function(a,b){var da=parseDateStr(a.date),db=parseDateStr(b.date);return da-db;});
  var grouped={};items.forEach(function(it){if(!grouped[it.date])grouped[it.date]=[];grouped[it.date].push(it);});
  var sd=Object.keys(grouped).sort(function(a,b){return parseDateStr(a)-parseDateStr(b)});
  var html='',lastPhase='',daySide=0;
  for(var di=0;di<sd.length;di++){
    var date=sd[di],entries=grouped[date];if(!entries.length)continue;
    var dval=parseDateStr(date),phase=dval<parseDateStr('06/06')?'\\u7b79\\u5907\\u671f':(dval<=parseDateStr('06/11')?'\\u8425\\u4e2d\\u00b7\\u524d\\u671f':(dval<=parseDateStr('06/22')?'\\u8425\\u4e2d\\u00b7\\u540e\\u671f':'\\u5ef6\\u671f & \\u7ed3\\u9879'));
    if(phase!==lastPhase){html+='<div class="tl-phase"><span>'+phase+'</span></div>';lastPhase=phase;daySide=0;}
    var side=daySide%2===0?'left':'right';daySide++;
    var evHtml='';
    for(var ei=0;ei<entries.length;ei++){var e=entries[ei];if(e.source==='schedule')evHtml+='<div class="tl-day-event"><span class="tl-time">'+esc(e.time)+'</span> <span class="tl-title">'+esc(e.text)+'</span></div>';else{var bdg=e.status==='\\u5df2\\u5b8c\\u6210'||e.status==='\\u5df2\\u786e\\u8ba4'?'done':(e.status==='\\u8fdb\\u884c\\u4e2d'?'progress':'todo');evHtml+='<div class="tl-day-event"><span class="tl-title">'+esc(e.text)+'</span><span style="font-size:.7rem;color:var(--muted)">'+(e.assignee?' \\u00b7 '+esc(e.assignee):'')+'</span><span class="badge '+bdg+'" style="float:right;font-size:.7rem">'+esc(e.status)+'</span></div>';}}
    html+='<div class="tl-day-block '+side+'"><div class="tl-day-box"><div class="tl-dbox-header"><span>\\ud83d\\udcc5 '+date+'</span><span class="count">'+entries.length+'\\u9879</span></div>'+evHtml+'</div><div class="tl-branch"></div><div class="tl-dot"></div></div>';
  }
  view.innerHTML=html;
}

// ── Settlement ──
var settleSelected=null;
var PIE_COLORS=['#d4a853','#6b9b4e','#5b8cb8','#c47d5a','#8b6bae','#c4553d','#5fa89b','#d49b3d','#9b6b8e','#6b8e6b'];

function renderSettlementAll() {
  try {
  var tasks=data.tasks||[];
  if(tasks.length===0){var sc=document.getElementById('settlementCard');if(sc)sc.innerHTML='<div class="empty-state">\\ud83d\\udced \\u6682\\u65e0\\u4efb\\u52a1\\u6570\\u636e\\uff0c\\u8bf7\\u5148\\u52a0\\u8f7d data.json</div>';return;}
  var stats={};tasks.forEach(function(t){var n=t.assignee||'(\\u672a\\u5206\\u914d)';if(!stats[n])stats[n]={points:0,done:0,total:0};stats[n].total++;stats[n].points+=(t.points||1);if(t.status==='\\u5df2\\u5b8c\\u6210'||t.status==='\\u5df2\\u786e\\u8ba4')stats[n].done++;});
  var sorted=Object.entries(stats).sort(function(a,b){return b[1].points-a[1].points});
  var totalPoints=sorted.reduce(function(s,e){return s+e[1].points},0);
  var cx=90,cy=90,r=80,cumAngle=0,slicesSvg='',legendHtml='';
  sorted.forEach(function(e,i){if(e[1].points===0)return;var angle=(e[1].points/totalPoints)*360;var start=cumAngle;cumAngle+=angle;var end=cumAngle;var x1=cx+r*Math.cos((start-90)*Math.PI/180),y1=cy+r*Math.sin((start-90)*Math.PI/180),x2=cx+r*Math.cos((end-90)*Math.PI/180),y2=cy+r*Math.sin((end-90)*Math.PI/180);slicesSvg+='<path d=\"M'+cx+','+cy+' L'+x1+','+y1+' A'+r+','+r+' 0 '+(angle>180?1:0)+',1 '+x2+','+y2+' Z\" fill=\"'+PIE_COLORS[i%10]+'\"/>';legendHtml+='<div class=\"pie-legend-item\"><span class=\"pie-legend-dot\" style=\"background:'+PIE_COLORS[i%10]+'\"></span> '+esc(e[0])+' \\u00b7 '+e[1].points+'\\u70b9 ('+(e[1].points/totalPoints*100).toFixed(1)+'%)</div>';});
  var pa=document.getElementById('pieChartArea');if(pa)pa.innerHTML='<svg width=\"180\" height=\"180\" viewBox=\"0 0 180 180\">'+slicesSvg+'</svg><div class=\"pie-legend\">'+legendHtml+'</div>';
  var sa=document.getElementById('settleAvatars');
  if(sa)sa.innerHTML=sorted.map(function(e){var n=e[0],mi=data.members&&data.members[n]?data.members[n]:{},si=mi.avatar_seed!==undefined?mi.avatar_seed:0;return'<button class=\"ms-avatar-btn'+(n===settleSelected?' active':'')+'\" onclick=\"renderWageSlip(\\''+escAttr(n)+'\\')\"><div class=\"ms-av-circle\">'+avatarCircle(si,64,0)+'</div><div class=\"ms-av-name\">'+esc(n)+'</div><div class=\"ms-av-badge\">'+e[1].done+'/'+e[1].total+'</div></button>';}).join('');
  if(!settleSelected||!stats[settleSelected])settleSelected=sorted[0]&&sorted[0][0];
  if(settleSelected)renderWageSlip(settleSelected);
  }catch(e){var sc2=document.getElementById('settlementCard');if(sc2)sc2.innerHTML='<div class=\"empty-state\">\\u7ed3\\u7b97\\u6e32\\u67d3\\u51fa\\u9519: '+e.message+'</div>';}
}

function renderWageSlip(name){
  settleSelected=name;
  var sa2=document.querySelectorAll('#settleAvatars .ms-avatar-btn');
  sa2.forEach(function(b){var n2=b.querySelector('.ms-av-name');if(n2)b.classList.toggle('active',n2.textContent===name);});
  var tasks=data.tasks.filter(function(t){return t.assignee===name}),done=tasks.filter(function(t){return t.status==='\\u5df2\\u5b8c\\u6210'||t.status==='\\u5df2\\u786e\\u8ba4'}),points=done.reduce(function(s,t){return s+(t.points||1)},0);
  var typeCounts={};done.forEach(function(t){var c=t.category||'\\u5176\\u4ed6';typeCounts[c]=(typeCounts[c]||0)+1;});
  var typeBadges=Object.entries(typeCounts).sort(function(a,b){return b[1]-a[1]}).map(function(e){return'<span style=\"display:inline-block;padding:4px 10px;margin:3px;border-radius:10px;background:#faf8f0;border:1px solid var(--border);font-size:.78rem\">'+esc(e[0])+' \\u00d7'+e[1]+'</span>';}).join('');
  var ntRate=2,ntEarned=points*ntRate,pool=(data.budget||{}).rmb_spent||11802,allDonePts=tasks.reduce(function(s,t){return(t.status==='\\u5df2\\u5b8c\\u6210'||t.status==='\\u5df2\\u786e\\u8ba4')?s+(t.points||1):s},0),rmbEarned=allDonePts>0?Math.round(pool*points/allDonePts):0,completionPct=tasks.length>0?Math.round(done.length/tasks.length*100):0;
  var mi4=data.members&&data.members[name]?data.members[name]:{},aviIdx=mi4.avatar_seed!==undefined?mi4.avatar_seed:0;
  var sc3=document.getElementById('settlementCard');
  if(sc3)sc3.innerHTML='<div style=\"max-width:460px;margin:0 auto\"><div style=\"text-align:center;margin-bottom:14px\"><div class=\"ms-avatar\" style=\"width:64px;height:64px;margin:0 auto 6px\">'+avatarImg(aviIdx,128,0)+avatarInitial(aviIdx)+'</div><div style=\"font-size:1.1rem;font-weight:700\">'+esc(name)+'</div><div style=\"font-size:.78rem;color:var(--muted)\">\\u5de5\\u4f5c\\u51ed\\u8bc1 \\u00b7 \\u7b2c\\u4e09\\u671f\\u5171\\u521b\\u8425</div></div><div style=\"display:flex;gap:10px;margin-bottom:14px\"><div style=\"flex:1;background:#e8f0e2;border-radius:10px;padding:14px;text-align:center\"><div style=\"font-size:.7rem;color:var(--muted);margin-bottom:2px\">\\ud83d\\udcb0 \\u6cd5\\u5e01</div><div style=\"font-size:1.6rem;font-weight:700;color:var(--green)\">\\u00a5'+rmbEarned+'</div></div><div style=\"flex:1;background:#fdf5e0;border-radius:10px;padding:14px;text-align:center\"><div style=\"font-size:.7rem;color:var(--muted);margin-bottom:2px\">\\ud83d\\udc8e NT</div><div style=\"font-size:1.6rem;font-weight:700;color:var(--accent)\">'+ntEarned+'</div></div></div><div style=\"background:linear-gradient(135deg,#fdf8ee,#faf5e8);border:2px solid var(--accent);border-radius:12px;padding:14px;margin-bottom:12px\"><div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:8px\"><span style=\"font-weight:700\">\\ud83c\\udfc6 \\u6210\\u5c31</span><span style=\"font-size:.78rem;color:var(--muted)\">'+done.length+'/'+tasks.length+' \\u4efb\\u52a1 \\u00b7 '+completionPct+'%</span></div><div style=\"margin-bottom:6px\">'+typeBadges+'</div><details style=\"font-size:.8rem\"><summary style=\"cursor:pointer;color:var(--accent);font-weight:600\">\\u67e5\\u770b\\u6210\\u5c31\\u8be6\\u60c5</summary><div style=\"padding:6px 0\">'+done.map(function(t){return'<div style=\"padding:3px 0;border-bottom:1px dotted var(--border);display:flex;justify-content:space-between\"><span>'+esc(t.name)+'</span><span style=\"color:var(--green)\">+'+ (t.points||1)+'\\u70b9</span></div>';}).join('')+'</div></details></div><details style=\"margin-bottom:8px;font-size:.78rem;background:#faf8f0;border-radius:8px;padding:8px 12px\"><summary style=\"cursor:pointer;color:var(--muted);font-weight:600\">\\ud83d\\udcd0 \\u8ba1\\u7b97\\u65b9\\u5f0f</summary><div style=\"padding:6px 0;color:var(--muted)\">\\u6fc0\\u52b1\\u70b9 = '+done.map(function(t){return t.points||1}).join('+')+' = <b>'+points+'\\u70b9</b><br>NT = '+points+' \\u00d7 '+ntRate+' = <b>'+ntEarned+' NT</b><br>RMB = ('+points+'/'+allDonePts+') \\u00d7 '+pool+' = <b>'+rmbEarned+'\\u5143</b></div></details><div style=\"text-align:center;font-size:.72rem;color:var(--muted)\">\\u2b1c \\u5f85\\u652f\\u4ed8 \\u00b7 \\u5fae\\u4fe1\\u8f6c\\u8d26 + \\u94fe\\u4e0a\\u7ed3\\u7b97</div></div>';
}

// ── Players tab ──
var selectedPlayer = null;
function renderPlayers() {
  var tasks = data.tasks || [];
  var staffNames = ['\\u781a\\u4ec1','\\u671d\\u6797','\\u5c0f\\u7ea2','\\u82e5\\u66e6','\\u6dd1\\u60e0','\\u8df3\\u5927\\u7237'];
  var players = [...new Set(tasks.map(function(t){return t.assignee}).filter(Boolean))].filter(function(n){return !staffNames.some(function(s){return n.includes(s)})});
  var pd = {}; tasks.forEach(function(t){var n=t.assignee||'';if(!players.includes(n))return;if(!pd[n])pd[n]={tasks:[],points:0,done:0,active:0,todo:0};pd[n].tasks.push(t);pd[n].points+=(t.points||1);if(t.status==='\\u5df2\\u5b8c\\u6210'||t.status==='\\u5df2\\u786e\\u8ba4')pd[n].done++;else if(t.status==='\\u8fdb\\u884c\\u4e2d')pd[n].active++;else pd[n].todo++;});
  var sorted=Object.entries(pd).sort(function(a,b){return b[1].tasks.length-a[1].tasks.length});
  var avRow=document.getElementById('playerAvatars'),empty=document.getElementById('playerEmpty');
  if(!avRow)return;
  if(sorted.length===0){var pdet=document.getElementById('playerDetail');if(pdet)pdet.innerHTML='';empty.classList.remove('hidden');return;}
  empty.classList.add('hidden');
  avRow.querySelectorAll('.ms-avatar-btn:not(.ms-add-btn)').forEach(function(b){b.remove()});
  var addBtn=avRow.querySelector('.ms-add-btn');
  sorted.forEach(function(e){var n=e[0],m=e[1],btn=document.createElement('button');btn.className='ms-avatar-btn'+(n===selectedPlayer?' active':'');btn.onclick=function(){selectedPlayer=n;renderPlayers();};var mi2=data.members&&data.members[n]?data.members[n]:{},si2=mi2.avatar_seed!==undefined?mi2.avatar_seed:0;btn.innerHTML='<div class=\"ms-av-circle\">'+avatarCircle(si2,64,0)+'</div><div class=\"ms-av-name\">'+esc(n)+'</div><div class=\"ms-av-badge\">'+m.tasks.length+'\\u4efb\\u52a1</div>';avRow.insertBefore(btn,addBtn);});
  if(!selectedPlayer||!pd[selectedPlayer])selectedPlayer=sorted[0][0];
  renderMemberDetailFor('player',selectedPlayer,pd[selectedPlayer]);
}

function renderMemberDetailFor(type,name,m){
  var dd=document.getElementById(type+'Detail');if(!m||!name){if(dd)dd.innerHTML='';return;}
  var total=m.tasks.length,pct=total>0?Math.round(m.done/total*100):0,mi=data.members&&data.members[name]?data.members[name]:{},ntInfo=mi.nt_actual||mi.nt_earned||0,role=mi.role||(total>=10?'\\u6838\\u5fc3\\u6210\\u5458':total>=5?'\\u6d3b\\u8dc3\\u6210\\u5458':'\\u53c2\\u4e0e\\u8005'),bio=mi.bio||'',genderIcon=mi.gender==='male'?'\\u2642\\ufe0f':mi.gender==='female'?'\\u2640\\ufe0f':'',asi=mi.avatar_seed!==undefined?mi.avatar_seed:0;
  var doneT=m.tasks.filter(function(t){return t.status==='\\u5df2\\u5b8c\\u6210'||t.status==='\\u5df2\\u786e\\u8ba4'}),activeT=m.tasks.filter(function(t){return t.status==='\\u8fdb\\u884c\\u4e2d'}),todoT=m.tasks.filter(function(t){return t.status!=='\\u5df2\\u5b8c\\u6210'&&t.status!=='\\u5df2\\u786e\\u8ba4'&&t.status!=='\\u8fdb\\u884c\\u4e2d'});
  if(dd)dd.innerHTML='<div class=\"member-sheet\"><div class=\"ms-left\"><div class=\"ms-avatar\">'+avatarImg(asi,120,0)+avatarInitial(asi)+'</div><div class=\"ms-name\">'+genderIcon+' '+esc(name)+'</div><div class=\"ms-role\">'+esc(role)+'</div>'+(bio?'<div style=\"font-size:.75rem;color:var(--muted);margin-bottom:8px;font-style:italic\">\"'+esc(bio)+'\"</div>':'')+'<div class=\"ms-stats\"><div class=\"stat-row\"><span>\\ud83d\\udccb \\u603b\\u4efb\\u52a1</span><span class=\"sv\">'+total+'</span></div><div class=\"stat-row\"><span>\\u2705 \\u5b8c\\u6210</span><span class=\"sv g\">'+m.done+'</span></div><div class=\"stat-row\"><span>\\ud83d\\udd04 \\u8fdb\\u884c\\u4e2d</span><span class=\"sv y\">'+m.active+'</span></div><div class=\"stat-row\"><span>\\u2b1c \\u5f85\\u5f00\\u59cb</span><span class=\"sv r\">'+m.todo+'</span></div><div class=\"stat-row\"><span>\\u2b50 \\u6fc0\\u52b1\\u70b9</span><span class=\"sv\">'+m.points+'</span></div>'+(ntInfo?'<div class=\"stat-row\"><span>\\ud83d\\udcb0 NT</span><span class=\"sv g\">'+ntInfo+'</span></div>':'')+'</div><div class=\"ms-bar-wrap\"><div class=\"fill\" style=\"width:'+pct+'%;background:var(--green)\"></div></div><div style=\"font-size:.7rem;color:var(--muted)\">'+pct+'% \\u5b8c\\u6210</div></div><div class=\"ms-right\">'+(todoT.length>0?'<div class=\"ms-task-col\"><h4>\\u2b1c \\u5f85\\u5f00\\u59cb ('+todoT.length+')</h4>'+todoT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class=\"ms-task-row\"><span>'+esc(t.name)+'</span><span style=\"font-size:.7rem;color:var(--red)\">'+(t.deadline||'')+'</span></div>'}).join('')+'</div>':'')+(activeT.length>0?'<div class=\"ms-task-col\"><h4>\\ud83d\\udd04 \\u8fdb\\u884c\\u4e2d ('+activeT.length+')</h4>'+activeT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class=\"ms-task-row\"><span>'+esc(t.name)+'</span><span style=\"font-size:.7rem;color:var(--muted)\">'+(t.deadline||'')+'</span></div>'}).join('')+'</div>':'')+(doneT.length>0?'<div class=\"ms-task-col\"><h4>\\u2705 \\u5df2\\u5b8c\\u6210 ('+doneT.length+')</h4>'+doneT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class=\"ms-task-row\"><span class=\"done\">'+esc(t.name)+'</span><span style=\"font-size:.7rem;color:var(--green)\">+'+(t.points||1)+'\\u70b9</span></div>'}).join('')+'</div>':'')+(m.tasks.length===0?'<div style=\"color:var(--muted);text-align:center;padding:20px\">\\u6682\\u65e0\\u4efb\\u52a1</div>':'')+'</div></div>';
}
'''

# Find </script> tag and inject before it
end_script = content.rfind('</script>')
if end_script > 0:
    content = content[:end_script] + inject + '\n' + content[end_script:]
    print(f'Injected before </script> at position {end_script}')
else:
    print('</script> not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Done. File size: {len(content)} bytes')
