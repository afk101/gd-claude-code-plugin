---
name: clawt:worktrees-parallel-exec
description: 仅在用户明确调用时使用（如 /clawt:worktrees-parallel-exec 或"使用 clawt 并行工作流"）。使用 Clawt 管理 Git Worktree，结合 Superpowers 框架进行并行开发。将多个独立任务拆分到各自 worktree，每个 worktree 运行独立 Agent 并发执行。不要在用户未明确要求时自动触发此技能。
---

## Clawt + Superpowers 并行开发工作流

### 概述

本项目使用 **Clawt** 管理 Git Worktree，结合 **Superpowers** 框架进行并行开发。当需要实现多个独立功能时：

- **主 Agent**：负责分析任务、创建 worktree、编写 spec/plan/findings、启动独立 Agent
- **Worktree Agent**：独立运行在各自 worktree 中，用户可直接交互

### 工作流程

```
用户发送任务 → 主 Agent 分析拆分 → 一次性向用户审阅确认每个任务需要其确认的方案 → 循环处理每个任务：
                                    [创建 worktree → 生成 spec/plan/findings → 生成任务文件 → clawt resume -f（后台）]
                                                                                            ↓
                                                    主 Agent 生命周期结束 ← 所有任务派发完成
                                                                                            ↓
用户与 Worktree Agent 交互 ← clawt resume -b <branch> ← Worktree Agent 独立运行（并行）
```

**核心特点**：
- 每个 worktree 运行独立的 Agent 进程
- 用户可直接与任意 worktree 的 Agent 对话（通过 `clawt resume -b`）
- 主 Agent 完成派发后即结束，无需中转通信

---

### 主 Agent 执行流程

#### 1. 识别独立任务

在开始前，先分析用户需求，识别可以独立并行开发的任务。每个独立任务将：
- 拥有独立的 worktree
- 拥有独立的 spec 设计文档（`YYYY-MM-DD-<topic>-design.md`）
- 拥有独立的 plan 实施计划（`YYYY-MM-DD-<feature-name>.md`）
- 拥有独立的 findings 研究记录（`YYYY-MM-DD-<topic>-findings.md`）
- 由独立的 Agent 执行

#### 2. 流水线处理每个任务

**对每个独立任务，按以下顺序处理，完成一个立即启动 Agent，再处理下一个：**

```
任务 1：
  1. clawt create -b feat-user-auth -y
  2. brainstorming → spec 写入 worktree 的 docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
                  → findings 写入 worktree 的 docs/superpowers/findings/YYYY-MM-DD-<topic>-findings.md
  3. writing-plans → plan 写入 worktree 的 docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md
  4. clawt tasks init → 生成任务模板文件
  5. 修改任务模板文件，填入分支名和任务描述
  6. 后台执行：clawt resume -f <任务文件路径> &
  7. 继续处理任务 2...
```

**⚠️ 关键约束：**
- **禁止使用 `using-git-worktrees` 技能创建 worktree，必须使用 clawt 命令**
- **必须使用 `-y` 参数**跳过交互式确认
- **`clawt resume -f` 必须后台运行**，因为它使用备选屏幕缓冲区

#### 3. 任务文件生成与执行

**⚠️ 重要：使用 `clawt resume -f` 而非 `clawt run -f`**

由于主 Agent 需要先 `clawt create -b` 创建 worktree 以便写入 spec/plan，而 `clawt run -f` 底层会再次调用 `clawt create`（导致冲突），因此必须使用 `clawt resume -f`。

`clawt resume -f` 的智能行为：
| 场景 | 行为 |
|-----|------|
| worktree 无历史会话 | 新建会话执行任务 |
| worktree 有历史会话 | 继续上次对话（追加 `--continue`） |

##### 前置检查：确保 .gitignore 忽略任务文件

由于 `clawt tasks init` 会在主 worktree 生成任务文档，**必须先检查** `.gitignore` 是否忽略了 `.clawt/tasks/` 目录：

```bash
# 检查 .gitignore 是否包含 .clawt/tasks/
grep -q "\.clawt/tasks" .gitignore 2>/dev/null || echo ".clawt/tasks/" >> .gitignore
```

**⚠️ 为什么必须忽略？**
- 任务文件是临时性的调度文件，不应提交到版本库
- 避免多人协作时产生冲突
- 保持主 worktree 的 git 状态干净

##### 步骤 1：生成任务模板

```bash
clawt tasks init
# 输出：
# ✓ 任务模板已生成: .clawt/tasks/clawt-tasks-2026-04-15-19-39-13.md
# 执行任务:
#   clawt run -f .clawt/tasks/...     # 创建 worktree 并执行（分支名需不存在）
#   clawt resume -f .clawt/tasks/...  # 在已有 worktree 中追问（分支名需已存在）
```

