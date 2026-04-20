# LangGraph + LiveKit 学习计划（2026年最新版）

> 🔥🔥🔥🔥🔥 **2026年4月最前沿的实时语音 Agent 方案**

---

## 项目结构

```
LangGraph-LiveKit/
├── phase1-quickstart/       # 阶段1：环境准备与快速上手
├── phase2-langgraph/        # 阶段2：LangGraph 基础与 Agent 编排
├── phase3-livekit-voice/    # 阶段3：LiveKit 实时语音 Agent 🔥🔥🔥🔥🔥🔥
├── phase4-mcp-deepagents/   # 阶段4：MCP Skill + DeepAgents
├── phase5-rl-advanced/      # 阶段5：Agentic RL 进阶（可选）
├── phase6-final-project/    # 阶段6：完整实战项目
├── PROGRESS.md              # 学习进度记录
├── LEARNING_PLAN.md         # 本文件
└── README.md                # 项目总览
```

---

## 阶段 1：环境准备与快速上手（1-2 天）

### 学习目标
- 成功运行第一个 LangGraph Agent
- 理解 LangGraph 核心架构（StateGraph、Node、Edge）
- 配置 LiveKit 开发环境

### 🔥🔥 面试高频考点
- LangGraph vs LangChain 的区别
- StateGraph（状态图）是什么
- Agent 的核心公式（通用）

### 具体步骤

#### 1.1 安装环境
```bash
# LangChain + LangGraph
pip install langchain langgraph langchain-openai

# LiveKit Agents
pip install livekit-agents livekit-plugins-openai livekit-plugins-langchain

# 开发工具
pip install python-dotenv aiohttp
```

