"""Split members tab into 游戏策划组 + 游戏玩家"""
import re

path = r'C:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add global state variables
old_state = 'let memberData = {};\nlet selectedMember = null;'
new_state = 'let staffData = {}, playerData = {}, selectedStaff = null, selectedPlayer = null;'
content = content.replace(old_state, new_state)

# Step 2: Replace renderMemberDetail function entirely
# Find its boundaries
start = content.find('function renderMemberDetail(name) {')
end = content.find('\n// ── Calendar cell', start)  # next function after renderMemberDetail
if end < 0:
    end = content.find('\n// ── Add/Edit', start)
if end < 0:
    end = content.find('\nfunction showAddMember', start)

old_detail = content[start:end]

new_detail = '''function renderMemberDetailFor(type, name, m) {
  const detailDiv = document.getElementById(type + 'Detail');
  if (!m || !name) { detailDiv.innerHTML = ''; return; }
  const total = m.tasks.length;
  const pct = total > 0 ? Math.round(m.done / total * 100) : 0;
  const memInfo = data.members?.[name] || {};
  const ntInfo = memInfo.nt_actual || memInfo.nt_earned || 0;
  const role = memInfo.role || (total >= 10 ? '核心成员' : total >= 5 ? '活跃成员' : '参与者');
  const bio = memInfo.bio || '';
  const genderIcon = memInfo.gender === 'male' ? '♂️' : memInfo.gender === 'female' ? '♀️' : '';
  const avatarSi = memInfo.avatar_seed !== undefined ? memInfo.avatar_seed : 0;
  const doneTasks = m.tasks.filter(t => t.status==='已完成'||t.status==='已确认');
  const activeTasks = m.tasks.filter(t => t.status==='进行中');
  const todoTasks = m.tasks.filter(t => t.status!=='已完成'&&t.status!=='已确认'&&t.status!=='进行中');

  detailDiv.innerHTML = `<div class="member-sheet">
    <div class="ms-left">
      <div class="ms-avatar">${avatarImg(avatarSi,120,0)}${avatarInitial(avatarSi)}</div>
      <div class="ms-name">${genderIcon} ${esc(name)} <button class="btn" style="padding:1px 6px;font-size:.65rem" onclick="showEditMember('${escAttr(name)}')">✎</button></div>
      <div class="ms-role">${esc(role)}</div>
      ${bio ? `<div style="font-size:.75rem;color:var(--muted);margin-bottom:8px;font-style:italic">"${esc(bio)}"</div>` : ''}
      <div class="ms-stats">
        <div class="stat-row"><span>📋 总任务</span><span class="sv">${total}</span></div>
        <div class="stat-row"><span>✅ 完成</span><span class="sv g">${m.done}</span></div>
        <div class="stat-row"><span>🔄 进行中</span><span class="sv y">${m.active}</span></div>
        <div class="stat-row"><span>⬜ 待开始</span><span class="sv r">${m.todo}</span></div>
        <div class="stat-row"><span>⭐ 激励点</span><span class="sv">${m.points}</span></div>
        ${ntInfo ? `<div class="stat-row"><span>💰 NT</span><span class="sv g">${ntInfo}</span></div>` : ''}
      </div>
      <div class="ms-bar-wrap"><div class="fill" style="width:${pct}%;background:var(--green)"></div></div>
      <div style="font-size:.7rem;color:var(--muted)">${pct}% 完成</div>
    </div>
    <div class="ms-right">
      ${todoTasks.length > 0 ? `<div class="ms-task-col"><h4>⬜ 待开始 (${todoTasks.length})</h4>${todoTasks.sort((a,b)=>parseDate(a.deadline)-parseDate(b.deadline)).map(t => `<div class="ms-task-row"><span>${esc(t.name)}</span><span style="font-size:.7rem;color:var(--red)">${t.deadline||''}</span></div>`).join('')}</div>` : ''}
      ${activeTasks.length > 0 ? `<div class="ms-task-col"><h4>🔄 进行中 (${activeTasks.length})</h4>${activeTasks.sort((a,b)=>parseDate(a.deadline)-parseDate(b.deadline)).map(t => `<div class="ms-task-row"><span>${esc(t.name)}</span><span style="font-size:.7rem;color:var(--muted)">${t.deadline||''}</span></div>`).join('')}</div>` : ''}
      ${doneTasks.length > 0 ? `<div class="ms-task-col"><h4>✅ 已完成 (${doneTasks.length})</h4>${doneTasks.sort((a,b)=>parseDate(a.deadline)-parseDate(b.deadline)).map(t => `<div class="ms-task-row"><span class="done">${esc(t.name)}</span><span style="font-size:.7rem;color:var(--green)">+${t.points||1}点</span></div>`).join('')}</div>` : ''}
      ${m.tasks.length === 0 ? '<div style="color:var(--muted);text-align:center;padding:20px">暂无任务</div>' : ''}
    </div>
  </div>`;
}'''

content = content.replace(old_detail, new_detail)
print(f"renderMemberDetail: {'OK' if old_detail in content else 'replaced OK'}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
