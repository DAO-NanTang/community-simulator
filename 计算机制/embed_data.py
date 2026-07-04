"""Embed data.json directly into dashboard.html"""
import json

# Read data.json
data_path = r'D:\桌面\共创营工具\data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Read the build_full.py template
# We'll replace the empty D variable with the real data
template_path = r'c:\Users\苏砚仁\thinknote\南塘 DAO\gnt计算机制\计算机制\build_full.py'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the D initialization
old = 'var D={tasks:[],members:{},budget:{},finance_cny:{},schedule:{}};'
new = 'var EMBEDDED_DATA=' + json.dumps(data, ensure_ascii=False) + ';'
new += 'var D=JSON.parse(JSON.stringify(EMBEDDED_DATA));'

content = content.replace(old, new)

# Also make loadOrCached use embedded data
old_cached = 'function loadOrCached(){var s=localStorage.getItem("camp_data");if(s){try{D=JSON.parse(s);switchTab("tasks");setStatus("已加载缓存 "+D.tasks.length+" 任务")}catch(e){}}}'
new_cached = 'function loadOrCached(){var s=localStorage.getItem("camp_data");if(s){try{D=JSON.parse(s)}catch(e){}}switchTab("tasks");setStatus("已加载 "+D.tasks.length+" 任务 (内嵌数据)")}'

content = content.replace(old_cached, new_cached)

# Write updated build script
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Now generate the HTML
import sys
html = None
exec(open(template_path, encoding='utf-8').read())

# Save to desktop
output = r'D:\桌面\共创营工具\dashboard.html'
# Read the generated HTML from the build script
# Actually we can't easily extract the html variable. Let me re-run the build.
print('Template updated. Run build_full.py to regenerate.')
