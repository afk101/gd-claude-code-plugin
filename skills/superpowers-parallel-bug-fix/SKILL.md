---
name: parallel-bug-fix
description: 仅在 Bug 修复流程中，存在 3 个或以上相互独立的 bug 时使用（由 workflow-router 调用，或用户明确调用）。为每个独立 bug 派遣专属 agent 并行调查修复，不适用于新功能开发。
---

# 并行 Bug 修复（Parallel Bug Fix）

## 概述

你将任务委派给具有独立上下文的专业 agent。通过精确设计它们的指令和上下文，确保它们保持专注并成功完成任务。它们不应该继承你的会话上下文或历史记录——你需要构建它们真正需要的内容。这也保留了你自己用于协调工作的上下文。

当你遇到多个不相关的失败（不同的测试文件、不同的子系统、不同的 bug）时，按顺序调查它们会浪费时间。每次调查都是独立的，可以并行进行。

**核心原则：** 为每个独立的问题领域分配一个 agent。让它们并发工作。

## 使用时机

```dot
digraph when_to_use {
    "Multiple failures?" [shape=diamond];
    "Are they independent?" [shape=diamond];
    "Single agent investigates all" [shape=box];
    "One agent per problem domain" [shape=box];
    "Can they work in parallel?" [shape=diamond];
    "Sequential agents" [shape=box];
    "Parallel dispatch" [shape=box];

    "Multiple failures?" -> "Are they independent?" [label="yes"];
    "Are they independent?" -> "Single agent investigates all" [label="no - related"];
    "Are they independent?" -> "Can they work in parallel?" [label="yes"];
    "Can they work in parallel?" -> "Parallel dispatch" [label="yes"];
    "Can they work in parallel?" -> "Sequential agents" [label="no - shared state"];
}
```

**适用场景：**
- 3个或更多测试文件因不同原因失败
- 多个子系统独立损坏
- 每个问题都可以在不了解其他问题上下文的情况下理解
- 调查之间没有共享状态

**不适用场景：**
- 失败是相关的（修复一个可能会修复其他）
- 需要了解完整的系统状态
- Agent 会相互干扰

## 模式

### 1. 识别独立领域

按损坏的内容对失败进行分组：
- 文件 A 测试：工具审批流程
- 文件 B 测试：批处理完成行为
- 文件 C 测试：中止功能

每个领域都是独立的——修复工具审批不会影响中止测试。

### 2. 创建聚焦的 Agent 任务

每个 agent 获得：
- **具体范围：** 一个测试文件或子系统
- **明确目标：** 让这些测试通过
- **约束条件：** 不要更改其他代码
- **预期输出：** 你发现和修复内容的摘要

### 3. 并行调度

```typescript
// In Claude Code / AI environment
Task("Fix agent-tool-abort.test.ts failures")
Task("Fix batch-completion-behavior.test.ts failures")
Task("Fix tool-approval-race-conditions.test.ts failures")
// 所有三个任务并发运行
```

### 4. 审查和整合

当 agent 返回时：
- 阅读每个摘要
- 验证修复不冲突
- 运行完整测试套件
- 整合所有更改

## Agent 提示结构

好的 agent 提示是：
1. **聚焦的** - 一个明确的问题领域
2. **自包含的** - 理解问题所需的所有上下文
3. **输出明确** - agent 应该返回什么？

```markdown
修复 src/agents/agent-tool-abort.test.ts 中的 3 个失败测试：

1. "should abort tool with partial output capture" - 期望消息中包含 'interrupted at'
2. "should handle mixed completed and aborted tools" - 快速工具被中止而不是完成
3. "should properly track pendingToolCount" - 期望 3 个结果但得到 0

这些是时序/竞态条件问题。你的任务：

1. 阅读测试文件并理解每个测试验证的内容
2. 识别根本原因 - 是时序问题还是实际的 bug？
3. 通过以下方式修复：
   - 用基于事件的等待替换任意超时
   - 如果发现则修复中止实现中的 bug
   - 如果测试行为已更改则调整测试期望

不要只是增加超时时间 - 找到真正的问题。

返回：你发现的问题和修复内容的摘要。
```

## 常见错误

**❌ 太宽泛：** "修复所有测试" - agent 会迷失方向
**✅ 具体：** "修复 agent-tool-abort.test.ts" - 聚焦的范围

**❌ 无上下文：** "修复竞态条件" - agent 不知道在哪里
**✅ 有上下文：** 粘贴错误消息和测试名称

**❌ 无约束：** Agent 可能会重构所有内容
**✅ 有约束：** "不要更改生产代码" 或 "仅修复测试"

**❌ 输出模糊：** "修复它" - 你不知道改了什么
**✅ 输出明确：** "返回根本原因和更改的摘要"

## 何时不使用

**相关的失败：** 修复一个可能会修复其他 - 先一起调查
**需要完整上下文：** 理解需要查看整个系统
**探索性调试：** 你还不知道什么坏了
**共享状态：** Agent 会相互干扰（编辑相同文件、使用相同资源）

## 会话中的真实示例

**场景：** 大重构后 3 个文件中有 6 个测试失败

**失败：**
- agent-tool-abort.test.ts：3 个失败（时序问题）
- batch-completion-behavior.test.ts：2 个失败（工具未执行）
- tool-approval-race-conditions.test.ts：1 个失败（执行计数 = 0）

**决策：** 独立领域 - 中止逻辑与批处理完成与竞态条件分离

**调度：**
```
Agent 1 → 修复 agent-tool-abort.test.ts
Agent 2 → 修复 batch-completion-behavior.test.ts
Agent 3 → 修复 tool-approval-race-conditions.test.ts
```

**结果：**
- Agent 1：用基于事件的等待替换超时
- Agent 2：修复事件结构 bug（threadId 在错误位置）
- Agent 3：添加等待异步工具执行完成的逻辑

**整合：** 所有修复独立，无冲突，完整套件通过

**节省时间：** 并行解决 3 个问题 vs 顺序解决

## 主要优势

1. **并行化** - 多个调查同时进行
2. **聚焦** - 每个 agent 范围狭窄，跟踪的上下文更少
3. **独立性** - Agent 不会相互干扰
4. **速度** - 在 1 个问题的时间内解决 3 个问题

## 验证

在 agent 返回后：
1. **审查每个摘要** - 理解发生了什么变化
2. **检查冲突** - Agent 是否编辑了相同代码？
3. **运行完整套件** - 验证所有修复一起工作
4. **抽查** - Agent 可能犯系统性错误

## 实际影响

来自调试会话（2025-10-03）：
- 3 个文件中有 6 个失败
- 并行调度 3 个 agent
- 所有调查并发完成
- 所有修复成功整合
- Agent 更改之间零冲突
