"""
阶段2：工具调用（Function Calling / Tools）
================================

知识点：
1. @tool 装饰器 - LangChain 工具定义方式
2. ToolExecutor - 工具执行器
3. 工具调用流程 - LLM 决定调用什么工具
4. ToolNode - LangGraph 中的工具节点

🔥🔥🔥🔥🔥 面试高频：如何实现工具调用？
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool


# ============================================
# 🔥🔥🔥🔥🔥 工具定义（@tool 装饰器）
# ============================================

@tool
def search_weather(location: str) -> str:
    """
    🔥🔥🔥 搜索天气工具

    Args:
        location: 地点名称，如"北京"、"上海"

    面试要点：
    - @tool 装饰器自动处理参数解析
    - docstring 会被 LLM 理解（决定何时调用）
    - 返回字符串（实际调用结果）
    """
    # 模拟天气数据
    weather_data = {
        "北京": "晴，25°C，空气质量良好",
        "上海": "多云，22°C，有轻微雾霾",
        "广州": "小雨，28°C，湿度较高",
    }
    return weather_data.get(location, f"{location}天气数据暂无，建议查询其他城市")


@tool
def calculate(expression: str) -> str:
    """
    🔥🔥🔥 计算工具

    Args:
        expression: 数学表达式，如"1+2*3"

    面试要点：
    - 工具参数要清晰定义
    - 返回格式要一致（字符串）
    """
    try:
        # 安全计算（实际生产要用更安全的方案）
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool
def search_info(query: str) -> str:
    """
    🔥🔥🔥 搜索信息工具

    Args:
        query: 搜索关键词
    """
    # 模拟搜索结果
    return f"搜索 '{query}' 的结果：找到了 3 条相关信息"


# 工具列表
TOOLS = [search_weather, calculate, search_info]


# ============================================
# 状态定义
# ============================================

class ToolAgentState(TypedDict):
    """带工具调用的 Agent 状态"""
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================
# 🔥🔥🔥🔥🔥 模拟 LLM 决策节点
# ============================================

def llm_node(state: ToolAgentState) -> dict:
    """
    🔥🔥🔥 LLM 决策节点：决定是否调用工具

    面试要点：
    - LLM 分析用户输入
    - LLM 决定调用哪个工具
    - 返回 AIMessage 包含 tool_calls
    """
    last_message = state["messages"][-1].content if state["messages"] else ""

    print(f"\n[LLM Node] 分析用户输入: {last_message}")

    # 🔥🔥🔥 模拟 LLM 的工具调用决策
    # 实际会用 ChatOpenAI().bind_tools(TOOLS)

    if "天气" in last_message:
        # 决定调用天气工具
        location = last_message.replace("天气", "").strip() or "北京"
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "search_weather",
                "args": {"location": location},
                "id": "call_1",
            }]
        )
        print(f"  决定调用工具: search_weather({location})")
        return {"messages": [ai_msg]}

    elif any(op in last_message for op in ["+", "-", "*", "/"]):
        # 决定调用计算工具
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "calculate",
                "args": {"expression": last_message},
                "id": "call_2",
            }]
        )
        print(f"  决定调用工具: calculate({last_message})")
        return {"messages": [ai_msg]}

    elif "搜索" in last_message or "查" in last_message:
        # 决定调用搜索工具
        query = last_message.replace("搜索", "").replace("查", "").strip()
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "search_info",
                "args": {"query": query},
                "id": "call_3",
            }]
        )
        print(f"  决定调用工具: search_info({query})")
        return {"messages": [ai_msg]}

    else:
        # 直接回复
        ai_msg = AIMessage(content=f"我理解了你的请求：{last_message}。需要我帮你做什么？")
        print(f"  直接回复")
        return {"messages": [ai_msg]}


# ============================================
# 🔥🔥🔥🔥🔥 工具执行节点
# ============================================

def tool_executor_node(state: ToolAgentState) -> dict:
    """
    🔥🔥🔥🔥🔥 工具执行节点：执行 LLM 决定的工具调用

    面试要点：
    - 从 AIMessage.tool_calls 获取调用信息
    - 执行对应工具
    - 返回 ToolMessage 包含执行结果
    """
    last_ai_message = state["messages"][-1]

    if not isinstance(last_ai_message, AIMessage):
        return {}

    tool_calls = last_ai_message.tool_calls
    if not tool_calls:
        return {}

    tool_messages = []

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        print(f"\n[Tool Node] 执行 {tool_name}({tool_args})")

        # 查找并执行工具
        tool_func = None
        for t in TOOLS:
            if t.name == tool_name:
                tool_func = t
                break

        if tool_func:
            # 执行工具
            result = tool_func.invoke(tool_args)
            print(f"  结果: {result}")

            # 🔥🔥🔥🔥🔥 返回 ToolMessage
            tool_msg = ToolMessage(
                content=result,
                tool_call_id=tool_id,
            )
            tool_messages.append(tool_msg)
        else:
            tool_msg = ToolMessage(
                content=f"错误: 未找到工具 {tool_name}",
                tool_call_id=tool_id,
            )
            tool_messages.append(tool_msg)

    return {"messages": tool_messages}


# ============================================
# 条件函数
# ============================================

def should_call_tools(state: ToolAgentState) -> str:
    """
    🔥🔥🔥 条件函数：判断是否需要调用工具

    面试要点：
    - 检查最后一条消息是否包含 tool_calls
    - 有 tool_calls 就去执行工具
    - 没有 tool_calls 就直接结束
    """
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


# ============================================
# 🔥🔥🔥🔥🔥 创建带工具的 Graph
# ============================================

def create_tool_graph():
    """
    🔥🔥🔥🔥🔥 面试必问：LangGraph 工具调用流程

    流程：
    1. 用户输入 -> LLM 节点
    2. LLM 决定是否调用工具
    3. 如果需要 -> 工具执行节点
    4. 工具结果返回 LLM
    5. LLM 生成最终回复
    """
    graph = StateGraph(ToolAgentState)

    # 添加节点
    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_executor_node)

    # 添加边
    graph.add_edge(START, "llm")

    # 🔥🔥🔥🔥🔥 条件边：是否调用工具
    graph.add_conditional_edges(
        "llm",
        should_call_tools,
        {
            "tools": "tools",  # 有工具调用 -> 执行工具
            "end": END,        # 无工具调用 -> 结束
        }
    )

    # 🔥🔥🔥🔥🔥 工具执行后返回 LLM（重要！）
    graph.add_edge("tools", "llm")

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_tool_agent():
    """运行工具调用 Agent"""
    app = create_tool_graph()

    test_queries = [
        "北京天气怎么样？",
        "计算 2+3*4",
        "搜索 LangGraph 相关信息",
        "你好，随便聊聊",  # 无工具调用
    ]

    print("\n" + "="*60)
    print("🔥🔥🔥🔥🔥 工具调用 Agent 示例")
    print("="*60)

    for query in test_queries:
        print(f"\n{'='*40}")
        print(f"用户输入: {query}")
        print("="*40)

        initial_state = {
            "messages": [HumanMessage(content=query)],
        }

        result = app.invoke(initial_state)

        print(f"\n>>> 对话历史:")
        for msg in result["messages"]:
            print(f"  [{msg.type}] {msg.content[:80] if msg.content else '(tool call)'}")


# ============================================
# 面试要点总结
# ============================================

"""
🔥🔥🔥🔥🔥 工具调用面试要点：

Q: LangChain 工具怎么定义？
A: 使用 @tool 装饰器，参数和 docstring 会被 LLM 理解

Q: 工具调用的完整流程？
A:
1. LLM 分析用户输入
2. LLM 返回 AIMessage 包含 tool_calls
3. 执行对应工具
4. 返回 ToolMessage 包含结果
5. LLM 收到 ToolMessage，生成最终回复

Q: ToolMessage 和 AIMessage 的区别？
A:
- AIMessage: LLM 生成的内容，可能包含 tool_calls
- ToolMessage: 工具执行的结果，包含 tool_call_id

Q: LangGraph 中的 ToolNode？
A:
- 预置的工具执行节点
- 自动处理 tool_calls
- 返回 ToolMessage
"""


if __name__ == "__main__":
    run_tool_agent()