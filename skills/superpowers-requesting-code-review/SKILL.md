---
name: requesting-code-review
description: 在完成任务、实现主要功能或合并前验证工作是否满足要求时使用
---

# 请求代码审查

派遣 superpowers:code-reviewer subagent 在问题扩散前捕获它们。审查者会获得经过精心设计的上下文进行评估 —— 而不是你会话的历史记录。这使审查者专注于工作成果而非你的思考过程，并为你自己的持续工作保留上下文。

**核心原则：** 尽早审查，频繁审查。

## 何时请求审查

**必须审查：**
- 在 subagent 驱动开发中的每个任务之后
- 完成主要功能之后
- 合并到 main 分支之前

**可选但有价值：**
- 遇到困难时（获得新鲜视角）
- 重构前（基线检查）
- 修复复杂 bug 之后

## 如何请求

**1. 获取 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派遣 code-reviewer subagent：**

使用 Task tool 调用 superpowers:code-reviewer 类型，填写 `code-reviewer.md` 中的模板

**占位符：**
- `{WHAT_WAS_IMPLEMENTED}` - 你刚刚构建的内容
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始 commit
- `{HEAD_SHA}` - 结束 commit
- `{DESCRIPTION}` - 简要总结

**3. 根据反馈采取行动：**
- 立即修复 Critical 问题
- 在继续之前修复 Important 问题
- 记录 Minor 问题以便稍后处理
- 如果审查者错了，予以反驳（附带理由）

## 示例

```
[刚完成任务 2：添加验证函数]

你：让我在继续之前请求代码审查。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[派遣 superpowers:code-reviewer subagent]
  WHAT_WAS_IMPLEMENTED: 会话索引的验证和修复函数
  PLAN_OR_REQUIREMENTS: 来自 docs/superpowers/plans/deployment-plan.md 的任务 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: 添加了 verifyIndex() 和 repairIndex()，包含 4 种问题类型

[Subagent 返回]：
  优势：清晰的架构，真实的测试
  问题：
    Important: 缺少进度指示器
    Minor: 报告间隔使用魔术数字 (100)
  评估：准备继续

你：[修复进度指示器]
[继续任务 3]
```

## 与工作流集成

**Subagent 驱动开发：**
- 在每个任务后审查
- 在问题复合之前捕获它们
- 在进入下一个任务前修复

**执行计划：**
- 在每批（3 个任务）后审查
- 获取反馈，应用，继续

**Ad-Hoc 开发：**
- 合并前审查
- 遇到困难时审查

## 危险信号

**永远不要：**
- 因为"很简单"而跳过审查
- 忽略 Critical 问题
- 在未修复 Important 问题的情况下继续
- 与有效的技术反馈争论

**如果审查者错了：**
- 用技术理由反驳
- 展示证明其有效的代码/测试
- 请求澄清

参见模板：requesting-code-review/code-reviewer.md
