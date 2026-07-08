"""在飞书 Base 中创建全部 11 张表并设置字段，生成的 table_id/field_id 写入 feishu_config.json"""
import json, os
from feishu_api import FeishuClient

# 飞书字段类型: 1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 7=复选框, 8=多行文本, 11=附件, 15=自动编号, 17=公式

TABLE_DEFS = {
    "用户表": [
        ("姓名", 1), ("角色", 1), ("性别", 3), ("头像种子", 2),
        ("个人简介", 8), ("钱包地址", 1),
        ("密码哈希", 1),      # ← 新增：登录凭据
        ("UID", 1),           # ← 新增：不变身份标识
        ("注册日期", 1),      # ← 新增：注册时间
        ("所属营期", 1), ("备注", 8)
    ],
    "营地表": [
        ("营期名称", 1), ("时间范围", 1), ("开始日期", 5), ("结束日期", 5),
        ("持续天数", 2), ("营期状态", 3), ("备注", 8)
    ],
    "任务表": [
        ("任务名称", 1), ("任务类型", 3), ("任务分类", 3),
        ("负责人", 1), ("开始日期", 1), ("截止日期", 1),
        ("确认人", 1), ("NT积分", 2), ("状态", 3),
        ("来源", 1), ("备注", 8),
        ("范围", 3), ("发布者", 1), ("发布日期", 1),
        ("最大可领人数", 2), ("可见范围", 1), ("审核人", 1),
        ("是否启用", 3), ("最低季数", 2),
        ("领取记录", 8),
    ],
    "NT流水表": [
        ("类型", 3), ("发起方", 1), ("接收方", 1),
        ("金额", 2), ("关联任务", 1), ("日期", 1),
        ("确认人", 1), ("范围", 3),
    ],
    "流水表": [
        ("日期", 5), ("类型", 3), ("事由", 1),
        ("金额", 2), ("货币", 3), ("关联人员", 1), ("备注", 8)
    ],
    "预算表": [
        ("项目名称", 1), ("项目分类", 3), ("预算金额", 2),
        ("实际金额", 2), ("货币", 3), ("所属营期", 1), ("备注", 8)
    ],
    "预算参数表": [          # ← 新增：创世终端 Step1 参数
        ("参数名", 1), ("参数值", 2), ("参数分类", 3),
        ("货币类型", 3), ("说明", 8), ("备注", 8)
    ],
    "日程表": [
        ("记录类型", 3), ("天数序号", 2), ("日期", 1), ("星期", 1),
        ("时间段", 1), ("板块名称", 3), ("活动内容", 8),
        ("锚点标记", 1), ("备注", 8)
    ],
    "决策表": [
        ("决策标题", 1), ("决策类型", 3), ("提出人", 1), ("提出日期", 5),
        ("状态", 3), ("内容", 8), ("决议", 8), ("备注", 8)
    ],
    "共建者卡片表": [        # ← 新增：Wizard Step3 角色分配
        ("姓名", 1), ("角色", 3), ("头像种子", 2),
        ("寄语", 8), ("NT角色", 7), ("所属营期", 1), ("备注", 8)
    ],
    "邀请码表": [            # ← 新增：邀请码管理
        ("码值", 1), ("类型", 3), ("状态", 3), ("创建日期", 5), ("备注", 8)
    ],
}


def setup():
    config_path = os.path.join(os.path.dirname(__file__), 'feishu_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    for table_name in TABLE_DEFS:
        if table_name not in cfg['tables']:
            cfg['tables'][table_name] = {'table_id': '', 'key_field': '', 'fields': {}}

    client = FeishuClient(config_path)
    app_token = cfg['app_token']

    for table_name, fields in TABLE_DEFS.items():
        print(f"\n[TABLE] {table_name}")
        try:
            table_id = client.create_table(table_name, fields)
            cfg['tables'][table_name]['table_id'] = table_id
            print(f"   [OK] table_id: {table_id}")

            resp = client._request('GET',
                f"{client.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields")
            created_fields = resp.get('data', {}).get('items', [])
            for f in created_fields:
                fname = f.get('field_name', '')
                fid = f.get('field_id', '')
                if fname in cfg['tables'][table_name].get('fields', {}):
                    cfg['tables'][table_name]['fields'][fname] = fid
            print(f"   Fields: {len(created_fields)}")

        except Exception as e:
            print(f"   [FAIL] {e}")
            try:
                existing = client.list_tables()
                for t in existing:
                    if t['name'] == table_name:
                        cfg['tables'][table_name]['table_id'] = t['table_id']
                        print(f"   [EXISTS] {t['table_id']}")
                        break
            except:
                pass

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("\n[DONE] 11 tables configured. feishu_config.json saved.")


if __name__ == '__main__':
    setup()
