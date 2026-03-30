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

## 任务拆分的核心原则：「不过度拆分」与「依赖合并」

任务拆分不是越细越好。拆分的目的是让多个 Agent 能**真正并行**地工作，如果拆出来的任务之间有强依赖，反而会导致联调困难、降低效率。因此，在决定如何拆分之前，你需要先做一次**依赖分析**。

### 原则一：简单任务不要拆

如果用户给你的任务本身就是一个完整的、内聚的工作单元，**不要为了拆而拆**。判断标准：

- **单一关注点**：任务围绕一个功能点/模块，拆开后每个子任务无法独立验证 → **不拆**
- **前后依赖紧密**：后一步的输入就是前一步的输出（例如「创建数据库表 → 写 CRUD 接口 → 写前端表单」这种链式依赖） → **不拆**，作为一个任务

### 原则二：有依赖的任务要合并

当用户给你一大堆任务时，你需要分析它们之间的依赖关系，把有依赖的任务**合并到同一个任务块**中。

**依赖分析的判断维度**：

1. **数据依赖**：任务 B 需要用到任务 A 的输出（新建的表、新定义的类型、新创建的组件）→ 合并
2. **接口依赖**：前端任务需要调用后端任务新建的 API → 合并（或者在前端任务中明确写出 API 契约，让前端可以 mock）
3. **文件冲突**：两个任务会修改同一个文件的同一区域 → 合并
4. **逻辑依赖**：任务 B 的实现方案取决于任务 A 怎么实现（例如 A 定义了状态管理的结构，B 要消费这个结构）→ 合并

**合并后的任务描述**应该保持清晰，用子标题或列表标明原本的各个子任务，让 Agent 知道这个任务包含多个步骤。

**示例**：用户给了 6 个小任务：
1. 创建 User 表
2. 写 User CRUD API
3. 写用户列表前端页面
4. 创建 Product 表
5. 写 Product CRUD API
6. 写商品列表前端页面

依赖分析：
- 1→2→3 是一条依赖链（表 → API → 前端页面）
- 4→5→6 是另一条独立的依赖链
- 两条链之间无依赖

**正确做法**：合并为 2 个任务：
- 任务 A：用户模块（创建 User 表 + CRUD API + 前端列表页）
- 任务 B：商品模块（创建 Product 表 + CRUD API + 前端列表页）

### 原则三：合理评估并行收益

拆分的唯一目的是**获得并行执行的收益**。在决定是否拆分时，问自己：

- 拆开后，这些任务能**同时开始**吗？如果不能（因为有依赖），拆分就没意义

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
3. **任务详情**（用户提供）：按照上面「任务拆分的核心原则」来决定如何组织任务。核心决策流程如下：

   **步骤 A — 判断任务复杂度**：
   - 如果用户给的是一个简单、内聚的任务（单一功能点，改动范围小），直接作为**一个任务**，不要拆分
   - 如果用户给的是多个功能需求或一大堆任务，进入步骤 B

   **步骤 B — 依赖分析**：
   - 列出所有子任务之间的依赖关系（数据依赖、接口依赖、文件冲突、逻辑依赖）
   - 把有依赖关系的子任务**合并为一个任务**
   - 只有真正互相独立、能并行执行的任务组才拆分为不同的任务块

   **步骤 C — 验证拆分结果**：
   - 每个任务块是否能**独立执行和验证**？
   - 合并分支时是否会产生**大量文件冲突**？
   - 如果以上任何一条不满足，重新合并相关任务

   **特殊情况**：用户想让你提供优化建议或者可以新增的功能时，各个独立的建议或功能应该分成多个任务（因为它们天然独立），每个任务都必须有任务背景，注意事项可选。
4. **关键信息完整保留**（⚠️ 最高优先级约束）：用户提供的关键定位信息和资源引用，在拆分为多个任务时，**必须原样、完整地复制到每一个相关任务的描述中**，绝对不允许省略、缩写或仅在公共背景区提及。这些关键信息包括但不限于：
   - **Figma 设计链接**（如 `https://figma.com/design/xxx?node-id=1-2`）
   - **图片/截图路径**（如 `/path/to/design.png`、`./assets/mockup.jpg`）
   - **DOM path / 元素定位**（如 `div.container > section.hero > h1`）
   - **API 端点 / 接口地址**（如 `POST /api/v1/users`）
   - **文件路径**（如 `src/components/Header.tsx`）
   - **数据库表名、字段名**
   - **具体的配置项、环境变量名**
   - **用户提供的任何 URL、链接、引用标识**

   **原因**：每个任务由独立的 Agent 并行执行，Agent 之间无法共享上下文，因此每个任务必须自包含所有必要信息。

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
- **合理拆分粒度**：每个任务应当是一个独立的、可并行执行的工作单元。不要过度拆分简单任务，有依赖的任务要合并到一起
- **⚠️ 关键信息自包含**：用户提供的 Figma 链接、图片路径、DOM 定位、API 地址等关键信息，必须完整复制到每一个需要该信息的任务中，不得省略。每个任务是独立执行的，不能依赖其他任务或公共区域的信息。

