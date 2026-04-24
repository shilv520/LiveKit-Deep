"""
阶段4：MCP + LiveKit Agent 集成
================================

核心知识点：
1. MCPServerHTTP - 连接 HTTP 方式的 MCP 服务器
2. MCPToolset - 将 MCP 工具包装给 Agent 使用
3. AgentSession 配合 MCP 工具
4. 同时运行 MCP 服务器和 Agent

本 Agent 连接 02_mcp_server.py 提供的 MCP 服务器。

参考源码：livekit-agents/examples/voice_agents/mcp/mcp-agent.py

前置条件：
1. 先运行 MCP 服务器：python 02_mcp_server.py
2. 再运行本 Agent：python 03_mcp_agent.py console

安装：
pip install mcp livekit-agents[mcp] livekit-plugins-silero
"""

import logging
import os

try:
    from dotenv import load_dotenv
    from livekit.agents import (
        Agent,
        AgentServer,
        AgentSession,
        JobContext,
        JobProcess,
        cli,
        inference,
        mcp,
    )
    from livekit.plugins import silero
    LIVEKIT_MCP_AVAILABLE = True
except ImportError:
    LIVEKIT_MCP_AVAILABLE = False
    print("[警告] LiveKit MCP 未安装。请运行:")
    print("pip install 'livekit-agents[mcp]' livekit-plugins-silero")

logger = logging.getLogger("mcp-agent")

if os.path.exists(".env"):
    load_dotenv()


# ============================================
# MCP + LiveKit 集成架构
# ============================================

"""
MCP 集成架构图：

┌─────────────────────────────────────────────────────────────┐
│                    LiveKit Agent                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AgentSession                                         │   │
│  │   stt: Deepgram（语音识别）                           │   │
│  │   llm: OpenAI（大模型）                               │   │
│  │   tts: Cartesia（语音合成）                           │   │
│  │   vad: Silero（语音检测）                             │   │
│  │                                                      │   │
│  │   tools: [                                           │   │
│  │     MCPToolset(                                      │   │
│  │       mcp_server=MCPServerHTTP(                      │   │
│  │         url="http://localhost:8000/sse"              │   │
│  │       )                                              │   │
│  │     )                                                │   │
│  │   ]                                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         ↓ SSE 连接
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server                                │
│  FastMCP 工具：                                              │
│    - get_weather(location)                                   │
│    - get_time()                                              │
│    - calculate(expression)                                   │
│    - search_knowledge(topic)                                 │
└─────────────────────────────────────────────────────────────┘

关键：MCPToolset 从 MCP 服务器获取工具并暴露给 Agent！
"""


# ============================================
# Agent 定义
# ============================================

class MCPAgent(Agent):
    """
    使用 MCP 工具的 Agent。

    关键点：
    - instructions：Agent 角色（提及 MCP 工具）
    - on_enter：欢迎消息
    - 工具来自 MCPToolset，不是这里定义的 @function_tool
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "你是一个拥有 MCP 工具的助手。"
                "你可以查询天气、获取时间、计算数学、"
                "搜索知识库。"
                "回答要简洁。"
                "当用户询问具体信息时使用工具。"
            ),
        )

    async def on_enter(self) -> None:
        """进入会话时生成欢迎消息。"""
        self.session.generate_reply(
            instructions="问候用户，提及你有天气、时间、计算和知识搜索工具。"
        )


# ============================================
# AgentServer 配置
# ============================================

server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """预加载 VAD 模型。"""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD 模型已加载")


server.setup_fnc = prewarm


# ============================================
# 入口函数 - MCP 集成
# ============================================

@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """
    Agent 入口函数，包含 MCP 集成。

    关键步骤：
    1. 创建 MCP 服务器连接
    2. 创建 MCPToolset
    3. 创建 AgentSession，tools=[MCPToolset]
    4. 启动会话
    """

    ctx.log_context_fields = {"room": ctx.room.name}

    # ============================================
    # MCP 集成（关键部分！）
    # ============================================

    # 1. 创建 MCP 服务器连接
    mcp_server = mcp.MCPServerHTTP(
        url="http://localhost:8000/sse",  # MCP 服务器地址
        # 可选：过滤工具
        # allowed_tools=["get_weather", "get_time"],
    )

    # 2. 创建 MCPToolset（包装 MCP 服务器给 Agent 使用）
    mcp_toolset = mcp.MCPToolset(
        id="demo_tools",
        mcp_server=mcp_server,
    )

    # ============================================
    # AgentSession 配合 MCP 工具
    # ============================================

    session = AgentSession(
        # 语音处理（与阶段3相同）
        stt=inference.STT("deepgram/nova-3", language="multi"),
        llm=inference.LLM("openai/gpt-4.1-mini"),
        tts=inference.TTS("cartesia/sonic-3"),
        vad=ctx.proc.userdata["vad"],

        # MCP 工具！（与阶段3的关键区别）
        tools=[mcp_toolset],
    )

    # 启动会话
    await session.start(
        agent=MCPAgent(),
        room=ctx.room,
    )

    logger.info("MCP Agent 会话已启动")


# ============================================
# 面试高频问答
# ============================================

"""
MCP 集成面试问题：

问题1：如何在 LiveKit 中连接 MCP 服务器？
回答：
  mcp_server = mcp.MCPServerHTTP(url="http://localhost:8000/sse")
  toolset = mcp.MCPToolset(id="...", mcp_server=mcp_server)

问题2：如何在 AgentSession 中使用 MCP 工具？
回答：
  session = AgentSession(
      stt=...,
      llm=...,
      tts=...,
      tools=[mcp_toolset],  # 添加 MCP 工具集
  )

问题3：MCPToolset 和 MCPServerHTTP 的区别？
回答：
  MCPServerHTTP：与 MCP 服务器的连接（HTTP/SSE）
  MCPToolset：包装器，将工具暴露给 Agent

问题4：可以使用多个 MCP 服务器吗？
回答：
  可以！
  tools=[
      MCPToolset(id="server1", mcp_server=MCPServerHTTP(url1)),
      MCPToolset(id="server2", mcp_server=MCPServerHTTP(url2)),
  ]

问题5：如何过滤工具？
回答：
  MCPServerHTTP(url="...", allowed_tools=["get_weather"])

问题6：如果 MCP 服务器宕机怎么办？
回答：
  MCPToolset.setup() 会失败
  Agent 将无法使用那些工具
"""

# ============================================
# 运行说明
# ============================================

"""
运行 MCP + LiveKit Agent 的方法：

步骤1：启动 MCP 服务器
─────────────────────────────────────
cd phase4-mcp-integration
python 02_mcp_server.py

（MCP 服务器在 http://localhost:8000/sse 上运行）

步骤2：运行 Agent（在另一个终端）
─────────────────────────────────────
python 03_mcp_agent.py console

或开发模式：
python 03_mcp_agent.py dev

测试命令：
- "北京天气怎么样？"
- "现在几点了？"
- "计算 123 + 456"
- "告诉我关于 Python 的信息"

Agent 会使用 MCP 工具来回答！
"""

if __name__ == "__main__":
    if LIVEKIT_MCP_AVAILABLE:
        print("=" * 60)
        print("MCP + LiveKit Agent")
        print("=" * 60)
        print("\n重要：先运行 MCP 服务器！")
        print("  python 02_mcp_server.py")
        print("\n然后运行本 Agent：")
        print("  python 03_mcp_agent.py console")
        print("=" * 60)

        cli.run_app(server)
    else:
        print("[错误] 请先安装依赖:")
        print("pip install 'livekit-agents[mcp]' livekit-plugins-silero")