#!/usr/bin/env bash
# 停止 brainstorming 服务器并清理资源
# 用法: stop-server.sh <session_dir>
#
# 终止服务器进程。仅当 session 目录位于 /tmp 下时才删除（临时目录）。
# 持久化目录（.superpowers/）会保留，以便后续查看 mockups。

SESSION_DIR="$1"

if [[ -z "$SESSION_DIR" ]]; then
  echo '{"error": "用法: stop-server.sh <session_dir>"}'
  exit 1
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"

if [[ -f "$PID_FILE" ]]; then
  pid=$(cat "$PID_FILE")

  # 尝试优雅地停止进程，如果进程仍存活则强制终止
  kill "$pid" 2>/dev/null || true

  # 等待优雅关闭（最多约 2 秒）
  for i in {1..20}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.1
  done

  # 如果进程仍在运行，升级为 SIGKILL
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true

    # 给 SIGKILL 一点时间生效
    sleep 0.1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    echo '{"status": "failed", "error": "进程仍在运行"}'
    exit 1
  fi

  rm -f "$PID_FILE" "${STATE_DIR}/server.log"

  # 仅删除临时的 /tmp 目录
  if [[ "$SESSION_DIR" == /tmp/* ]]; then
    rm -rf "$SESSION_DIR"
  fi

  echo '{"status": "stopped"}'
else
  echo '{"status": "not_running"}'
fi
