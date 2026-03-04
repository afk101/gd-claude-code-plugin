# 变更分析指南

## 变更类型判断流程

### 判断优先级

按以下顺序依次判断变更类型：

1. **是否为回退提交？** → `revert`
2. **是否存在新功能？** → `feat`
3. **是否修复了 Bug？** → `fix`
4. **是否仅修改文档？** → `docs`
5. **是否仅修改代码风格？** → `style`
6. **是否为性能优化？** → `perf`
7. **是否为重构（无功能变更、无 Bug 修复）？** → `refactor`
8. **是否涉及测试？** → `test`
9. **是否涉及构建系统？** → `build`
10. **是否涉及 CI/CD？** → `ci`
11. **其他情况** → `chore`

### 文件类型与提交类型的对应关系

| 文件模式 | 通常对应的类型 |
|----------|----------------|
| `*.md`, `*.txt`, `*.rst` | `docs` |
| `*.test.*`, `*.spec.*`, `__tests__/` | `test` |
| `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` | `ci` |
| `package.json`（仅依赖变更）, `Makefile`, `webpack.config.*` | `build` |
| `.eslintrc`, `.prettierrc`（仅格式配置） | `style` |
| `*.css`, `*.scss`（仅格式调整） | `style` |

### 作用域推断策略

根据修改文件的路径推断合适的作用域：

```
src/api/users.js          → scope: api 或 users
src/components/Button.tsx  → scope: ui 或 button
src/auth/login.js         → scope: auth
database/migrations/       → scope: db
config/settings.js        → scope: config
package.json              → scope: deps
docs/guide.md             → scope: docs
```

**Monorepo 场景：**

```
packages/core/src/index.ts    → scope: core
packages/ui/src/Button.tsx    → scope: ui
apps/web/src/pages/Home.tsx   → scope: web
```

## 复杂场景处理

### 混合变更

当一次暂存包含多种类型的变更时：

1. **优先选择最主要的变更类型**
2. **在正文中用 `-` 列出所有变更**
3. **建议用户拆分提交**（如变更差异过大）

示例：
```
feat(auth): 新增登录功能及单元测试

- 新增用户登录接口
- 添加登录接口的单元测试
- 更新 API 文档中的认证章节
```

### 破坏性变更检测

以下情况需标记为破坏性变更：

- API 接口参数变更（新增必填参数、删除参数、修改参数类型）
- API 响应格式变更
- 移除公开的函数、类或模块
- 修改配置文件的必填项
- 数据库 Schema 不兼容变更
- 修改默认行为

标记方式：
```
# 方式一：在类型后加感叹号
feat(api)!: 修改用户接口响应格式

# 方式二：在脚注中添加
BREAKING CHANGE: 用户接口响应格式从数组改为分页对象
```

### 多文件变更的作用域选择

当修改涉及多个目录时：

1. **有明确共同作用域** → 使用该作用域（如都在 `auth` 模块下）
2. **跨多个模块但有主要模块** → 使用主要模块作为作用域
3. **无法归属单一作用域** → 省略作用域

### Revert 提交格式

```
revert: feat(api): 新增用户接口

回退提交 abc1234（新增用户接口），原因为接口设计需要重新评审

Refs: abc1234
```

## 描述撰写技巧

### 好的描述示例

```
feat(auth): 添加邮箱重置密码功能              ✅ 清晰、具体
fix(ui): 修复移动端按钮重叠问题                ✅ 指出问题和位置
refactor(api): 提取校验中间件                  ✅ 说明重构内容
perf(db): 为 user_email 字段添加索引           ✅ 具体的优化手段
```

### 不好的描述示例

```
feat: 更新代码                                   ❌ 太模糊
fix: 修复 bug                                    ❌ 没有说明修了什么
refactor: 重构代码                               ❌ 重复自身
chore: 杂项变更                                  ❌ 无意义
```

### 描述的祈使语气转换

| 不推荐写法 | 推荐写法 |
|------------|----------|
| 添加了新功能 | 添加新功能 |
| 正在修复登录问题 | 修复登录问题 |
| 已更新文档 | 更新文档 |
| 移除了废弃的接口 | 移除废弃接口 |
| 改变了默认配置 | 修改默认配置 |

## 正文撰写指南

### 何时需要正文

- 变更涉及 3 个以上文件
- 包含破坏性变更
- 变更原因不明显（仅看描述无法理解为什么这样做）
- 涉及复杂的业务逻辑变更

### 正文内容模板

```
[简要说明变更动机]

[具体变更列表，使用 - 符号]
- 变更项 1
- 变更项 2
- 变更项 3

[可选：影响范围或注意事项]
```

### 正文示例

```
feat(payment): 接入微信支付功能

接入微信支付 SDK，支持 H5 和小程序场景的支付流程

- 新增 WeChatPayService 处理支付请求
- 添加支付回调验签逻辑
- 新增支付状态轮询机制
- 添加支付相关的错误码定义

注意：需要在环境变量中配置 WECHAT_MCH_ID 和 WECHAT_API_KEY
```
