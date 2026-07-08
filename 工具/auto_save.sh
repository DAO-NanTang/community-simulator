#!/bin/bash
# 每 10 分钟自动 git commit + push
cd "c:/Users/苏砚仁/thinknote/南塘 DAO/gnt计算机制/工具"

while true; do
  sleep 600  # 10 分钟

  # 如果有改动就提交
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add dashboard.html "*.md" "*.py" "*.json" "*.html" 2>/dev/null
    git commit -m "自动保存：$(date '+%m-%d %H:%M')" 2>/dev/null
    git push github main 2>/dev/null
    echo "[$(date '+%H:%M')] Auto-saved"
  fi
done
