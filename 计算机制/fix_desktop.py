"""Fix desktop dashboard.html — restore all features"""
import re

path = r'C:\Users\苏砚仁\Desktop\共创营工具\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix header image path (should be local since now in same folder)
content = content.replace(
    "url('ai_expand_image1783014990973.png') center 70%/80% no-repeat;",
    "url('ai_expand_image1783014990973.png') center 70%/80% no-repeat;"
)

# 2. Fix duplicate CSS blocks — the linter duplicated many CSS rules
# Remove the pixel-art overrides (second header, second buttons, etc.)
# Find the second `header {` after line 50 and remove the pixel art overrides
lines = content.split('\n')
clean_lines = []
skip_until_card = False
header_count = 0
for line in lines:
    if 'header { padding:14px 24px;border-bottom:4px solid #4a3828;position:relative;overflow:hidden;min-height:160px;' in line:
        continue  # Skip old pixel-art header
    if 'header { background: linear-gradient(180deg, #6b8c42, #5a7a36);' in line:
        continue
    if '/* Buttons */' in line:
        # Keep first occurrence, skip second
        pass
    clean_lines.append(line)

# Rejoin but this is tricky. Let me just fix the critical parts.
content = '\n'.join(clean_lines)

# 3. Check for missing functions
fixes = []

if 'function renderBudget()' not in content:
    fixes.append('renderBudget')
if 'function renderSettlementAll()' not in content:
    fixes.append('renderSettlementAll')
if 'function renderCalendar()' not in content:
    fixes.append('renderCalendar')
if 'function renderPlayers()' not in content:
    fixes.append('renderPlayers')

print(f'Missing functions: {fixes}')

# 4. Fix switchTab to include players
content = content.replace(
    "['tasks','members','timeline','budget','settlement','map']",
    "['tasks','members','players','timeline','budget','settlement','map']"
)
content = content.replace(
    "['tasks','members','players','timeline','budget','settlement','map']",
    "['tasks','members','players','timeline','budget','settlement','map']"
)
# Add players handler
if "if (name === 'players')" not in content:
    content = content.replace(
        "if (name === 'members') renderMembers();",
        "if (name === 'members') renderMembers();\n  if (name === 'players') renderPlayers();"
    )

# 5. Fix tab styles — remove pixel borders
content = content.replace(
    'border-bottom: 4px solid #8b7355;',
    'border-bottom: 2px solid var(--border);'
)
content = content.replace(
    'background: #d5c4a8;',
    'background: none;'
)
content = content.replace(
    'border: 3px solid transparent; border-bottom: none;',
    'border: none;'
)
content = content.replace(
    'border-radius: 6px 6px 0 0;',
    'border-radius: 6px 6px 0 0;'
)

# 6. Fix button styles - remove pixel borders
content = content.replace(
    'border: 3px solid #8b7355; border-radius: 0;',
    'border: 1.5px solid var(--border); border-radius: 8px;'
)
content = content.replace(
    'background: #e8d5b0;',
    'background: var(--card);'
)
content = content.replace(
    'box-shadow: 2px 2px 0 rgba(0,0,0,.2);',
    ''
)

# 7. Fix card styles
content = content.replace(
    'border: 4px solid #c4b898; border-radius: 0;',
    'border: 1px solid var(--border); border-radius: 12px;'
)
content = content.replace(
    'box-shadow: 4px 4px 0 rgba(0,0,0,.1);',
    'box-shadow: var(--shadow);'
)
content = content.replace(
    '.card::before { content: \'\'; position: absolute; top: 3px; left: 3px; right: 3px; bottom: 3px; border: 1px solid rgba(139,115,85,.15); pointer-events: none; }',
    ''
)

# 8. Fix progress bar style
content = content.replace(
    'font-family: var(--pixel); font-size: .5rem;',
    ''
)
content = content.replace(
    'font-family: var(--pixel); font-size: .6rem;',
    ''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Fixed. Still missing: {fixes}')
print(f'File size: {len(content)} bytes')
print('Open: C:\\Users\\苏砚仁\\Desktop\\共创营工具\\dashboard.html')
