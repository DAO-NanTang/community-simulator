"""本地 HTTP 代理：localhost:8765，桥接 Dashboard ↔ 飞书多维表格（11 张表完整版）"""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from feishu_api import FeishuClient

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
client = None


def get_client():
    global client
    if client is None:
        client = FeishuClient(CONFIG_PATH)
    return client


def _s(v, d=''):
    if v is None: return d
    return str(v)


def _i(v, d=0):
    try: return int(v or d)
    except: return d


def _read_table(table_name):
    """读取一张表，返回 [{字段名: 值}, ...]"""
    cli = get_client()
    cfg = cli.cfg
    tcfg = cfg['tables'].get(table_name)
    if not tcfg or not tcfg.get('table_id'):
        return []
    records = cli.get_records(tcfg['table_id'])
    rev_map = {v: k for k, v in tcfg['fields'].items()}
    items = []
    for rec in records:
        fs_fields = rec.get('fields', {})
        item = {}
        for fid, val in fs_fields.items():
            name = rev_map.get(fid, fid)
            if isinstance(val, list) and len(val) > 0:
                item[name] = val[0].get('text', val[0]) if isinstance(val[0], dict) else val[0]
            else:
                item[name] = val
        items.append(item)
    return items


def load_all():
    """从飞书加载所有数据，组装为 Dashboard 的 data 对象 + nt_users"""
    # ── 读取各表 ──
    users_data    = _read_table('用户表')
    tasks_data    = _read_table('任务表')
    flow_nt_data  = _read_table('NT流水表')
    flow_cny_data = _read_table('流水表')
    budget_data   = _read_table('预算表')
    budget_params = _read_table('预算参数表')
    decisions_data= _read_table('决策表')
    schedule_data = _read_table('日程表')
    camp_data     = _read_table('营地表')
    staff_data    = _read_table('共建者卡片表')
    invite_data   = _read_table('邀请码表')

    # ── 组装 data 对象 ──
    data_obj = {
        'tasks': [], 'members': {}, 'finance': [], 'finance_cny': {'transactions': []},
        'budget': {}, 'budget_items': [], 'decisions': [], 'schedule': {},
        'camp_progress': {'step': 1, 'steps': {'1':'active','2':'locked','3':'locked','4':'locked','5':'locked'}},
        'camp_dates': {'start': '', 'end': '', 'duration_days': 15, 'milestones': []},
        'staff_cards': [], '_initialized': True,
        # 附带的 localStorage 数据
        '_nt_users': {},
        '_nt_invite_codes': [],
        '_nt_world_codes': [],
    }

    # ── 用户表 → data.members + _nt_users ──
    for u in users_data:
        name = _s(u.get('姓名'))
        if not name: continue
        data_obj['members'][name] = {
            'name': name, 'role': _s(u.get('角色')),
            'gender': _s(u.get('性别')), 'avatar_seed': _i(u.get('头像种子')),
            'bio': _s(u.get('个人简介')), 'wallet': _s(u.get('钱包地址')),
        }
        data_obj['_nt_users'][name] = {
            'name': name, 'role': _s(u.get('角色')),
            'password': _s(u.get('密码哈希')), 'uid': _s(u.get('UID')),
            'avatar_seed': _i(u.get('头像种子')),
            'season': _s(u.get('所属营期')), 'created': _s(u.get('注册日期')),
        }

    # ── 任务表 → data.tasks ──
    for t in tasks_data:
        try:
            claimants = json.loads(_s(t.get('领取记录'))) if _s(t.get('领取记录')) else []
        except:
            claimants = []
        data_obj['tasks'].append({
            'name': _s(t.get('任务名称')), 'type': _s(t.get('任务类型')),
            'category': _s(t.get('任务分类')), 'assignee': _s(t.get('负责人')),
            'start': _s(t.get('开始日期')), 'deadline': _s(t.get('截止日期')),
            'confirmer': _s(t.get('确认人')), 'points': _i(t.get('NT积分')),
            'status': _s(t.get('状态')), 'source': _s(t.get('来源')),
            'note': _s(t.get('备注')), 'scope': _s(t.get('范围'), 'camp'),
            'poster': _s(t.get('发布者')), 'posted_at': _s(t.get('发布日期')),
            'max_slots': _i(t.get('最大可领人数')),
            'visibility': _s(t.get('可见范围'), 'all'),
            'reviewer': _s(t.get('审核人')),
            'active': _s(t.get('是否启用'), 'yes'),
            'min_season': _i(t.get('最低季数')),
            'claimants': claimants,
            'materials': [], 'subtasks': [], 'outputs': [], 'steps': '',
        })

    # ── NT流水表 → data.finance ──
    for f in flow_nt_data:
        data_obj['finance'].append({
            'type': _s(f.get('类型')), 'from': _s(f.get('发起方')),
            'to': _s(f.get('接收方')), 'amount': _i(f.get('金额')),
            'task_name': _s(f.get('关联任务')), 'date': _s(f.get('日期')),
            'confirmed_by': _s(f.get('确认人')), 'scope': _s(f.get('范围'), 'camp'),
        })

    # ── RMB流水表 → data.finance_cny ──
    for f in flow_cny_data:
        data_obj['finance_cny']['transactions'].append({
            'date': _s(f.get('日期')), 'type': _s(f.get('类型')),
            'person': _s(f.get('关联人员')),
            'amount': _i(f.get('金额')), 'currency': _s(f.get('货币'), 'RMB'),
            'desc': _s(f.get('事由')),
        })

    # ── 预算表 → data.budget_items ──
    for b in budget_data:
        data_obj['budget_items'].append({
            'id': _i(b.get('项目名称'), 0) if b.get('项目名称','').isdigit() else 0,
            'name': _s(b.get('项目名称')),
            'type': _s(b.get('项目分类')),
            'rmb': _i(b.get('预算金额')), 'nt': _i(b.get('实际金额')),
            'group': _s(b.get('所属营期')), 'note': _s(b.get('备注')),
            'calcType': 'fixed', 'isCustom': False,
        })

    # ── 预算参数表 → data.budget ──
    for p in budget_params:
        key = _s(p.get('参数名'))
        val = _i(p.get('参数值'))
        if key: data_obj['budget'][key] = val

    # ── 日程表 → data.schedule ──
    schedule = {'dates': [], 'weekdays': [], 'slots': []}
    for s in schedule_data:
        day_idx = _i(s.get('天数序号'))
        date_str = _s(s.get('日期'))
        if date_str and date_str not in schedule['dates']:
            schedule['dates'].append(date_str)
        weekday = _s(s.get('星期'))
        if weekday and weekday not in schedule['weekdays']:
            schedule['weekdays'].append(weekday)
        time_slot = _s(s.get('时间段'))
        section = _s(s.get('板块名称'))
        activity = _s(s.get('活动内容'))
        if time_slot:
            existing = [sl for sl in schedule['slots'] if sl.get('time') == time_slot]
            if existing:
                if not existing[0].get('sections'):
                    existing[0]['sections'] = {}
                if section not in existing[0]['sections']:
                    existing[0]['sections'][section] = []
                if activity:
                    existing[0]['sections'][section].append(activity)
            else:
                slot = {'time': time_slot}
                if section:
                    slot['sections'] = {section: [activity] if activity else []}
                schedule['slots'].append(slot)
    data_obj['schedule'] = schedule

    # ── 决策表 → data.decisions ──
    for d in decisions_data:
        data_obj['decisions'].append({
            'title': _s(d.get('决策标题')), 'type': _s(d.get('决策类型')),
            'status': _s(d.get('状态')), 'content': _s(d.get('内容')),
            'resolution': _s(d.get('决议')), 'date': _s(d.get('提出日期')),
            'proposer': _s(d.get('提出人')),
        })

    # ── 营地表 → data.camp_dates ──
    if camp_data:
        c = camp_data[0]
        data_obj['camp_dates'] = {
            'start': _s(c.get('开始日期')), 'end': _s(c.get('结束日期')),
            'duration_days': _i(c.get('持续天数'), 15), 'milestones': [],
        }

    # ── 共建者卡片表 → data.staff_cards ──
    for sc in staff_data:
        data_obj['staff_cards'].append({
            'name': _s(sc.get('姓名')), 'role': _s(sc.get('角色')),
            'avatar_seed': _i(sc.get('头像种子')), 'note': _s(sc.get('寄语')),
            '_nt_salary': 0,
        })

    # ── 邀请码表 → _nt_invite_codes / _nt_world_codes ──
    for inv in invite_data:
        code_type = _s(inv.get('类型'))
        code_val = _s(inv.get('码值'))
        if code_type == 'npc':
            data_obj['_nt_invite_codes'].append(code_val)
        elif code_type == 'world':
            data_obj['_nt_world_codes'].append(code_val)

    return data_obj


