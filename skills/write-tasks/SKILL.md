---
name: "clawt:write-tasks"
description: >
  This skill should be used when the user asks to "write tasks", "create task file",
  "write clawt tasks", "generate task file", "create clawt task document",
  "write task document", "batch tasks", "write batch task file",
  or mentions "clawt tasks" or "task file" in the context of creating parallel Claude Code Agent tasks.
  Generates clawt-compatible task files with proper CLAWT-TASKS format for batch execution.
version: 1.0.0
---

# Clawt 任务文件生成器

根据用户描述的项目背景和任务需求，生成符合 clawt 任务文件格式规范的 Markdown 文档，用于 `clawt run -f` 批量并行执行 Claude Code Agent 任务。

## 核心工作流程

### 第一步：确保 .gitignore 配置

在写入任务文件之前，检查项目根目录的 `.gitignore` 是否已包含 `.clawt/tasks` 条目。

- 若 `.gitignore` 中已存在 `.clawt/tasks` 或 `.clawt/tasks/`，跳过
- 若不存在，在 `.gitignore` 末尾追加：

```
# clawt 任务文件（自动生成，无需版本控制）
.clawt/tasks/
```

- 若 `.gitignore` 文件不存在，则不处理

### 第二步：创建输出目录

确保 `.clawt/tasks/` 目录存在：

```bash
mkdir -p .clawt/tasks
```

### 第三步：收集任务信息

1. **背景**：项目技术栈、当前状态、相关上下文
2. **全局注意事项**：所有任务都需遵守的约束、规范、特别说明
3. **任务详情*(用户提供)：如果用户给到的是一个明确的任务，那就只创建一个。而如果用户提到的任务可以拆分成多个“独立”的任务，那你必须拆分为多个任务。
注意点：你必须评估是否可以拆分成独立的任务。例如，用户想让你提供优化建议或者可以新增的功能，那你就必须将各个独立的建议或者功能分成多个任务，每个任务都必须有任务背景，注意事项可选。

若所有信息都有，直接进入生成步骤，无需额外询问具体任务。

### 第四步：生成任务文件

**文件命名**：`clawt-tasks-YYYY-MM-DD-HH-mm-ss.md`

- 使用当前时间戳，格式为年-月-日-时-分-秒
- 示例：`clawt-tasks-2000-01-01-14-30-00.md`

**文件路径**：`.clawt/tasks/clawt-tasks-YYYY-MM-DD-HH-mm-ss.md`

**文件内容结构**：

```markdown
# [项目/任务批次描述]

[项目背景信息，对当前项目、技术栈、现状的描述]

## 注意事项

[所有任务共通的约束和规范]

---

<!-- CLAWT-TASKS:START -->
# branch: <分支名>
<任务描述，可多行>
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: <分支名>
<任务描述，可多行>
<!-- CLAWT-TASKS:END -->
```

### 第五步：输出执行命令

文件生成后，输出可直接复制执行的 clawt 命令：

```bash
clawt run -f .clawt/tasks/clawt-tasks-YYYY-MM-DD-HH-mm-ss.md
```

## 任务描述编写指南

每个任务块中的描述应做到：

- **具体明确**：说清楚需要做什么，不要使用模糊的表述
- **包含验收标准**：在任务描述中列明预期的结果或完成标准
- **提供必要上下文**：相关的文件路径、函数名、API 接口等具体引用
- **合理拆分粒度**：每个任务应当是一个独立的、可并行执行的工作单元

### 好的任务描述示例

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-user-auth
实现用户认证模块：
- 在 src/api/auth.ts 中实现 JWT token 签发与验证
- 创建 POST /api/login 和 POST /api/register 接口
- 密码使用 bcrypt 加密存储
- 实现 token 刷新机制，access token 过期时间 15 分钟
- 编写对应的单元测试
<!-- CLAWT-TASKS:END -->
```

### 不好的任务描述示例

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-auth
做一下用户登录
<!-- CLAWT-TASKS:END -->
```

## 分支名命名规范

- 使用 `feat-xxx`（新功能）、`fix-xxx`（修复）、`refactor-xxx`（重构）、`docs-xxx`（文档）、`test-xxx`（测试）等前缀
- 使用小写字母和连字符 `-` 连接
- 保持简洁但有描述性
- 避免使用 `/`、`.`、`:`、`*`、`?`、空格等特殊字符

## 额外参考

查阅 `references/task-format.md` 获取完整的 clawt 任务文件格式规范、分支名非法字符列表及详细使用示例。
