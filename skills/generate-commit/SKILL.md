---
name: generate-commit
description: >
  This skill should be used when the user asks to "generate commit message", "create conventional commit",
  "write commit message", "commit changes", "generate git commit", "conventional commit", or mentions
  "commit message" in the context of staged git changes. Analyzes git diff output and generates clean
  conventional commit messages following the Conventional Commits specification.
version: 1.0.0
---

# Conventional Commit Message Generator

根据 Git 暂存区的变更内容，生成符合 Conventional Commits 规范的提交信息。

## 核心工作流程

### 第一步：获取暂存区变更

运行以下命令获取当前暂存区的变更信息：

```bash
git diff --cached --stat
git diff --cached
```

若暂存区无内容，检查工作区是否有变更（`git status`）。如果工作区存在未暂存的变更，自动执行 `git add .` 将所有变更添加到暂存区，无需经过用户确认，然后继续后续流程。若工作区也无任何变更，提示用户当前没有可提交的内容。

### 第二步：分析变更内容

根据 diff 输出，按以下顺序判断：

1. **确定主类型（type）** — 根据变更性质从类型表中选择
2. **识别作用域（scope）** — 从修改的目录或模块中提取
3. **撰写描述（description）** — 聚焦最重要的变更
4. **判断是否为破坏性变更** — 检查是否存在不兼容的 API 改动
5. **编写正文（body）** — 对复杂变更说明"做了什么"和"为什么"
6. **添加脚注（footer）** — 关联 issue 或标注 BREAKING CHANGE

### 第三步：生成提交信息

按照以下格式输出：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 第四步：自动执行提交

生成提交信息后，直接执行 `git commit -m "<提交信息>"` 完成提交，无需经过用户确认。整个流程（分析变更 → 生成消息 → 执行提交）应一气呵成，自动完成。

## 提交类型速查表

| 类型 | 说明 | 版本影响 |
|------|------|----------|
| `feat` | 新功能或新特性 | MINOR |
| `fix` | 修复 Bug 或错误 | PATCH |
| `docs` | 仅文档变更 | - |
| `style` | 代码风格变更（空格、格式、分号等） | - |
| `refactor` | 重构代码（不涉及新功能或修复） | - |
| `perf` | 性能优化 | - |
| `test` | 添加或修复测试 | - |
| `build` | 构建系统或外部依赖变更 | - |
| `ci` | CI/CD 配置变更 | - |
| `chore` | 维护任务、工具变更 | - |
| `revert` | 回退之前的提交 | - |

## 作用域（Scope）指南

- 使用小括号包裹：`feat(api):`, `fix(ui):`
- 常见作用域：`api`, `ui`, `auth`, `db`, `config`, `deps`, `docs`
- Monorepo 场景：使用包名或模块名
- 保持简洁、小写

## 描述（Description）规则

- 使用祈使语气（"添加" 而非 "添加了" 或 "已添加"）
- 首字母小写
- 末尾不加句号
- 最多 50 个字符
- 简洁但具有描述性

## 正文（Body）规则

- 与描述之间空一行
- 解释"做了什么"和"为什么"，而非"怎么做"
- 每行不超过 72 个字符
- 对复杂变更提供额外说明

## 脚注（Footer）规则

- 与正文之间空一行
- 破坏性变更：`BREAKING CHANGE: <说明>`
- 关联 Issue：`Closes #123`, `Refs #456`

## 输出规范

### 关键限制

- **禁止**包含任何状态标记（如 `[Memory Bank: Active]`）
- **禁止**包含任何与任务格式相关的标记
- **仅输出**干净的 conventional commit 消息
- 使用中文回答解释性内容
- 若一次提交实现了多个功能，使用 `-` 符号逐行列出

### 单一功能示例

```
feat(auth): 添加 JWT token 自动刷新机制

避免用户因 token 过期而频繁登录

Closes #234
```

### 多功能示例

```
feat(user): 新增用户管理功能

- 新增用户注册接口
- 新增邮箱验证功能
- 添加用户头像上传支持

BREAKING CHANGE: 用户注册接口新增必填字段 email

Closes #567
```

### 破坏性变更示例

```
feat(api)!: 重新设计认证接口

重新设计认证接口，使用 OAuth 2.0 替换旧的 session 认证方式

BREAKING CHANGE: /api/auth 接口请求参数和响应格式已完全变更

Refs #789
```

## 变更分析策略

参考 `references/analysis-guide.md` 获取详细的变更分析方法和边界情况处理指南。

## 额外说明

- 当暂存区包含多种类型的变更时，建议用户拆分为多个提交
- 若无法明确判断类型，默认使用 `chore`
- 对于 revert 类型，在正文中包含被回退的提交哈希
