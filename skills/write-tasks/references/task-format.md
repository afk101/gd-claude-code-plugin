# Clawt 任务文件格式详细规范

## 文件格式概述

任务文件使用 Markdown 格式，内嵌 HTML 注释标签来界定任务块。标签外的任何文本都不会被 clawt 解析，可自由书写背景信息、说明等内容。

## 任务块结构

每个任务用 `<!-- CLAWT-TASKS:START -->` 和 `<!-- CLAWT-TASKS:END -->` 包裹：

```markdown
<!-- CLAWT-TASKS:START -->
# branch: <分支名>
任务描述内容（支持多行）
<!-- CLAWT-TASKS:END -->
```

## 格式规则

1. **任务块界定**：每个任务必须用 `<!-- CLAWT-TASKS:START -->` 和 `<!-- CLAWT-TASKS:END -->` 包裹
2. **分支名声明**：块内用 `# branch: <分支名>` 声明分支名（冒号前后的空格可灵活）
3. **任务描述**：块内除分支名行以外的所有行，合并为任务描述（支持多行）
4. **块外内容忽略**：标签外的任何文本都不会被解析，可用于写项目背景、注意事项等
5. **必填校验**：每个块必须包含任务描述；分支名必填

## 分支名规范

分支名中的非法字符会被自动替换为 `-`：

| 字符 | 说明 |
|------|------|
| `/`  | 路径分隔符 |
| `\`  | 路径分隔符（Windows） |
| `.`  | 可能导致隐藏目录 |
| `:`  | Windows 非法字符 |
| `*`  | 通配符 |
| `?`  | 通配符 |
| `"`  | 引号 |
| `<`  | 重定向符 |
| `>`  | 重定向符 |
| `\|` | 管道符 |
| 空格 | 路径空格 |

建议使用 `feat-xxx`、`fix-xxx`、`refactor-xxx` 等常见 Git 分支命名风格。

## 完整示例

```markdown
# 项目背景

本项目是一个电商平台的后端服务，目前需要完成以下几个功能模块的开发。

## 技术栈
- Node.js + TypeScript
- PostgreSQL
- Redis

## 注意事项
- 所有 API 需要遵循 RESTful 规范
- 数据库操作统一使用 ORM
- 需要编写单元测试

---

<!-- CLAWT-TASKS:START -->
# branch: feat-user-auth
实现用户认证模块：
- JWT token 签发与验证
- 登录/注册接口
- 密码加密存储
- 刷新 token 机制
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: feat-product-crud
实现商品管理 CRUD 接口：
- 商品列表（支持分页、筛选、排序）
- 商品详情
- 商品创建与编辑
- 商品上下架
<!-- CLAWT-TASKS:END -->

<!-- CLAWT-TASKS:START -->
# branch: fix-order-calc
修复订单金额计算错误：
当存在多种优惠券叠加使用时，折扣金额计算不正确，
需要按照优惠券优先级依次计算折扣。
<!-- CLAWT-TASKS:END -->
```


