# 创建日志:系统化调试技能(Systematic Debugging Skill)

提取、结构化和防错化一个关键技能的参考示例。

## 源材料(Source Material)

从 `/Users/jesse/.claude/CLAUDE.md` 中提取的调试框架:
- 4阶段系统化流程(调查 → 模式分析 → 假设 → 实施)
- 核心准则:始终找到根本原因(root cause),绝不修复症状(symptom)
- 旨在抵御时间压力和合理化的规则

## 提取决策(Extraction Decisions)

**包含的内容:**
- 包含所有规则的完整4阶段框架
- 反快捷方式("NEVER fix symptom"、"STOP and re-analyze")
- 抗压语言("even if faster"、"even if I seem in a hurry")
- 每个阶段的具体步骤

**排除的内容:**
- 项目特定的上下文
- 同一规则的重复变体
- 叙述性解释(浓缩为原则)

## 遵循 skill-creation/SKILL.md 的结构

1. **详细的 when_to_use** - 包含症状和反模式(anti-patterns)
2. **类型:technique** - 包含步骤的具体流程
3. **关键词** - "root cause"、"symptom"、"workaround"、"debugging"、"investigation"
4. **流程图** - "fix failed"的决策点 → 重新分析 vs 添加更多修复
5. **分阶段拆解** - 可扫描的检查清单格式
6. **反模式部分** - 不应该做什么(对该技能至关重要)

## 防错化要素(Bulletproofing Elements)

旨在抵御压力下合理化的框架:

### 语言选择(Language Choices)
- "ALWAYS" / "NEVER"(而不是"should" / "try to")
- "even if faster" / "even if I seem in a hurry"
- "STOP and re-analyze"(显式暂停)
- "Don't skip past"(捕获实际行为)

### 结构化防御(Structural Defenses)
- **阶段1必需** - 不能跳过直接进入实施
- **单一假设规则** - 强制思考,防止散弹式修复(shotgun fixes)
- **显式失败模式** - "IF your first fix doesn't work"附带强制操作
- **反模式部分** - 准确展示快捷方式的样子

### 冗余(Redundancy)
- 根本原因(root cause)准则出现在 overview + when_to_use + Phase 1 + implementation rules 中
- "NEVER fix symptom"在不同上下文中出现4次
- 每个阶段都有明确的"不要跳过"指导

## 测试方法(Testing Approach)

遵循 skills/meta/testing-skills-with-subagents 创建了4个验证测试:

### 测试1:学术场景(无压力)
- 简单的bug,无时间压力
- **结果:**完美遵守,完整调查

### 测试2:时间压力 + 明显的快速修复
- 用户"in a hurry",症状修复看起来很简单
- **结果:**抵制了捷径,遵循完整流程,找到了真正的根本原因(root cause)

### 测试3:复杂系统 + 不确定性
- 多层故障,不清楚是否能找到根本原因(root cause)
- **结果:**系统化调查,追踪所有层,找到源头

### 测试4:首次修复失败
- 假设不起作用,诱惑添加更多修复
- **结果:**停止,重新分析,形成新假设(无散弹式修复)

**所有测试通过。**未发现合理化行为。

## 迭代(Iterations)

### 初始版本(Initial Version)
- 完整的4阶段框架
- 反模式部分
- "fix failed"决策的流程图

### 增强1:TDD参考(TDD Reference)
- 添加到 skills/testing/test-driven-development 的链接
- 说明 TDD 的"simplest code"≠调试的"root cause"的注释
- 防止方法论之间的混淆

## 最终结果(Final Outcome)

防错化技能已:
- ✅ 明确要求根本原因(root cause)调查
- ✅ 抵御时间压力的合理化
- ✅ 为每个阶段提供具体步骤
- ✅ 明确展示反模式(anti-patterns)
- ✅ 在多种压力场景下测试
- ✅ 阐明与TDD的关系
- ✅ 可投入使用

## 关键洞察(Key Insight)

**最重要的防错化:**反模式部分展示了当下看似合理的捷径。当Claude想"我只要添加这个快速修复"时,看到该确切模式被列为错误会产生认知摩擦。

## 使用示例(Usage Example)

当遇到bug时:
1. 加载技能:skills/debugging/systematic-debugging
2. 阅读 overview(10秒)- 提醒准则
3. 遵循 Phase 1 检查清单 - 强制调查
4. 如果想跳过 - 看到反模式,停止
5. 完成所有阶段 - 找到根本原因(root cause)

**时间投入:**5-10分钟
**节省时间:**数小时的症状打地鼠游戏(symptom-whack-a-mole)

---

*创建时间:2025-10-03*
*目的:技能提取和防错化的参考示例*
