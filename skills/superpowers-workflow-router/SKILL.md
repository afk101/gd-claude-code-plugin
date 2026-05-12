---
name: workflow-router
description: 仅在用户明确调用时使用（如 /workflow-router 或"使用 workflow-router"）。根据任务类型编排调用其他 skills 的顺序流程。
---

# 工作流路由

根据任务类型判断走哪条流程，然后作为编排者按顺序引导调用各 skill。**本 skill 自身不写代码、不做实现**，只负责识别路径和编排顺序。

## 第一步：判断任务类型

向用户确认（如果不明确）：

> "这个任务是 **新增功能** 还是 **bug 修复**？"

判断依据：

| 信号 | 类型 |
|------|------|
| 新建、添加、实现、开发、支持… | 新增功能 |
| 报错、失败、崩溃、不对、异常… | Bug 修复 |

---

## 流程 A：新增功能

```
brainstorming
    ↓
writing-plans
    ↓
subagent-driven-development
    ↓  ← 每个任务内部，implementer subagent 遵循 test-driven-development
    ↓  ← 每个任务完成后，主 agent 执行以下两步：
requesting-code-review   ← 主 agent 派遣 code-reviewer subagent，获取审查报告
receiving-code-review    ← 主 agent 拿到报告后处理反馈
    ↓  ← 所有任务完成，声称完成前：
verification-before-completion
```

### 各步说明

**1. `superpowers:brainstorming`**
写任何代码前必须先完成此步。探索上下文、逐一澄清需求、提出方案、分段获得用户批准、写入 spec 文档和 findings 文档并提交、规范自审、等待用户最终批准。
→ 用户批准规范后，进入下一步。

**2. `superpowers:writing-plans`**
基于批准的 spec，编写细粒度实施计划。每步 2-5 分钟，TDD 节奏，完整代码，精确路径，禁止占位符。完成后自审。
→ 计划保存完毕后，进入下一步。

**3. `superpowers:subagent-driven-development`**
对每个任务循环：
- 派遣 implementer subagent（subagent 内部遵循 `superpowers:test-driven-development`）
- implementer 完成后：派遣 spec 合规审查 subagent
- spec 合规通过后：派遣代码质量审查 subagent
- 任一审查发现问题 → implementer 修复 → 再次审查，直到批准
- 所有任务完成后：派遣最终 code reviewer subagent 全量审查

**4. `superpowers:requesting-code-review`**（每个任务完成后，主 agent 执行）
获取 BASE_SHA 和 HEAD_SHA，使用模板派遣 code-reviewer subagent，等待返回分级报告（Critical / Important / Minor）。

**5. `superpowers:receiving-code-review`**（紧跟上一步，主 agent 执行）
拿到审查报告后按规范处理：验证每条建议的技术合理性，按优先级实施（Critical 立即修复，Important 修复后才继续，Minor 记录后处理），每条单独测试，有据反驳错误建议。禁止表演性同意。

**6. `superpowers:verification-before-completion`**（所有任务完成，声称完成前）
运行完整验证命令，凭输出证据声明完成。禁止"应该通过"、"看起来正确"等未验证表述。

---

## 流程 B：Bug 修复

```
systematic-debugging
    ↓  ← Phase 4 写复现测试时
test-driven-development
    ↓  ← 声称修复完成前
verification-before-completion
    ↓  ← 可选：存在 3+ 个相互独立的 bug 时
parallel-bug-fix
```

### 各步说明

**1. `superpowers:systematic-debugging`**
必须先调用，禁止跳过直接修复。严格按四个阶段执行：
- **Phase 1** 根本原因调查：读错误 → 复现 → 检查最近变更 → 收集证据 → 追踪数据流到源头
- **Phase 2** 模式分析：找可工作的类似实现，逐行对比差异
- **Phase 3** 假设与测试：单一假设，最小变更验证，一次只改一个变量
- **Phase 4** 实现：先用 `superpowers:test-driven-development` 写复现失败测试，再写修复，再验证无回归

**3 次修复失败后**：停止，不再尝试，与用户讨论是否存在架构问题。

**2. `superpowers:test-driven-development`**（在 Phase 4 时触发）
先写复现 bug 的失败测试并确认其正确失败，再写修复使其通过，再 REFACTOR。没有失败测试就不写修复代码。

**3. `superpowers:verification-before-completion`**（声称修复完成前）
运行完整测试套件，凭输出确认修复有效且无回归。

**4. `superpowers:parallel-bug-fix`**（可选）
当存在 3 个或以上**相互独立**的 bug 时使用。每个 bug 分配独立 agent，给定具体范围、明确目标、约束条件（不修改其他代码）、预期输出。所有 agent 完成后：检查摘要 → 确认修复无冲突 → 运行完整测试套件。

不适用场景：bug 相互关联、需要完整系统状态、agent 会编辑同一文件。

---

## 编排者职责

作为编排者，在每步开始前宣布：

> "现在进入第 N 步：`superpowers:<skill-name>`"

每步完成后确认状态，再进入下一步。遇到障碍立即停止并寻求澄清，不猜测，不强行突破。
