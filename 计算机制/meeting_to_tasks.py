"""
会议记录 → 任务 JSON 提取流水线
===================================

从 iMeeting 发言记录中提取结构化任务信息，输出 dashboard.html 可用的 data.json。

两种运行模式：
  基础模式（零依赖）：正则匹配，立即可用
  AI 增强模式（可选）：BGE-M3 语义搜索 + Qwen2.5 智能提取

用法：
  python meeting_to_tasks.py                          # 基础模式，处理所有会议记录
  python meeting_to_tasks.py 会议记录/某个文件.md      # 处理单个文件
  python meeting_to_tasks.py --ai                     # AI 增强模式（需先安装依赖）
  python meeting_to_tasks.py --setup                  # 安装 AI 增强模式依赖
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ──────────────────────────────────────────────
# 路径配置
# ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
RECORD_DIR = BASE_DIR.parent / "会议记录"
OUTPUT_DIR = BASE_DIR / "工具"
OUTPUT_FILE = OUTPUT_DIR / "data.json"

# ──────────────────────────────────────────────
# 任务提取规则（基础模式）
# ──────────────────────────────────────────────

# 任务关键词——命中任意一个说明这段发言在讲任务
TASK_KEYWORDS = [
    "任务", "分工", "负责", "认领", "完成", "截止",
    "宣传", "文案", "拍摄", "课程", "预算", "物料",
    "结项", "复盘", "招生", "签到", "接待", "采购",
    "微信", "公众号", "设计", "海报", "视频",
    "动员会", "同步会", "日程", "会场", "住宿",
    "必须做", "要做", "需要做", "安排", "跟进",
    "分包", "兜底",
]

# 任务分类模式
TASK_CATEGORIES = {
    "宣传": ["宣传", "文案", "拍摄", "照片", "公众号", "海报", "视频", "推文", "小红书", "朋友圈"],
    "课程": ["课程", "教学", "共创人", "上课", "教案", "课件"],
    "生活": ["住宿", "餐饮", "打车", "采购", "物料", "场地", "接待", "签到"],
    "财务": ["预算", "支出", "收入", "学费", "资助", "报销", "费用", "成本"],
    "管理": ["会议", "议程", "动议", "表决", "主持", "记录", "通知"],
    "结项": ["结项", "复盘", "报告", "总结", "模板"],
}

# 人员名单（从 gnt_stats.py 名字映射表提取 + 常见外部人员）
KNOWN_MEMBERS = [
    "砚仁", "淑惠", "和光同尘", "跳跳", "小红",
    "富章", "付珍", "风筝", "付丹", "兵哥", "刘兵", "刘斌",
    "甘雨", "亭真", "杨云标", "张超", "慢慢", "刘宇",
    "小洪", "朝林", "建乔", "虹阳", "高琳", "杨振", "必兵",
]


def find_person_in_text(text):
    """在文本中查找已知人员名字"""
    found = []
    for name in KNOWN_MEMBERS:
        if name in text:
            found.append(name)
    return list(set(found))


def is_noise_text(text):
    """过滤噪音：太短、纯标点、纯语气词、问句碎片"""
    text = text.strip()
    if len(text) < 4:
        return True
    if re.match(r'^[?？!！.。,，、…\s]+$', text):
        return True
    if re.match(r'^(嗯|啊|哦|呃|OK|ok|好的|对的|可以|没问题|是的)[\s，。,]*$', text):
        return True
    # 以问号结尾且<10字的碎片
    if text.endswith("？") and len(text) < 10:
        return True
    return False


def extract_decisions(md_text, source_file):
    """从会议记录中提取正式通过的动议/决策"""
    decisions = []

    # 模式1：通过的主动议代码块
    for match in re.finditer(r'通过的主动议[：:]?\s*\n?\s*```\s*\n(.*?)```', md_text, re.DOTALL):
        decisions.append({
            "type": "主动议",
            "content": match.group(1).strip(),
            "source": source_file,
            "status": "通过",
        })

    # 模式2：通过的修正案
    for match in re.finditer(r'通过的修正案[：:]?\s*\n?\s*```\s*\n(.*?)```', md_text, re.DOTALL):
        decisions.append({
            "type": "修正案",
            "content": match.group(1).strip(),
            "source": source_file,
            "status": "通过",
        })

    # 模式3：委托（通过默认一致同意）
    for match in re.finditer(r'委托获得默认一致同意.*?\n.*?委托的议题.*?\n\s*```\s*\n(.*?)```', md_text, re.DOTALL):
        decisions.append({
            "type": "委托",
            "content": match.group(1).strip(),
            "source": source_file,
            "status": "通过",
        })

    return decisions


def extract_numbered_items(text):
    """从文本中提取编号条目（如 1. xxx 2. xxx 或 一、xxx 二、xxx）"""
    items = []
    # 数字编号：1. xxx 或 1、xxx
    for m in re.finditer(r'(?:^|\n)\s*(?:\d+[\.\、\)]|（[一二三四五六七八九十]+）|[一二三四五六七八九十]+[\.\、])\s*(.{6,100}?)(?=\n\s*(?:\d+[\.\、\)]|（[一二三四五六七八九十]+）|[一二三四五六七八九十]+[\.\、])|\n\n|\Z)', text, re.DOTALL):
        item_text = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
        # 清理嵌套编号
        item_text = re.sub(r'^\d+[\.\、]', '', item_text).strip()
        if not is_noise_text(item_text) and len(item_text) >= 6:
            items.append(item_text)
    return items


def extract_tasks_basic(md_text, source_file):
    """
    基础模式：从会议记录中提取结构化任务。

    分层提取策略：
    L1: 通过的正式动议（最可靠）
    L2: 发言整理中的编号列表（可靠）
    L3: 含明确「负责/做/交给」的陈述（中等可靠）
    """
    tasks = []
    seen = set()

    # ── 提取发言人映射（用于后续匹配谁在说什么） ──
    # 不做复杂映射，直接整体分析

    # ── L1: 从正式动议中提取任务 ──
    decision_blocks = re.findall(
        r'(?:通过的主动议|通过的修正案|委托的议题)[：:]?\s*\n?\s*```\s*\n(.*?)```',
        md_text, re.DOTALL
    )
    for block in decision_blocks:
        items = extract_numbered_items(block)
        for item in items:
            if item in seen:
                continue
            # 尝试从中提取负责人和时间
            persons = find_person_in_text(item)
            category = "管理"
            for cat, kws in TASK_CATEGORIES.items():
                if any(kw in item for kw in kws):
                    category = cat
                    break
            date_match = re.search(r'(\d+月\d+[日号]|\d+/\d+)', item)
            tasks.append({
                "name": item[:60],
                "category": category,
                "assignee": persons[0] if persons else "",
                "deadline": date_match.group(1) if date_match else "",
                "confirmer": "",
                "source": source_file,
                "status": "已确定",
                "type": "初始",
            })
            seen.add(item)

    # ── L2: 从发言整理中提取编号任务列表 ──
    tidy_sections = re.findall(
        r'\*\*发言整理:\*\*\s*\n(.*?)(?=\n\n\d+\.\s+\*\*|\n\d+\.\s+\*\*|\Z)',
        md_text, re.DOTALL
    )
    for tidy_text in tidy_sections:
        # 找到这个整理段落对应的发言人
        # 在原始文本中往前找发言人
        speaker = ""

        items = extract_numbered_items(tidy_text)
        # 也处理「- xxx」格式的列表
        for m in re.finditer(r'(?:^|\n)\s*[-–—]\s*(.{8,100}?)(?=\n\s*[-–—]|\n\n|\Z)', tidy_text, re.DOTALL):
            item_text = m.group(1).strip()
            if not is_noise_text(item_text) and len(item_text) >= 8:
                items.append(item_text)

        for item in items:
            # 去重
            simple = re.sub(r'[^\w一-鿿]', '', item)[:30]
            if simple in seen:
                continue
            seen.add(simple)

            persons = find_person_in_text(item)
            category = "其他"
            for cat, kws in TASK_CATEGORIES.items():
                if any(kw in item for kw in kws):
                    category = cat
                    break
            date_match = re.search(r'(\d+月\d+[日号]|\d+/\d+)', item)

            # 检查是否来自已确定的动议块
            is_decided = any(
                item[:20] in block or block[:20] in item
                for block in decision_blocks
            )

            tasks.append({
                "name": item[:80],
                "category": category,
                "assignee": persons[0] if persons else "",
                "deadline": date_match.group(1) if date_match else "",
                "confirmer": "",
                "source": source_file,
                "status": "已确定" if is_decided else "待确认",
                "type": "初始",
            })

    # ── L3: 明确的任务分配陈述 ──
    # 找「XX负责YY」「让XX做YY」「XX去YY」的模式
    assignment_patterns = [
        (r'([^\s，。,]{2,4})\s*(?:负责|来做|去做|处理|跟进)\s*[「『]?([^」』，。,\n]{3,40})[」』]?', 2, 1),
        (r'(?:让|叫|由|交给|委托)\s*([^\s，。,\n]{2,4})\s*(?:负责|来做|去做|处理)\s*[「『]?([^」』，。,\n]{3,40})[」』]?', 2, 1),
    ]

    for pattern, content_group, person_group in assignment_patterns:
        for m in re.finditer(pattern, md_text):
            person = m.group(person_group).strip()
            content = m.group(content_group).strip()
            if is_noise_text(content):
                continue
            if person not in KNOWN_MEMBERS and len(person) > 3:
                continue  # 排除非人名的匹配

            simple = re.sub(r'[^\w一-鿿]', '', content)[:30]
            if simple in seen:
                continue
            seen.add(simple)

            category = "其他"
            for cat, kws in TASK_CATEGORIES.items():
                if any(kw in content for kw in kws):
                    category = cat
                    break

            tasks.append({
                "name": content[:80],
                "category": category,
                "assignee": person,
                "deadline": "",
                "confirmer": "",
                "source": source_file,
                "status": "待确认",
                "type": "初始",
            })

    return tasks


def extract_members_from_text(md_text):
    """从参会者表中提取成员"""
    members = []
    table_match = re.search(r'\|\s*姓名\s*\|.*?\n\|[-\s:|]+\|\s*\n((?:\|.*?\n)+)', md_text)
    if table_match:
        for line in table_match.group(1).strip().split('\n'):
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if cols:
                members.append({
                    "name": cols[0],
                    "role": cols[1] if len(cols) > 1 else "参会者",
                    "attendance": cols[2] if len(cols) > 2 else "亲自出席",
                })
    return members


def process_meeting_file(filepath):
    """处理单个会议记录文件"""
    print(f"  处理: {filepath.name}")

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 提取元信息
    meta = {}
    meta["title"] = ""
    title_match = re.search(r'^#\s*(.*)', text, re.MULTILINE)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    if date_match:
        meta["date"] = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
    else:
        meta["date"] = ""

    org_match = re.search(r'\*\*组织名称\*\*:\s*(.*)', text)
    meta["organization"] = org_match.group(1).strip() if org_match else ""

    # 提取任务和决策
    tasks = extract_tasks_basic(text, filepath.name)
    decisions = extract_decisions(text, filepath.name)

    # 提取成员
    members = extract_members_from_text(text)

    print(f"    提取到 {len(tasks)} 个任务, {len(decisions)} 个决策, {len(members)} 个成员")

    return {
        "meta": meta,
        "tasks": tasks,
        "decisions": decisions,
        "members": members,
    }


def deduplicate_tasks(all_tasks):
    """合并相似任务（按名称相似度去重）"""
    unique = []
    seen_names = set()

    for task in all_tasks:
        name = task["name"]
        # 简化比较：去掉标点后比较
        simple_name = re.sub(r'[^\w一-鿿]', '', name)
        if simple_name in seen_names:
            # 找到已有的同名任务，补充信息
            for existing in unique:
                existing_simple = re.sub(r'[^\w一-鿿]', '', existing["name"])
                if existing_simple == simple_name:
                    if not existing["assignee"] and task["assignee"]:
                        existing["assignee"] = task["assignee"]
                    if not existing["deadline"] and task["deadline"]:
                        existing["deadline"] = task["deadline"]
                    if task["status"] == "已确定":
                        existing["status"] = "已确定"
                    break
        else:
            seen_names.add(simple_name)
            unique.append(task)

    return unique


# ══════════════════════════════════════════════
# AI 增强模式（可选）
# ══════════════════════════════════════════════

HAS_AI = False
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

HAS_AI = HAS_ST and HAS_OLLAMA


def setup_ai_dependencies():
    """安装 AI 增强模式所需依赖"""
    import subprocess
    import sys

    packages = [
        "sentence-transformers",
        "torch",
        "ollama",
    ]

    print("正在安装 AI 增强模式依赖...\n")
    for pkg in packages:
        print(f"  安装 {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

    print("\n请确保 Ollama 已安装并拉取了 qwen2.5:7b 模型：")
    print("  1. 下载 Ollama: https://ollama.com/download/windows")
    print("  2. ollama pull qwen2.5:7b")
    print("\n✅ 依赖安装完成！现在可以运行 python meeting_to_tasks.py --ai")


def search_relevant_paragraphs(md_text, query, model, top_k=5):
    """
    用 BGE-M3 在会议记录中搜索与 query 最相关的段落。
    """
    # 按自然段落切分
    paragraphs = [p.strip() for p in re.split(r'\n\n+', md_text) if len(p.strip()) > 30]

    if len(paragraphs) == 0:
        return []

    # 向量化所有段落
    print(f"    BGE-M3: 向量化 {len(paragraphs)} 个段落...")
    para_embeddings = model.encode(paragraphs, show_progress_bar=False)

    # 向量化查询
    query_embedding = model.encode([query])

    # 计算相似度
    from sentence_transformers.util import cos_sim
    similarities = cos_sim(query_embedding, para_embeddings)[0]

    # 取 top_k
    top_indices = similarities.argsort(descending=True)[:top_k].tolist()

    results = []
    for i in top_indices:
        score = float(similarities[i])
        if score > 0.3:  # 最低相似度阈值
            results.append({
                "text": paragraphs[i][:1000],  # 截断
                "score": round(score, 3),
            })

    return results


def extract_tasks_ai(md_text, source_file):
    """
    AI 增强模式：BGE-M3 搜索 + Qwen2.5 智能提取。

    流水线：
    1. BGE-M3 找到会议记录中所有与「任务」相关的段落
    2. Qwen2.5 对每个段落提取结构化任务信息
    3. 返回 JSON
    """
    # ── 加载 BGE-M3 ──
    print("  加载 BGE-M3（本地模型，约 2.2GB）...")
    model_path = str(Path.home() / ".cache" / "modelscope" / "hub" / "models" / "BAAI" / "bge-m3")
    if Path(model_path).exists():
        model = SentenceTransformer(model_path)
    else:
        model = SentenceTransformer("BAAI/bge-m3")

    # ── 搜索任务相关段落 ──
    queries = [
        "任务分配、分工、谁负责什么",
        "截止日期、时间节点、什么时候完成",
        "决策、表决、通过的动议",
        "预算、费用、成本、资助",
        "合作、合约、所有权、分红",
    ]

    all_paragraphs = set()
    for query in queries:
        results = search_relevant_paragraphs(md_text, query, model, top_k=8)
        for r in results:
            all_paragraphs.add(r["text"])

    print(f"  BGE-M3: 找到 {len(all_paragraphs)} 个相关段落")

    # ── Qwen2.5 提取 ──
    tasks = []
    decisions = []

    extract_prompt = """你是一个会议记录分析助手。请从以下发言段落中提取：
