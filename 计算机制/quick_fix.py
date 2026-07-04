"""Quick fix: add isStaff2 function to vault copy, save to Desktop"""
vault = r'C:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\工具\dashboard.html'
desktop = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'

with open(vault, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first script tag content
script_start = content.find('<script>')
if script_start < 0:
    print('No script tag found')
    exit()

# Add isStaff2 function right after the first script tag
isStaff2_code = '\nfunction isStaff2(n){var sn=["砚仁","朝林","小红","若曦","淑惠","跳大爷"];return sn.some(function(s){return n.includes(s)})}\n'
insert_pos = content.find('let data = {', script_start)
if insert_pos < 0:
    insert_pos = content.find('var data = {', script_start)
if insert_pos < 0:
    insert_pos = content.find('// ── State', script_start)
    if insert_pos > 0:
        insert_pos = content.find('\n', insert_pos + 20)

if insert_pos > 0:
    content = content[:insert_pos] + isStaff2_code + content[insert_pos:]
    print(f'Added isStaff2 at position {insert_pos}')
else:
    print('Could not find insertion point')

# Also fix any `isStaff2 is not defined` errors by ensuring the function is globally accessible
# Already done above

with open(desktop, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Saved to Desktop. Size: {len(content)} bytes')
print('Path: ' + desktop)
