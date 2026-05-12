# 代码质量审查者提示模板

在派发代码质量审查者子代理时使用此模板。

**目的：** 验证实现是否构建良好（整洁、经过测试、可维护）

**仅在规范合规性审查通过后派发。**

```
Task tool (superpowers:code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]
```

**除了标准的代码质量关注点外，审查者还应检查：**
- 每个文件是否具有一个明确的职责和定义良好的接口？
- 单元是否已分解以便可以独立理解和测试？
- 实现是否遵循计划中的文件结构？
- 此实现是否创建了已经很大的新文件，或显著增加了现有文件的大小？（不要标记预先存在的文件大小——重点关注此更改所贡献的内容。）

**代码审查者返回：** 优势、问题（关键/重要/次要）、评估
