import re
path = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all function declarations
funcs = re.findall(r'function (\w+)\(', content)
print(f'Total function declarations: {len(funcs)}')
seen = {}
for f in funcs:
    seen[f] = seen.get(f, 0) + 1
dups = {k:v for k,v in seen.items() if v > 1}
if dups:
    print(f'DUPLICATE functions: {dups}')
else:
    print('No duplicate functions')

# Check for const redeclarations
consts = re.findall(r'^const (\w+)', content, re.MULTILINE)
seen2 = {}
for c in consts:
    seen2[c] = seen2.get(c, 0) + 1
dups2 = {k:v for k,v in seen2.items() if v > 1}
if dups2:
    print(f'DUPLICATE consts: {dups2}')

# Check key functions exist
needed = ['loadData','exportData','switchTab','renderTasks','renderMembers',
          'renderBudget','renderSettlementAll','renderCalendar','renderTimeline',
          'renderStrategyMap','renderPlayers','updateAll']
missing = [n for n in needed if f'function {n}(' not in content]
if missing:
    print(f'MISSING functions: {missing}')

# Check for syntax: mismatched braces
opens = content.count('{')
closes = content.count('}')
print(f'Braces: {{ {opens}, }} {closes} -> diff={opens-closes}')