#### 1.2 需要阅读的资源
| 资源 | 学习重点 |
|-----|---------|
| [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/) | StateGraph、Node、Edge |
| [LiveKit Agents 文档](https://docs.livekit.io/agents/) | 实时语音架构 |
| [LangGraph + LiveKit 示例](https://github.com/dqbd/langgraph-livekit-agents) | 实战代码 |

#### 1.3 核心概念清单
| 概念 | 说明 | 面试频率 |
|-----|------|---------|
| **StateGraph** | 状态图，LangGraph 核心 | 🔥🔥🔥 |
| **Node** | 状态图中的节点（函数） | 🔥🔥 |
| **Edge** | 状态图中的边（流转条件） | 🔥🔥 |
| **CompiledGraph** | 编译后的可执行图 | 🔥 |
| **AgentExecutor** | LangChain 的 Agent 执行器 | 🔥🔥 |
| **LiveKit Room** | 实时语音房间 | 🔥🔥🔥 |

#### 1.4 第一个 LangGraph Agent 示例
```python
# 🔥🔥🔥 面试常考：LangGraph StateGraph 结构
from langgraph.graph import StateGraph, END

# 定义状态
class AgentState(dict):
    messages: list
    next_action: str

# 创建状态图
graph = StateGraph(AgentState)

# 添加节点
graph.add_node("think", think_node)      # 思考节点
graph.add_node("act", act_node)          # 执行节点
graph.add_node("observe", observe_node)  # 观察节点

# 添加边（流转逻辑）
graph.add_edge("think", "act")
graph.add_edge("act", "observe")
graph.add_edge("observe", "think")       # 循环直到结束

# 设置入口点
graph.set_entry_point("think")

# 编译图
app = graph.compile()
```

### 实践练习
1. 创建一个简单的 ReAct 循环图
2. 观察状态如何在节点间流转
3. 添加条件边（判断是否结束）

---

## 阶段 2：LangGraph 基础与 Agent 编排（3-5 天）

### 学习目标
- 掌握 StateGraph 的完整用法
- 理解 Checkpointing（持久化状态）
- 学会工具调用（Function Calling）

### 🔥🔥🔥 面试高频考点
- StateGraph vs Pipeline 的区别
- Checkpointing 是什么？为什么重要？
- 如何实现多 Agent 协作？

### 2.1 StateGraph 进阶

#### 核心代码示例 🔥🔥🔥
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

# 🔥🔥🔥 Checkpointing（面试必问）
checkpointer = MemorySaver()  # 状态持久化

# 带条件边的图
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)

# 🔥🔥🔥 条件边（面试常考）
graph.add_conditional_edges(
    "agent",
    should_continue,  # 判断函数
    {
        "continue": "tools",
        "end": END,
    }
)
graph.add_edge("tools", "agent")

# 编译并添加 Checkpointer
app = graph.compile(checkpointer=checkpointer)
```

### 2.2 工具调用（Tools）

#### 🔥🔥🔥 LangChain Tools vs AgentScope Tools
```python
# 🔥🔥🔥 LangChain 工具定义（面试常考）
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """搜索信息。"""
    return f"搜索结果：{query}"

@tool  
def calculate(expression: str) -> float:
    """计算数学表达式。"""
    return eval(expression)

# AgentScope 对比（已在阶段1学过）
# def calculate(expr: str) -> ToolResponse:
#     return ToolResponse(content=...)
```

### 2.3 多 Agent 协作

```python
# 🔥🔥🔥 多 Agent 图（面试热点）
from langgraph.graph import StateGraph

graph = StateGraph(MultiAgentState)
graph.add_node("researcher", researcher_node)
graph.add_node("critic", critic_node)
graph.add_node("writer", writer_node)

# 协作流程
graph.add_edge("researcher", "critic")
graph.add_edge("critic", "writer")
graph.set_entry_point("researcher")
```

### 面试高频问答 🔥🔥🔥

**Q1: LangGraph 和 LangChain 的区别？**
> - **LangChain**: 链式调用（Chain），线性流程
> - **LangGraph**: 状态图（StateGraph），支持循环、分支、并行
> - LangGraph 更适合复杂 Agent 编排

**Q2: Checkpointing 有什么用？**
> - 持久化 Agent 状态
> - 支持"暂停-恢复"
> - 可回溯历史状态（时间旅行调试）
> - 生产环境必备（应对中断）

**Q3: 条件边如何实现？**
> `add_conditional_edges(node, condition_fn, {path1: node1, path2: node2})`

---

## 阶段 3：LiveKit 实时语音 Agent 🔥🔥🔥（4-6 天）

### 学习目标
- 掌握 LiveKit Agents 完整架构
- 实现低延迟实时语音交互
- 理解 WebRTC、VAD、打断机制

### 🔥🔥🔥🔥🔥 面试最高频考点（2026年热点）

### 3.1 LiveKit 核心架构
```
LiveKit Agents 架构：
┌─────────────────────────────────────────────┐
│  LiveKit Room（实时房间）                     │
│      ↓                                      │
│  AgentSession（Agent 会话）                  │
│      ↓                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ STT     │  │ LLM     │  │ TTS     │     │
│  │(语音识别)│  │(大模型) │  │(语音合成)│     │
│  └─────────┘  └─────────┘  └─────────┘     │
│      ↓                                      │
│  VAD（语音活动检测）+ 打断处理                │
└─────────────────────────────────────────────┘
```

### 3.2 第一个 LiveKit 语音 Agent 🔥🔥🔥

```python
# 🔥🔥🔥🔥🔥 实时语音 Agent（面试必问）
import asyncio
from livekit.agents import AgentSession, Agent, RoomInput
from livekit.plugins.openai import STT, LLM, TTS

async def main():
    # 🔥🔥🔥 创建语音 Agent
    session = AgentSession(
        stt=STT(),            # 语音识别（Whisper）
        llm=LLM(model="gpt-4o"),  # 大模型
        tts=TTS(),            # 语音合成
        vad=VAD(),            # 🔥🔥🔥 语音活动检测
    )

    # 🔥🔥🔥🔥🔥 接入 LiveKit 房间
    await session.start(room=room)
    
    # 实时处理语音流
    for event in session.stream():
        if event.type == "speech":
            await session.reply(event.text)

asyncio.run(main())
```

### 3.3 LangGraph + LiveKit 集成 🔥🔥🔥🔥🔥

```python
# 🔥🔥🔥🔥🔥 核心集成代码（面试最高频）
from livekit.plugins.langchain import LLMAdapter
from langgraph.graph import StateGraph

# 创建 LangGraph Agent
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)
graph.add_conditional_edges(...)
compiled_graph = graph.compile()

# 🔥🔥🔥🔥🔥 把 LangGraph 接入 LiveKit
session = AgentSession(
    llm=LLMAdapter(compiled_graph),  # 🔥🔥🔥🔥🔥 关键：用 LangGraph 替代普通 LLM
    stt=STT(),
    tts=TTS(),
)

