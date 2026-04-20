"""
阶段1：LangGraph 快速上手
================================

知识点：
1. StateGraph（状态图）- LangGraph 的核心概念
2. Node（节点）- 状态图中的处理单元
3. Edge（边）- 节点间的流转逻辑
4. CompiledGraph（编译后的图）- 可执行的 Agent

面试高频考点：
- LangGraph vs LangChain 的区别
- StateGraph 是什么？为什么需要？
- Agent 的核心公式
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# ============================================
# 知识点1：定义状态（State）
# ============================================
# 状态是 Agent 运行时的数据容器，所有节点共享这个状态
# TypedDict 定义状态结构，Annotated 用于特殊操作（如消息累加）

class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[list[BaseMessage], add_messages]  # 消息历史（自动累加）
    next_action: str  # 下一步动作：think/act/end
    thinking: str  # 当前思考内容


# ============================================
# 知识点2：定义节点（Node）
# ============================================
# 每个节点是一个函数，接收状态，返回状态更新
# 节点名很重要，会在图中使用

def think_node(state: AgentState) -> dict:
    """
    思考节点：分析当前状态，决定下一步
    """
    print(f"[Think] 分析消息数量: {len(state['messages'])}")

    # 模拟思考过程
    last_message = state["messages"][-1] if state["messages"] else None

    if last_message and "done" in last_message.content.lower():
        return {"next_action": "end", "thinking": "用户表示完成，结束对话"}

    return {"next_action": "act", "thinking": "继续处理用户请求"}


def act_node(state: AgentState) -> dict:
    """
    执行节点：基于思考结果执行动作
    """
    print(f"[Act] 执行动作，思考内容: {state['thinking']}")

    # 模拟执行并生成回复
    last_user_msg = state["messages"][-1].content if state["messages"] else "hello"
    response = f"收到您的消息: '{last_user_msg}'，正在处理中..."

    return {"messages": [AIMessage(content=response)]}


def observe_node(state: AgentState) -> dict:
    """
    观察节点：检查执行结果，准备下一轮思考
    """
    print(f"[Observe] 观察执行结果")
    return {"next_action": "think"}  # 默认返回思考节点


# ============================================
# 知识点3：创建状态图（StateGraph）
# ============================================
# StateGraph 是 Agent 的骨架，定义了节点和边的拓扑结构

def create_simple_graph():
    """
    创建最简单的 StateGraph

    🔥🔥🔥 面试常考：StateGraph 结构
    """
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("observe", observe_node)

    # 添加边（流转逻辑）
    graph.add_edge(START, "think")  # 入口点
    graph.add_edge("think", "act")  # think -> act
    graph.add_edge("act", "observe")  # act -> observe

    # 设置结束条件
    graph.add_conditional_edges(
        "observe",
        lambda state: state["next_action"],  # 条件函数
        {
            "think": "think",  # 继续循环
            "end": END,  # 结束
        }
    )

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_example():
    """
    运行第一个 LangGraph Agent
    """
    app = create_simple_graph()

    # 初始状态
    initial_state = {
        "messages": [HumanMessage(content="你好，请帮我分析一下")],
        "next_action": "think",
        "thinking": "",
    }

    # 执行图
    print("\n" + "="*50)
    print("开始执行 LangGraph Agent")
    print("="*50 + "\n")

    result = app.invoke(initial_state)

    print("\n" + "="*50)
    print("执行结果")
    print("="*50)
    print(f"消息历史: {len(result['messages'])} 条")
    for msg in result["messages"]:
        print(f"  - {msg.type}: {msg.content[:50]}...")
    print(f"最终状态: {result['next_action']}")

    return result


if __name__ == "__main__":
    run_example()