# ═══════════════════════════════════════════
# HTTP Handler
# ═══════════════════════════════════════════

class FeishuHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        self.send_response(200); self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        if self.path == '/api/health':
            self.wfile.write(json.dumps({'status': 'ok'}, ensure_ascii=False).encode())
        elif self.path == '/api/load-all':
            try:
                data = load_all()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}, ensure_ascii=False).encode())
        else:
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body_raw = self.rfile.read(content_len) if content_len > 0 else b'{}'

        self.send_response(200); self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        if self.path == '/api/save':
            try:
                data = json.loads(body_raw)
                cli = get_client()
                cfg = cli.cfg
                stats = {}

                def _upsert(table_name, key_field, records):
                    tcfg = cfg['tables'].get(table_name)
                    if not tcfg or not tcfg.get('table_id') or not records:
                        return None
                    return cli.upsert_records(tcfg['table_id'], key_field, records, tcfg['fields'])

                # ── 任务表 ──
                task_recs = []
                for t in data.get('tasks', []):
                    claimants_json = json.dumps(t.get('claimants') or [], ensure_ascii=False)
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
                        '领取记录': claimants_json,
                    })
                r = _upsert('任务表', '任务名称', task_recs)
                if r: stats['任务表'] = r

                # ── 用户表（含密码 + UID）──
                user_recs = []
                # 先从 data.members 取基本字段
                for name, m in (data.get('members') or {}).items():
                    rec = {
                        '姓名': name, '角色': _s(m.get('role')),
                        '性别': _s(m.get('gender')),
                        '头像种子': _i(m.get('avatar_seed')),
                        '个人简介': _s(m.get('bio')),
                        '钱包地址': _s(m.get('wallet')),
                    }
                    user_recs.append(rec)
                # 再从 _nt_users 补充密码/UID/注册日期
                nt_users = data.get('_nt_users') or {}
                for rec in user_recs:
                    uname = rec['姓名']
                    nu = nt_users.get(uname) or {}
                    rec['密码哈希'] = _s(nu.get('password') or nu.get('_password'))
                    rec['UID'] = _s(nu.get('uid') or nu.get('_uid'))
                    rec['注册日期'] = _s(nu.get('created'))
                    rec['所属营期'] = _s(nu.get('season'))
                # 处理只在 _nt_users 里、不在 members 里的人
                for uname, nu in nt_users.items():
                    if not any(r['姓名'] == uname for r in user_recs):
                        user_recs.append({
                            '姓名': uname, '角色': _s(nu.get('role')),
                            '头像种子': _i(nu.get('avatar_seed')),
                            '密码哈希': _s(nu.get('password') or nu.get('_password')),
                            'UID': _s(nu.get('uid') or nu.get('_uid')),
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

                # ── 预算表（budget_items）──
                budget_recs = []
                for bi in (data.get('budget_items') or []):
                    budget_recs.append({
                        '项目名称': _s(bi.get('name')),
                        '项目分类': _s(bi.get('type')),
                        '预算金额': _i(bi.get('rmb')),
                        '实际金额': _i(bi.get('nt')),
                        '货币': 'RMB+NT',
                        '所属营期': _s(bi.get('group')),
                        '备注': _s(bi.get('note')),
                    })
                r = _upsert('预算表', '项目名称', budget_recs)
                if r: stats['预算表'] = r

                # ── 预算参数表（budget）──
                param_recs = []
                for key, val in (data.get('budget') or {}).items():
                    if key and val is not None:
                        param_recs.append({
                            '参数名': _s(key), '参数值': _i(val),
                            '参数分类': '预算参数', '说明': '',
                        })
                r = _upsert('预算参数表', '参数名', param_recs)
                if r: stats['预算参数表'] = r

                # ── 共建者卡片表 ──
                staff_recs = []
                for sc in (data.get('staff_cards') or []):
                    staff_recs.append({
                        '姓名': _s(sc.get('name')), '角色': _s(sc.get('role')),
                        '头像种子': _i(sc.get('avatar_seed')),
                        '寄语': _s(sc.get('note')),
                        'NT角色': True if _s(sc.get('role')) == 'NT' else False,
                    })
                r = _upsert('共建者卡片表', '姓名', staff_recs)
                if r: stats['共建者卡片表'] = r

                # ── 邀请码表 ──
                invite_recs = []
                for code in (data.get('_nt_invite_codes') or []):
                    invite_recs.append({'码值': _s(code), '类型': 'npc', '状态': '有效'})
                for code in (data.get('_nt_world_codes') or []):
                    invite_recs.append({'码值': _s(code), '类型': 'world', '状态': '有效'})
                r = _upsert('邀请码表', '码值', invite_recs)
                if r: stats['邀请码表'] = r

                self.wfile.write(json.dumps({
                    'success': True, 'stats': stats
                }, ensure_ascii=False).encode())
            except Exception as e:
                import traceback
                self.wfile.write(json.dumps({
                    'success': False, 'error': str(e), 'traceback': traceback.format_exc()
                }, ensure_ascii=False).encode())
        else:
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    port = 8765
    server = HTTPServer(('127.0.0.1', port), FeishuHandler)
    print(f"FS Feishu proxy running at http://localhost:{port}")
    print(f"   GET  /api/load-all  → load data from Feishu (11 tables)")
    print(f"   POST /api/save      → save data to Feishu (11 tables)")
    print(f"   GET  /api/health    → health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBYE Server stopped")
        server.server_close()
