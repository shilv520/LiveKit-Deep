"""
阶段3：LangGraph + LiveKit 集成
================================

知识点：
1. LLMAdapter - 将 LangGraph 图接入 LiveKit
2. LangGraph 作为 LLM 层
3. LiveKit 处理语音层（STT/TTS/VAD/打断）
4. 两种框架的分工

参考源码：livekit-agents/examples/voice_agents/langgraph_agent.py

前置条件：
pip install langgraph langchain-openai livekit-agents livekit-plugins-langchain
"""

import logging
import os

# 模拟导入
try:
    from dotenv import load_dotenv
    from typing import Annotated, TypedDict

    from langchain.chat_models import init_chat_model
    from langchain_core.messages import BaseMessage
    from langgraph.graph import START, StateGraph
    from langgraph.graph.message import add_messages

    from livekit.agents import (
        Agent,
        AgentServer,
        AgentSession,
        JobContext,
        JobProcess,
        cli,
        inference,
    )
    from livekit.plugins import silero
    from livekit.plugins.langchain import LLMAdapter

    LANGGRAPH_LIVEKIT_AVAILABLE = True
except ImportError:
    LANGGRAPH_LIVEKIT_AVAILABLE = False
    print("[WARN] 请安装依赖：")
    print("pip install langgraph langchain-openai livekit-agents livekit-plugins-langchain")

logger = logging.getLogger("langgraph-agent")

if os.path.exists(".env"):
    load_dotenv()


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 核心概念：分工
# ============================================

"""
LangGraph + LiveKit 分工：

┌─────────────────────────────────────────────────────────┐
│                    LiveKit 层                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │ STT     │  │ TTS     │  │ VAD     │                 │
│  │(语音识别)│  │(语音合成)│  │(语音检测)│                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
│                                                         │
│  职责：                                                  │
│  - 音频传输（WebRTC）                                    │
│  - 语音处理（STT/TTS）                                   │
│  - 打断机制（VAD + Turn Detection）                      │
└─────────────────────────────────────────────────────────┘
                    ↓ 文本 ↑ 文本
┌─────────────────────────────────────────────────────────┐
│                    LangGraph 层                          │
│  ┌─────────────────────────────────────┐               │
│  │ StateGraph                          │               │
│  │  ┌─────────┐  ┌─────────┐           │               │
│  │  │节点1    │→ │节点2    │→ ...       │               │
│  │  └─────────┘  └─────────┘           │               │
│  └─────────────────────────────────────┘               │
│                                                         │
│  职责：                                                  │
│  - 业务逻辑（节点、边）                                  │
│  - Agent 编排（多 Agent 协作）                           │
│  - 工具调用（@tool）                                     │
└─────────────────────────────────────────────────────────┘

🔥🔥🔥🔥🔥 关键：LLMAdapter 桥接两层
"""


# ============================================
# 🔥🔥🔥🔥🔥 LangGraph 图定义
# ============================================

class State(TypedDict):
    """
    🔥🔥🔥 LangGraph 状态定义

    messages: 消息历史（自动累加）
    """
    messages: Annotated[list[BaseMessage], add_messages]


def create_langgraph() -> StateGraph:
    """
    🔥🔥🔥🔥🔥 创建 LangGraph 图

    面试要点：
    - 图定义与纯 LangGraph 项目相同
    - LiveKit 只是用 LLMAdapter 包装这个图
    """

    # 初始化 LLM
    openai_llm = init_chat_model(
        model="openai:gpt-4.1-mini",
    )

    # 定义节点
    def chatbot_node(state: State):
        """
        简单的聊天节点

        调用 LLM，返回消息
        """
        response = openai_llm.invoke(state["messages"])
        return {"messages": [response]}

    # 创建图
    builder = StateGraph(State)

    # 🔥🔥🔥🔥🔥 添加节点（与阶段1/2相同）
    builder.add_node("chatbot", chatbot_node)

    # 🔥🔥🔥🔥🔥 添加边
    builder.add_edge(START, "chatbot")

    # 编译图
    return builder.compile()


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 LiveKit 入口
# ============================================

server = AgentServer()


def prewarm(proc: JobProcess):
    """预热 VAD"""
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """
    🔥🔥🔥🔥🔥🔥🔥🔥🔥 集成入口

    面试最高频！

    关键步骤：
    1. 创建 LangGraph 图
    2. 用 LLMAdapter 包装图
    3. 创建 Agent（使用 LLMAdapter）
    4. 创建 AgentSession（只有 STT/TTS/VAD）
    5. 启动会话
    """

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 步骤1：创建 LangGraph 图
    graph = create_langgraph()

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 步骤2：用 LLMAdapter 包装
    # langchain.LLMAdapter(graph) 将 LangGraph 图转为 LLM 接口
    # 这样 LiveKit 就能调用 LangGraph 的逻辑
    llm_adapter = LLMAdapter(graph)

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 步骤3：创建 Agent
    # Agent 的 llm 使用 LLMAdapter，而不是普通 LLM
    agent = Agent(
        instructions="",  # LangGraph 中处理指令
        llm=llm_adapter,  # 🔥🔥🔥🔥🔥 关键：使用 LLMAdapter
    )

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 步骤4：创建 AgentSession
    # 注意：这里不配置 llm，因为 Agent 已经有了
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        # LiveKit 处理语音层
        stt=inference.STT("deepgram/nova-3", language="multi"),
        tts=inference.TTS("cartesia/sonic-3"),
        # turn_detection 用于打断机制
    )

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 步骤5：启动会话
    await session.start(
        agent=agent,
        room=ctx.room,
    )

    # 生成欢迎语
    await session.generate_reply(
        instructions="ask the user how they are doing?"
    )


# ============================================
# 面试要点总结
# ============================================

"""
🔥🔥🔥🔥🔥🔥🔥🔥🔥 LangGraph + LiveKit 集成面试要点：

Q1: LangGraph 和 LiveKit 怎么分工？
A:
- LangGraph: 业务逻辑、Agent 编排、工具调用
- LiveKit: 语音处理、音频传输、打断机制

Q2: LLMAdapter 是什么？
A:
- 将 LangGraph 图包装成 LLM 接口
- LiveKit 通过 LLMAdapter 调用 LangGraph
- 语法：LLMAdapter(graph)

Q3: 集成的关键步骤？
A:
1. create_langgraph() 创建图
2. LLMAdapter(graph) 包装
3. Agent(llm=llm_adapter) 使用
4. AgentSession 只配 STT/TTS/VAD

Q4: Agent 的 instructions 为什么是空的？
A:
- LangGraph 图中处理指令
- Agent 只作为 LLM 的载体

Q5: 这种集成有什么优势？
A:
- LangGraph 的复杂编排能力
- LiveKit 的实时语音能力
- 各司其职，职责清晰
"""


# ============================================
# 运行说明
# ============================================

"""
运行步骤：

1. 安装依赖：
pip install langgraph langchain-openai livekit-agents livekit-plugins-langchain

2. 配置 .env：
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=sk-xxx
DEEPGRAM_API_KEY=xxx
CARTESIA_API_KEY=xxx

3. 启动 LiveKit Server：
docker run -d -p 7880:7880 livekit/livekit-server

4. 运行 Agent：
python langgraph_integration.py dev

或终端测试：
python langgraph_integration.py console
"""

if __name__ == "__main__":
    if LANGGRAPH_LIVEKIT_AVAILABLE:
        cli.run_app(server)
    else:
        print("[ERROR] 请先安装依赖")
        print("pip install langgraph langchain-openai livekit-agents livekit-plugins-langchain")