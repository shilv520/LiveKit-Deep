"""
阶段4：使用 FastMCP 创建 MCP Server
================================

核心知识点：
1. FastMCP - 快速创建 MCP 服务器
2. @mcp.tool() - 定义工具
3. @mcp.resource() - 定义资源
4. 传输模式 - SSE vs Stdio

本文件创建一个独立的 MCP 服务器，提供多种工具。

参考源码：livekit-agents/examples/voice_agents/mcp/server.py

前置条件：
pip install mcp

先运行本服务器，然后运行 03_mcp_agent.py 连接使用。
"""

import logging
from datetime import datetime

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[警告] MCP 未安装。请运行: pip install mcp")

logger = logging.getLogger("mcp-server")

# ============================================
# 使用 FastMCP 创建 MCP Server
# ============================================

"""
FastMCP 让创建 MCP 服务器变得简单：

1. 创建 FastMCP 实例
2. 用 @mcp.tool() 定义工具
3. 用 mcp.run(transport="sse") 运行服务器

LLM 会从函数的 docstring 理解工具描述！
"""

mcp = FastMCP("演示工具服务器")


# ============================================
# 定义 MCP 工具
# ============================================

@mcp.tool()
def get_weather(location: str) -> str:
    """
    获取某地的天气信息。

    参数：
        location: 城市名称（如 "北京"、"上海"）

    返回：
        天气描述字符串
    """
    logger.info(f"MCP 工具调用: get_weather({location})")

    # 模拟天气数据
    weather_data = {
        "北京": "晴天，25度，湿度40%",
        "上海": "多云，22度，湿度60%",
        "广州": "雨天，28度，湿度80%",
        "纽约": "晴朗，18度，湿度35%",
        "东京": "部分多云，20度，湿度50%",
    }

    return weather_data.get(location, f"没有 {location} 的天气数据。可用城市：北京、上海、广州")


@mcp.tool()
def get_time() -> str:
    """
    获取当前日期和时间。

    返回：
        当前时间字符串，格式：YYYY-MM-DD HH:MM:SS
    """
    logger.info("MCP 工具调用: get_time()")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间: {now}"


@mcp.tool()
def calculate(expression: str) -> str:
    """
    计算数学表达式。

    参数：
        expression: 数学表达式（如 "2+3*4"、"100/5"）

    返回：
        计算结果
    """
    logger.info(f"MCP 工具调用: calculate({expression})")

    try:
        # 安全计算（只允许基本数学运算）
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "错误：只允许基本数学运算"

        result = eval(expression)
        return f"结果: {result}"
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def search_knowledge(topic: str) -> str:
    """
    在知识库中搜索信息。

    参数：
        topic: 要搜索的主题（如 "Python"、"AI"）

    返回：
        知识信息
    """
    logger.info(f"MCP 工具调用: search_knowledge({topic})")

    # 模拟知识库
    knowledge = {
        "Python": "Python 是 Guido van Rossum 于 1991 年创建的编程语言。",
        "AI": "人工智能是机器模拟人类智能的技术。",
        "MCP": "Model Context Protocol 是 AI 工具的标准化协议。",
        "LiveKit": "LiveKit 是实时音视频应用的平台。",
    }

    return knowledge.get(topic, f"没有 '{topic}' 的信息。可用主题：Python、AI、MCP、LiveKit")


# ============================================
# 定义 MCP 资源（可选）
# ============================================

@mcp.resource("config://settings")
def get_config() -> str:
    """
    获取服务器配置作为资源。

    资源和工具不同 - 资源提供数据，不执行动作。
    """
    return """{
        "server_name": "演示工具服务器",
        "version": "1.0",
        "tools": ["get_weather", "get_time", "calculate", "search_knowledge"]
    }"""


# ============================================
# 面试高频问答
# ============================================

"""
MCP Server 面试问题：

问题1：如何创建 MCP 工具？
回答：
  @mcp.tool()
  def my_tool(param: str) -> str:
      '''工具描述（LLM 会读取这个！）'''
      return "结果"

问题2：@mcp.tool() 和 @mcp.resource() 的区别？
回答：
  tool：执行动作，接收参数，返回结果
  resource：数据提供者，只读，类似文件或配置

问题3：有哪些传输模式？
回答：
  SSE (Server-Sent Events)：HTTP 方式，用于 Web 服务器
  Stdio：标准输入输出，用于 CLI 工具

问题4：LLM 如何知道工具参数？
回答：
  从 Python 类型注解和 docstring 自动生成！
  FastMCP 自动创建 JSON schema。

问题5：MCP 服务器可以独立运行吗？
回答：
  可以！MCP 服务器是独立进程。
  多个 Agent 可以连接同一个服务器。

问题6：如何在 MCPToolset 中过滤工具？
回答：
  MCPServerHTTP(url="...", allowed_tools=["get_weather", "get_time"])
  只允许指定的工具被 Agent 使用。
"""

# ============================================
# 运行 MCP Server
# ============================================

"""
运行本 MCP 服务器的方法：

方法1：SSE 传输（HTTP 方式）
─────────────────────────────────────
python 02_mcp_server.py
（默认在 http://localhost:8000/sse 上运行 SSE）

方法2：Stdio 传输（CLI 方式）
─────────────────────────────────────
python 02_mcp_server.py --transport stdio

然后运行 Agent：
python 03_mcp_agent.py console
"""

if __name__ == "__main__":
    if MCP_AVAILABLE:
        print("=" * 60)
        print("MCP 服务器启动中...")
        print("=" * 60)
        print("\n可用工具：")
        print("  - get_weather(location)  获取天气")
        print("  - get_time()             获取时间")
        print("  - calculate(expression)  计算数学")
        print("  - search_knowledge(topic) 搜索知识")
        print("\n传输方式：SSE (Server-Sent Events)")
        print("地址：http://localhost:8000/sse")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 60)

        # 运行 MCP 服务器，使用 SSE 传输
        mcp.run(transport="sse")
    else:
        print("[错误] 请先安装 MCP: pip install mcp")