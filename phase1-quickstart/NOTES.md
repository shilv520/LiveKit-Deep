# 阶段1 学习笔记：LangGraph 快速上手

## 核心知识点

### 1. StateGraph（状态图）🔥🔥🔥🔥🔥

**是什么？**
- LangGraph 的核心组件，用于构建 Agent 的工作流程图
- 类似流程图，但支持循环、分支、并行等复杂逻辑

**为什么需要？**
- LangChain 的 Chain 只能线性执行，无法处理循环和复杂分支
- Agent 需要"思考-执行-观察"的循环能力

**核心结构：**
```python
from langgraph.graph import StateGraph, END, START

graph = StateGraph(StateType)  # 创建图
graph.add_node("node_name", node_function)  # 添加节点
graph.add_edge("from_node", "to_node")  # 添加边
graph.add_conditional_edges("node", condition_fn, {path: target})  # 条件边
graph.set_entry_point("node")  # 设置入口
app = graph.compile()  # 编译成可执行图
```

---

### 2. Node（节点）🔥🔥🔥

**是什么？**
- 状态图中的处理单元
- 每个节点是一个 Python 函数

**特点：**
- 接收当前状态作为参数
- 返回状态更新（字典形式）
- 节点间共享状态

**示例：**
```python
def think_node(state: AgentState) -> dict:
    # 处理逻辑
    return {"thought": "我的思考内容"}  # 状态更新
```

---

### 3. Edge（边）🔥🔥🔥

**类型：**

| 类型 | 说明 | 语法 |
|-----|------|-----|
| 普通边 | 固定流转 | `add_edge("from", "to")` |
| 条件边 | 动态路由 | `add_conditional_edges(node, fn, mapping)` |
| 入口边 | 从 START 开始 | `add_edge(START, "node")` |
| 结束边 | 到 END 结束 | 在条件映射中加入 END |

---

### 4. 条件边（Conditional Edges）🔥🔥🔥🔥🔥

**面试必问！**

```python
graph.add_conditional_edges(
    "observe",            # 源节点
    lambda state: state["next_action"],  # 条件函数
    {
        "think": "think", # 条件值 -> 目标节点
        "end": END,       # 条件值 -> END
    }
)
```

**关键点：**
- 条件函数返回字符串/枚举值
- 返回值映射到目标节点
- 是 Agent 循环的关键机制

---

### 5. ReAct 模式 🔥🔥🔥🔥🔥

**面试最高频考点！**

**是什么？**
- Reasoning + Acting 的经典 Agent 模式
- 源自论文 "ReAct: Synergizing Reasoning and Acting in Language Models"

**核心流程：**
```
Thought: 我需要查天气
Action: weather_tool
Action Input: 北京
Observation: 北京今天晴，25°C
Thought: 我得到答案了
Action: finish
```

**实现要点：**
1. Think 节点：分析问题，决定动作
2. Act 节点：执行工具调用
3. Observe 节点：分析结果
4. 循环直到完成

---

### 6. AgentState（状态定义）🔥🔥🔥

**推荐结构：**
```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # 消息历史
    next_action: str  # 下一步动作
    # ... 其他字段
```

**关键：**
- TypedDict 定义类型
- Annotated + add_messages 自动累加消息
- 所有节点共享同一个状态对象

---

## 面试高频问答

### Q1: LangGraph 和 LangChain 的区别？

| 维度 | LangChain | LangGraph |
|-----|-----------|-----------|
| 结构 | Chain（链式） | Graph（图式） |
| 流程 | 线性 | 循环、分支、并行 |
| 状态 | 隐式传递 | 显式 State 对象 |
| 适用 | 简单流程 | 复杂 Agent |
| 调试 | 较难 | 时间旅行调试 |

**一句话总结：LangChain 是链，LangGraph 是图；图比链更灵活，更适合 Agent。**

---

### Q2: StateGraph 的核心公式？

```python
# 🔥🔥🔥 Agent 核心公式
graph = StateGraph(State)
graph.add_node("node", function)
graph.add_edge("from", "to")
graph.add_conditional_edges("node", condition, mapping)
app = graph.compile()
result = app.invoke(initial_state)
```

---

### Q3: 条件边怎么实现？

**三要素：**
1. 源节点
2. 条件函数（返回路径名）
3. 路径映射（路径名 -> 目标节点）

---

### Q4: ReAct 的 think-act-observe 循环？

**三个节点 + 一个条件边：**
```
think -> act -> observe -> (条件判断)
                         ↓
                    continue? -> think (循环)
                         ↓
                    finish? -> END
```

---

## 实践要点

1. **先定义 State**：状态是 Agent 的数据骨架
2. **再定义 Node**：节点是 Agent 的处理逻辑
3. **最后定义 Edge**：边是 Agent 的流程控制
4. **编译后执行**：`compile()` 生成可执行图

---

## 下一步

阶段2 将学习：
- Checkpointing（状态持久化）
- 工具调用（Function Calling）
- 多 Agent 协作