"""Fix broken renderMembers function"""
path = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The broken section starts at "// (member state moved to top)"
# and includes broken renderMembers + broken selectMember + broken renderMemberDetail
# We need to find where it ends

old_marker = '// (member state moved to top)'
idx = content.find(old_marker)
if idx < 0:
    print('Marker not found')
    exit()

# Find the END of the broken block: it should be right before the injected functions
# Look for the injected comment
end_marker = '// ── Budget'
end_idx = content.find(end_marker, idx)
if end_idx < 0:
    end_marker = '// (CHARACTER_SEEDS moved'
    end_idx = content.find(end_marker, idx)
if end_idx < 0:
    end_marker = "function escAttr(s)"
    end_idx = content.find(end_marker, idx + 500)

print(f"Removing from {idx} to {end_idx} ({end_idx - idx} chars)")

# Build the replacement clean code
new_code = r'''
function renderMembers() {
  var tasks = data.tasks || [];
  var staffNames = ['砚仁','朝林','小红','若曦','淑惠','跳大爷'];
  memberData = {};
  tasks.forEach(function(t) {
    var name = t.assignee || '(未分配)';
    if (!staffNames.some(function(s){return name.includes(s)})) return;
    if (!memberData[name]) memberData[name] = { tasks: [], points: 0, done: 0, active: 0, todo: 0 };
    memberData[name].tasks.push(t);
    memberData[name].points += (t.points || 1);
    if (t.status === '已完成' || t.status === '已确认') memberData[name].done++;
    else if (t.status === '进行中') memberData[name].active++;
    else memberData[name].todo++;
  });
  var sorted = Object.entries(memberData).sort(function(a,b){ return b[1].tasks.length - a[1].tasks.length; });
  var avRow = document.getElementById('memberAvatars');
  var empty = document.getElementById('memberEmpty');
  if (sorted.length === 0) {
    if(avRow) avRow.innerHTML = '';
    var md = document.getElementById('memberDetail'); if(md) md.innerHTML = '';
    if(empty) empty.classList.remove('hidden');
    return;
  }
  if(empty) empty.classList.add('hidden');
  if(avRow) avRow.querySelectorAll('.ms-avatar-btn:not(.ms-add-btn)').forEach(function(b){b.remove()});
  var addBtn = avRow ? avRow.querySelector('.ms-add-btn') : null;
  sorted.forEach(function(e) {
    var name = e[0], m = e[1];
    var btn = document.createElement('button');
    btn.className = 'ms-avatar-btn' + (name === selectedMember ? ' active' : '');
    btn.onclick = function(){ selectedMember = name; renderMembers(); };
    var mi = data.members && data.members[name] ? data.members[name] : {};
    var si = mi.avatar_seed !== undefined ? mi.avatar_seed : 0;
    btn.innerHTML = '<div class="ms-av-circle">' + avatarCircle(si,64,0) + '</div><div class="ms-av-name">' + esc(name) + '</div><div class="ms-av-badge">' + m.tasks.length + '任务</div>';
    if(avRow && addBtn) avRow.insertBefore(btn, addBtn);
  });
  if (!selectedMember || !memberData[selectedMember]) selectedMember = sorted[0][0];
  renderMemberDetail(selectedMember);
}

function renderMemberDetail(name) {
  var m = memberData[name];
  var dd = document.getElementById('memberDetail');
  if (!m || !name) { if(dd) dd.innerHTML = ''; return; }
  var total = m.tasks.length;
  var pct = total > 0 ? Math.round(m.done / total * 100) : 0;
  var mi = data.members && data.members[name] ? data.members[name] : {};
  var ntInfo = mi.nt_actual || mi.nt_earned || 0;
  var role = mi.role || (total >= 10 ? '核心成员' : total >= 5 ? '活跃成员' : '参与者');
  var bio = mi.bio || '';
  var genderIcon = mi.gender === 'male' ? '♂️' : mi.gender === 'female' ? '♀️' : '';
  var asi = mi.avatar_seed !== undefined ? mi.avatar_seed : 0;
  var doneT = m.tasks.filter(function(t){return t.status==='已完成'||t.status==='已确认'});
  var activeT = m.tasks.filter(function(t){return t.status==='进行中'});
  var todoT = m.tasks.filter(function(t){return t.status!=='已完成'&&t.status!=='已确认'&&t.status!=='进行中'});
  var h = '<div class="member-sheet"><div class="ms-left"><div class="ms-avatar">'+avatarImg(asi,120,0)+avatarInitial(asi)+'</div><div class="ms-name">'+genderIcon+' '+esc(name)+'</div><div class="ms-role">'+esc(role)+'</div>'+(bio?'<div style="font-size:.75rem;color:var(--muted);margin-bottom:8px;font-style:italic">"'+esc(bio)+'"</div>':'')+'<div class="ms-stats"><div class="stat-row"><span>📋 总任务</span><span class="sv">'+total+'</span></div><div class="stat-row"><span>✅ 完成</span><span class="sv g">'+m.done+'</span></div><div class="stat-row"><span>🔄 进行中</span><span class="sv y">'+m.active+'</span></div><div class="stat-row"><span>⬜ 待开始</span><span class="sv r">'+m.todo+'</span></div><div class="stat-row"><span>⭐ 激励点</span><span class="sv">'+m.points+'</span></div>'+(ntInfo?'<div class="stat-row"><span>💰 NT</span><span class="sv g">'+ntInfo+'</span></div>':'')+'</div><div class="ms-bar-wrap"><div class="fill" style="width:'+pct+'%;background:var(--green)"></div></div><div style="font-size:.7rem;color:var(--muted)">'+pct+'% 完成</div></div><div class="ms-right">'+(todoT.length>0?'<div class="ms-task-col"><h4>⬜ 待开始 ('+todoT.length+')</h4>'+todoT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class="ms-task-row"><span>'+esc(t.name)+'</span><span style="font-size:.7rem;color:var(--red)">'+(t.deadline||'')+'</span></div>'}).join('')+'</div>':'')+(activeT.length>0?'<div class="ms-task-col"><h4>🔄 进行中 ('+activeT.length+')</h4>'+activeT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class="ms-task-row"><span>'+esc(t.name)+'</span><span style="font-size:.7rem;color:var(--muted)">'+(t.deadline||'')+'</span></div>'}).join('')+'</div>':'')+(doneT.length>0?'<div class="ms-task-col"><h4>✅ 已完成 ('+doneT.length+')</h4>'+doneT.sort(function(a,b){return parseDate(a.deadline)-parseDate(b.deadline)}).map(function(t){return'<div class="ms-task-row"><span class="done">'+esc(t.name)+'</span><span style="font-size:.7rem;color:var(--green)">+'+(t.points||1)+'点</span></div>'}).join('')+'</div>':'')+(m.tasks.length===0?'<div style="color:var(--muted);text-align:center;padding:20px">暂无任务</div>':'')+'</div></div>';
  if(dd) dd.innerHTML = h;
}
'''

content = content[:idx] + new_code + content[end_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Done. Size: {len(content)} bytes')
