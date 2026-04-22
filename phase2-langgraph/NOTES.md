# 阶段2 学习笔记：LangGraph 基础与 Agent 编排

## 核心知识点

### 1. Checkpointing（状态持久化）🔥🔥🔥🔥🔥

**是什么？**
- Agent 状态的持久化机制
- 支持"暂停-恢复"、时间旅行调试

**为什么重要？**
- 生产必备：应对意外中断
- 调试利器：回溯历史状态
- 多轮对话：跨会话保存状态

**⚠️ 重要：LangGraph 内置 Checkpointer**

| Checkpointer | 状态 | 说明 |
|-------------|------|-----|
| MemorySaver | ✅ 内置 | 内存存储，开箱即用 |
| RedisSaver | ❌ 不存在 | 需自己实现 |
| SqliteSaver | ❌ 不存在 | 需自己实现 |

**生产环境方案：自定义 Redis Checkpointer**

```python
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple

class RedisCheckpointer(BaseCheckpointSaver):
    def __init__(self, redis_url: str):
        import redis
        self.client = redis.from_url(redis_url)
    
    async def aget_tuple(self, config) -> CheckpointTuple | None:
        # 从 Redis 获取 checkpoint
        ...
    
    async def aput(self, config, checkpoint, metadata, new_versions):
        # 保存 checkpoint 到 Redis
        ...

# 使用
checkpointer = RedisCheckpointer("redis://localhost:6379")
app = graph.compile(checkpointer=checkpointer)
```

**MemorySaver 核心代码（开发测试）：**
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # 内置，直接可用
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "session-1"}}
result = app.invoke(state, config)

# 查看历史
checkpoints = list(app.get_state_history(config))

# 回溯状态
app.update_state(config, checkpoint.values)
```

---

### 2. 工具调用（Function Calling）🔥🔥🔥🔥🔥

**LangChain 工具定义：**
```python
from langchain_core.tools import tool

@tool
def search_weather(location: str) -> str:
    """搜索天气信息

    Args:
        location: 地点名称
    """
    return f"{location}天气：晴，25°C"
```

**工具调用流程：**
```
用户输入 → LLM 分析 → AIMessage(tool_calls)
    → 工具执行 → ToolMessage
    → LLM 生成回复 → 最终输出
```

**关键消息类型：**
| 类型 | 说明 |
|-----|------|
| AIMessage | LLM 生成，可能含 tool_calls |
| ToolMessage | 工具执行结果 |

---

### 3. 多 Agent 协作 🔥🔥🔥🔥🔥

**经典模式：**
```
Researcher → Critic → (循环改进) → Writer → END
```

**核心要点：**
- 共享状态实现 Agent 间通信
- 条件边实现循环和移交
- 每个 Agent 有独立职责

**状态共享示例：**
```python
class MultiAgentState(TypedDict):
    research_result: str  # 研究员写入
    critique_feedback: str  # 批评家写入
    final_output: str  # 写作 Agent 写入
```

---

### 4. Agent Handoff（Agent 移交）🔥🔥🔥🔥🔥

**两种实现方式：**

| 方式 | 实现 | 适用场景 |
|-----|------|---------|
| LiveKit | 工具返回新 Agent 对象 | 语音 Agent |
| LangGraph | 条件边路由到不同节点 | 通用工作流 |

**LiveKit 方式：**
```python
@function_tool
async def handoff_tool(self, context, data):
    return NewAgent(data)  # 直接返回新 Agent
```

**LangGraph 方式：**
```python
graph.add_conditional_edges(
    "agent1",
    lambda s: "agent2" if s["ready"] else "agent1",
    {"agent2": "agent2", "agent1": "agent1"}
)
```

---

### 5. Checkpointer vs Memory 🔥🔥🔥🔥🔥

**很多人混淆这两个概念！**

| 概念 | 用途 | 实现 |
|-----|------|-----|
| **Checkpointer** | 状态持久化（暂停-恢复、时间旅行） | MemorySaver / SqliteSaver / RedisSaver |
| **短期记忆** | 当前对话的上下文 | State 中的 `messages` 字段 |
| **长期记忆** | 跨会话的用户信息 | Redis / 向量数据库（需自己实现） |

**关键区别：**
```
Checkpointer:
┌─────────────────────────────────┐
│ 保存的是 AgentState（整个状态）   │
│ - messages（短期记忆 ✓）         │
│ - 其他字段                       │
│ - 执行位置                       │
│                                 │
│ 目的：状态管理，不是记忆管理       │
└─────────────────────────────────┘

