---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# 编写计划

## 概述

编写全面的实施计划,假设工程师对我们的代码库零了解且品味存疑。记录他们需要知道的一切:每个任务需要触及哪些文件、代码、测试、可能需要检查的文档,以及如何测试。以小粒度任务的形式给出整个计划。DRY。YAGNI。TDD。频繁提交。

假设他们是有经验的开发者,但几乎不了解我们的工具集或问题领域。假设他们不太了解良好的测试设计。

**开始时宣布:**"我正在使用 writing-plans skill 创建实施计划。"

**计划保存位置:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (用户对计划位置的首选项会覆盖此默认值)

## 范围检查

如果规格说明涵盖多个独立的子系统,它应该在 brainstorming 期间被分解为子项目规格说明。如果没有,建议将其分解为单独的计划 — 每个子系统一个计划。每个计划都应该能独立产生可工作、可测试的软件。

## 文件结构

在定义任务之前,规划出将要创建或修改哪些文件以及每个文件的职责。这是确定分解决策的地方。

- 设计具有清晰边界和明确定义接口的单元。每个文件应该有一个明确的职责。
- 你最能理解可以一次性保持在上下文中的代码,当文件聚焦时你的编辑更可靠。优先选择较小的、聚焦的文件,而不是做太多事情的大型文件。
- 一起变化的文件应该放在一起。按职责分离,而不是按技术层分离。
- 在现有代码库中,遵循既定的模式。如果代码库使用大文件,不要单方面重构 — 但如果你要修改的文件已经变得笨重,在计划中包含拆分是合理的。

此结构为任务分解提供依据。每个任务应该产生独立合理的自包含变更。

## 小粒度任务粒度

**每个步骤是一个动作(2-5分钟):**
- "编写失败的测试" - 步骤
- "运行它以确保它失败" - 步骤
- "实现使测试通过的最小代码" - 步骤
- "运行测试并确保它们通过" - 步骤
- "提交" - 步骤

## 计划文档头部

**每个计划必须以此头部开始:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## 任务结构

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 禁止占位符

每个步骤必须包含工程师需要的实际内容。这些是**计划失败** — 永远不要写它们:
- "TBD"、"TODO"、"implement later"、"fill in details"
- "添加适当的错误处理" / "添加验证" / "处理边界情况"
- "为上述编写测试"(没有实际的测试代码)
- "类似于任务 N"(重复代码 — 工程师可能不按顺序阅读任务)
- 描述做什么而不展示如何做的步骤(代码步骤需要代码块)
- 引用未在任何任务中定义的类型、函数或方法

## 记住
- 始终使用精确的文件路径
- 每个步骤中的完整代码 — 如果某个步骤更改代码,请展示代码
- 精确的命令和预期输出
- DRY、YAGNI、TDD、频繁提交

## 自我审查

编写完整个计划后,用全新的眼光审视规格说明,并根据它检查计划。这是你自己运行的检查清单 — 不是 subagent 调度。

**1. 规格说明覆盖:** 快速浏览规格说明中的每个部分/需求。你能指出实现它的任务吗?列出任何缺口。

**2. 占位符扫描:** 在计划中搜索危险信号 — 上文"禁止占位符"部分中的任何模式。修复它们。

**3. 类型一致性:** 你在后续任务中使用的类型、方法签名和属性名称是否与早期任务中定义的匹配?任务 3 中名为 `clearLayers()` 的函数但在任务 7 中是 `clearFullLayers()` 就是一个 bug。

如果发现问题,直接修复。无需重新审查 — 修复后继续。如果发现没有任务的规格说明需求,添加该任务。

## 执行移交

计划保存后，向用户展示计划并请求确认计划内容：

**"计划完成并保存到 `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`。请确认计划内容没有问题，确认后将自动调用 `superpowers:subagent-driven-development` 开始执行。"**

**必须**等待用户确认计划内容。用户确认后，你才能调用 `superpowers:subagent-driven-development`，对每个任务派遣独立 subagent 执行（每个任务一个新 subagent + 两阶段审查：规范符合性 → 代码质量）。
