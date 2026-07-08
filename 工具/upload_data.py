"""一次性上传现有 data.json + nt_users 到飞书（建表后运行一次即可）"""
import json, os
from feishu_api import FeishuClient


def _s(v, d=''):
    if v is None: return d
    return str(v)


def _i(v, d=0):
    try: return int(v or d)
    except: return d


def upload():
    client = FeishuClient()
    cfg = client.cfg

    data_path = os.path.join(os.path.dirname(__file__), 'data.json')
    if not os.path.exists(data_path):
        print("data.json not found.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取 nt_users
    nt_users = {}
    try:
        nt_users = json.loads(localStorage_get('nt_users') or '{}')
    except:
        nt_users = {}

    # 读取邀请码
    nt_invite = []
    nt_world = []
    try:
        nt_invite = json.loads(localStorage_get('nt_invite_codes') or '[]')
    except:
        pass
    try:
        nt_world = json.loads(localStorage_get('nt_world_codes') or '[]')
    except:
        pass

    stats = {}

    def _upsert(table_name, key_field, records):
        tcfg = cfg['tables'].get(table_name)
        if not tcfg or not tcfg.get('table_id') or not records:
            return None
        return client.upsert_records(tcfg['table_id'], key_field, records, tcfg['fields'])

    # ── 任务表 ──
    task_recs = []
    for t in data.get('tasks', []):
        task_recs.append({
            '任务名称': _s(t.get('name')), '任务类型': _s(t.get('type')),
            '任务分类': _s(t.get('category')), '负责人': _s(t.get('assignee')),
            '开始日期': _s(t.get('start')), '截止日期': _s(t.get('deadline')),
            '确认人': _s(t.get('confirmer')), 'NT积分': _i(t.get('points')),
            '状态': _s(t.get('status')), '来源': _s(t.get('source')),
            '备注': _s(t.get('note')), '范围': _s(t.get('scope'), 'camp'),
            '发布者': _s(t.get('poster')), '发布日期': _s(t.get('posted_at')),
            '最大可领人数': _i(t.get('max_slots')),
            '可见范围': _s(t.get('visibility'), 'all'),
            '审核人': _s(t.get('reviewer')),
            '是否启用': _s(t.get('active'), 'yes'),
            '最低季数': _i(t.get('min_season')),
            '领取记录': json.dumps(t.get('claimants') or [], ensure_ascii=False),
        })
    r = _upsert('任务表', '任务名称', task_recs)
    if r: stats['任务表'] = r

    # ── 用户表（含密码 + UID）──
    user_recs = []
    for name, m in (data.get('members') or {}).items():
        nu = nt_users.get(name) or {}
        user_recs.append({
            '姓名': name, '角色': _s(m.get('role')),
            '性别': _s(m.get('gender')), '头像种子': _i(m.get('avatar_seed')),
            '个人简介': _s(m.get('bio')), '钱包地址': _s(m.get('wallet')),
            '密码哈希': _s(nu.get('password')),
            'UID': _s(nu.get('uid')),
            '注册日期': _s(nu.get('created')),
            '所属营期': _s(nu.get('season')),
        })
    for name, nu in nt_users.items():
        if not any(r['姓名'] == name for r in user_recs):
            user_recs.append({
                '姓名': name, '角色': _s(nu.get('role')),
                '头像种子': _i(nu.get('avatar_seed')),
                '密码哈希': _s(nu.get('password')),
                'UID': _s(nu.get('uid')),
                '注册日期': _s(nu.get('created')),
                '所属营期': _s(nu.get('season')),
            })
    r = _upsert('用户表', '姓名', user_recs)
    if r: stats['用户表'] = r

    # ── NT流水表 ──
    nt_recs = []
    for tx in data.get('finance', []):
        nt_recs.append({
            '类型': _s(tx.get('type')), '发起方': _s(tx.get('from')),
            '接收方': _s(tx.get('to')), '金额': _i(tx.get('amount')),
            '关联任务': _s(tx.get('task_name')), '日期': _s(tx.get('date')),
            '确认人': _s(tx.get('confirmed_by')), '范围': _s(tx.get('scope'), 'camp'),
        })
    r = _upsert('NT流水表', '关联任务', nt_recs)
    if r: stats['NT流水表'] = r

    # ── RMB流水表 ──
    cny_recs = []
    for tx in (data.get('finance_cny', {}).get('transactions') or []):
        cny_recs.append({
            '日期': _s(tx.get('date')), '类型': _s(tx.get('type')),
            '事由': _s(tx.get('desc') or tx.get('description')),
            '金额': _i(tx.get('amount') or tx.get('rmb')),
            '货币': _s(tx.get('currency'), 'RMB'),
            '关联人员': _s(tx.get('person')),
        })
    r = _upsert('流水表', '事由', cny_recs)
    if r: stats['流水表'] = r

    # ── 预算表 ──
    budget_recs = []
    for bi in data.get('budget_items') or []:
        budget_recs.append({
            '项目名称': _s(bi.get('name')), '项目分类': _s(bi.get('type')),
            '预算金额': _i(bi.get('rmb')), '实际金额': _i(bi.get('nt')),
            '货币': 'RMB+NT', '所属营期': _s(bi.get('group')),
            '备注': _s(bi.get('note')),
        })
    r = _upsert('预算表', '项目名称', budget_recs)
    if r: stats['预算表'] = r

    # ── 预算参数表 ──
    param_recs = []
    for key, val in (data.get('budget') or {}).items():
        if key and val is not None:
            param_recs.append({'参数名': _s(key), '参数值': _i(val), '参数分类': '预算参数', '说明': ''})
    r = _upsert('预算参数表', '参数名', param_recs)
    if r: stats['预算参数表'] = r

    # ── 共建者卡片表 ──
    staff_recs = []
    for sc in data.get('staff_cards') or []:
        staff_recs.append({
            '姓名': _s(sc.get('name')), '角色': _s(sc.get('role')),
            '头像种子': _i(sc.get('avatar_seed')), '寄语': _s(sc.get('note')),
            'NT角色': True if _s(sc.get('role')) == 'NT' else False,
        })
    r = _upsert('共建者卡片表', '姓名', staff_recs)
    if r: stats['共建者卡片表'] = r

    # ── 邀请码表 ──
    invite_recs = []
    for code in nt_invite:
        invite_recs.append({'码值': _s(code), '类型': 'npc', '状态': '有效'})
    for code in nt_world:
        invite_recs.append({'码值': _s(code), '类型': 'world', '状态': '有效'})
    r = _upsert('邀请码表', '码值', invite_recs)
    if r: stats['邀请码表'] = r

    print("\nUpload results:")
    for table, r in stats.items():
        print(f"  {table}: {r.get('created',0)} created, {r.get('updated',0)} updated")
    print("\nDone!")


def localStorage_get(key):
    """模拟 localStorage.getItem —— 上传脚本无法访问浏览器，需手动导出"""
    fname = os.path.join(os.path.dirname(__file__), f'_local_{key}.json')
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            return f.read()
    return None


if __name__ == '__main__':
    print("提示：如果要从浏览器导出 localStorage 数据，请在 Dashboard 控制台执行：")
    print("  copy(JSON.stringify({nt_users: localStorage.nt_users, nt_invite_codes: localStorage.nt_invite_codes, nt_world_codes: localStorage.nt_world_codes}))")
    print("  然后粘贴保存为 _local_nt_users.json 等文件")
    print()
    upload()
