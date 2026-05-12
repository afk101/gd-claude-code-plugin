# 基于条件的等待 (Condition-Based Waiting)

## 概述

不稳定测试 (Flaky tests) 通常通过任意延迟来猜测时机。这会导致竞态条件 (race conditions)，使得测试在快速机器上通过，但在负载下或 CI 环境中失败。

**核心原则：** 等待你关心的实际条件，而不是猜测需要多长时间。

## 何时使用

```dot
digraph when_to_use {
    "Test uses setTimeout/sleep?" [shape=diamond];
    "Testing timing behavior?" [shape=diamond];
    "Document WHY timeout needed" [shape=box];
    "Use condition-based waiting" [shape=box];

    "Test uses setTimeout/sleep?" -> "Testing timing behavior?" [label="yes"];
    "Testing timing behavior?" -> "Document WHY timeout needed" [label="yes"];
    "Testing timing behavior?" -> "Use condition-based waiting" [label="no"];
}
```

**使用场景：**
- 测试包含任意延迟（`setTimeout`、`sleep`、`time.sleep()`）
- 测试不稳定（有时通过，在负载下失败）
- 并行运行时测试超时
- 等待异步操作完成

**不适用场景：**
- 测试实际的时序行为（防抖 debounce、节流间隔 throttle intervals）
- 如果使用任意超时，必须说明原因

## 核心模式

```typescript
// ❌ 之前：猜测时机
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ 之后：等待条件
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## 快速模式

| 场景 | 模式 |
|----------|---------|
| 等待事件 | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| 等待状态 | `waitFor(() => machine.state === 'ready')` |
| 等待计数 | `waitFor(() => items.length >= 5)` |
| 等待文件 | `waitFor(() => fs.existsSync(path))` |
| 复杂条件 | `waitFor(() => obj.ready && obj.value > 10)` |

## 实现

通用轮询函数：
```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
  }
}
```

参见本目录中的 `condition-based-waiting-example.ts`，其中包含实际调试会话中的完整实现和领域特定辅助函数（`waitForEvent`、`waitForEventCount`、`waitForEventMatch`）。

## 常见错误

**❌ 轮询过快：** `setTimeout(check, 1)` - 浪费 CPU
**✅ 修正：** 每 10ms 轮询一次

**❌ 无超时：** 如果条件永远不满足会无限循环
**✅ 修正：** 始终包含超时和明确的错误信息

**❌ 数据过期：** 在循环前缓存状态
**✅ 修正：** 在循环内调用 getter 获取新鲜数据

## 何时使用任意超时是正确的

```typescript
// 工具每 100ms 触发一次 - 需要 2 次触发来验证部分输出
await waitForEvent(manager, 'TOOL_STARTED'); // 首先：等待条件
await new Promise(r => setTimeout(r, 200));   // 然后：等待时序行为
// 200ms = 2 次触发，每次间隔 100ms - 已记录并有充分理由
```

**要求：**
1. 首先等待触发条件
2. 基于已知时序（而非猜测）
3. 添加注释说明原因

## 实际影响

来自调试会话（2025-10-03）：
- 修复了 3 个文件中的 15 个不稳定测试
- 通过率：60% → 100%
- 执行时间：快 40%
- 不再出现竞态条件
