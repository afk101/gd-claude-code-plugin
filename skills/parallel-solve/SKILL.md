---
name: "clawt:parallel-solve"
description: >
  This skill should be used when the user asks to "parallel solve", "try multiple solutions",
  "brainstorm and solve in parallel", "parallel debug", "try different approaches",
  "solve with clawt", "multi-branch solve", "concurrent fix", "parallel fix",
  or when a problem has been attempted 2+ times in the current conversation without success.
  Brainstorms multiple differentiated solutions, executes them concurrently via clawt worktrees,
  validates results, and iterates until a working solution is found.
version: 1.0.0
---

# Clawt 并行求解器

当一个问题在对话中反复尝试仍无法解决时，通过头脑风暴产出多个差异化方案，利用 clawt 工具并发执行，
然后验证结果，失败时自动循环修正，直到找到可行方案。

## 触发时机

### 主动触发

用户明确要求并行求解，例如：
- "并行试几个方案"
- "用 clawt 并行解决"
- "多开几个分支试试"

### 半自动建议

当检测到以下情况时，**主动建议**用户启用并行求解（不自动执行，需用户确认）：
- 当前对话中同一问题已尝试修复 **2 次及以上**仍未解决
- 建议话术："这个问题已经尝试了多次，建议使用并行求解（`/parallel-solve`）同时尝试多个不同方案，提高成功率。是否启用？"

## 核心工作流程

### 第一步：问题分析与方案头脑风暴

1. **深度分析问题**：
   - 回顾对话中所有失败尝试，提取失败原因
   - 明确问题的根因和约束条件
   - 识别之前未尝试过的方向

2. **头脑风暴差异化方案**：
   - 方案数量由 skill 自行决定（**上限 10 个**），根据问题复杂度和可行方向数量灵活调整
   - 每个方案必须采用**不同的技术路线或策略**，不能仅仅是参数微调
   - 方案之间应有明显差异性，覆盖不同的解题思路
   - 需评估每个方案的可行性和风险

3. **输出方案概要**：向用户展示所有方案的简要描述，让用户了解即将并行尝试的方向（不需要用户确认，仅作信息展示）

### 第二步：生成任务文件并执行

1. **使用 `clawt:write-tasks` skill 生成任务文件**

   调用 `clawt:write-tasks` skill 生成符合 CLAWT-TASKS 格式的任务文件（.gitignore 配置、目录创建、文件格式等均由该 skill 处理）。

   **parallel-solve 特有约束**（在调用 write-tasks 时需遵守）：
   - **分支名前缀**：所有分支必须使用 `clawt-solve-` 前缀，后接方案简述，例如：
     - `clawt-solve-use-native-api`
     - `clawt-solve-replace-library`
     - `clawt-solve-refactor-approach`
   - **标题格式**：任务文件标题使用 `并行求解：[问题简述]`
   - **问题背景区域**：必须包含问题的完整描述、已尝试的方案及失败原因
   - **注意事项区域**：必须包含所有方案都需遵守的约束、不能影响的现有功能等

   **任务文件模板**：

   ```markdown
   # 并行求解：[问题简述]

   ## 问题背景
   [问题的完整描述]
   已尝试过以下方案均失败：
   - [失败方案 1 及原因]
   - [失败方案 2 及原因]

   ## 注意事项
   - 技术栈：[项目技术栈]
   - [约束条件 1]
   - [约束条件 2]

   ---

   <!-- CLAWT-TASKS:START -->
   # branch: clawt-solve-<方案关键词>
   ## 方案：[方案名称]

   **核心思路**：[与其他方案的差异化路线说明]

   **实现步骤**：
   1. [步骤 1]
   2. [步骤 2]
   3. [步骤 3]

   **验证方式**：
   - [如何验证问题已解决]
   - [如何确认没有引入新问题]

   **注意**：[该方案特有的风险点或限制]
   <!-- CLAWT-TASKS:END -->

   <!-- CLAWT-TASKS:START -->
   # branch: clawt-solve-<另一个方案关键词>
   ## 方案：[方案名称]

   **核心思路**：[不同于上一个方案的技术路线]

   **实现步骤**：
   1. [步骤 1]
   2. [步骤 2]

   **验证方式**：
   - [验证标准]

   **注意**：[注意事项]
   <!-- CLAWT-TASKS:END -->
   ```

