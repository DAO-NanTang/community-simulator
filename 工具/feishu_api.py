"""飞书多维表格 API 封装"""
import json, time, requests, os

class FeishuClient:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.cfg = json.load(f)
        self.token = None
        self.token_expires = 0
        self.base_url = "https://open.feishu.cn/open-apis"

    def _get_token(self):
        now = time.time()
        if self.token and now < self.token_expires - 300:
            return self.token
        resp = requests.post(f"{self.base_url}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.cfg['app_id'], "app_secret": self.cfg['app_secret']})
        data = resp.json()
        if data.get('code') != 0:
            raise Exception(f"Token error: {data}")
        self.token = data['tenant_access_token']
        self.token_expires = now + data.get('expire', 7200)
        return self.token

    def _request(self, method, url, body=None):
        headers = {'Authorization': f'Bearer {self._get_token()}',
                   'Content-Type': 'application/json; charset=utf-8'}
        for attempt in range(3):
            resp = requests.request(method, url, headers=headers, json=body)
            code = resp.json().get('code', -1)
            if code == 0:
                return resp.json()
            if code == 99991400:  # rate limit
                time.sleep(2 ** attempt)
                continue
            if code in (99991663, 99991668):  # token expired
                self.token = None
                headers['Authorization'] = f'Bearer {self._get_token()}'
                continue
            raise Exception(f"API error (code={code}): {resp.json()}")
        raise Exception(f"API failed after retries: {resp.json()}")

    def list_tables(self):
        """列出 Base 中所有表"""
        app_token = self.cfg['app_token']
        resp = self._request('GET',
            f"{self.base_url}/bitable/v1/apps/{app_token}/tables")
        return resp.get('data', {}).get('items', [])

    def create_table(self, name, fields_config):
        """在 Base 中新建一张表并设置字段"""
        app_token = self.cfg['app_token']
        # 1. 创建表
        resp = self._request('POST',
            f"{self.base_url}/bitable/v1/apps/{app_token}/tables",
            {"table": {"name": name}})
        table_id = resp['data']['table_id']
        # 2. 批量创建字段
        for field_name, field_type in fields_config:
            self._request('POST',
                f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
                {"field_name": field_name, "type": field_type})
        return table_id

    def get_records(self, table_id, page_size=500):
        """分页拉取所有记录"""
        app_token = self.cfg['app_token']
        records = []
        page_token = None
        while True:
            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size={page_size}"
            if page_token:
                url += f"&page_token={page_token}"
            resp = self._request('GET', url)
            items = resp.get('data', {}).get('items', [])
            records.extend(items)
            if not resp.get('data', {}).get('has_more'):
                break
            page_token = resp['data'].get('page_token')
        return records

    def upsert_records(self, table_id, key_field, records, field_map):
        """按 key_field 匹配：存在更新，不存在新建。field_map: {项目字段名: 飞书field_id}"""
        app_token = self.cfg['app_token']
        # 拉取现有记录建立索引
        existing = self.get_records(table_id)
        key_index = {}
        for rec in existing:
            fields = rec.get('fields', {})
            key_val = self._get_field_val(fields, key_field, field_map)
            if key_val:
                key_index[key_val] = rec['record_id']

        creates, updates = [], []
        for rec in records:
            key_val = rec.get(key_field, '')
            body = self._to_feishu_fields(rec, field_map)
            if key_val in key_index:
                updates.append((key_index[key_val], body))
            else:
                creates.append(body)

        results = {'created': 0, 'updated': 0}
        # 批量创建
        for i in range(0, len(creates), 500):
            batch = creates[i:i+500]
            resp = self._request('POST',
                f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
                {"records": [{"fields": b} for b in batch]})
            results['created'] += len(resp.get('data', {}).get('records', []))
        # 批量更新
        for i in range(0, len(updates), 500):
            batch = updates[i:i+500]
            resp = self._request('POST',
                f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
                {"records": [{"record_id": rid, "fields": body} for rid, body in batch]})
            results['updated'] += len(resp.get('data', {}).get('records', []))
        return results

    def _get_field_val(self, fs_fields, key, field_map):
        """从飞书字段中按项目字段名取值"""
        fid = field_map.get(key)
        if not fid: return None
        val = fs_fields.get(fid)
        if isinstance(val, list) and len(val) > 0:
            return val[0].get('text', '') if isinstance(val[0], dict) else val[0]
        return val

    def _to_feishu_fields(self, rec, field_map):
        """将项目字段记录转为飞书字段格式"""
        result = {}
        for key, val in rec.items():
            fid = field_map.get(key)
            if fid and val is not None:
                result[fid] = val if isinstance(val, (int, float)) else str(val)
        return result


# ── CLI usage ──
if __name__ == '__main__':
    client = FeishuClient()
    tables = client.list_tables()
    print(f"Tables in Base: {len(tables)}")
    for t in tables:
        print(f"  {t['name']} (id: {t['table_id']})")