**⚠️ 本工作流使用 `clawt resume -f`**：因为 worktree 已通过 `clawt create -b` 创建，分支名已存在。

##### 步骤 2：修改任务模板文件

将模板文件修改为实际任务内容（**必须指定具体文件名**）：

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-user-auth
请阅读以下文档，严格按照计划执行：
- 设计文档：docs/superpowers/specs/YYYY-MM-DD-user-auth-design.md
- 研究记录：docs/superpowers/findings/YYYY-MM-DD-user-auth-findings.md
- 实施计划：docs/superpowers/plans/YYYY-MM-DD-user-auth.md

遵循 TDD 开发流程，按计划中的步骤顺序执行所有任务。
<!-- CLAWT-TASKS:END -->
```

**⚠️ 必须指定具体文件名（含日期前缀）**：
- ❌ 错误：`请阅读 docs/superpowers/specs/ 下的文档`（目录下可能有多个旧文档）
- ❌ 错误：`docs/superpowers/specs/user-auth.md`（缺少日期前缀，无法区分版本）
- ✅ 正确：`docs/superpowers/specs/YYYY-MM-DD-user-auth-design.md`（含日期的完整文件名）

##### 步骤 3：后台执行

```bash
# 必须后台运行！使用 resume -f 而非 run -f
clawt resume -f .clawt/tasks/clawt-tasks-2026-04-15-16-14-34.md &
```

**⚠️ 关键说明：**
- **使用 `clawt resume -f`**：因为 worktree 已通过 `clawt create` 创建，`run -f` 会重复创建导致冲突
- **必须后台运行（加 `&`）**：`clawt resume -f` 使用备选屏幕缓冲区，前台运行会阻塞主 Agent 的终端
- **智能会话管理**：无历史会话时新建，有历史会话时继续上次对话

---

### 用户交互方式

#### 查看任务状态

```bash
# 查看所有 worktree 状态
clawt status

# 查看所有 worktree 列表
clawt list
```

#### 与 Worktree Agent 交互

```bash
# 恢复与指定 worktree 的会话（继续上一次对话，保留完整上下文）
clawt resume -b feat-user-auth

# 此时用户直接与该 worktree 的 Agent 对话
# Agent 拥有上一次会话的完整上下文（包括已执行的任务、代码修改、对话历史）
# 可以继续开发、修改需求、或接受新指令
```

**⚠️ `clawt resume` 的关键特性：**
- **继续对话**：不是启动新会话，而是恢复上一次的会话
- **保留上下文**：Agent 记得之前做了什么、改了哪些代码、讨论了什么
- **无缝衔接**：用户可以直接说"把刚才的登录接口改成..."，Agent 能理解"刚才"指的是什么

#### 验证与合并

```bash
# 验证分支变更
clawt validate feat-user-auth

# 合并已验证的分支
clawt merge feat-user-auth

