"""Add 游戏玩家 tab between 游戏策划组 and 日历系统"""
import re

path = r'C:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add tab button
old_tab = '''<button class="tab" onclick="switchTab('members')" style="border-bottom:2px solid transparent;margin-bottom:0">👥 游戏策划组</button>
      <button class="tab" onclick="switchTab('timeline')" style="border-bottom:2px solid transparent;margin-bottom:0">📅 日历系统</button>'''
new_tab = '''<button class="tab" onclick="switchTab('members')" style="border-bottom:2px solid transparent;margin-bottom:0">👥 游戏策划组</button>
      <button class="tab" onclick="switchTab('players')" style="border-bottom:2px solid transparent;margin-bottom:0">⚔️ 游戏玩家</button>
      <button class="tab" onclick="switchTab('timeline')" style="border-bottom:2px solid transparent;margin-bottom:0">📅 日历系统</button>'''
if old_tab in content:
    content = content.replace(old_tab, new_tab)
    print('Tab button added')
else:
    print('Tab button NOT FOUND')

# 2. Add tab-players div after tab-members
old_members_end = '</div>\n\n  <!-- Tab: Map -->\n  <div id="tab-map"'
# The players tab should go between members and map... wait, the order is:
# tasks, map, members, players, timeline, budget, settlement
# But in the HTML, the div order doesn't matter - they just need to exist.
# Let me add it after tab-members

old_insert = '  <!-- Tab: Timeline -->'
new_insert = '''  <!-- Tab: Players -->
  <div id="tab-players" class="hidden">
    <div class="ms-avatar-row" id="playerAvatars">
      <button class="ms-avatar-btn ms-add-btn" onclick="showAddMember()" style="opacity:.6">
        <div class="ms-av-circle" style="background:#e0dcd4;border:2px dashed var(--border)"><span style="font-size:1.2rem;color:var(--muted)">＋</span></div>
        <div class="ms-av-name">新增</div>
      </button>
    </div>
    <div id="playerDetail"></div>
    <div class="empty-state hidden" id="playerEmpty">👤 还没有玩家数据</div>
  </div>

  <!-- Tab: Timeline -->'''

if old_insert in content:
    content = content.replace(old_insert, new_insert)
    print('Tab-players div added')
else:
    print('Tab-players div NOT FOUND')

# 3. Update switchTab
old_switch = "['tasks','members','timeline','budget','settlement','map']"
new_switch = "['tasks','members','players','timeline','budget','settlement','map']"
content = content.replace(old_switch, new_switch)
print('switchTab updated')

# 4. Add switchTab handler for players
old_sw = "  if (name === 'members') renderMembers();"
new_sw = "  if (name === 'members') renderMembers();\n  if (name === 'players') renderPlayers();"
content = content.replace(old_sw, new_sw)
print('switchTab players handler added')

# 5. Add renderPlayers function
old_func = 'function escAttr(s) { return (s||\'\').replace'
new_func = '''function renderPlayers() {
  const tasks = data.tasks || [];
  const staffNames = ['砚仁','朝林','小红','若曦','淑惠','跳大爷'];
  const players = [...new Set(tasks.map(t => t.assignee).filter(Boolean))].filter(n => !staffNames.some(s => n.includes(s)));
  const playerData = {};
  tasks.forEach(t => {
    const name = t.assignee || '';
    if (!players.includes(name)) return;
    if (!playerData[name]) playerData[name] = { tasks: [], points: 0, done: 0, active: 0, todo: 0 };
    playerData[name].tasks.push(t);
    playerData[name].points += (t.points || 1);
    if (t.status === '已完成' || t.status === '已确认') playerData[name].done++;
    else if (t.status === '进行中') playerData[name].active++;
    else playerData[name].todo++;
  });
  const sorted = Object.entries(playerData).sort((a,b) => b[1].tasks.length - a[1].tasks.length);
  const avRow = document.getElementById('playerAvatars');
  const empty = document.getElementById('playerEmpty');
  if (!avRow) return;
  if (sorted.length === 0) {
    document.getElementById('playerDetail').innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');
  avRow.querySelectorAll('.ms-avatar-btn:not(.ms-add-btn)').forEach(b => b.remove());
  const addBtn = avRow.querySelector('.ms-add-btn');
  sorted.forEach(([name, m]) => {
    const btn = document.createElement('button');
    btn.className = 'ms-avatar-btn' + (name === selectedPlayer ? ' active' : '');
    btn.onclick = () => { selectedPlayer = name; renderPlayers(); };
    const mi = data.members?.[name] || {};
    const si = mi.avatar_seed !== undefined ? mi.avatar_seed : 0;
    btn.innerHTML = '<div class=\"ms-av-circle\">'+avatarCircle(si,64,0)+'</div><div class=\"ms-av-name\">'+esc(name)+'</div><div class=\"ms-av-badge\">'+m.tasks.length+'任务</div>';
    avRow.insertBefore(btn, addBtn);
  });
  if (!selectedPlayer || !playerData[selectedPlayer]) selectedPlayer = sorted[0][0];
  renderMemberDetailFor('player', selectedPlayer, playerData[selectedPlayer]);
}

function escAttr(s) { return (s||'').replace'''

content = content.replace(old_func, new_func)
print('renderPlayers added')

# 6. Restore original renderMembers (undo the split)
# Find current renderMembers and replace with original
old_rm_start = 'const STAFF_NAMES2 ='
new_rm = 'function renderMembers() {\n  const tasks = data.tasks || [];\n  memberData = {};\n  tasks.forEach(t => {\n    const name = t.assignee || \'(未分配)\';\n    const staffNames2 = [\'砚仁\',\'朝林\',\'小红\',\'若曦\',\'淑惠\',\'跳大爷\'];\n    if (staffNames2.some(s => name.includes(s))) {\n      if (!memberData[name]) memberData[name] = { tasks: [], points: 0, done: 0, active: 0, todo: 0 };\n      memberData[name].tasks.push(t);\n      memberData[name].points += (t.points || 1);\n      if (t.status === \'已完成\' || t.status === \'已确认\') memberData[name].done++;\n      else if (t.status === \'进行中\') memberData[name].active++;\n      else memberData[name].todo++;\n    }\n  });'

idx = content.find(old_rm_start)
if idx >= 0:
    # Find the end of this broken code
    end_idx = content.find('function renderMembers() {', idx + 100)
    if end_idx < 0:
        end_idx = content.find('function isStaff2', idx + 100)
    # Replace from STAFF_NAMES2 to the start of the next proper renderMembers
    content = content[:idx] + '// (original renderMembers restored)\n' + content[end_idx:]
    print('Old broken renderMembers removed')
else:
    print('STAFF_NAMES2 not found - may already be fixed')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
