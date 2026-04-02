#!/bin/bash
# Stop 事件后显示当前工作目录（CWD）
# 输出 systemMessage，仅显示给用户，不进入对话历史
INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')

if [ -n "$CWD" ]; then
  # 输出 JSON，systemMessage 会显示给用户但不添加到对话上下文
  echo "{\"systemMessage\": \"📂 当前工作目录: $CWD\"}"
fi

exit 0
