"""Restore missing functions that the linter reverted"""
path = r'C:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check what's missing
missing = []
for fn in ['renderBudget','renderSettlementAll','renderCalendar','renderTimeline','renderPlayers']:
    if f'function {fn}(' not in content:
        missing.append(fn)
print(f'Missing: {missing}')

# Quick fix: just verify the file has enough to load data
has_load = 'function loadData()' in content
has_switch = 'function switchTab' in content
print(f'loadData: {has_load}, switchTab: {has_switch}')

# The file is broken by the linter. Best approach: tell the user.
# But let me at least check what version we have
headers = content.split('\n')[:5]
print(f'First line: {headers[0]}')
print(f'Title: {content[content.find("<title>")+7:content.find("</title>")]}')
