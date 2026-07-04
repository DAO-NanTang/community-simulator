"""Embed data.json into dashboard.html. Usage: python embed.py <data.json path> <output.html path> <template.py path>"""
import json, sys

data_path = sys.argv[1]
output_path = sys.argv[2]
tmpl_path = sys.argv[3]

# 1. Read data.json
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Data: {len(data.get("tasks",[]))} tasks')

# 2. Read template
with open(tmpl_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 3. Replace empty D with real data
old = 'var D={tasks:[],members:{},budget:{},finance_cny:{},schedule:{}};'
data_json = json.dumps(data, ensure_ascii=False)
new = 'var D=' + data_json + ';'
content = content.replace(old, new)

# 4. Update loadOrCached
old_cache = 'function loadOrCached(){var s=localStorage.getItem("camp_data");if(s){try{D=JSON.parse(s);switchTab("tasks");setStatus("已加载缓存 "+D.tasks.length+" 任务")}catch(e){}}}'
new_cache = 'function loadOrCached(){switchTab("tasks");setStatus("已加载 "+D.tasks.length+" 任务")}'
content = content.replace(old_cache, new_cache)

# 5. Exec to generate HTML
namespace = {}
exec(content, namespace)
html = namespace.get('html', '')

if html:
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Done! {len(html)} bytes')
else:
    print('ERROR: no html var')
