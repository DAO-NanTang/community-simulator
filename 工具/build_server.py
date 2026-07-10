#!/usr/bin/env python3
"""剥离 NT-TEST 围栏 → 生成干净的 dashboard.server.html"""
import sys, os, subprocess, re

SRC = 'dashboard.html'
OUT = 'dashboard.server.html'
START = 'NT-TEST:START'
END   = 'NT-TEST:END'

def build():
    if not os.path.exists(SRC):
        sys.exit(f'❌ 找不到 {SRC}')

    lines = open(SRC, 'r', encoding='utf-8').readlines()
    out_lines = []
    depth = 0          # >0 = 在围栏内
    start_ln = 0       # 最近一次 START 所在行号（1‑based）

    for i, raw in enumerate(lines, 1):
        has_start = START in raw
        has_end   = END in raw

        if has_start and has_end:
            sys.exit(f'❌ 行 {i}: START 和 END 不能在同一行 — {raw.strip()[:80]}')

        if has_start:
            if depth == 0:
                start_ln = i
            depth += 1
            continue        # 跳过 START 标记行

        if has_end:
            if depth == 0:
                sys.exit(f'❌ 行 {i}: 多余的 END（前面没有 START） — {raw.strip()[:80]}')
            depth -= 1
            continue        # 跳过 END 标记行

        if depth == 0:
            out_lines.append(raw)

    if depth > 0:
        sys.exit(f'❌ 行 {start_ln}: START 缺少对应的 END（嵌套层数 {depth}）')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f'✅ {OUT} 已生成（{len(out_lines)} 行，剥离 {len(lines) - len(out_lines)} 行）')

    # ── 自检：node --check ──
    js = ''.join(out_lines)
    m = re.search(r'<script[^>]*>(.*?)</script>', js, re.DOTALL)
    if not m:
        sys.exit('❌ 生成文件中未找到 <script> 块，无法校验 JS 语法')
    script_code = m.group(1)

    # 临时写入检查
    tmp = OUT + '.check.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(script_code)

    try:
        subprocess.run(['node', '--check', tmp], check=True, capture_output=True, text=True)
        print('✅ node --check JS 语法通过')
    except subprocess.CalledProcessError as e:
        print('❌ JS 语法错误：')
        print(e.stderr)
        sys.exit(1)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # ── 快速内容验证 ──
    with open(OUT, 'r', encoding='utf-8') as f:
        out_text = f.read()
    for keyword in ['btnDevtools', '_frozenMs', '内测世界', 'devtoolsSidebar', 'nt_virtual_ms']:
        if keyword in out_text:
            sys.exit(f'❌ 验证失败：产出中仍包含 "{keyword}"')

    print('✅ 内容验证通过（无内测关键字残留）')

if __name__ == '__main__':
    build()
