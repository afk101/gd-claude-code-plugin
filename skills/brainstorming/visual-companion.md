# visual-companion指南

基于浏览器的可视化头脑风暴companion，用于展示模型、图表和选项。

## 何时使用

按问题决定，而非按会话决定。测试标准：**用户通过查看内容是否比阅读文字更容易理解？**

**使用浏览器** 当内容本身是可视化的：

- **UI 模型** — 线框图、布局、导航结构、组件设计
- **架构图** — 系统组件、数据流、关系图
- **并排视觉对比** — 比较两个布局、两个配色方案、两个设计方向
- **设计打磨** — 当问题关于外观和感觉、间距、视觉层次时
- **空间关系** — 状态机、流程图、实体关系图渲染

**使用终端** 当内容是文本或表格时：

- **需求和范围问题** — "X 是什么意思？"、"哪些功能在范围内？"
- **概念性 A/B/C 选择** — 在用文字描述的方法之间选择
- **权衡列表** — 优缺点、对比表
- **技术决策** — API 设计、数据建模、架构方法选择
- **澄清问题** — 任何答案是用文字而非视觉偏好表达的问题

关于 UI 主题的问题不一定是视觉问题。"您想要什么样的向导？"是概念性的 — 使用终端。"这些向导布局中哪个感觉合适？"是视觉性的 — 使用浏览器。

## 工作原理

服务器监视目录中的 HTML 文件并将最新的文件提供给浏览器。您将 HTML 内容写入 `screen_dir`，用户在浏览器中查看并可以点击选择选项。选择记录到 `state_dir/events`，您在下一轮读取它。

**内容片段 vs 完整文档：** 如果您的 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务器将按原样提供（仅注入辅助脚本）。否则，服务器会自动将您的内容包装在框架模板中 — 添加页眉、CSS 主题、选择指示器和所有交互基础设施。**默认编写内容片段。** 只有当您需要完全控制页面时才编写完整文档。

## 启动会话

```bash
# 使用持久化启动服务器（模型保存到项目）
scripts/start-server.sh --project-dir /path/to/project

# 返回: {"type":"server-started","port":52341,"url":"http://localhost:52341",
#           "screen_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/content",
#           "state_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/state"}
```

从响应中保存 `screen_dir` 和 `state_dir`。告诉用户打开 URL。

**查找连接信息：** 服务器将其启动 JSON 写入 `$STATE_DIR/server-info`。如果您在后台启动服务器且没有捕获 stdout，请读取该文件以获取 URL 和端口。使用 `--project-dir` 时，检查 `<project>/.superpowers/brainstorm/` 以获取会话目录。

**注意：** 将项目根目录作为 `--project-dir` 传递，这样模型会持久化在 `.superpowers/brainstorm/` 中，并在服务器重启后保留。没有它，文件会进入 `/tmp` 并被清理。提醒用户将 `.superpowers/` 添加到 `.gitignore`（如果尚未添加）。

**按平台启动服务器：**

**Claude Code (macOS / Linux):**
```bash
# 默认模式即可 — 脚本本身会将服务器置于后台
scripts/start-server.sh --project-dir /path/to/project
```

**Claude Code (Windows):**
```bash
# Windows 自动检测并使用前台模式，这会阻塞工具调用。
# 在 Bash 工具调用上使用 run_in_background: true，以便服务器
# 在对话轮次之间保持存活。
scripts/start-server.sh --project-dir /path/to/project
```
通过 Bash 工具调用时，设置 `run_in_background: true`。然后在下一轮读取 `$STATE_DIR/server-info` 以获取 URL 和端口。

**Codex:**
```bash
# Codex 会回收后台进程。脚本自动检测 CODEX_CI 并
# 切换到前台模式。正常运行即可 — 无需额外标志。
scripts/start-server.sh --project-dir /path/to/project
```

**Gemini CLI:**
```bash
# 使用 --foreground 并在 shell 工具调用上设置 is_background: true
# 以便进程在轮次之间保持存活
scripts/start-server.sh --project-dir /path/to/project --foreground
```

**其他环境：** 服务器必须在对话轮次之间在后台保持运行。如果您的环境会回收分离的进程，请使用 `--foreground` 并使用平台的后台执行机制启动命令。

如果 URL 无法从您的浏览器访问（在远程/容器化设置中常见），绑定非回环主机：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

使用 `--url-host` 控制返回的 URL JSON 中打印的主机名。

## 循环

1. **检查服务器是否存活**，然后**将 HTML 写入** `screen_dir` 中的新文件：
   - 每次写入前，检查 `$STATE_DIR/server-info` 是否存在。如果不存在（或 `$STATE_DIR/server-stopped` 存在），说明服务器已关闭 — 在继续之前使用 `start-server.sh` 重启。服务器在 30 分钟不活动后自动退出。
   - 使用语义化文件名：`platform.html`、`visual-style.html`、`layout.html`
   - **切勿重用文件名** — 每个屏幕使用新文件
   - 使用 Write 工具 — **切勿使用 cat/heredoc**（会将噪声转储到终端）
   - 服务器自动提供最新文件

2. **告诉用户期待什么并结束您的回合：**
   - 提醒他们 URL（每一步，不仅仅是第一次）
   - 简要文字总结屏幕上的内容（例如，"显示主页的 3 个布局选项"）
   - 要求他们在终端中响应："看一下并告诉我您的想法。如果愿意，可以点击选择选项。"