await session.start(room)
```

### 3.4 关键特性 🔥🔥🔥

| 特性 | 说明 | 面试频率 |
|-----|------|---------|
| **WebRTC** | 🔥🔥🔥 低延迟传输（<100ms） | 🔥🔥🔥 |
| **VAD** | 🔥🔥🔥 语音活动检测（判断是否说话） | 🔥🔥🔥 |
| **打断** | 🔥🔥🔥🔥🔥 用户说话时自动打断 Agent | 🔥🔥🔥🔥🔥 |
| **轮次检测** | 🔥🔥🔥 自然对话节奏 | 🔥🔥🔥 |
| **电话接入** | 🔥🔥🔥 支持电话 API | 🔥🔥🔥 |

### 面试高频问答 🔥🔥🔥🔥🔥

**Q4: LiveKit 的延迟为什么这么低？**
> - WebRTC 原生传输（UDP）
> - 流式处理（边说边处理）
> - 无需等待完整音频

**Q5: VAD 是什么？为什么重要？**
> - Voice Activity Detection
> - 判断用户是否在说话
> - 区分"说话"和"静音"
> - 打断机制的基础

**Q6: 用户打断 Agent 是怎么实现的？**
> - VAD 检测到用户开始说话
> - 立即停止 TTS 播放
> - 开始处理用户新输入
> - LiveKit 原生支持

---

## 阶段 4：MCP Skill + DeepAgents（3-5 天）

### 学习目标
- 掌握 MCP（Model Context Protocol）集成
- 学会 DeepAgents 无缝升级
- 实现多 Agent 语音协作

### 🔥🔥🔥 面试高频考点

### 4.1 MCP Skill 集成

```python
# 🔥🔥🔥 MCP 工具集成
from langchain.tools import MCPTool

# 连接 MCP Server
mcp_tool = MCPTool(
    server_url="https://mcp.weather.com",
    tool_name="get_weather",
)

# 加入 LangGraph
graph.add_node("mcp_weather", mcp_weather_node)
```

### 4.2 DeepAgents 升级 🔥🔥🔥🔥🔥

```python
# 🔥🔥🔥🔥🔥 DeepAgents（面试热点）
from deepagents import create_deep_agent

# 🔥🔥🔥🔥🔥 从 LangGraph 升级到 Deep Agent
deep_agent = create_deep_agent(
    llm=ChatOpenAI(model="gpt-4o"),
    tools=[search, calculate],
    planner=True,          # 🔥🔥🔥 自动规划
    filesystem=True,       # 🔥🔥🔥 虚拟文件系统
    subagents=True,        # 🔥🔥🔥 子智能体生成
)

# 🔥🔥🔥🔥🔥 直接接入 LiveKit（无缝）
session = AgentSession(
    llm=LLMAdapter(deep_agent.compile()),  # 和普通 LangGraph 一样！
    stt=STT(),
    tts=TTS(),
)
```

### DeepAgents vs 普通 LangGraph 🔥🔥🔥

| 特性 | 普通 LangGraph | DeepAgents |
|-----|---------------|------------|
| 规划能力 | 手动实现 | 🔥🔥🔥 自动规划 |
| 文件系统 | 无 | 🔥🔥🔥 虚拟文件系统 |
| 子智能体 | 手动编排 | 🔥🔥🔥 自动生成 |
| 升级成本 | - | 🔥🔥🔥🔥🔥 5行代码 |

---

## 阶段 5：Agentic RL 进阶（可选，5-7 天）

### 学习目标
- 了解如何为 LangGraph Agent 添加 RL
- 掌握 ART / Agent Lightning 工具

### 🔥🔥🔥 面试加分项

```python
# 🔥🔥🔥 用 ART 做 RL 训练
from openpipe.art import AgentReinforcementTrainer

trainer = AgentReinforcementTrainer(
    agent_graph=compiled_graph,
    reward_model=reward_fn,
)

