#!/bin/bash
# Claude Code 通知 Hook 脚本
# 功能：从 stdin 读取 Hook 事件 JSON，提取事件信息和用户原始输入，发送 macOS 桌面通知
# 支持的事件：Notification（需要用户操作）、Stop（任务执行完毕）

# 读取 stdin 的 JSON 数据
INPUT=$(cat)

# 提取关键字段
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "unknown"')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""')
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')

# 从 transcript 文件提取用户第一条真正的对话内容
# 排除 isMeta 消息（内置 CLI 命令如 /clear、/compact 等）和空行
USER_PROMPT=""
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
  USER_PROMPT=$(awk '/"type":"user"/{if(/"isMeta":true/) next; print; exit}' "$TRANSCRIPT" \
    | jq -r '.message.content | if type == "string" then . elif type == "array" then map(select(.type == "text") | .text) | join("") else "" end' 2>/dev/null \
    | sed 's/<[^>]*>//g' | tr '\n' ' ' | sed 's/  */ /g; s/^ *//; s/ *$//')
fi

# 清理用户输入：去掉换行符，替换为空格
USER_PROMPT=$(echo "$USER_PROMPT" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//;s/ *$//')

# 截断用户输入
MAX_LEN=45
if [ ${#USER_PROMPT} -gt $MAX_LEN ]; then
  USER_PROMPT="${USER_PROMPT:0:$MAX_LEN}..."
fi

# 根据事件类型构造通知标题和内容
# 通知布局：-title 放事件标题，-message 放用户输入 + cwd（自动换行）
case "$EVENT" in
  "Notification")
    TITLE="⚠️ Claude Code - 需要你的操作"
    if [ -n "$USER_PROMPT" ]; then
      MESSAGE="${USER_PROMPT}"
    else
      MESSAGE="请回到终端进行选择"
    fi
    ;;
  "Stop")
    TITLE="✅ Claude Code - 任务执行完毕"
    if [ -n "$USER_PROMPT" ]; then
      MESSAGE="${USER_PROMPT}"
    else
      MESSAGE="任务已完成，可以验证结果"
    fi
    ;;
  *)
    # 未知事件类型，不发送通知
    exit 0
    ;;
esac

# 拼接 cwd 到 message 中（用换行分隔）
if [ -n "$CWD" ]; then
  MESSAGE=$(printf '%s\n%s' "$MESSAGE" "$CWD")
fi

# 获取当前 Claude Code 所在的 tty（用于点击通知后跳转到对应终端 tab，支持 iTerm2 和 Terminal.app）
CURRENT_TTY=$(ps -o tty= -p $PPID 2>/dev/null | tr -d ' ')

# 检测宿主终端应用：沿进程树向上查找
HOST_APP=""
HOST_BUNDLE=""
_PID=$$
for _i in $(seq 1 15); do
  _PID=$(ps -o ppid= -p $_PID 2>/dev/null | tr -d ' ')
  [ -z "$_PID" ] || [ "$_PID" = "0" ] || [ "$_PID" = "1" ] && break
  _COMM=$(ps -o comm= -p $_PID 2>/dev/null)
  case "$_COMM" in
    *iTerm*)               HOST_APP="iterm2";     break ;;
    *Terminal)             HOST_APP="terminal";   HOST_BUNDLE="com.apple.Terminal"; break ;;
    *Code*)                HOST_APP="vscode";     HOST_BUNDLE="com.microsoft.VSCode"; break ;;
    *Cursor*)              HOST_APP="cursor";     HOST_BUNDLE="com.todesktop.230313mzl4w4u92"; break ;;
    *Windsurf*)            HOST_APP="windsurf";   HOST_BUNDLE="com.exafunction.windsurf"; break ;;
    *Kiro*)                HOST_APP="kiro";       HOST_BUNDLE="dev.kiro.desktop"; break ;;
    *CodeBuddy*)           HOST_APP="codebuddy";  HOST_BUNDLE="com.tencent.codebuddycn"; break ;;
    *Qoder*)               HOST_APP="qoder";      HOST_BUNDLE="com.qoder.ide"; break ;;
    *CatPaw*|*catpaw*)     HOST_APP="catpaw";     HOST_BUNDLE="com.catpaw.ide"; break ;;
    *Trae*|*trae*)         HOST_APP="trae";       HOST_BUNDLE="cn.trae.app"; break ;;
    *Warp*)                HOST_APP="warp";       HOST_BUNDLE="dev.warp.Warp-Stable"; break ;;
    *Alacritty*)           HOST_APP="alacritty";  HOST_BUNDLE="org.alacritty"; break ;;
    *kitty*)               HOST_APP="kitty";      HOST_BUNDLE="net.kovidgoyal.kitty"; break ;;
    *WezTerm*|*wezterm*)   HOST_APP="wezterm";    HOST_BUNDLE="com.github.wez.wezterm"; break ;;
  esac
done

# 构造点击通知后的跳转脚本
# 使用临时脚本文件避免 -execute 参数中的引号嵌套导致参数解析错误
JUMP_SCRIPT="/tmp/claude-notify-jump-$$.sh"
if [ "$HOST_APP" = "iterm2" ] && [ -n "$CURRENT_TTY" ]; then
  # iTerm2：通过 AppleScript 激活并跳转到对应 tty 的 tab
  cat > "$JUMP_SCRIPT" <<ASCRIPT
#!/bin/bash
osascript <<'APPLESCRIPT'
tell application "iTerm2"
  activate
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        if tty of s contains "$CURRENT_TTY" then
          select t
          return
        end if
      end repeat
    end repeat
  end repeat
end tell
APPLESCRIPT
rm -f "$JUMP_SCRIPT"
ASCRIPT
  chmod +x "$JUMP_SCRIPT"
elif [ "$HOST_APP" = "terminal" ] && [ -n "$CURRENT_TTY" ]; then
  # macOS Terminal.app：通过 AppleScript 激活并跳转到对应 tty 的 tab
  cat > "$JUMP_SCRIPT" <<CSCRIPT
#!/bin/bash
osascript <<'APPLESCRIPT'
tell application "Terminal"
  activate
  repeat with w in windows
    repeat with t in tabs of w
      if tty of t contains "$CURRENT_TTY" then
        set selected tab of w to t
        set index of w to 1
        return
      end if
    end repeat
  end repeat
end tell
APPLESCRIPT
rm -f "$JUMP_SCRIPT"
CSCRIPT
  chmod +x "$JUMP_SCRIPT"
elif [ -n "$HOST_BUNDLE" ]; then
  # 其他已知终端：激活对应应用到前台
  cat > "$JUMP_SCRIPT" <<BSCRIPT
#!/bin/bash
open -b $HOST_BUNDLE
rm -f "$JUMP_SCRIPT"
BSCRIPT
  chmod +x "$JUMP_SCRIPT"
else
  # 未识别的终端：空操作
  JUMP_SCRIPT=""
fi

# 发送 macOS 桌面通知（使用 terminal-notifier，带 Glass 声音提醒）
if [ -n "$JUMP_SCRIPT" ]; then
  terminal-notifier -title "$TITLE" -message "$MESSAGE" -sound Glass -execute "$JUMP_SCRIPT"
else
  terminal-notifier -title "$TITLE" -message "$MESSAGE" -sound Glass
fi

exit 0
