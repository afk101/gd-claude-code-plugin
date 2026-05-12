# Defense-in-Depth Validation（深度防御验证）

## Overview（概述）

当你修复一个由无效数据引起的 bug 时，在某个地方添加 validation 可能感觉已经足够了。但是这个单一检查可能会被不同的代码路径、refactoring 或 mocks 绕过。

**Core principle（核心原则）：** 在数据流经的每一层都进行 validation。让 bug 在结构上变得不可能发生。

## Why Multiple Layers（为什么需要多层）

Single validation（单层验证）："We fixed the bug"（我们修复了 bug）
Multiple layers（多层验证）："We made the bug impossible"（我们让 bug 变得不可能发生）

不同的层捕获不同的情况：
- Entry validation（入口验证）捕获大多数 bug
- Business logic（业务逻辑）捕获边缘情况
- Environment guards（环境守卫）防止特定上下文的危险
- Debug logging（调试日志）在其他层失败时提供帮助

## The Four Layers（四个层次）

### Layer 1: Entry Point Validation（入口点验证）
**Purpose（目的）：** 在 API boundary（边界）拒绝明显无效的输入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... 继续执行
}
```

### Layer 2: Business Logic Validation（业务逻辑验证）
**Purpose（目的）：** 确保数据对该操作有意义

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... 继续执行
}
```

### Layer 3: Environment Guards（环境守卫）
**Purpose（目的）：** 在特定上下文中防止危险操作

```typescript
async function gitInit(directory: string) {
  // 在测试中，拒绝在临时目录外进行 git init
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... 继续执行
}
```

### Layer 4: Debug Instrumentation（调试工具）
**Purpose（目的）：** 捕获上下文信息用于取证

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... 继续执行
}
```

## Applying the Pattern（应用模式）

当你发现一个 bug 时：

1. **Trace the data flow（追踪数据流）** - 错误值从哪里产生？在哪里使用？
2. **Map all checkpoints（映射所有检查点）** - 列出数据流经的每个点
3. **Add validation at each layer（在每一层添加验证）** - Entry、business、environment、debug
4. **Test each layer（测试每一层）** - 尝试绕过 layer 1，验证 layer 2 能捕获它

## Example from Session（会话示例）

Bug：空的 `projectDir` 导致在源代码中执行 `git init`

**Data flow（数据流）：**
1. Test setup（测试设置）→ empty string（空字符串）
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 中运行

**Four layers added（添加的四个层次）：**
- Layer 1: `Project.create()` 验证不为空/存在/可写
- Layer 2: `WorkspaceManager` 验证 projectDir 不为空
- Layer 3: `WorktreeManager` 在测试中拒绝在 tmpdir 之外进行 git init
- Layer 4: git init 前的 stack trace 日志记录

**Result（结果）：** 所有 1847 个测试通过，bug 无法复现

## Key Insight（关键洞察）

所有四个层次都是必要的。在测试过程中，每一层都捕获了其他层遗漏的 bug：
- 不同的代码路径绕过了 entry validation（入口验证）
- Mocks 绕过了 business logic checks（业务逻辑检查）
- 不同平台上的边缘情况需要 environment guards（环境守卫）
- Debug logging（调试日志）识别了结构性误用

**不要止步于一个验证点。** 在每一层都添加检查。
