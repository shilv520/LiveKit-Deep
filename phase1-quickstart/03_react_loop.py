"""
阶段1：ReAct 循环图
================================

知识点：
1. ReAct 模式 - Reasoning + Acting 的经典 Agent 模式
2. 循环结构 - think -> act -> observe -> think 循环
3. 工具调用 - Agent 执行外部动作的能力

🔥🔥🔥 面试高频：ReAct Agent 的核心流程
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# ReAct 状态定义
class ReActState(TypedDict):
    """ReAct Agent 状态"""
    messages: Annotated[list[BaseMessage], add_messages]
    thought: str  # 当前思考
    action: str  # 当前动作
    action_input: str  # 动作输入
    observation: str  # 观察结果
    iteration: int  # 迭代次数
    max_iterations: int  # 最大迭代次数


# ============================================
# 模拟工具
# ============================================

TOOLS = {
    "search": lambda q: f"搜索结果: 关于 '{q}' 找到了 3 条相关信息",
    "calculate": lambda q: f"计算结果: {q} = 42",
    "weather": lambda q: f"天气结果: {q} 今天晴朗，温度 25°C",
}


# ============================================
# ReAct 节点定义
# ============================================

def think_node(state: ReActState) -> dict:
    """
    🔥🔥🔥 思考节点：分析问题，规划下一步

    ReAct 核心公式：
    Thought: 我需要...
    Action: [工具名]
    Action Input: [工具输入]
    """
    iteration = state["iteration"] + 1
    last_msg = state["messages"][-1].content if state["messages"] else ""

    # 简单的思考逻辑（实际会用 LLM）
    if "天气" in last_msg:
        thought = "用户想知道天气，我需要调用天气工具"
        action = "weather"
        action_input = last_msg.replace("天气", "").strip() or "北京"
    elif "搜索" in last_msg:
        thought = "用户需要搜索信息"
        action = "search"
        action_input = last_msg
    elif "计算" in last_msg:
        thought = "用户需要计算"
        action = "calculate"
        action_input = last_msg
    else:
        thought = "我可以直接回答用户"
        action = "respond"
        action_input = last_msg

    print(f"\n[第{iteration}轮思考]")
    print(f"  Thought: {thought}")
    print(f"  Action: {action}")
    print(f"  Action Input: {action_input}")

    return {
        "thought": thought,
        "action": action,
        "action_input": action_input,
        "iteration": iteration,
    }


def act_node(state: ReActState) -> dict:
    """
    🔥🔥🔥 执行节点：调用工具执行动作
    """
    action = state["action"]
    action_input = state["action_input"]

    if action in TOOLS:
        observation = TOOLS[action](action_input)
    elif action == "respond":
        observation = f"直接回复: {action_input}"
    else:
        observation = f"错误: 未知动作 {action}"

    print(f"  Observation: {observation}")

    return {"observation": observation}


def observe_node(state: ReActState) -> dict:
    """
    🔥🔥🔥 观察节点：分析执行结果，决定是否继续

    Observation -> 新 Thought 循环
    """
    # 将观察结果加入消息
    observation_msg = AIMessage(content=f"Observation: {state['observation']}")

    # 检查是否达到最大迭代
    if state["iteration"] >= state["max_iterations"]:
        return {
            "messages": [observation_msg],
            "action": "finish",
        }

    # 检查是否已经得到答案
    if state["observation"] and "结果" in state["observation"]:
        return {
            "messages": [observation_msg],
            "action": "finish",
        }

    return {
        "messages": [observation_msg],
        "action": "continue",
    }


def finish_node(state: ReActState) -> dict:
    """结束节点：生成最终回复"""
    final_response = f"最终回答: 根据分析，{state['observation']}"
    return {
        "messages": [AIMessage(content=final_response)],
    }


# ============================================
# 🔥🔥🔥🔥🔥 ReAct 条件路由
# ============================================

def should_continue(state: ReActState) -> str:
    """
    条件函数：决定下一步路径
    """
    if state["action"] == "finish":
        return "finish"
    elif state["action"] == "respond":
        return "respond"
    return "continue"


def create_react_graph():
    """
    🔥🔥🔥🔥🔥 创建 ReAct 循环图

    面试常考：ReAct 的 think-act-observe 循环
    """
    graph = StateGraph(ReActState)

    # 添加节点
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("observe", observe_node)
    graph.add_node("finish", finish_node)

    # 定义边
    graph.add_edge(START, "think")
    graph.add_edge("think", "act")
    graph.add_edge("act", "observe")

    # 🔥🔥🔥 条件边：观察后的决策
    graph.add_conditional_edges(
        "observe",
        should_continue,
        {
            "continue": "think",  # 🔥🔥🔥 循环回到思考
            "respond": "finish",
            "finish": "finish",
        }
    )

    graph.add_edge("finish", END)

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_react():
    """运行 ReAct Agent"""
    app = create_react_graph()

    test_queries = [
        "北京天气怎么样？",
        "帮我搜索一下 LangGraph",
    ]

    print("\n" + "="*60)
    print("🔥🔥🔥 ReAct Agent 示例")
    print("="*60)

    for query in test_queries:
        print(f"\n{'='*40}")
        print(f"用户提问: {query}")
        print("="*40)

        initial_state = {
            "messages": [HumanMessage(content=query)],
            "thought": "",
            "action": "",
            "action_input": "",
            "observation": "",
            "iteration": 0,
            "max_iterations": 5,
        }

        result = app.invoke(initial_state)

        print(f"\n>>> 最终回复:")
        for msg in result["messages"]:
            if msg.type == "ai":
                print(f"  {msg.content}")

        print(f"\n总迭代次数: {result['iteration']}")


if __name__ == "__main__":
    run_react()