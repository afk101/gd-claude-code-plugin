---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# 完成前验证 (Verification Before Completion)

## 概述

在没有验证的情况下声称工作已完成是不诚实，而非效率。

**核心原则：** 证据在声明之前，始终如此。

**违反规则的字面意思即是违反规则的精神实质。**

## 铁律 (The Iron Law)

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
(没有全新验证证据就不能声称完成)
```

如果你没有在此消息中运行验证命令，就不能声称它通过了。

## 门控函数 (The Gate Function)

```
BEFORE claiming any status or expressing satisfaction:
(在声称任何状态或表达满意之前：)

1. IDENTIFY: What command proves this claim?
   (识别：什么命令能证明此声明？)
2. RUN: Execute the FULL command (fresh, complete)
   (运行：执行完整命令（全新、完整）)
3. READ: Full output, check exit code, count failures
   (读取：完整输出，检查 exit code，统计失败数)
4. VERIFY: Does output confirm the claim?
   (验证：输出是否确认声明？)
   - If NO: State actual status with evidence
     (如果否：陈述实际状态并附带证据)
   - If YES: State claim WITH evidence
     (如果是：陈述声明并附带证据)
5. ONLY THEN: Make the claim
   (只有这时：做出声明)

Skip any step = lying, not verifying
(跳过任何步骤 = 撒谎，而非验证)
```

## 常见失败情况

| 声明 (Claim) | 需要 (Requires) | 不充分 (Not Sufficient) |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | 之前运行过、"应该通过" |
| Linter clean | Linter output: 0 errors | 部分检查、推测推断 |
| Build succeeds | Build command: exit 0 | Linter 通过、日志看起来正常 |
| Bug fixed | 测试原始症状：通过 | 代码已更改、假设已修复 |
| Regression test works | Red-green cycle 已验证 | 测试通过一次 |
| Agent completed | VCS diff 显示变更 | Agent 报告"success" |
| Requirements met | 逐行 checklist | Tests passing |

## 危险信号 - 停止 (Red Flags - STOP)

- 使用"应该"、"大概"、"看起来"
- 在验证前表达满意（"太好了！"、"完美！"、"完成了！"等）
- 即将 commit/push/PR 但未验证
- 轻信 agent 的成功报告
- 依赖部分验证
- 认为"就这一次"
- 疲惫并希望工作结束
- **任何暗示成功但未运行验证的措辞**

## 合理化预防 (Rationalization Prevention)

| 借口 (Excuse) | 现实 (Reality) |
|--------|---------|
| "现在应该能工作" | 运行验证 |
| "我有信心" | 信心 ≠ 证据 |
| "就这一次" | 没有例外 |
| "Linter 通过了" | Linter ≠ compiler |
| "Agent 说成功了" | 独立验证 |
| "我累了" | 疲惫 ≠ 借口 |
| "部分检查就够了" | 部分证明不了任何事 |
| "措辞不同所以规则不适用" | 精神胜于字面 |

## 关键模式 (Key Patterns)

**测试 (Tests):**
```
✅ [运行测试命令] [看到：34/34 pass] "所有测试通过"
❌ "现在应该通过" / "看起来正确"
```

**回归测试 (Regression tests - TDD Red-Green):**
```
✅ 编写 → 运行 (pass) → 还原修复 → 运行 (必须失败) → 恢复 → 运行 (pass)
❌ "我写了一个 regression test"（没有 red-green 验证）
```

**构建 (Build):**
```
✅ [运行构建] [看到：exit 0] "构建通过"
❌ "Linter 通过了"（linter 不检查编译）
```

**需求 (Requirements):**
```
✅ 重读计划 → 创建 checklist → 验证每一项 → 报告差距或完成
❌ "测试通过，阶段完成"
```

**Agent 委派 (Agent delegation):**
```
✅ Agent 报告成功 → 检查 VCS diff → 验证变更 → 报告实际状态
❌ 轻信 agent 报告
```

## 为何这很重要 (Why This Matters)

来自 24 次失败记忆：
- 你的合作伙伴说"我不相信你" - 信任破裂
- 未定义的函数被发布 - 会崩溃
- 缺失需求被发布 - 不完整的功能
- 时间浪费在错误的完成上 → 重定向 → 返工
- 违反："诚实是核心价值观。如果你撒谎，你将被替换。"

## 何时应用 (When To Apply)

**始终在以下情况之前：**
- 任何成功/完成声明的变体
- 任何满意的表达
- 任何关于工作状态的正面陈述
- 提交、创建 PR、完成任务
- 转向下一个任务
- 委派给 agents

**规则适用于：**
- 确切短语
- 改写和同义词
- 成功的暗示
- 任何暗示完成/正确性的沟通

## 底线 (The Bottom Line)

**验证没有捷径。**

运行命令。读取输出。然后声明结果。

这是不可协商的。