# 移除不再需要的 worktree
clawt remove feat-user-auth -y
```

---

### ⚠️ 关键规范

#### 1. 文档自包含原则（最高优先级）

**每个 worktree 的 spec/plan/findings 必须完全自包含**，包含执行该任务所需的全部信息：

- ✅ Figma 链接、设计稿路径
- ✅ 图片路径、资源文件位置
- ✅ DOM 定位、CSS 选择器
- ✅ API 地址、接口文档
- ✅ 数据结构、类型定义
- ✅ 业务逻辑、验收标准

**❌ 禁止跨 worktree 引用**：
- 不得引用"见其他 worktree"、"参考 feat-user-auth 的设计"
- 每个 worktree 的 Agent 完全独立，无法访问其他 worktree 的内容

#### 2. 分支命名规范

| 前缀 | 用途 | 示例 |
|-----|------|------|
| `feat-` | 新功能 | `feat-user-auth` |
| `fix-` | Bug 修复 | `fix-login-error` |
| `refactor-` | 重构 | `refactor-api-layer` |
| `docs-` | 文档 | `docs-api-guide` |
| `test-` | 测试 | `test-auth-module` |

**命名规则**：
- ✅ 使用小写字母和连字符 `-` 连接
- ✅ 保持简洁但有描述性
- ❌ 禁止使用 `/`、`.`、`:`、`*`、`?`、空格等特殊字符

#### 3. Clawt 命令规范

| 操作 | 命令 | 说明 |
|-----|------|------|
| 创建 worktree | `clawt create -b <branch> -y` | 必须使用 `-y` |
| 生成任务模板 | `clawt tasks init` | 输出路径在命令输出中 |
| 执行任务文件 | `clawt resume -f <path> &` | **必须后台运行** |
| 恢复会话 | `clawt resume -b <branch>` | 用户与 Agent 交互 |
| 移除 worktree | `clawt remove <branch> -y` | 必须使用 `-y` |
| 查看状态 | `clawt status` | 查看所有 worktree 状态 |
| 列出 worktree | `clawt list` | 列出当前项目所有 worktree |

**⚠️ 禁止**：
- 使用 `git worktree add` 直接创建（绕过 clawt 管理）
- 使用 `git worktree remove` 直接移除（会遗留验证分支）
- 手动删除 `~/.clawt/worktrees/` 下的目录
- 前台运行 `clawt resume -f`（会阻塞终端）

#### 4. 主 Agent 职责边界

**主 Agent 仅负责**：
1. 分析用户需求，拆分独立任务
2. 使用 clawt 创建 worktrees
3. 为每个 worktree 生成 spec、findings 和 plan（直接写入 worktree 的 docs/ 目录，文件名含日期前缀）
4. 生成任务文件并后台启动 `clawt resume -f`
5. 派发所有任务后，生命周期结束

**⚠️ 绝对禁止**：
- **禁止修改主 worktree 的任何代码**
- **禁止在主 worktree 中创建 spec/plan/findings 文件**
- spec、findings、plan 必须写到 `clawt create` 创建的对应 worktree 目录中

**不负责**：
- 与 worktree Agent 通信（用户直接 `clawt resume -b` 交互）
- 验证代码（用户使用 `clawt validate`）
- 合并代码（用户使用 `clawt merge`）
- 移除 worktree（用户使用 `clawt remove`）

---

### 完整示例

用户输入：
> 帮我实现用户认证和订单系统两个模块

主 Agent 执行：

```bash
# === 任务 1: 用户认证 ===
clawt create -b feat-user-auth -y
# 写入 spec     到 ~/.clawt/worktrees/<project>/feat-user-auth/docs/superpowers/specs/YYYY-MM-DD-user-auth-design.md
# 写入 findings 到 ~/.clawt/worktrees/<project>/feat-user-auth/docs/superpowers/findings/YYYY-MM-DD-user-auth-findings.md
# 写入 plan     到 ~/.clawt/worktrees/<project>/feat-user-auth/docs/superpowers/plans/YYYY-MM-DD-user-auth.md
clawt tasks init
# 修改 .clawt/tasks/clawt-tasks-xxx.md
clawt resume -f .clawt/tasks/clawt-tasks-xxx.md &

# === 任务 2: 订单系统 ===
clawt create -b feat-order-system -y
# 写入 spec     到 ~/.clawt/worktrees/<project>/feat-order-system/docs/superpowers/specs/YYYY-MM-DD-order-system-design.md
# 写入 findings 到 ~/.clawt/worktrees/<project>/feat-order-system/docs/superpowers/findings/YYYY-MM-DD-order-system-findings.md
# 写入 plan     到 ~/.clawt/worktrees/<project>/feat-order-system/docs/superpowers/plans/YYYY-MM-DD-order-system.md
clawt tasks init
# 修改 .clawt/tasks/clawt-tasks-yyy.md
clawt resume -f .clawt/tasks/clawt-tasks-yyy.md &

# === 主 Agent 完成 ===
# 提示用户可使用以下命令与各 worktree Agent 交互：
#   clawt resume -b feat-user-auth
#   clawt resume -b feat-order-system
```

用户后续操作：

```bash
# 与用户认证模块的 Agent 对话
clawt resume -b feat-user-auth
# > 请把登录接口改成支持手机号登录

# 查看所有任务状态
clawt status

# 验证和合并
clawt validate feat-user-auth
clawt merge feat-user-auth
clawt remove feat-user-auth -y
```

---

### 快速参考

```bash
# === 主 Agent 命令 ===
clawt create -b <branch> -y     # 创建 worktree
clawt tasks init                 # 生成任务模板
clawt resume -f <path> &         # 后台执行任务（必须加 &）

# === 用户命令 ===
clawt resume -b <branch>         # 与 worktree Agent 交互
clawt status                     # 查看状态
clawt list                       # 列出 worktree
clawt validate <branch>          # 验证变更
clawt merge <branch>             # 合并分支
clawt remove <branch> -y         # 移除 worktree
clawt home                       # 切回主分支
```

```
# === 工作流速查 ===

主 Agent 流程：
1. 分析用户需求，识别独立任务
2. 对每个任务（流水线处理）：
   a. clawt create -b <branch> -y
   b. brainstorming → spec（YYYY-MM-DD-<topic>-design.md）写入 worktree
                    → findings（YYYY-MM-DD-<topic>-findings.md）写入 worktree
   c. writing-plans → plan（YYYY-MM-DD-<feature-name>.md）写入 worktree
   d. clawt tasks init
   e. 修改任务模板文件（引用含日期的具体文件名）
   f. clawt resume -f <path> &（后台执行）
3. 所有任务派发完成，主 Agent 结束

用户后续操作：
- clawt resume -b <branch> 与任意 Agent 交互
- clawt validate/merge/remove 管理分支
```
