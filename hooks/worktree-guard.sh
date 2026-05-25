#!/bin/bash
# 检测当前是否位于 .clawt/worktrees 中
# 如果是，通过 additionalContext 注入警告信息，告知 Claude 不要修改主 worktree 的代码

# 从 stdin 读取 JSON 输入
INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')

# 检测是否在 worktree 中
# 仅匹配路径模式：包含 .clawt/worktrees
IS_WORKTREE=false
WORKTREE_PATH=""

if echo "$CWD" | grep -qE '/\.clawt/worktrees/'; then
  IS_WORKTREE=true
  WORKTREE_NAME=$(echo "$CWD" | grep -oE '\.clawt/worktrees/[^/]+' | sed 's/.*worktrees\///')
  WORKTREE_PATH="$CWD"
fi

# 如果在 worktree 中，输出 additionalContext 警告
if [ "$IS_WORKTREE" = "true" ]; then
  WARNING="⚠️ WORKTREE Safety Notice: You are currently in a git worktree (path: ${WORKTREE_PATH}). Strictly prohibited from modifying code in the main worktree. You can only modify files within the current worktree directory. If you need to operate on files in the main worktree, stop the operation and seek user approval."

  # 输出 JSON，additionalContext 会作为上下文附加到用户的提示词旁边
  jq -n --arg ctx "$WARNING" '{
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: $ctx
    }
  }'
else
  # 不在 worktree 中，正常放行
  exit 0
fi

exit 0
