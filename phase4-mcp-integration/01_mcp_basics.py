"""
阶段4：MCP (Model Context Protocol) 基础概念
================================

核心知识点：
1. MCP 是什么 - 标准化的工具协议
2. MCP Server vs MCP Client
3. FastMCP - 快速创建服务端
4. 传输类型 - SSE、Stdio、Streamable HTTP

MCP 让 Agent 通过标准化协议连接外部服务。
可以理解为"AI 工具的 USB 接口" - 插上就能用！

参考源码：livekit-agents/examples/voice_agents/mcp/
官方文档：https://modelcontextprotocol.io/

前置条件：
pip install mcp livekit-agents[mcp]
"""

# ============================================
# MCP 核心概念
# ============================================

"""
MCP 架构图：

┌─────────────────────────────────────────────────────────────┐
│                    MCP Client（Agent端）                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AgentSession                                         │   │
│  │   └── MCPToolset                                     │   │
│  │        └── MCPServerHTTP / MCPServerStdio            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        ↓ HTTP/SSE 或 Stdio
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server（服务端）                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ FastMCP                                              │   │
│  │   @mcp.tool()                                        │   │
│  │   def get_weather(location): ...                     │   │
│  │                                                      │   │
│  │   @mcp.resource()                                    │   │
│  │   def get_data(): ...                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘


为什么需要 MCP？（面试高频！）
─────────────────────────────────
1. 标准化 - 所有工具使用同一协议
2. 分离 - 工具服务独立运行
3. 灵活 - 可连接多个 MCP 服务器
4. 复用 - 一个 MCP 服务可被多个 Agent 使用


MCP 传输类型：
─────────────────────────────────
1. SSE (Server-Sent Events) - HTTP 方式，旧标准
2. Streamable HTTP - 新标准，推荐使用
3. Stdio - 本地进程方式，用于 CLI 工具


LiveKit MCP 核心类：
─────────────────────────────────
MCPServer         - 基类（抽象类）
MCPServerHTTP     - HTTP/SSE 连接
MCPServerStdio    - Stdio（本地进程）连接
MCPToolset        - 工具集包装器，用于 Agent
"""

# ============================================
# 代码示例：用 FastMCP 创建 MCP Server
# ============================================

"""
创建 MCP Server（server.py）：

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo Tools")

@mcp.tool()
def get_weather(location: str) -> str:
    '''获取某地的天气信息'''
    return f"{location} 的天气是晴天，25度"

@mcp.tool()
def get_time() -> str:
    '''获取当前时间'''
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 运行服务器
if __name__ == "__main__":
    mcp.run(transport="sse")  # 或 "stdio"

这样就创建了一个包含2个工具的 MCP 服务器！
"""

# ============================================
# 代码示例：在 LiveKit 中使用 MCP
# ============================================

"""
在 LiveKit Agent 中使用 MCP（agent.py）：

from livekit.agents import Agent, AgentSession, mcp

# 1. 创建 MCP 服务器连接
mcp_server = mcp.MCPServerHTTP(
    url="http://localhost:8000/sse",  # MCP 服务器地址
)

# 2. 创建 MCPToolset
mcp_toolset = mcp.MCPToolset(
    id="my_tools",
    mcp_server=mcp_server,
)

# 3. 在 AgentSession 中使用
session = AgentSession(
    stt=...,
    llm=...,
    tts=...,
    tools=[mcp_toolset],  # 添加 MCP 工具！
)

# Agent 现在可以使用 MCP 服务器提供的工具了！
"""

# ============================================
# 面试高频问答
# ============================================

"""
面试问题：

问题1：MCP 是什么？
回答：
  Model Context Protocol - AI 工具的标准化协议。
  就像硬件的 USB 接口，MCP 是 AI 工具的统一接口。
  让 Agent 能够标准化地连接外部服务。

问题2：MCP 和 @function_tool 的区别？
回答：
  @function_tool：工具定义在 Agent 代码内部
  MCP：工具来自外部服务器，可跨 Agent 共享

问题3：MCP 传输类型有哪些？
回答：
  SSE (Server-Sent Events)：HTTP 方式，较旧
  Streamable HTTP：新标准，推荐使用
  Stdio：本地进程方式，用于 CLI 工具如文件系统

问题4：如何创建 MCP Server？
回答：
  使用 FastMCP：
  from mcp.server.fastmcp import FastMCP
  mcp = FastMCP("名称")
  @mcp.tool()
  def my_tool(param): return result
  mcp.run(transport="sse")

问题5：如何在 LiveKit 中使用 MCP？
回答：
  mcp_server = mcp.MCPServerHTTP(url="...")
  toolset = mcp.MCPToolset(id="...", mcp_server=mcp_server)
  AgentSession(tools=[toolset])

问题6：MCPToolset 和 MCPServer 的区别？
回答：
  MCPServer：与 MCP 服务的连接（HTTP 或 Stdio）
  MCPToolset：包装器，将工具暴露给 Agent
"""

if __name__ == "__main__":
    print("阶段4：MCP 基础概念")
    print("=" * 50)
    print("\nMCP = Model Context Protocol")
    print("AI 工具的标准化协议")
    print("\n运行以下命令学习 MCP：")
    print("  python 02_mcp_server.py    # 创建 MCP 服务器")
    print("  python 03_mcp_agent.py     # 在 Agent 中使用 MCP")