Memory（长期记忆）:
┌─────────────────────────────────┐
│ 保存的是用户相关信息              │
│ - 用户偏好                       │
│ - 历史交互                       │
│ - 知识库                         │
│                                 │
│ 目的：跨会话的信息积累            │
└─────────────────────────────────┘
```

---

### 6. LiveKit 的存储策略 🔥🔥🔥

**源码分析结论：LiveKit Agents 没有内置长期存储！**

```python
# livekit-agents/livekit/agents/llm/chat_context.py
class ChatContext:
    def __init__(self, items: list[ChatItem] = NOT_GIVEN):
        self._items: list[ChatItem] = []  # 纯内存存储
```

**特点：**
- 对话历史保存在内存中的 `ChatContext` 对象
- 会话结束后数据消失
- 没有自动持久化到数据库

**如果需要长期存储，需要自己实现：**
| 方案 | 适用场景 | 实现 |
|-----|---------|------|
| LangGraph Checkpointer | 状态持久化 | SqliteSaver / RedisSaver |
| Redis | 快速读写、分布式 | redis-py + 自定义 Memory |
| 向量数据库 | 语义检索、知识库 | Pinecone / Milvus |

---

### 7. TTS + WebRTC + VAD 的关系 🔥🔥🔥🔥🔥🔥🔥🔥🔥

**面试最高频！三者紧密协作，构成实时语音 Agent 的核心。**

```
┌─────────────────────────────────────────────────────────────┐
│              LiveKit 实时语音 Agent 流程                     │
│                                                             │
│  用户说话                                                   │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ WebRTC      │ ← 实时音频传输（UDP，<100ms）              │
│  │ 接收音频    │                                            │
│  └─────────────┘                                            │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ VAD         │ ← 判断用户是否在说话                       │
│  │ 语音检测    │   检测到说话 → 开始处理                    │
│  └─────────────┘                                            │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ STT         │ ← 语音转文字                               │
│  │ (ASR)       │                                            │
│  └─────────────┘                                            │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ LLM         │ ← 大模型生成回复                           │
│  └─────────────┘                                            │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ TTS         │ ← 文字转语音 🔥🔥🔥🔥🔥                    │
│  │ 流式合成    │   边生成边播放                             │
│  └─────────────┘                                            │
│     ↓                                                       │
│  ┌─────────────┐                                            │
│  │ WebRTC      │ ← 实时音频传输给用户                       │
│  │ 发送音频    │                                            │
│  └─────────────┘                                            │
│                                                             │
│  打断机制：                                                  │
│  VAD 检测用户说话 → 立即停止 TTS → 开始新的处理循环          │
└─────────────────────────────────────────────────────────────┘
```

**三者的具体关系：**

| 组件 | 作用 | 与其他组件的关系 |
|-----|------|-----------------|
| **WebRTC** | 音频传输通道 | TTS 输出的 AudioFrame 通过 WebRTC 发送 |
| **VAD** | 语音活动检测 | 检测用户说话 → 触发打断 TTS |
| **TTS** | 文字转语音 | LLM 输出 → TTS 合成 → WebRTC 发送 |

**流式 TTS（核心能力）：**
```python
# 边生成边播放，实现低延迟
async with tts.stream() as stream:
    stream.push_text("你")  # 先合成"你"
    stream.push_text("好")  # 再合成"好"
    stream.flush()          # 刷新输出
    
    async for audio in stream:
        # 边合成边播放（实时性关键！）
        await webrtc_send(audio.frame)
```

---

### 8. LiveKit Agents 在大型项目中的定位 🔥🔥🔥

**可以作为大型 Agent 系统的语音交互层！**

```
┌─────────────────────────────────────────────────────────┐
│                    大型 Agent 系统                        │
│                                                         │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │ Orchestrator    │ ←──→ │ Decision Agent  │          │
│  │ (LangGraph)     │      │ (LangGraph)     │          │
│  └─────────────────┘      └─────────────────┘          │
│         ↓                        ↓                      │
│  ┌─────────────────┐      ┌─────────────────┐          │
│  │ Voice Agent     │ ←──→ │ Research Agent  │          │
│  │ (LiveKit)       │      │ (LangGraph)     │          │
│  │ 🔥🔥🔥🔥🔥       │      └─────────────────┘          │
│  └─────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

**集成方式：**
| 方式 | 说明 |
|-----|------|
| LangGraph + LLMAdapter | LiveKit 作为 LangGraph 的一个节点 |
| MCP 工具 | 通过 MCP 调用其他 Agent 的能力 |
| API 调用 | HTTP/WebSocket 与其他服务通信 |

---

## 阶段2 文件结构