# 训练 Agent
trained_graph = trainer.train(dataset)
```

**注意**：这是可选进阶，基础学完后可补充。

---

## 阶段 6：完整实战项目（7-10 天）

### 项目目标
构建一个完整的实时语音贾维斯：
- 🔥🔥🔥 实时语音交互（LiveKit）
- 🔥🔥🔥 Agentic 决策（LangGraph）
- 🔥🔥🔥 MCP Skill 工具调用
- 🔥🔥🔥 DeepAgents 升级
- 🔥🔥🔥 Redis 持久化记忆
- 🔥🔥🔥 React/Vue 前端

### 项目结构
```
voice-jarvis/
├── backend/
│   ├── agent/
│   │   ├── graph.py          # LangGraph StateGraph
│   │   ├── tools.py          # MCP + 自定义工具
│   │   └── deep_agent.py     # DeepAgents 版本
│   ├── voice/
│   │   ├── livekit_agent.py  # LiveKit 实时语音
│   │   └── vad.py            # 语音活动检测
│   ├── memory/
│   │   └── redis_memory.py   # Redis 持久化
│   └── api/
│   │   └── main.py           # FastAPI 接口
│   └── websocket/
│   │   └── voice_ws.py       # WebSocket 语音流
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VoiceInput.tsx    # 语音输入
│   │   │   ├── VoiceOutput.tsx   # 语音播放
│   │   │   └ ChatHistory.tsx     # 对话历史
│   │   ├── hooks/
│   │   │   ├── useLiveKit.ts     # LiveKit 连接
│   │   │   ├── useAudio.ts       # 音频处理
│   │   ├── App.tsx
│   └── package.json
│
├── livekit/
│   ├── docker-compose.yaml   # LiveKit 服务部署
│   └── room.yaml             # 房间配置
│
└── README.md
```

---

## 面试高频问答汇总 🔥🔥🔥🔥🔥

### 必问问题（最高优先级）

| 编号 | 问题 | 重要程度 |
|-----|-----|---------|
| Q1 | LangGraph vs LangChain 区别？ | 🔥🔥🔥 |
| Q2 | StateGraph 是什么？ | 🔥🔥🔥🔥🔥 |
| Q3 | Checkpointing 有什么用？ | 🔥🔥🔥 |
| Q4 | LiveKit 延迟为什么低？ | 🔥🔥🔥🔥🔥 |
| Q5 | VAD 是什么？ | 🔥🔥🔥🔥🔥 |
| Q6 | 用户打断 Agent 怎么实现？ | 🔥🔥🔥🔥🔥🔥 |
| Q7 | LangGraph + LiveKit 怎么集成？ | 🔥🔥🔥🔥🔥🔥 |
| Q8 | DeepAgents vs 普通 LangGraph？ | 🔥🔥🔥🔥🔥 |

### 加分问题

| 编号 | 问题 | 重要程度 |
|-----|-----|---------|
| Q9 | MCP 是什么？为什么需要？ | 🔥🔥🔥 |
| Q10 | 如何为 Agent 加 RL 训练？ | 🔥🔥🔥 |
| Q11 | Redis Memory vs SQLite？ | 🔥🔥🔥 |

---

## 学习进度追踪

| 阶段 | 状态 | 描述 |
|-----|------|-----|
| Phase 1 | ⬜ 待开始 | LangGraph 基础、StateGraph |
| Phase 2 | ⬜ 待开始 | 工具调用、Checkpointing、多 Agent |
| Phase 3 | ⬜ 待开始 | 🔥🔥🔥 LiveKit 实时语音（核心） |
| Phase 4 | ⬜ 待开始 | MCP + DeepAgents 升级 |
| Phase 5 | ⬜ 待开始 | Agentic RL（可选） |
| Phase 6 | ⬜ 待开始 | 完整实战项目 |

---

## 官方资源链接

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LiveKit Agents**: https://docs.livekit.io/agents/
- **DeepAgents**: https://github.com/langchain-ai/deepagents
- **LangGraph + LiveKit 示例**: https://github.com/dqbd/langgraph-livekit-agents
- **ART (RL 训练)**: https://github.com/openpipe/art
- **Agent Lightning**: https://github.com/microsoft/agent-lightning

---

## 与 AgentScope 对比速查表

| 概念 | AgentScope | LangGraph + LiveKit | 通用概念 |
|-----|-----------|---------------------|---------|
| Agent | ReActAgent | StateGraph + AgentExecutor | Agent 核心 |
| 工具 | Toolkit + ToolResponse | @tool 装饰器 | 工具调用 |
| 记忆 | InMemoryMemory/Redis | Checkpointer + Redis | 持久化 |
| 编排 | MsgHub | 🔥🔥🔥 StateGraph | 流程编排 |
| 语音 | RealtimeAgent | 🔥🔥🔥🔥🔥 LiveKit Agents | 实时语音 |
| RL | Trinity-RFT | ART/Agent Lightning | 强化学习 |

---

准备好了吗？回复 **"开始阶段1"**，我们立刻动手搭建环境并运行第一个 LangGraph Agent！🚀