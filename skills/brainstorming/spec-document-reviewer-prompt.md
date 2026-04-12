# Spec Document Reviewer Prompt Template

当派遣 spec document reviewer subagent 时使用此模板。

**目的:** 验证规范文档是完整的、一致的,并且已准备好进行实施规划。

**派遣时机:** Spec document 已写入 docs/clawt/specs/

```
Task tool (general-purpose):
  description: "Review spec document"
  prompt: |

    **待审查的 Spec:** [SPEC_FILE_PATH]

    ## 检查内容

    | 类别 | 查找内容 |
    |----------|------------------|
    | 完整性 | TODOs、占位符、"TBD"、未完成的章节 |
    | 一致性 | 内部矛盾、冲突的需求 |
    | 清晰度 | 需求模糊到可能导致他人构建错误的东西 |
    | 范围 | 足够聚焦于单个计划 — 不覆盖多个独立的子系统 |
    | YAGNI | 未请求的功能、过度工程化 |

    ## 校准标准

    **仅标记会在实施规划期间导致真实问题的问题。**
    缺失的章节、矛盾、或模糊到可以有两种不同解释的需求 — 这些是问题。
    措辞的微调、风格偏好、"章节不如其他详细"等不是问题。

    除非存在会导致有缺陷计划的严重缺陷,否则应批准。

    ## 输出格式

    ## Spec 审查

    **Status:** Approved | Issues Found

    **问题 (如有):**
    - [Section X]: [具体问题] - [对规划的影响]

    **建议 (仅供参考,不阻止批准):**
    - [改进建议]
```

**审查者返回:** Status、问题(如有)、建议
