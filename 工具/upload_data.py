"""一次性上传现有数据到飞书"""
import json, os
from feishu_api import FeishuClient

def upload():
    client = FeishuClient()
    cfg = client.cfg

    # 读取现有数据
    data_path = os.path.join(os.path.dirname(__file__), 'data.json')
    if not os.path.exists(data_path):
        print("❌ data.json not found, trying localStorage...")
        print("Please export data from Dashboard first (齿轮 → 导出数据)")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {}

    # 任务表
    tcfg = cfg['tables']['任务表']
    if tcfg.get('table_id'):
        records = []
        for t in data.get('tasks', []):
            records.append({
                '任务名称': t.get('name',''), 'NT积分': t.get('points',0),
                '状态': t.get('status',''), '任务分类': t.get('category',''),
                '负责人': t.get('assignee',''), '截止日期': t.get('deadline',''),
                '来源': t.get('source',''), '确认人': t.get('confirmer','')
            })
        r = client.upsert_records(tcfg['table_id'], '任务名称', records, tcfg['fields'])
        stats['任务表'] = r

    # 用户表
    ucfg = cfg['tables']['用户表']
    if ucfg.get('table_id'):
        records = []
        for name, m in (data.get('members') or {}).items():
            records.append({
                '姓名': name, '角色': m.get('role',''), '性别': m.get('gender',''),
                '头像种子': m.get('avatar_seed',0), '个人简介': m.get('bio','')
            })
        r = client.upsert_records(ucfg['table_id'], '姓名', records, ucfg['fields'])
        stats['用户表'] = r

    # 流水表
    fcfg = cfg['tables']['流水表']
    if fcfg.get('table_id'):
        records = []
        for tx in (data.get('finance_cny', {}).get('transactions') or []):
            records.append({
                '日期': tx.get('date',''), '类型': tx.get('type',''),
                '事由': tx.get('description',''), '金额': tx.get('amount',0),
                '关联人员': tx.get('person','')
            })
        r = client.upsert_records(fcfg['table_id'], '事由', records, fcfg['fields'])
        stats['流水表'] = r

    print("\n📊 Upload stats:")
    for table, r in stats.items():
        print(f"   {table}: {r.get('created',0)} created, {r.get('updated',0)} updated")


if __name__ == '__main__':
    upload()
