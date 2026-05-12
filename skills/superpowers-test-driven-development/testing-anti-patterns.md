# 测试反模式

**在以下情况下加载此参考：** 编写或修改测试、添加 mock，或者想要向生产代码添加仅用于测试的方法时。

## 概述

测试必须验证真实行为，而不是 mock 行为。Mock 是一种隔离手段，而不是被测试的对象。

**核心原则：** 测试代码的实际行为，而不是 mock 的行为。

**遵循严格的 TDD 可以防止这些反模式。**

## 铁律

```
1. 永远不要测试 mock 行为
2. 永远不要向生产类添加仅用于测试的方法
3. 永远不要在不理解依赖关系的情况下使用 mock
```

## 反模式 1：测试 Mock 行为

**错误示例：**
```typescript
// ❌ 错误：测试 mock 是否存在
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**为什么这是错误的：**
- 你在验证 mock 是否工作，而不是验证组件是否工作
- 当 mock 存在时测试通过，不存在时测试失败
- 无法告诉你任何关于真实行为的信息

**你的合作伙伴的纠正：** "我们是在测试 mock 的行为吗？"

**正确的做法：**
```typescript
// ✅ 正确：测试真实组件或者不要 mock 它
test('renders sidebar', () => {
  render(<Page />);  // 不要 mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});

// 或者如果必须为了隔离而 mock sidebar：
// 不要对 mock 进行断言 - 测试 Page 在 sidebar 存在时的行为
```

### 门控函数

```
在对任何 mock 元素进行断言之前：
  询问："我是在测试真实的组件行为还是仅仅测试 mock 的存在？"

  如果是在测试 mock 的存在：
    停止 - 删除断言或者取消组件的 mock

  改为测试真实行为
```

## 反模式 2：生产代码中的仅测试方法

**错误示例：**
```typescript
// ❌ 错误：destroy() 仅在测试中使用
class Session {
  async destroy() {  // 看起来像是生产 API！
    await this._workspaceManager?.destroyWorkspace(this.id);
    // ... 清理
  }
}

// 在测试中
afterEach(() => session.destroy());
```

**为什么这是错误的：**
- 生产类被仅用于测试的代码污染
- 如果在生产中意外调用会很危险
- 违反了 YAGNI 原则和关注点分离原则
- 混淆了对象生命周期和实体生命周期

**正确的做法：**
```typescript
// ✅ 正确：测试工具负责测试清理
// Session 没有 destroy() 方法 - 它在生产中是无状态的

// 在 test-utils/ 中
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// 在测试中
afterEach(() => cleanupSession(session));
```

### 门控函数

```
在向生产类添加任何方法之前：
  询问："这个方法是否仅被测试使用？"

  如果是：
    停止 - 不要添加它
    将其放在测试工具中

  询问："这个类是否拥有此资源的生命周期？"

  如果否：
    停止 - 这个方法不应该在这个类中
```

## 反模式 3：不理解就进行 Mock

**错误示例：**
```typescript
// ❌ 错误：Mock 破坏了测试逻辑
test('detects duplicate server', () => {
  // Mock 阻止了测试依赖的配置写入！
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // 应该抛出异常 - 但不会！
});
```

**为什么这是错误的：**
- 被 mock 的方法有测试依赖的副作用（写入配置）
- 为了"安全"而过度 mock 破坏了实际行为
- 测试因为错误的原因通过或神秘失败

**正确的做法：**
```typescript
// ✅ 正确：在正确的层次进行 Mock
test('detects duplicate server', () => {
  // Mock 慢速部分，保留测试需要的行为
  vi.mock('MCPServerManager'); // 仅 mock 慢速的服务器启动

  await addServer(config);  // 配置已写入
  await addServer(config);  // 检测到重复 ✓
});
```

### 门控函数

```
在 mock 任何方法之前：
  停止 - 先不要 mock

  1. 询问："真实方法有什么副作用？"
  2. 询问："此测试是否依赖这些副作用中的任何一个？"
  3. 询问："我是否完全理解此测试需要什么？"

  如果依赖副作用：
    在更低层次进行 mock（实际的慢速/外部操作）
    或者使用保留必要行为的测试替身
    而不是测试依赖的高级方法

  如果不确定测试依赖什么：
    首先使用真实实现运行测试
    观察实际需要发生什么
    然后在正确的层次添加最小化的 mock

  危险信号：
    - "为了安全我会 mock 这个"
    - "这可能很慢，最好 mock 它"
    - 在不理解依赖链的情况下进行 mock
```

## 反模式 4：不完整的 Mock

**错误示例：**
```typescript
// ❌ 错误：部分 mock - 仅包含你认为需要的字段
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // 缺失：下游代码使用的 metadata
};

// 稍后：当代码访问 response.metadata.requestId 时会出错
```

**为什么这是错误的：**
- **部分 mock 隐藏了结构假设** - 你只 mock 了你知道的字段
- **下游代码可能依赖你未包含的字段** - 导致静默失败
- **测试通过但集成失败** - Mock 不完整，真实 API 完整
- **虚假的信心** - 测试无法证明任何关于真实行为的信息

**铁律：** Mock 现实中存在的完整数据结构，而不仅仅是当前测试使用的字段。

**正确的做法：**
```typescript
// ✅ 正确：反映真实 API 的完整性
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // 真实 API 返回的所有字段
};
```

### 门控函数

```
在创建 mock 响应之前：
  检查："真实 API 响应包含哪些字段？"

  行动：
    1. 从文档/示例中检查实际的 API 响应
    2. 包含系统可能下游消费的所有字段
    3. 验证 mock 完全匹配真实响应模式

  关键：
    如果你正在创建 mock，你必须理解整个结构
    当代码依赖被省略的字段时，部分 mock 会静默失败

  如果不确定：包含所有已文档化的字段
