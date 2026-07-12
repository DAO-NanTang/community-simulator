"""
gNT 投票权通知生成器

读取 gnt_stats.json + 工资 CSV，按模板生成 Notion 格式的通知 markdown。

用法：
  python generate_notification.py S5
  python generate_notification.py S5 --output S6季度gNT投票权通知.md
"""

import csv
import json
import re
import sys
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
SALARY_DIR = BASE_DIR / "工资条"

# ── 季度 → 月份映射 ──
# S4=2025Q4(10-12), S5=2026Q1(1-3), S6=2026Q2(4-6), ...
def quarter_to_months(season: str) -> tuple[int, int, int]:
    m = re.match(r"S(\d+)", season)
    if not m:
        return (1, 2, 3)
    s = int(m.group(1))
    # 每年 4 个季度; S1-4 = 2025, S5-8 = 2026, ...
    year_offset = (s - 1) // 4
    q_in_year = (s - 1) % 4  # 0=Q1, 1=Q2, 2=Q3, 3=Q4
    start_month = q_in_year * 3 + 1  # Q1→1, Q2→4, Q3→7, Q4→10
    return (start_month, start_month + 1, start_month + 2)


def month_label(m: int) -> str:
    return f"{m}月"


# ── 工资表别名 → 标准名（与 gnt_stats.py 的 NAME_MAPPING 保持一致） ──
CSV_NAME_MAP = {
    "cc": "CC",
    "kiko": "KIKO",
    "跳": "跳跳",
    "建桥": "健乔",
    "标哥": "杨云标",
}


def _normalize_csv_name(raw: str) -> str:
    """将工资 CSV 中的原始名映射为标准名"""
    return CSV_NAME_MAP.get(raw, raw)


def parse_salary_csv_for_months(season: str) -> dict:
    """读取工资 CSV，按季度内每个月汇总每人一般渠道 NT"""
    csv_files = sorted(SALARY_DIR.glob("*.csv"))
    months = quarter_to_months(season)
    result = {m: defaultdict(float) for m in months}

    for csv_file in csv_files:
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nt_str = row.get("NT", "").strip()
                if not nt_str or nt_str == "0":
                    continue
                nt = float(nt_str)
                quarter_raw = row.get("季度", "").strip()
                creditor = row.get("债权人", "").strip()

                # 只取属于目标季度的行
                if season not in quarter_raw:
                    continue

                # 提取月份
                month_match = re.search(r"(\d{1,2})月份", quarter_raw)
                if not month_match:
                    continue
                row_month = int(month_match.group(1))
                if row_month not in months:
                    continue

                # 提取人名（去掉 Notion 链接），并映射为标准名
                raw_name = creditor.split("(")[0].strip() if "(" in creditor else creditor
                name = _normalize_csv_name(raw_name)
                result[row_month][name] += nt

    return result


def get_month_nt(salary_by_month: dict, name: str, month: int) -> float:
    return salary_by_month.get(month, {}).get(name, 0)


def build_monthly_breakdown(season: str, qualified_names: list, gnt_results: dict) -> list:
    """为合格成员构建月度 NT 明细"""
    salary_by_month = parse_salary_csv_for_months(season)
    months = quarter_to_months(season)
    breakdown = []

    # 从 gnt_results 反查一般 NT，用于推算该成员在目标季度各月的 NT
    # gnt_results 中的 general_nt 已经按季度汇总，我们需要逐月拆分
    # 由于名字映射关系，需要用原始名查 CSV
    # 这里直接从 CSV 提取
    for name in qualified_names:
        month_vals = []
        total = 0
        for m in months:
            val = get_month_nt(salary_by_month, name, m)
            month_vals.append(val)
            total += val
        breakdown.append((name, month_vals, total))

    return breakdown


