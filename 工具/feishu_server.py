"""本地 HTTP 代理：localhost:8765，桥接 Dashboard ↔ 飞书多维表格"""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from feishu_api import FeishuClient

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
client = None  # lazy init


def get_client():
    global client
    if client is None:
        client = FeishuClient(CONFIG_PATH)
    return client


def load_all():
    """从飞书加载所有数据，组装为 Dashboard 的 data 对象格式"""
    cli = get_client()
    cfg = cli.cfg
    app_token = cfg['app_token']
    result = {}

    for table_name, tcfg in cfg['tables'].items():
        tid = tcfg.get('table_id')
        if not tid:
            continue
        records = cli.get_records(tid)
        # 转字段名
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
        result[table_name] = items

    # 组装为 data 格式
    data_obj = {'tasks': [], 'members': {}, 'finance': [], 'budget': {}, 'decisions': [],
                'schedule': {}, 'finance_cny': {'transactions': []}, '_initialized': True}

    for u in result.get('用户表', []):
        data_obj['members'][u.get('姓名','')] = {
            'name': u.get('姓名',''), 'role': u.get('角色',''), 'gender': u.get('性别',''),
            'avatar_seed': u.get('头像种子',0), 'bio': u.get('个人简介','')
        }
    for t in result.get('任务表', []):
        data_obj['tasks'].append({
            'name': t.get('任务名称',''), 'assignee': t.get('负责人',''), 'points': int(t.get('NT积分',0) or 0),
            'deadline': t.get('截止日期',''), 'status': t.get('状态',''), 'category': t.get('任务分类',''),
            'source': t.get('来源',''), 'confirmer': t.get('确认人','')
        })
    for f in result.get('流水表', []):
        data_obj['finance_cny']['transactions'].append({
            'date': f.get('日期',''), 'type': f.get('类型',''), 'person': f.get('关联人员',''),
            'amount': f.get('金额',0), 'currency': f.get('货币','RMB'), 'description': f.get('事由','')
        })
    for d in result.get('决策表', []):
        data_obj['decisions'].append({
            'title': d.get('决策标题',''), 'type': d.get('决策类型',''), 'status': d.get('状态',''),
            'content': d.get('内容',''), 'resolution': d.get('决议','')
        })

    return data_obj


class FeishuHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self._cors()
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

        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        if self.path == '/api/save':
            try:
                data = json.loads(body_raw)
                cli = get_client()
                cfg = cli.cfg
                stats = {}

                # 任务表
                tcfg = cfg['tables']['任务表']
                if tcfg.get('table_id'):
                    records = []
                    for t in data.get('tasks', []):
                        records.append({
                            '任务名称': t.get('name',''), '负责人': t.get('assignee',''),
                            'NT积分': t.get('points',0), '状态': t.get('status',''),
                            '任务分类': t.get('category',''), '截止日期': t.get('deadline',''),
                            '来源': t.get('source',''), '确认人': t.get('confirmer','')
                        })
                    r = cli.upsert_records(tcfg['table_id'], '任务名称', records, tcfg['fields'])
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
                    r = cli.upsert_records(ucfg['table_id'], '姓名', records, ucfg['fields'])
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
                    r = cli.upsert_records(fcfg['table_id'], '事由', records, fcfg['fields'])
                    stats['流水表'] = r

                self.wfile.write(json.dumps({
                    'success': True, 'stats': stats
                }, ensure_ascii=False).encode())
            except Exception as e:
                self.wfile.write(json.dumps({
                    'success': False, 'error': str(e)
                }, ensure_ascii=False).encode())
        else:
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


if __name__ == '__main__':
    port = 8765
    server = HTTPServer(('127.0.0.1', port), FeishuHandler)
    print(f"FS Feishu proxy running at http://localhost:{port}")
    print(f"   GET  /api/load-all  → load data from Feishu")
    print(f"   POST /api/save      → save data to Feishu")
    print(f"   GET  /api/health    → health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBYE Server stopped")
        server.server_close()
