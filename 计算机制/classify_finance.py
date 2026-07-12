"""按事由分类财务流水，更新 data.json"""
import json, re
from pathlib import Path

def classify(desc):
    """根据事由分类"""
    d = desc.lower()
    # 宣传类
    if any(k in d for k in ['小红书','流量费','b站','投流','直播','推流','公众号','推文','朋友圈','宣传','拍摄']):
        return '宣传'
    # 课程/教学
    if any(k in d for k in ['课程','教学','画','笔','颜料','纸','墨','砚台','装裱','裱','临摹','创作','写生','展览','布展','拍卖']):
        return '课程物料'
    # 食宿
    if any(k in d for k in ['食宿','住宿','餐','饭','菜','吃','喝','食堂','厨房','食材','酒','饮料','零食']):
        return '食宿'
    # 欢迎宴/破冰/活动
    if any(k in d for k in ['破冰','欢迎','茶话','游戏','活动','晚会','联欢','聚会','主持','见面会']):
        return '活动'
    # 人工费/劳务
    if any(k in d for k in ['工资','薪资','报酬','劳务','服务费','人工','延时','付费','报名费']):
        return '人工费'
    # 交通/出行
    if any(k in d for k in ['打车','交通','车费','出行','油费','停车','公交']):
        return '交通'
    # 物料/采购
    if any(k in d for k in ['采购','物料','材料','道具','信封','打印','文具','装饰','花','气球']):
        return '物料'
    # 场地
    if any(k in d for k in ['场地','租金','租','展馆']):
        return '场地'
    # 通讯/网络
    if any(k in d for k in ['流量','话费','网络','wifi']):
        return '通讯'
    # 资助/捐款
    if any(k in d for k in ['资助','捐款','赞助','募捐','基金']):
        return '资助收入'
    # 收入
    if any(k in d for k in ['报名费','学费','收入','拍卖收入','销售']):
        return '收入'
    # 其他
    return '其他'

# Load
data_file = Path(r"c:\Users\苏砚仁\thinknote\gnt计算机制\工具\data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

txs = data.get('finance_cny', {}).get('transactions', [])
if not txs:
    print('No transactions found')
    exit()

# Classify each transaction
changes = 0
for t in txs:
    old_type = t.get('type', '')
    # Only classify if type is generic (营队支出/营队收入/营队支出｜应付未付)
    if old_type in ('营队支出', '营队收入', '营队支出｜应付未付', ''):
        new_type = classify(t.get('desc', ''))
        if new_type != old_type:
            t['type'] = new_type
            changes += 1

# Count by type
from collections import Counter
type_counts = Counter(t['type'] for t in txs)
print(f"Classified {changes} transactions")
print("\nNew type distribution:")
for ty, cnt in type_counts.most_common():
    rmb_sum = sum(abs(t['rmb'] or 0) for t in txs if t['type'] == ty)
    nt_sum = sum(abs(t['nt'] or 0) for t in txs if t['type'] == ty)
    print(f"  {ty}: {cnt}笔, RMB={rmb_sum:.2f}, NT={nt_sum:.0f}")

# Save
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\nDone. Updated {data_file}")