### 依赖合并的示例

**用户需求**：「帮我完成这些任务：1.创建用户表 2.写用户CRUD接口 3.写用户列表页面 4.创建订单表 5.写订单CRUD接口 6.写订单列表页面」

**依赖分析**：
- 1→2→3 形成依赖链（用户表 → 用户API → 用户前端页面）
- 4→5→6 形成依赖链（订单表 → 订单API → 订单前端页面）
- 两条链之间无依赖，可以并行

**✅ 正确做法**（合并依赖链，拆分独立模块）：

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-user-module
实现用户管理模块（包含数据库、后端 API、前端页面的完整链路）：

1. 创建用户表（在 src/db/migrations/ 下新增迁移文件）
   - 字段：id, username, email, password_hash, created_at, updated_at
2. 实现用户 CRUD API（在 src/api/users.ts 中）
   - GET /api/users - 用户列表（分页）
   - GET /api/users/:id - 用户详情
   - POST /api/users - 创建用户
   - PUT /api/users/:id - 更新用户
   - DELETE /api/users/:id - 删除用户
3. 实现用户列表前端页面（在 src/pages/UserList.tsx 中）
   - 表格展示用户数据，支持分页
   - 支持新增、编辑、删除操作
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: feat-order-module
实现订单管理模块（包含数据库、后端 API、前端页面的完整链路）：

1. 创建订单表（在 src/db/migrations/ 下新增迁移文件）
   - 字段：id, user_id, total_amount, status, created_at, updated_at
2. 实现订单 CRUD API（在 src/api/orders.ts 中）
   - GET /api/orders - 订单列表（分页）
   - GET /api/orders/:id - 订单详情
   - POST /api/orders - 创建订单
   - PUT /api/orders/:id - 更新订单状态
3. 实现订单列表前端页面（在 src/pages/OrderList.tsx 中）
   - 表格展示订单数据，支持分页
   - 支持查看详情、更新状态操作
<!-- CLAWT-TASKS:END -->
```

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

### ⚠️ 关键信息保留 — 正确 vs 错误示例

**场景**：用户提供了 Figma 链接 `https://figma.com/design/abc123?node-id=10-20` 和截图 `/tmp/design-mockup.png`，要求实现页面的 Header 和 Footer 两个组件。

**❌ 错误做法**（关键信息丢失）：

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-header
根据设计稿实现 Header 组件：
- 包含 Logo、导航菜单、用户头像
- 响应式布局，移动端显示汉堡菜单
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: feat-footer
根据设计稿实现 Footer 组件：
- 包含版权信息、社交媒体链接
- 底部固定布局
<!-- CLAWT-TASKS:END -->
```

**✅ 正确做法**（每个任务都完整包含关键信息）：

```markdown
<!-- CLAWT-TASKS:START -->
# branch: feat-header
根据设计稿实现 Header 组件：

设计稿参考：
- Figma 链接：https://figma.com/design/abc123?node-id=10-20
- 设计截图：/tmp/design-mockup.png

实现要求：
- 包含 Logo、导航菜单、用户头像
- 响应式布局，移动端显示汉堡菜单
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: feat-footer
根据设计稿实现 Footer 组件：

设计稿参考：
- Figma 链接：https://figma.com/design/abc123?node-id=10-20
- 设计截图：/tmp/design-mockup.png

实现要求：
- 包含版权信息、社交媒体链接
- 底部固定布局
<!-- CLAWT-TASKS:END -->
```

## 分支名命名规范

- 使用 `feat-xxx`（新功能）、`fix-xxx`（修复）、`refactor-xxx`（重构）、`docs-xxx`（文档）、`test-xxx`（测试）等前缀
- 使用小写字母和连字符 `-` 连接
- 保持简洁但有描述性
- 避免使用 `/`、`.`、`:`、`*`、`?`、空格等特殊字符

## 额外参考

查阅 `references/task-format.md` 获取完整的 clawt 任务文件格式规范、分支名非法字符列表及详细使用示例。