1. 被讨论或确定的任务（任务名称、负责人、截止日期）
2. 通过的决策或动议

对于每个任务，请输出JSON格式：
{"tasks": [{"name": "任务名", "assignee": "负责人", "deadline": "截止日期", "status": "已确定/讨论中"}], "decisions": [{"content": "决策内容"}]}

只输出JSON，不要其他文字。如果没有任务或决策，输出空数组。

发言段落：
"""

    for para in list(all_paragraphs)[:15]:  # 限制段落数避免过长
        try:
            response = ollama.chat(
                model="qwen2.5:7b",
                messages=[{"role": "user", "content": extract_prompt + para[:2000]}],
                options={"temperature": 0.1},
            )
            content = response["message"]["content"]

            # 解析 JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                for t in data.get("tasks", []):
                    t["source"] = source_file
                    tasks.append(t)
                for d in data.get("decisions", []):
                    d["source"] = source_file
                    decisions.append(d)
        except Exception as e:
            print(f"    Qwen 提取出错: {e}")
            continue

    return tasks, decisions


# ══════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(description="会议记录 → 任务 JSON 提取")
    parser.add_argument("files", nargs="*", help="要处理的会议记录文件（留空处理全部）")
    parser.add_argument("--ai", action="store_true", help="启用 AI 增强模式（BGE-M3 + Qwen2.5）")
    parser.add_argument("--setup", action="store_true", help="安装 AI 增强模式依赖")
    args = parser.parse_args()

    # ── 安装模式 ──
    if args.setup:
        setup_ai_dependencies()
        return

    # ── 确定处理文件 ──
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = sorted(RECORD_DIR.glob("*.md"))
        # 排除分析报告
        files = [f for f in files if "分析" not in f.name and "要点清单" not in f.name]

    if not files:
        print("❌ 没有找到会议记录文件")
        return

    print(f"\n{'='*60}")
    print(f"  会议记录 → 任务 JSON 提取")
    print(f"  模式: {'AI 增强 (BGE-M3 + Qwen2.5)' if args.ai else '基础 (正则匹配)'}")
    print(f"  文件数: {len(files)}")
    print(f"{'='*60}\n")

    # ── 检查 AI 模式依赖 ──
    if args.ai and not HAS_AI:
        print("❌ AI 增强模式依赖未安装。")
        print("  请先运行: python meeting_to_tasks.py --setup")
        print("  然后确保 Ollama 已安装并拉取 qwen2.5:7b")
        return

    # ── 处理文件 ──
    all_tasks = []
    all_decisions = []
    all_members = []
    meeting_summaries = []

    for filepath in files:
        if args.ai:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            tasks, decisions = extract_tasks_ai(text, filepath.name)
            members = extract_members_from_text(text)
            meta = {"title": filepath.stem, "date": "", "organization": ""}
        else:
            result = process_meeting_file(filepath)
            tasks = result["tasks"]
            decisions = result["decisions"]
            members = result["members"]
            meta = result["meta"]

        all_tasks.extend(tasks)
        all_decisions.extend(decisions)
        all_members.extend(members)
        meeting_summaries.append({
            "file": filepath.name,
            "title": meta["title"],
            "date": meta["date"],
            "organization": meta["organization"],
            "task_count": len(tasks),
            "decision_count": len(decisions),
        })

    # ── 去重 ──
    unique_tasks = deduplicate_tasks(all_tasks)

    # ── 构建输出 ──
    output = {
        "generated_at": datetime.now().isoformat(),
        "mode": "ai" if args.ai else "basic",
        "summary": {
            "total_meetings": len(files),
            "total_tasks": len(unique_tasks),
            "total_decisions": len(all_decisions),
            "meetings": meeting_summaries,
        },
        "tasks": unique_tasks,
        "decisions": all_decisions,
        "members": {m["name"]: m for m in all_members},  # 去重
    }

    # ── 保存 ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  [OK] Done!")
    print(f"  Meetings: {len(files)}")
    print(f"  Tasks: {len(unique_tasks)} (deduplicated)")
    print(f"  Decisions: {len(all_decisions)}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"{'='*60}\n")

    # ── 简要预览 ──
    if unique_tasks:
        print("[Tasks Preview]:")
        print("-" * 60)
        for t in unique_tasks[:20]:
            status_icon = "[DONE]" if t["status"] == "已确定" else "[TODO]"
            print(f"  {status_icon} {t['name']:<20s} -> {t['assignee']:<12s} {t['deadline']}")
        if len(unique_tasks) > 20:
            print(f"  ... {len(unique_tasks)} tasks total, see {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
