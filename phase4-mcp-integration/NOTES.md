# 阶段4学习笔记：MCP (Model Context Protocol) 集成

## 核心概念

### 1. MCP 是什么？

MCP = Model Context Protocol（模型上下文协议）

- AI 工具的标准化协议
- 可以理解为"AI 工具的 USB 接口" - 插上就能用
- 工具服务与 Agent 分离
- 一个 MCP 服务器可以被多个 Agent 使用

### 2. MCP 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client（Agent端）                      │
│  AgentSession                                                │
│    └── MCPToolset                                            │
│         └── MCPServerHTTP / MCPServerStdio                   │
└─────────────────────────────────────────────────────────────┘
                        ↓ SSE 或 Stdio
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server（服务端）                       │
│  FastMCP                                                     │
│    @mcp.tool()                                               │
│    def get_weather(location): ...                            │
└─────────────────────────────────────────────────────────────┘
```

---

## MCP vs @function_tool 对比

| 方面 | @function_tool | MCP |
|------|----------------|-----|
| 位置 | Agent 代码内部 | 外部服务器 |
| 共享 | 单个 Agent 使用 | 多 Agent 共享 |
| 部署 | 和 Agent 一起 | 独立部署 |
| 更新 | 重启 Agent | 热更新工具 |
| 示例 | 简单工具 | 复杂服务 |

### 详细代码对比

#### @function_tool 方式（工具在 Agent 内部）

```python
# 所有工具都定义在 Agent 文件中
from livekit.agents import Agent
from livekit.agents.llm import function_tool

class VoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="你是助手",
            tools=[],  # 工具在这里定义
        )

    # 工具1：定义在 Agent 类内部
    @function_tool
    async def get_weather(self, context, location: str) -> str:
        '''获取天气'''
        return f"{location} 晴天，25度"

    # 工具2：也在 Agent 内部
    @function_tool
    async def get_time(self, context) -> str:
        '''获取时间'''
        return "2026-04-21 12:00:00"

# 问题：
# - 如果另一个 Agent 也需要天气工具，必须重复定义
# - 修改工具需要重启整个 Agent
# - 工具和 Agent 紧耦合
```

#### MCP 方式（工具在独立服务器）

```python
# 文件1：mcp_server.py（独立运行的服务器）
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("工具服务器")

@mcp.tool()
def get_weather(location: str) -> str:
    '''获取天气'''
    return f"{location} 晴天，25度"

@mcp.tool()
def get_time() -> str:
    '''获取时间'''
    return "2026-04-21 12:00:00"

# 运行：python mcp_server.py
# 服务器独立运行在 http://localhost:8000/sse


# 文件2：agent1.py（Agent A 使用这些工具）
session = AgentSession(
    tools=[MCPToolset(mcp_server=MCPServerHTTP(url="http://localhost:8000/sse"))]
)


# 文件3：agent2.py（Agent B 也使用同样的工具）
session = AgentSession(
    tools=[MCPToolset(mcp_server=MCPServerHTTP(url="http://localhost:8000/sse"))]
)

# 优点：
# - 多个 Agent 共享同一套工具，无需重复代码
# - 修改工具只需重启 MCP 服务器，Agent 不受影响
# - 工具和 Agent 解耦
```

#### 使用场景对比

| 场景 | @function_tool | MCP |
|------|----------------|-----|
| 单个 Agent | ✅ 简单直接 | 略复杂 |
| 多个 Agent 共享工具 | ❌ 需要重复代码 | ✅ 共享服务器 |
| 工具频繁更新 | ❌ 重启 Agent | ✅ 只重启服务器 |
| 工具来自第三方 | ❌ 需要自己实现 | ✅ 直接连接（如 Zapier） |

---

## LiveKit MCP 核心类

| 类 | 作用 |
|---|------|
| `MCPServer` | 基类（抽象类） |
| `MCPServerHTTP` | HTTP/SSE 连接 |
| `MCPServerStdio` | Stdio（本地进程）连接 |
| `MCPToolset` | 工具集包装器，用于 Agent |

---

## 创建 MCP Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("我的工具")

@mcp.tool()
def get_weather(location: str) -> str:
    '''获取某地天气'''
    return f"{location} 天气晴朗，25度"

if __name__ == "__main__":
    mcp.run(transport="sse")
```

---

## 在 LiveKit 中使用 MCP

```python
from livekit.agents import mcp

# 1. 创建 MCP 服务器连接
mcp_server = mcp.MCPServerHTTP(
    url="http://localhost:8000/sse",
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
    tools=[mcp_toolset],
)
```

---

## 传输类型

| 传输方式 | 说明 | 适用场景 |
|----------|------|----------|
| SSE | Server-Sent Events | Web 服务器 |
| Streamable HTTP | 新标准 | 推荐 |
| Stdio | 标准 I/O | CLI 工具 |

---

## 面试高频问答

### 问题1：MCP 是什么？

> Model Context Protocol - AI 工具的标准化协议。
> 就像硬件的 USB 接口，MCP 是 AI 工具的统一接口。
> 让 Agent 能够标准化地连接外部服务。

### 问题2：MCP 和 @function_tool 的区别？

> @function_tool：工具在 Agent 代码内部，单 Agent 使用
> MCP：工具来自外部服务器，可跨 Agent 共享

### 问题3：MCPToolset 和 MCPServer 的区别？

> MCPServer：与 MCP 服务的连接
> MCPToolset：包装器，将工具暴露给 Agent

### 问题4：如何过滤工具？

> `MCPServerHTTP(url="...", allowed_tools=["get_weather"])`

### 问题5：可以使用多个 MCP 服务器吗？

> 可以，添加多个 MCPToolset：
> ```python
> tools=[
>     MCPToolset(id="s1", mcp_server=MCPServerHTTP(url1)),
>     MCPToolset(id="s2", mcp_server=MCPServerHTTP(url2)),
> ]
> ```

---

## 阶段4 文件结构

```
phase4-mcp-integration/
├── 01_mcp_basics.py      # MCP 基础概念
├── 02_mcp_server.py      # 创建 MCP Server
├── 03_mcp_agent.py       # MCP + LiveKit Agent
├── NOTES.md              # 本笔记
└── .env                  # API keys（从阶段3复制）
```

---

## 运行方法

```bash
# 步骤1：启动 MCP Server
python 02_mcp_server.py

# 步骤2：运行 Agent（另一个终端）
python 03_mcp_agent.py console

# 测试：
# - "北京天气怎么样？"
# - "现在几点了？"
# - "计算 123 + 456"
```

---

## 真实世界的 MCP 服务器

| 服务器 | 提供的工具 |
|--------|-----------|
| Zapier MCP | 6000+ 应用集成 |
| Filesystem MCP | 读写文件 |
| GitHub MCP | 仓库操作 |
| Slack MCP | 发送消息 |

---

## 源码对照

| 知识点 | 源码位置 |
|--------|----------|
| MCP 核心 | `livekit/agents/llm/mcp.py` |
| MCP Agent 示例 | `examples/voice_agents/mcp/mcp-agent.py` |
| MCP Server 示例 | `examples/voice_agents/mcp/server.py` |
| Zapier 集成 | `examples/voice_agents/zapier_mcp_integration.py` |

---

## 前置条件

```bash
pip install mcp
pip install 'livekit-agents[mcp]'
pip install livekit-plugins-silero
```