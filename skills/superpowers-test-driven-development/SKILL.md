---
name: test-driven-development
description: 在实现任何功能或修复 bug 之前使用，在编写实现代码之前
---

# Test-Driven Development (TDD)

## 概述

先编写测试。观察它失败。编写最少的代码使其通过。

**核心原则：** 如果你没有看到测试失败，你就不知道它是否测试了正确的内容。

**违反规则的字面意思就是违反规则的精神。**

## 何时使用

**总是：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外（询问你的合作伙伴）：**
- 一次性原型
- 生成的代码
- 配置文件

在想"就这一次跳过 TDD"？停止。那是自我合理化。

## 铁律

```
没有失败的测试在前，就不写生产代码
```

在测试之前写了代码？删除它。重新开始。

**没有例外：**
- 不要保留它作为"参考"
- 不要在编写测试时"改编"它
- 不要查看它
- 删除就是删除

从测试开始全新实现。就这样。

## Red-Green-Refactor

```dot
digraph tdd_cycle {
    rankdir=LR;
    red [label="RED\n编写失败的测试", shape=box, style=filled, fillcolor="#ffcccc"];
    verify_red [label="验证正确\n失败", shape=diamond];
    green [label="GREEN\n最少代码", shape=box, style=filled, fillcolor="#ccffcc"];
    verify_green [label="验证通过\n全绿", shape=diamond];
    refactor [label="REFACTOR\n清理", shape=box, style=filled, fillcolor="#ccccff"];
    next [label="下一步", shape=ellipse];

    red -> verify_red;
    verify_red -> green [label="是"];
    verify_red -> red [label="错误\n失败"];
    green -> verify_green;
    verify_green -> refactor [label="是"];
    verify_green -> green [label="否"];
    refactor -> verify_green [label="保持\n绿色"];
    verify_green -> next;
    next -> red;
}
```

### RED - 编写失败的测试

编写一个最小化的测试来展示应该发生什么。

<Good>
```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
清晰的名称，测试真实行为，一件事
</Good>

<Bad>
```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
模糊的名称，测试 mock 而不是代码
</Bad>

**要求：**
- 一个行为
- 清晰的名称
- 真实代码（除非不可避免，否则不使用 mock）

### 验证 RED - 观察它失败

**必须。永不跳过。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试失败（不是错误）
- 失败消息符合预期
- 因为功能缺失而失败（不是拼写错误）

**测试通过了？** 你在测试已存在的行为。修复测试。

**测试报错了？** 修复错误，重新运行直到它正确失败。

### GREEN - 最少代码

编写最简单的代码来通过测试。

<Good>
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
刚好足够通过
</Good>

<Bad>
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
过度设计
</Bad>

不要添加功能、重构其他代码或"改进"超出测试范围的内容。

### 验证 GREEN - 观察它通过

**必须。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试通过
- 其他测试仍然通过
- 输出干净（无错误、警告）

**测试失败？** 修复代码，不是测试。

**其他测试失败？** 立即修复。

### REFACTOR - 清理

仅在绿色之后：
- 消除重复
- 改进命名
- 提取辅助函数

保持测试绿色。不要添加行为。

### 重复

为下一个功能编写下一个失败的测试。

## 好的测试

| 品质 | 好 | 坏 |
|---------|------|-----|
| **最小化** | 一件事。名称中有"和"？拆分它。 | `test('validates email and domain and whitespace')` |
| **清晰** | 名称描述行为 | `test('test1')` |
| **展示意图** | 演示期望的 API | 模糊了代码应该做什么 |

## 为什么顺序很重要

**"我会在之后编写测试来验证它工作"**

在代码之后编写的测试会立即通过。立即通过证明不了什么：
- 可能测试了错误的东西
- 可能测试了实现，而不是行为
- 可能遗漏了你忘记的边界情况
- 你从未看到它捕获 bug

测试先行迫使你看到测试失败，证明它确实测试了某些东西。

**"我已经手动测试了所有边界情况"**

手动测试是临时的。你认为你测试了一切，但是：
- 没有你测试内容的记录
- 代码更改时无法重新运行
- 在压力下容易忘记情况
- "我试过时它工作了" ≠ 全面

自动化测试是系统化的。它们每次都以相同的方式运行。

**"删除 X 小时的工作是浪费"**

沉没成本谬误。时间已经过去了。你现在选择：
- 删除并用 TDD 重写（X 小时，高信心）
- 保留并在之后添加测试（30 分钟，低信心，可能有 bug）

