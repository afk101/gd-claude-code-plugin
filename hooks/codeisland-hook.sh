#!/bin/bash
# CodeIsland hook v2 — native bridge with shell fallback
BRIDGE="$HOME/.claude/hooks/codeisland-bridge"
[ -x "$BRIDGE" ] && exec "$BRIDGE"
# Fallback: original shell approach (no binary installed yet)
SOCK="/tmp/codeisland-$(id -u).sock"
[ -S "$SOCK" ] || exit 0
INPUT=$(cat)
_ITERM_GUID="${ITERM_SESSION_ID##*:}"
TERM_INFO="\"_term_app\":\"${TERM_PROGRAM:-}\",\"_iterm_session\":\"${_ITERM_GUID:-}\",\"_tty\":\"$(tty 2>/dev/null || true)\",\"_ppid\":$PPID"
PATCHED="${INPUT%\}},${TERM_INFO}}"
if echo "$INPUT" | grep -q '"PermissionRequest"'; then
  echo "$PATCHED" | nc -U -w 120 "$SOCK" 2>/dev/null || true
else
  echo "$PATCHED" | nc -U -w 2 "$SOCK" 2>/dev/null || true
fi