2. **确保在主 worktree 的主工作分支上（干净环境）**

   所有 clawt 命令都必须在主 worktree（包含 `.git` 目录）中执行。通过以下步骤确保环境就绪：

   **a) 执行 `clawt home`**：
   - 如果当前已在主 worktree → 自动切换回主工作分支（如有验证分支残留会自动清理）
   - 如果当前在目标 worktree → 命令会输出 `cd <主 worktree 路径>` 提示，**先执行该 `cd` 命令**切换到主 worktree，然后**再次执行 `clawt home`** 确保切回主工作分支

   **b) 检查工作区和暂存区是否干净**：
   - 执行 `git status` 检查
   - 如果工作区或暂存区有未提交的改动 → **停止执行，提醒用户先处理**  
   - 工作区干净后继续下一步

3. **自动执行 clawt 命令**

   直接执行以下命令，**无需用户确认**：

   ```bash
   clawt run -f <任务文件路径>
   ```

4. **等待所有任务完成**

   clawt 会在所有任务完成后返回，此时进入验证阶段。

### 第三步：验证结果

对每个方案分支执行验证：

1. **判断是否需要 `-r` 运行指令**

   根据项目类型决定是否使用 `-r` 参数（详细判断流程见 `references/workflow-detail.md` 中的「验证判断逻辑」章节）。
   - **检查项目配置**：优先使用 `clawt init show --json` 中已配置的 `validateRunCommand`，如果已经配置，则不需要使用-r指令。

2. **依次验证每个方案**

   ```bash
   clawt validate -b clawt-solve-<方案名>
   # 或带运行指令
   clawt validate -b clawt-solve-<方案名> -r "<运行指令>"
   ```

3. **评估方案是否真正解决了问题**

   `clawt validate` 只是将目标 worktree 的修改搬到主 worktree 的验证分支上，并执行 `-r` 指令。但 `-r` 通过（如构建成功、测试通过）**不等于问题已解决**，还需要在验证分支上检查该方案的修改是否真正实现了预期目标：
   - 阅读验证分支上的代码变更，确认实现逻辑是否正确
   - 对照方案的验收标准逐项核对
   - 确认修改没有引入新的问题或副作用
   - 日志是否符合预期

4. **每个方案必须构建验证闭环**

   每个并发执行的独立方案都必须设计自己的验证方式，确保能自主判断"问题是否真正解决"。验证闭环的设计应写入任务描述中，让 agent 在实现方案时同步完成验证逻辑。

   **前端项目**：通过 browser-tools MCP 工具构建验证闭环：
   - **获取浏览器控制台日志**：热更新自动生效后，使用 `getConsoleLogs` / `getConsoleErrors` 检查是否有报错或预期的调试输出
   - **截取屏幕截图**：使用 `takeScreenshot` 进行视觉验证，确认 UI 渲染结果是否符合预期
   - **运行调试模式**：使用 `runDebuggerMode` 进行深度调试
   - **在任务描述中指导 agent 添加调试日志**：每个方案的任务描述中应包含"添加 `console.log` 关键调试信息"的指令，以便通过浏览器日志验证执行结果

   **后端 / CLI / 库项目**：通过编写测试用例、执行命令并比对输出、检查日志等方式构建验证闭环。在任务描述中明确要求 agent 编写针对性测试或验证脚本。

### 第四步：结果处理

#### 情况 A：有方案验证通过

- **不自动 merge**
- 清晰告知用户：
  - 哪个方案验证通过
  - 对应的分支名
  - 该方案的核心实现思路
  - 后续操作建议（用户可手动执行 `clawt merge -b <分支名>` 合并）

#### 情况 B：所有方案均未通过 → 进入循环修正

详细的循环修正策略见 `references/workflow-detail.md` 中的「循环修正策略」章节。核心要点：
- **不放弃任何独立方案**，全部继续修正
- **直接修改原始任务文件**，追加每个方案的失败原因和修正方向
- 使用 `clawt resume -f <原始任务文件路径>` 批量并发 resume
- 再次验证后如仍失败则继续循环，**最多 5 轮**
- 超过上限后汇总报告给用户

### 第五步：清理

所有流程结束后（无论成功还是达到循环上限）：
- 输出所有方案的状态汇总（通过/失败/进行中）(需要列出对应的worktree分支名)

## 任务描述编写指南

每个方案的任务描述应包含：

1. **方案概述**：详细说明核心思路
2. **技术路线**：具体使用什么技术/库/模式
3. **实现步骤**：清晰的步骤列表
4. **验收标准**：如何判断方案成功
5. **注意事项**：特别需要避免的坑或需要注意的兼容性问题

## 额外参考

查阅 `references/workflow-detail.md` 获取详细的头脑风暴方法论、验证判断逻辑、循环修正策略等补充说明。