"浪费"是保留你不能信任的代码。没有真实测试的工作代码是技术债务。

**"TDD 是教条的，务实意味着适应"**

TDD 就是务实的：
- 在提交前发现 bug（比之后调试更快）
- 防止回归（测试立即捕获破坏）
- 记录行为（测试展示如何使用代码）
- 启用重构（自由更改，测试捕获破坏）

"务实"的捷径 = 在生产环境中调试 = 更慢。

**"之后的测试达到相同的目标 - 是精神而不是仪式"**

不。之后的测试回答"这做什么？" 测试先行回答"这应该做什么？"

之后的测试受你的实现偏倚。你测试你构建的东西，而不是要求的东西。你验证记住的边界情况，而不是发现的边界情况。

测试先行强制在实现之前发现边界情况。之后的测试验证你记住了一切（你没有）。

之后 30 分钟的测试 ≠ TDD。你得到了覆盖率，失去了测试有效的证明。

## 常见的自我合理化

| 借口 | 现实 |
|--------|---------|
| "太简单不需要测试" | 简单的代码也会出错。测试只需 30 秒。 |
| "我会在之后测试" | 立即通过的测试证明不了什么。 |
| "之后的测试达到相同目标" | 之后的测试 = "这做什么？" 测试先行 = "这应该做什么？" |
| "已经手动测试过了" | 临时的 ≠ 系统化的。没有记录，无法重新运行。 |
| "删除 X 小时是浪费" | 沉没成本谬误。保留未验证的代码是技术债务。 |
| "保留作为参考，先编写测试" | 你会改编它。那就是之后测试。删除就是删除。 |
| "需要先探索" | 好的。扔掉探索，用 TDD 开始。 |
| "测试难 = 设计不清楚" | 倾听测试。难以测试 = 难以使用。 |
| "TDD 会让我变慢" | TDD 比调试快。务实 = 测试先行。 |
| "手动测试更快" | 手动测试证明不了边界情况。你会在每次更改时重新测试。 |
| "现有代码没有测试" | 你正在改进它。为现有代码添加测试。 |

## 危险信号 - 停止并重新开始

- 测试之前编写代码
- 实现之后测试
- 测试立即通过
- 无法解释为什么测试失败
- "稍后"添加测试
- 自我合理化"就这一次"
- "我已经手动测试过了"
- "之后的测试达到相同目的"
- "是精神而不是仪式"
- "保留作为参考"或"改编现有代码"
- "已经花费了 X 小时，删除是浪费"
- "TDD 是教条的，我是务实的"
- "这是不同的因为..."

**所有这些都意味着：删除代码。用 TDD 重新开始。**

## 示例：Bug 修复

**Bug：** 空邮箱被接受

**RED**
```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

**验证 RED**
```bash
$ npm test
FAIL: expected 'Email required', got undefined
```

**GREEN**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

**验证 GREEN**
```bash
$ npm test
PASS
```

**REFACTOR**
如果需要，为多个字段提取验证。

## 验证清单

在标记工作完成之前：

- [ ] 每个新函数/方法都有测试
- [ ] 在实现之前观察每个测试失败
- [ ] 每个测试都因为预期原因失败（功能缺失，不是拼写错误）
- [ ] 编写最少代码通过每个测试
- [ ] 所有测试通过
- [ ] 输出干净（无错误、警告）
- [ ] 测试使用真实代码（仅在不可避免时使用 mock）
- [ ] 覆盖边界情况和错误

无法勾选所有框？你跳过了 TDD。重新开始。

## 当卡住时

| 问题 | 解决方案 |
|---------|----------|
| 不知道如何测试 | 编写期望的 API。先编写断言。询问你的合作伙伴。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须模拟一切 | 代码耦合太重。使用依赖注入。 |
| 测试设置庞大 | 提取辅助函数。仍然复杂？简化设计。 |

## 调试集成

发现 bug？编写重现它的失败测试。遵循 TDD 循环。测试证明修复并防止回归。

永远不要在没有测试的情况下修复 bug。

## 测试反模式

当添加 mock 或测试工具时，阅读 @testing-anti-patterns.md 以避免常见陷阱：
- 测试 mock 行为而不是真实行为
- 向生产类添加仅测试方法
- 在不理解依赖关系的情况下进行 mock

## 最终规则

```
生产代码 → 测试存在且先失败
否则 → 不是 TDD
```

没有合作伙伴的许可不得有例外。
