import re
path = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if not m:
    print('No script found')
    exit()

js = m.group(1)
lines = js.split('\n')
print(f'Script: {len(lines)} lines')

# Check for brace/paren balance
dq_count = js.count('"')
sq_count = js.count("'")
print(f'Double quotes: {dq_count} ({"EVEN" if dq_count%2==0 else "ODD - PROBLEM!"})')
print(f'Single quotes: {sq_count} ({"EVEN" if sq_count%2==0 else "ODD - PROBLEM!"})')
print(f'Braces: {js.count("{")} open, {js.count("}")} close (diff={js.count("{")-js.count("}")})')
print(f'Parens: {js.count("(")} open, {js.count(")")} close (diff={js.count("(")-js.count(")")})')

# Check for obvious errors
if 'isStaff2' in js: print('WARNING: isStaff2 still referenced')
if 'function loadData' in js: print('loadData: OK')
else: print('loadData: MISSING!')

# Check key functions
for fn in ['loadData','switchTab','renderTasks','renderMembers','renderPlayers','renderMap','renderBudget','renderSettlement','renderTimeline']:
    if f'function {fn}(' in js: print(f'  {fn}: OK')
    else: print(f'  {fn}: MISSING')
