# gd-claude-code-plugin

Claude Code 增强插件集合 — 包含智能体（Agents）、技能（Skills）和钩子（Hooks）。

## 功能概览

### 智能体（Agents）

| 名称 | 说明 |
|------|------|
| **bug-analyzer** | 深度代码执行流分析与根因调试专家，擅长构建执行链图、追踪变量状态变化 |
| **code-reviewer** | 精通现代 AI 驱动代码分析、安全漏洞、性能优化和生产可靠性的代码审查专家 |
| **dev-planner** | 开发计划专家，将需求拆解为详细可执行的开发计划，含任务分解、依赖分析和时间线估算 |
| **story-generator** | 用户故事生成器，从 git diff、PRD 文档或对话中提取并结构化用户故事与验收标准 |
| **ui-sketcher** | 通用 UI 蓝图工程师，将功能需求转化为 ASCII 界面设计、用户故事和交互规格 |

### 技能（Skills）

| 名称 | 说明 |
|------|------|
| **generate-commit** | 分析 git diff，生成符合 Conventional Commits 规范的提交信息并自动提交 |
| **read-github** | 通过 gitmcp.io 智能读取 GitHub 仓库文档和代码，语义搜索、零幻觉 |
| **skill-development** | 技能开发指南，帮助创建高质量的 Claude Code 插件技能 |

### 钩子（Hooks）

| 名称 | 触发事件 | 说明 |
|------|----------|------|
| **notify.sh** | Notification / Stop | macOS 桌面通知，支持 iTerm2、Terminal.app、VS Code、Cursor 等终端的点击跳转 |
| **show-cwd.sh** | SessionStart / Stop | 恢复会话或任务完成后显示当前工作目录 |


## 安装

### 方式一：通过自建 Marketplace 安装（推荐）

```bash
# 添加自建市场
/plugin marketplace add afk101/.claude

# 浏览并安装插件
/plugin install gd-claude-code-plugin
```

### 方式二：本地安装

```bash
# 克隆仓库
git clone https://github.com/afk101/.claude.git

# 使用 --plugin-dir 加载
claude --plugin-dir /path/to/gd-claude-code-plugin
```

### 方式三：手动复制

将需要的文件复制到 `~/.claude/` 对应目录下：

```bash
# 复制智能体
cp agents/*.md ~/.claude/agents/

# 复制技能
cp -r skills/* ~/.claude/skills/

# 复制钩子
cp hooks/*.sh ~/.claude/hooks/

```

## 前置依赖

### notify.sh（桌面通知钩子）

需要安装 [terminal-notifier](https://github.com/julienXX/terminal-notifier)：

```bash
brew install terminal-notifier
```

同时需要系统安装 `jq`：

```bash
brew install jq
```

### read-github skill

需要安装 Node.js 和 npx（用于运行 mcp-remote）：

```bash
brew install node
```

## 目录结构

```
.claude/  (本仓库根目录)
├── .claude-plugin/
│   └── plugin.json              # 插件清单
├── agents/                      # 智能体
│   ├── bug-analyzer.md
│   ├── code-reviewer.md
│   ├── dev-planner.md
│   ├── story-generator.md
│   └── ui-sketcher.md
├── skills/                      # 技能
│   ├── generate-commit/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── read-github-1.0.1/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── skill-development/
│       ├── SKILL.md
│       └── references/
├── hooks/                       # 钩子
│   ├── hooks.json
│   ├── notify.sh
│   └── show-cwd.sh
├── marketplace.json             # 自建市场清单
├── CLAUDE.md                    # 全局用户指令
├── settings.json                # 用户设置
├── README.md
└── LICENSE
```

## 许可证

MIT License