3. **在您的下一轮** — 用户在终端中响应后：
   - 如果存在，读取 `$STATE_DIR/events` — 这包含用户的浏览器交互（点击、选择）作为 JSON 行
   - 与用户的终端文本合并以获得完整图片
   - 终端消息是主要反馈；`state_dir/events` 提供结构化交互数据

4. **迭代或推进** — 如果反馈改变了当前屏幕，写入新文件（例如 `layout-v2.html`）。只有在当前步骤经过验证后才移动到下一个问题。

5. **返回终端时卸载** — 当下一步不需要浏览器时（例如，澄清问题、权衡讨论），推送等待屏幕以清除陈旧内容：

   ```html
   <!-- 文件名: waiting.html (或 waiting-2.html, 等) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">在终端中继续...</p>
   </div>
   ```

   这可以防止用户在对话继续时盯着已解决的选择。当下一个视觉问题出现时，像往常一样推送新内容文件。

6. 重复直到完成。

## 编写内容片段

只编写页面内的内容。服务器自动将其包装在框架模板中（页眉、主题 CSS、选择指示器和所有交互基础设施）。

**最小示例：**

```html
<h2>哪种布局更好？</h2>
<p class="subtitle">考虑可读性和视觉层次</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>单列</h3>
      <p>简洁、专注的阅读体验</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>双列</h3>
      <p>侧边栏导航与主内容</p>
    </div>
  </div>
</div>
```

就是这样。不需要 `<html>`、不需要 CSS、不需要 `<script>` 标签。服务器提供了所有这些。

## 可用的 CSS 类

框架模板为您的内容提供以下 CSS 类：

### 选项（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>标题</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

**多选：** 向容器添加 `data-multiselect` 以允许用户选择多个选项。每次点击切换项目。指示条显示计数。

```html
<div class="options" data-multiselect>
  <!-- 相同的选项标记 — 用户可以选择/取消选择多个 -->
</div>
```

### 卡片（视觉设计）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- 模型内容 --></div>
    <div class="card-body">
      <h3>名称</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

### 模型容器

```html
<div class="mockup">
  <div class="mockup-header">预览: 仪表板布局</div>
  <div class="mockup-body"><!-- 您的模型 HTML --></div>
</div>
```

### 分割视图（并排）

```html
<div class="split">
  <div class="mockup"><!-- 左侧 --></div>
  <div class="mockup"><!-- 右侧 --></div>
</div>
```

### 优缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>优点</h4><ul><li>好处</li></ul></div>
  <div class="cons"><h4>缺点</h4><ul><li>缺点</li></ul></div>
</div>
```

### 模型元素（线框构建块）

```html
<div class="mock-nav">Logo | 首页 | 关于 | 联系</div>
<div style="display: flex;">
  <div class="mock-sidebar">导航</div>
  <div class="mock-content">主要内容区域</div>
</div>
<button class="mock-button">操作按钮</button>
<input class="mock-input" placeholder="输入字段">
<div class="placeholder">占位符区域</div>
```

### 排版和部分

- `h2` — 页面标题
- `h3` — 部分标题
- `.subtitle` — 标题下方的次要文字
- `.section` — 带底部边距的内容块
- `.label` — 小型大写标签文字

## 浏览器事件格式

当用户在浏览器中点击选项时，他们的交互被记录到 `$STATE_DIR/events`（每行一个 JSON 对象）。当您推送新屏幕时，文件会自动清空。

```jsonl
{"type":"click","choice":"a","text":"选项 A - 简单布局","timestamp":1706000101}
{"type":"click","choice":"c","text":"选项 C - 复杂网格","timestamp":1706000108}
{"type":"click","choice":"b","text":"选项 B - 混合","timestamp":1706000115}
```

完整的事件流显示用户的探索路径 — 他们可能在确定之前点击多个选项。最后一个 `choice` 事件通常是最终选择，但点击模式可以揭示犹豫或值得询问的偏好。

如果 `$STATE_DIR/events` 不存在，说明用户没有与浏览器交互 — 仅使用他们的终端文本。

## 设计技巧

- **根据问题调整保真度** — 布局使用线框图，打磨问题使用打磨
- **在每个页面上解释问题** — "哪种布局感觉更专业？"，而不是仅仅"选一个"
- **推进前先迭代** — 如果反馈改变了当前屏幕，编写新版本
- **每个屏幕最多 2-4 个选项**
- **在重要时使用真实内容** — 对于摄影作品集，使用实际图片（Unsplash）。占位符内容会掩盖设计问题。
- **保持模型简单** — 关注布局和结构，而非像素级完美的设计

## 文件命名

- 使用语义化名称：`platform.html`、`visual-style.html`、`layout.html`
- 切勿重用文件名 — 每个屏幕必须是一个新文件
- 对于迭代：附加版本后缀，如 `layout-v2.html`、`layout-v3.html`
- 服务器按修改时间提供最新文件

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

如果会话使用了 `--project-dir`，模型文件会持久化在 `.superpowers/brainstorm/` 中以供后续参考。只有 `/tmp` 会话在停止时会被删除。

## 参考

- 框架模板（CSS 参考）：`scripts/frame-template.html`
- 辅助脚本（客户端）：`scripts/helper.js`