```

## 反模式 5：集成测试作为事后思考

**错误示例：**
```
✅ 实现完成
❌ 未编写测试
"准备好测试了"
```

**为什么这是错误的：**
- 测试是实现的一部分，而不是可选的后续工作
- TDD 会捕捉到这种情况
- 没有测试就不能声称完成

**正确的做法：**
```
TDD 循环：
1. 编写失败的测试
2. 实现以使测试通过
3. 重构
4. 然后才能声称完成
```

## 当 Mock 变得过于复杂时

**警告信号：**
- Mock 设置比测试逻辑还长
- 为了让测试通过而 mock 所有内容
- Mock 缺少真实组件拥有的方法
- 当 mock 改变时测试会失败

**你的合作伙伴的问题：** "我们这里真的需要使用 mock 吗？"

**考虑：** 使用真实组件的集成测试通常比复杂的 mock 更简单

## TDD 防止这些反模式

**为什么 TDD 有帮助：**
1. **先编写测试** → 强迫你思考实际要测试什么
2. **观察测试失败** → 确认测试的是真实行为，而不是 mock
3. **最小化实现** → 不会有仅测试方法混入
4. **真实依赖** → 在 mock 之前你看到测试实际需要什么

**如果你在测试 mock 行为，你就违反了 TDD** - 你在没有先观察测试对真实代码失败的情况下添加了 mock。

## 快速参考

| 反模式 | 修复方法 |
|--------|----------|
| 对 mock 元素进行断言 | 测试真实组件或取消 mock |
| 生产代码中的仅测试方法 | 移到测试工具中 |
| 不理解就 mock | 先理解依赖关系，最小化 mock |
| 不完整的 mock | 完全反映真实 API |
| 测试作为事后思考 | TDD - 测试先行 |
| 过度复杂的 mock | 考虑使用集成测试 |

## 危险信号

- 断言检查 `*-mock` 测试 ID
- 仅在测试文件中调用的方法
- Mock 设置占测试的 50% 以上
- 移除 mock 时测试失败
- 无法解释为什么需要 mock
- 为了"安全"而进行 mock

## 底线

**Mock 是隔离的工具，而不是被测试的对象。**

如果 TDD 揭示你正在测试 mock 行为，那你就做错了。

修复：测试真实行为或质疑为什么根本要使用 mock。
