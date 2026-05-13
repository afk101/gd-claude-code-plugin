---
name: workflow-router
description: 仅在用户明确调用时使用（如 /workflow-router 或"使用 workflow-router"）。根据任务类型编排调用其他 skills 的顺序流程。
---

# 工作流路由

根据任务类型判断走哪条流程，然后作为编排者按顺序引导调用各 skill。**本 skill 自身不写代码、不做实现**，只负责识别路径和编排顺序。

---

## 第一步：判断任务类型

向用户确认（如果不明确）：

> "这个任务是 **新增功能** 还是 **bug 修复**？"

| 信号 | 类型 |
|------|------|
| 新建、添加、实现、开发、支持… | 新增功能 → 流程 A |
| 报错、失败、崩溃、不对、异常… | Bug 修复 → 流程 B |

---

## 流程 A：新增功能

```
brainstorming        ← 探索需求，产出 spec + findings
    ↓
writing-plans        ← 基于 spec 制定实施计划
    ↓
[实现阶段]           ← 见下方「共用实现阶段」
```

**前置步骤说明：**

**`superpowers:brainstorming`**
写任何代码前必须先完成此步。探索上下文、逐一澄清需求、提出方案、分段获得用户批准、写入 spec 文档和 findings 文档并提交、规范自审、等待用户最终批准。
→ 用户批准规范后，进入 writing-plans。

**`superpowers:writing-plans`**
基于批准的 spec，编写细粒度实施计划。每步 2-5 分钟，TDD 节奏，完整代码，精确路径，禁止占位符。完成后自审。
→ 计划保存完毕后，进入实现阶段。

---

## 流程 B：Bug 修复

```
systematic-debugging ← 调查根本原因，向用户提问，迭代 findings
    ↓
brainstorming        ← 根本原因已知，讨论修复方案，产出 spec，有新发现则追加 findings
    ↓
writing-plans        ← 基于 spec 制定修复计划
    ↓
[实现阶段]           ← 见下方「共用实现阶段」
                        当存在 3+ 个相互独立的 bug 时，用 parallel-bug-fix 替代 subagent-driven-development
```

**前置步骤说明：**

**`superpowers:systematic-debugging`**
调查阶段，先于一切其他行动。遇到信息盲区时向用户提问，持续迭代 findings，直到根本原因明确。执行 Phase 1-3（调查阶段），**Phase 4（实现）不在此执行，由后续 brainstorming → writing-plans → 实现阶段负责**：
- **Phase 1** 根本原因调查：创建 findings → 读错误 → 复现 → 检查最近变更 → **遇到不确定时向用户提问** → 收集证据 → 追踪数据流到源头
- **Phase 2** 模式分析：找可工作的类似实现，逐行对比差异
- **Phase 3** 假设与测试：单一假设，最小变更验证，确认根本原因

根本原因明确后，**不要在这里写修复代码**，进入 brainstorming。
**3 次假设验证失败后**：停止，与用户讨论是否存在架构问题。

**`superpowers:brainstorming`**（角色与流程 A 不同）
根本原因已知，与用户讨论修复方案：
- 提出 2-3 种修复方案及权衡（快速修复 vs 根治、影响范围、风险）
- 编写 spec 文档：修复目标、验收标准、回归测试要求
- 如有方案讨论中产生的新发现，追加到已有 findings 文件（不新建）
→ 用户批准 spec 后，进入 writing-plans。

**`superpowers:writing-plans`**
基于批准的 spec，制定具体修复计划：精确到文件和代码行、复现测试步骤、回归测试步骤。
→ 计划保存完毕后，进入实现阶段。

**`superpowers:parallel-bug-fix`**（替代 subagent-driven-development，当存在 3+ 个相互独立的 bug 时）
当 bug 数量达到 3 个或以上且相互独立时，用此 skill **替代** subagent-driven-development 作为实现手段。每个 bug 分配独立 agent，给定具体范围、明确目标、约束条件（不修改其他代码）、预期输出。所有 agent 完成后：检查摘要 → 确认修复无冲突 → 派遣 final code reviewer 全量审查并处理反馈 → 进入 verification-before-completion。
不适用场景：bug 相互关联、需要完整系统状态、agent 会编辑同一文件。

---

## 共用实现阶段

两个流程在 writing-plans 完成后，均进入此阶段：

```
subagent-driven-development
    ↓  ← 每个任务内部：implementer subagent 遵循 test-driven-development（先写失败测试，再写实现）
         → spec 合规审查 → 代码质量审查
    ↓  ← 所有任务完成后：派遣 final code reviewer 全量审查，主 agent 处理反馈
    ↓  ← 声称完成前：
verification-before-completion
```

**`superpowers:subagent-driven-development`**
对每个任务循环：
- 派遣 implementer subagent（内部遵循 `superpowers:test-driven-development`）
- implementer 完成后：派遣 spec 合规审查 subagent
- spec 合规通过后：派遣代码质量审查 subagent
- 任一审查发现问题 → implementer 修复 → 再次审查，直到批准
- 所有任务完成后：派遣 final code reviewer subagent 全量审查，主 agent 按优先级处理反馈（Critical 立即修复，Important 修复后才继续，Minor 记录后处理），有据反驳错误建议，禁止表演性同意

**`superpowers:verification-before-completion`**（所有任务完成，声称完成前）
运行完整验证命令，凭输出证据声明完成。禁止"应该通过"、"看起来正确"等未验证表述。

---

## 编排者职责

在每步开始前**必须真正调用对应的 skill**，而不仅仅是在语言上声明：

**错误做法：**
> "现在我将使用 brainstorming skill 来……"（只是说了，没有实际调用）

**正确做法：**
使用 `superpowers:<skill-name>` 触发该 skill，让它的指令真正加载到上下文中并驱动行为。等该 skill 完成其完整流程后，再进入下一步。

每步完成后确认状态，再进入下一步。遇到障碍立即停止并寻求澄清，不猜测，不强行突破。
