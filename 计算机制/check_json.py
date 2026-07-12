import json
path = r'C:\Users\苏砚仁\Desktop\共创营工具\data.json'
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks = len(data.get('tasks', []))
    members = len(data.get('members', {}))
    print(f'OK: {tasks} tasks, {members} members')
except json.JSONDecodeError as e:
    print(f'JSON Error: {e}')
except Exception as e:
    print(f'Error: {e}')
