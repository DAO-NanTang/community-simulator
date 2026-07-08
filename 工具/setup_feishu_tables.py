"""在飞书 Base 中创建 7 张表并设置字段，生成的 table_id/field_id 写入 feishu_config.json"""
import json, os
from feishu_api import FeishuClient

TABLE_DEFS = {
    "用户表": [
        ("姓名", 1), ("用户类型", 3), ("性别", 3), ("角色", 1),
        ("头像种子", 2), ("个人简介", 1), ("所属营期", 1), ("备注", 1)
    ],
    "营地表": [
        ("营期名称", 1), ("时间范围", 1), ("开始日期", 5), ("结束日期", 5),
        ("营期状态", 3), ("备注", 1)
    ],
    "任务表": [
        ("记录类型", 3), ("任务名称", 1), ("任务对象", 3), ("任务分类", 3),
        ("NT积分", 2), ("状态", 3), ("负责人", 1), ("截止日期", 1),
        ("确认人", 1), ("来源", 1), ("备注", 1)
    ],
    "流水表": [
        ("日期", 5), ("类型", 3), ("事由", 1), ("金额", 2), ("货币", 3),
        ("收支方向", 3), ("关联人员", 1), ("关联任务", 1), ("备注", 1)
    ],
    "预算表": [
        ("项目名称", 1), ("项目分类", 3), ("预算金额", 2), ("实际金额", 2),
        ("货币", 3), ("所属营期", 1), ("备注", 1)
    ],
    "日程表": [
        ("记录类型", 3), ("天数序号", 2), ("日期", 1), ("星期", 1),
        ("时间段", 1), ("板块名称", 3), ("活动内容", 1), ("备注", 1)
    ],
    "决策表": [
        ("决策标题", 1), ("决策类型", 3), ("提出人", 1), ("提出日期", 5),
        ("状态", 3), ("内容", 1), ("决议", 1), ("备注", 1)
    ]
}
# 飞书字段类型: 1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 7=复选框, 8=多行文本, 11=附件, 15=自动编号, 17=公式


def setup():
    config_path = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    client = FeishuClient(config_path)
    app_token = cfg['app_token']

    for table_name, fields in TABLE_DEFS.items():
        print(f"\n[TABLE] Creating table: {table_name}")
        try:
            table_id = client.create_table(table_name, fields)
            cfg['tables'][table_name]['table_id'] = table_id
            print(f"   [OK] table_id: {table_id}")

            # 拉取已创建的字段以获取 field_id
            resp = client._request('GET',
                f"{client.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields")
            created_fields = resp.get('data', {}).get('items', [])
            for f in created_fields:
                fname = f.get('field_name', '')
                fid = f.get('field_id', '')
                if fname in cfg['tables'][table_name]['fields']:
                    cfg['tables'][table_name]['fields'][fname] = fid
            print(f"   Fields: {len(created_fields)} created")

        except Exception as e:
            print(f"   [FAIL] Failed: {e}")
            # 尝试查找已存在的表
            try:
                existing = client.list_tables()
                for t in existing:
                    if t['name'] == table_name:
                        cfg['tables'][table_name]['table_id'] = t['table_id']
                        print(f"   [EXISTS] Found existing: {t['table_id']}")
                        break
            except:
                pass

        # 每创建一张表就保存一次配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("\n[OK] Setup complete. config saved to feishu_config.json")


if __name__ == '__main__':
    setup()