def generate_notification(season: str, json_path: str) -> str:
    """生成完整通知 markdown"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gnt_results = data["gnt_results"]
    quarterly = data["quarterly"]

    if season not in gnt_results:
        return f"错误：未找到 {season} 季度的核算数据。"

    results = gnt_results[season]
    qdata = quarterly.get(season, {})

    # 分离合格 / 不合格成员
    qualified = []
    unqualified = []
    for name, info in results.items():
        entry = {
            "name": name,
            "attend_count": qdata.get(name, {}).get("attend_count", 0),
            "effective_speech": qdata.get(name, {}).get("effective_speech_count", 0),
            "special_nt": info["special_nt"],
            "general_nt": info["general_nt"],
            "new_gnt": info["new_gnt"],
            "prev_retained": info["prev_retained"],
            "available_gnt": info["available_gnt"],
            "burned": info["burned"],
            "retained": info["retained"],
            "voting_power": info["voting_power"],
        }
        if info["voting_power"] > 0:
            qualified.append(entry)
        else:
            unqualified.append(entry)

    qualified.sort(key=lambda x: -x["voting_power"])
    unqualified.sort(key=lambda x: -x["available_gnt"])

    # 计算下一季度编号
    s_num = int(re.match(r"S(\d+)", season).group(1))
    next_season = f"S{s_num + 1}"
    next_months = quarter_to_months(next_season)

    # 通知发布日期
    publish_date = datetime.now().strftime("%Y 年 %m 月 %d 日")

    # 季度对应月份
    months = quarter_to_months(season)
    month_range = f"{months[0]}–{months[2]} 月"

    # ── 构建 markdown ──
    lines = []
    lines.append(f"## 2026 年 {next_season} 季度（{months[0]}–{months[2]} 月）gNT 投票权公示")
    lines.append("")
    lines.append("### 一、核心规则重申")
    lines.append("")
    lines.append(f"- **投票资格门槛**：累积可用 gNT ≥ {int(GNT_BURN_THRESHOLD)}，即累积 NT ≥ {int(GNT_BURN_THRESHOLD * 2)}。")
    lines.append("- **需打入多签钱包的 gNT 额度**（必须**精确**，多一分或少一分均不计算票权）。")
    lines.append("- **不满足门槛者**无需打入，可保留自己的 NT，不参与本季度投票。")
    lines.append(f"- **gNT 多签钱包地址**：`{MULTISIG_ADDR}`")
    lines.append(f"- **多签人**：{MULTISIG_COORDINATORS}")
    lines.append("")
    lines.append("![[ScreenShot_2026-04-11_181508_219.png|152]]")
    lines.append("")

    # 二、票权结构
    lines.append("### 二、票权结构与燃烧机制说明")
    lines.append("")
    lines.append("#### 1. gNT 是怎么来的？")
    lines.append("")
    lines.append(f"每个季度末，系统对所有成员进行 gNT 核算。每个人的**新 gNT** = 特殊渠道 NT + 一般渠道 NT × 50%。")
    lines.append("")
    lines.append(f"- **特殊渠道 NT**（100% 兑换）：参加 DAO 会议（10 NT/次）+ 有效发言（单次会议发言 ≥ 3 次 = 1 次有效发言，+10 NT/次）。")
    lines.append("- **一般渠道 NT**（50% 兑换）：组长薪资等，按工资条发放。")
    lines.append("")
    lines.append("#### 2. 累积规则")
    lines.append("")
    lines.append(f"每季度，系统把**上季度剩余的 gNT** 与**本季度新产生的 gNT** 相加，得到**可用 gNT**：")
    lines.append("")
    lines.append("```")
    lines.append("可用 gNT = 本季度新 gNT + 上季度剩余 gNT")
    lines.append("```")
    lines.append("")
    lines.append("#### 3. 燃烧与投票权")
    lines.append("")
    lines.append(f"当可用 gNT 达到 **{int(GNT_BURN_THRESHOLD)}** 以上时，即可参与燃烧、获得票权：")
    lines.append("")
    lines.append("```")
    lines.append("燃烧量 = 可用 gNT × 50%")
    lines.append("票权  = √(燃烧量)")
    lines.append("下季保留 = 可用 gNT × 50%（锁定在多签钱包）")
    lines.append("```")
    lines.append("")
    lines.append("> **举例**：某成员可用 gNT = 2000，则需将 2000 gNT 打入多签钱包；其中 1000 被燃烧获得票权 = √1000 ≈ 31.62，另 1000 锁定在多签中作为下季保留。")
    lines.append("")
    lines.append("#### 4. 不足 500 的情况")
    lines.append("")
    lines.append("如果可用 gNT < 500：")
    lines.append("- **不燃烧、无票权、不打入多签。**")
    lines.append("- 本季度新增 gNT 作废，上季度保留继续滚存至下季度。")
    lines.append("")
    lines.append(f"#### 5. {season} 核算 → {next_season} 投票")
    lines.append("")
    lines.append(f"**{season} 季度（{month_range}）核算出的票权，在 {next_season} 季度（{next_months[0]}–{next_months[2]} 月）行使。** 获得投票权者需将 {season} 的**全部可用 gNT** 转入多签钱包。")
    lines.append("")

    # 三、统计周期
    lines.append("### 三、统计周期与范围")
    lines.append("")
    lines.append(f"- **核算周期**：2026年{months[0]}月1日 – 2026年{months[2]}月31日（{season} 季度）")
    lines.append(f"- **投票季度**：2026年{next_months[0]}月 – 2026年{next_months[2]}月（{next_season} 季度）")
    lines.append("")

    # 四、成员名单
    lines.append("### 四、成员名单与需打入金额")
    lines.append("")
    lines.append(f"#### ✅ 可铸造投票权的成员（可用 gNT ≥ {int(GNT_BURN_THRESHOLD)}）")
    lines.append("")
    lines.append(f'以下成员在 {season} 季度核算中可用 gNT 达到 {int(GNT_BURN_THRESHOLD)} 以上，获得了 {next_season} 季度投票权。请在公示期内将**下方“需打入多签 gNT”数额精确**转入多签钱包。未按期足额打入者，投票权资格失效。')
    lines.append("")
    lines.append(f"| 成员 | 出席 | 有效发言 | 特殊 NT | 一般 NT | 新 gNT | 需打入多签 gNT（全部可用 gNT） | 燃烧量 | {next_season} 票权 | 锁定下季 |")
    lines.append("|------|------|----------|---------|---------|--------|-------------------------------|--------|---------|----------|")

    for e in qualified:
        lines.append(
            f"| {e['name']} | {e['attend_count']} | {e['effective_speech']} "
            f"| {int(e['special_nt'])} | {int(e['general_nt'])} | {int(e['new_gnt'])} "
            f"| **{int(e['available_gnt'])}** | {int(e['burned'])} "
            f"| **{e['voting_power']:.2f}** | {int(e['retained'])} |"
        )

    lines.append("")
    lines.append(f"> **共 {len(qualified)} 人获得 {next_season} 季度投票权。**")
    lines.append(f"> - **票权 = √(燃烧量)**，燃烧量 = 需打入多签 gNT 的一半。")
    lines.append(f"> - **另一半锁定在多签钱包**，作为下季度（S{s_num + 2}）的保留 gNT 滚存。")
    lines.append("")

    # 不合格名单
    if unqualified:
        lines.append(f"#### ❌ 不能铸造投票权的成员（可用 gNT < {int(GNT_BURN_THRESHOLD)}）")
        lines.append("")
        lines.append(f"以下成员因 {season} 季度可用 gNT 不足 {int(GNT_BURN_THRESHOLD)}，**不满足投票门槛**，无需向多签钱包打入 gNT，可保留全部 NT。不参与本季度投票。")
        lines.append("")
        lines.append("| 成员 | 出席 | 有效发言 | 特殊 NT | 一般 NT | 新 gNT | 可用 gNT |")
        lines.append("|------|------|----------|---------|---------|--------|----------|")
        for e in unqualified:
            lines.append(
                f"| {e['name']} | {e['attend_count']} | {e['effective_speech']} "
                f"| {int(e['special_nt'])} | {int(e['general_nt'])} "
                f"| {int(e['new_gnt'])} | {int(e['available_gnt'])} |"
            )
        lines.append("")
        lines.append(
            f"> 以上 {len(unqualified)} 人因可用 gNT 不足 {int(GNT_BURN_THRESHOLD)}，"
            f"本季度不燃烧、无票权、无需打入多签。上季度保留部分将继续滚存至 {next_season} 季度，"
            f"{next_season} 若累积可用 gNT 达到 {int(GNT_BURN_THRESHOLD)} 即可重新获得投票权。"
        )
        lines.append("")
    else:
        lines.append(f"#### ❌ 不能铸造投票权的成员")
        lines.append("")
        lines.append("本季度所有成员均满足投票门槛。")
        lines.append("")

    # 五、操作与后续说明
    lines.append("### 五、操作与后续说明")
    lines.append("")
    lines.append("1. **打入期限**：公示期结束后第 1 个工作日（具体日期另行通知）前完成打入。")
    lines.append('2. **打入方式**：将上方“需打入多签 gNT”列的**精确数额**转入多签钱包地址。多签钱包内 NT 的 50% 统一划转至国库燃烧，50% 锁定作为下季保留。差额将导致票权资格失效。')
    lines.append("3. **票权计算**：成功打入后，当季有效票权 = √(燃烧 gNT 额度)。")
    lines.append("4. **公示与异议**：本公告公示期 3 个工作日。如有异议（如 NT 统计遗漏、人员合并错误等），请联系治理组运营专员核实。")
    lines.append("5. **投票责任**：获得投票权者应积极参与当季提案。连续两季度投票率低于 30% 的，冻结下一季度投票资格。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 月度明细表
    lines.append(f"## 2026 年 {month_range} NT 累计明细（核对版）")
    lines.append("")

    # 解析月度数据
    salary_by_month = parse_salary_csv_for_months(season)
    qualified_names = [e["name"] for e in qualified]

    # 构建月度明细（用一般 NT 逐月拆分）
    detail_rows = []
    for e in qualified:
        name = e["name"]
        mv = []
        total = 0
        for m in months:
            val = get_month_nt(salary_by_month, name, m)
            mv.append(val)
            total += val
        detail_rows.append((name, mv, total))

    # 月度表头
    header_parts = ["成员"]
    for m in months:
        header_parts.append(f"{m} 月 NT")
    header_parts.append("**总计 NT**")
    header_parts.append("备注")
    lines.append("| " + " | ".join(header_parts) + " |")
    lines.append("| " + " | ".join(["----"] * len(header_parts)) + " |")

    for name, mv, total in detail_rows:
        month_strs = []
        for i, m in enumerate(months):
            v = mv[i]
            if v > 0:
                month_strs.append(str(int(v)))
            else:
                month_strs.append("0")

        # 检查该月该人是否有 >1 条记录，有则用括号标注
        for i, m in enumerate(months):
            if mv[i] > 0:
                records_for_month = 0
                for csv_file in sorted(SALARY_DIR.glob("*.csv")):
                    with open(csv_file, "r", encoding="utf-8-sig") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            q_raw = row.get("季度", "").strip()
                            if season not in q_raw:
                                continue
                            m_match = re.search(r"(\d{1,2})月份", q_raw)
                            if not m_match or int(m_match.group(1)) != m:
                                continue
                            creditor = row.get("债权人", "").strip()
                            raw = creditor.split("(")[0].strip()
                            normalized = _normalize_csv_name(raw)
                            if normalized == name:
                                records_for_month += 1
                if records_for_month > 1:
                    vals = []
                    for csv_file in sorted(SALARY_DIR.glob("*.csv")):
                        with open(csv_file, "r", encoding="utf-8-sig") as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                q_raw = row.get("季度", "").strip()
                                if season not in q_raw:
                                    continue
                                m_match = re.search(r"(\d{1,2})月份", q_raw)
                                if not m_match or int(m_match.group(1)) != m:
                                    continue
                                creditor = row.get("债权人", "").strip()
                                raw = creditor.split("(")[0].strip()
                                normalized = _normalize_csv_name(raw)
                                if normalized == name:
                                    nt_str = row.get("NT", "0").strip()
                                    vals.append(nt_str)
                    if len(vals) > 1:
                        month_strs[i] = f"{int(mv[i])}（{' + '.join(vals)}）"

        parts = [name] + month_strs + [f"**{int(total)}**", ""]
        lines.append("| " + " | ".join(parts) + " |")

    lines.append("")
    lines.append("> **说明**：")
    lines.append(f"> - 以上仅统计 {season} 季度（{month_range}）的一般渠道 NT（工资条），不含特殊渠道 NT（会议出席/发言）。")
    lines.append(f"> - 完整 gNT 核算同时计入特殊渠道 NT + 一般渠道 NT × 50%。")
    lines.append(f"> - 若您对本人累计 NT 有异议，请在公示期内联系治理组运营专员，并提供相应凭证。")
    lines.append(f"> - 此明细用于后续投票权资格核对（资格门槛：累积可用 gNT ≥ {int(GNT_BURN_THRESHOLD)}）。")
    lines.append("")
    lines.append(f"**发布单位**：治理组")
    lines.append(f"**发布日期**：{publish_date}")

    return "\n".join(lines)


# ── 配置（与 gnt_stats.py 保持一致） ──
GNT_BURN_THRESHOLD = 500
MULTISIG_ADDR = "oeth:0x637c0ECa93C834d4E96D5312AA4FEBaC69322f11"
MULTISIG_COORDINATORS = "砚仁，建乔"


def main():
    parser = argparse.ArgumentParser(description="生成 gNT 投票权通知")
    parser.add_argument("season", help="核算季度编号，如 S5（S5 的票权在 S6 使用）")
    parser.add_argument("--json", default=None, help="gnt_stats.json 路径（默认自动查找）")
    parser.add_argument("--output", "-o", default=None, help="输出文件名（默认 auto）")
    args = parser.parse_args()

    # 定位 JSON
    if args.json:
        json_path = Path(args.json)
    else:
        json_path = SCRIPT_DIR / "gnt_stats.json"

    if not json_path.exists():
        print(f"错误：未找到 {json_path}")
        print("请先运行 gnt_stats.py 生成核算数据。")
        sys.exit(1)

    # 生成通知
    md = generate_notification(args.season, str(json_path))

    # 输出
    if args.output:
        out_path = SCRIPT_DIR / args.output
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"已保存: {out_path}")
    else:
        # 默认文件名
        s_num = re.match(r"S(\d+)", args.season)
        next_s = f"S{int(s_num.group(1)) + 1}" if s_num else "next"
        out_path = SCRIPT_DIR / f"{next_s}季度gNT投票权通知.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"已保存: {out_path}")

    print()
    print(md)


if __name__ == "__main__":
    main()