```
phase2-langgraph/
├── 01_checkpointing.py      # 状态持久化
├── 02_tools.py              # 工具调用
├── 03_multi_agent.py        # 多 Agent 协作
├── 04_agent_handoff.py      # Agent Handoff
└── NOTES.md                 # 本笔记
```

---

## 面试高频问答

### Q1: Checkpointer 有什么用？

> 1. **持久化状态** - Agent 状态不会丢失
> 2. **暂停-恢复** - 支持 Agent 中断后继续（生产必备）
> 3. **时间旅行调试** - 可回溯历史状态定位问题
> 4. **多轮对话** - 支持长时间、跨会话对话

---

### Q1.1: 生产环境用什么 Checkpointer？

> **⚠️ LangGraph 只内置 MemorySaver！**
>
> 生产环境需要**自己实现持久化方案**：
>
> ```python
> from langgraph.checkpoint.base import BaseCheckpointSaver
>
> class RedisCheckpointer(BaseCheckpointSaver):
>     def __init__(self, redis_url):
>         import redis
>         self.client = redis.from_url(redis_url)
>     
>     async def aget_tuple(self, config): ...
>     async def aput(self, config, checkpoint, ...): ...
> ```
>
> | 方案 | 优点 | 缺点 |
> |-----|------|-----|
> | MemorySaver | 内置、简单 | 重启丢失 |
> | 自定义 Redis | 持久化、分布式 | 需自己实现 |
> | 自定义 SQLite | 持久化、单机 | 需自己实现 |

---

### Q2: 工具调用的完整流程？

```
用户输入 → LLM → AIMessage(tool_calls=[{name, args}])
    → 执行工具 → ToolMessage(content=result)
    → LLM → 最终回复
```

---

### Q3: 多 Agent 如何通信？

> 通过**共享状态**传递信息。每个 Agent 读写状态中的特定字段。

---

### Q4: Agent Handoff 怎么实现？

> **LiveKit**：工具函数返回新 Agent 对象
> **LangGraph**：条件边路由到不同 Agent 节点

---

### Q5: 常见协作模式？

| 模式 | 说明 | 示例 |
|-----|------|-----|
| 串行 | Agent1 → Agent2 → Agent3 | 流水线 |
| 循环 | Agent1 → Agent2 → (判断) → Agent1/3 | 审核改进 |
| 层级 | Manager 分配给 Workers | 任务分发 |
| 并行 | 多 Agent 同时处理 | 并行计算 |

---

### Q6: Checkpointer 是短期记忆吗？

> ❌ 不完全是。
> 
> Checkpointer 保存的是**整个 AgentState**，其中包含 messages（短期记忆），但主要用途是**状态管理**（暂停-恢复、时间旅行调试）。
>
> 如果需要**长期记忆**，需要单独实现（Redis、向量数据库）。

---

### Q7: LiveKit 用什么做长期存储？

> LiveKit Agents **没有内置长期存储**。对话历史保存在内存中的 `ChatContext`。
>
> 需要长期记忆时，自己实现：
> - LangGraph Checkpointer（SqliteSaver/RedisSaver）
> - Redis / 向量数据库

---

### Q8: TTS 和 WebRTC、VAD 有什么关系？

> 三者紧密协作，构成实时语音 Agent 的核心：
>
> 1. **WebRTC**：音频传输通道，TTS 输出的 AudioFrame 通过 WebRTC 发送
> 2. **VAD**：检测用户说话，触发打断 TTS
> 3. **TTS**：将 LLM 文字回复转为语音，通过 WebRTC 实时播放
>
> 流式 TTS 是关键：边生成边播放，实现低延迟。

---

### Q9: LiveKit Agents 能作为大型项目的一个 Agent 吗？

> ✅ 可以。
>
> LiveKit Agents 专注于**语音交互层**，在大型 Agent 系统中可以：
> 1. 作为用户语音入口
> 2. 通过 LangGraph 集成（LLMAdapter）
> 3. 通过 MCP/API 与其他 Agent 协作

---

## 与源码对比

| 知识点 | 源码位置 |
|-------|---------|
| Multi-Agent | [multi_agent.py](../livekit-agents/examples/voice_agents/multi_agent.py) |
| Agent Handoff | 同上，工具返回新 Agent |
| LangGraph 集成 | [langgraph_agent.py](../livekit-agents/examples/voice_agents/langgraph_agent.py) |

---

## 下一步

阶段3 将学习：
- LiveKit 实时语音 Agent 🔥🔥🔥🔥🔥
- WebRTC 低延迟传输
- VAD 语音活动检测
- 打断机制
- LangGraph + LiveKit 集成