"""
阶段1：条件边（Conditional Edges）
================================

知识点：
1. 条件边 - 根据状态动态决定流转路径
2. 路径映射 - 条件结果到目标节点的映射
3. 循环与退出 - Agent 的核心控制机制

🔥🔥🔥 面试高频：如何实现条件边？
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END, START

# 定义动作类型（Literal 用于类型安全）
ActionType = Literal["search", "calculate", "respond", "end"]


class AgentState(TypedDict):
    """带动作类型的 Agent 状态"""
    user_input: str
    action: ActionType
    result: str
    history: list[str]


# ============================================
# 路由节点：决定下一步动作
# ============================================

def route_node(state: AgentState) -> dict:
    """
    路由节点：分析用户输入，决定执行什么动作
    """
    input_text = state["user_input"].lower()

    # 简单的关键词匹配路由
    if "搜索" in input_text or "查找" in input_text:
        return {"action": "search"}
    elif "计算" in input_text or "算" in input_text:
        return {"action": "calculate"}
    elif "结束" in input_text or "bye" in input_text:
        return {"action": "end"}
    else:
        return {"action": "respond"}


# ============================================
# 动作节点
# ============================================

def search_node(state: AgentState) -> dict:
    """搜索节点"""
    result = f"搜索结果: 找到了关于 '{state['user_input']}' 的相关信息"
    return {
        "result": result,
        "history": state["history"] + [result],
        "action": "respond",  # 搜索后需要响应
    }


def calculate_node(state: AgentState) -> dict:
    """计算节点"""
    # 提取数字进行简单计算
    result = f"计算结果: 已处理 '{state['user_input']}' 的计算请求"
    return {
        "result": result,
        "history": state["history"] + [result],
        "action": "respond",
    }


def respond_node(state: AgentState) -> dict:
    """响应节点：生成最终回复"""
    if state["result"]:
        response = f"回答: {state['result']}"
    else:
        response = f"回答: 我理解了您的请求 '{state['user_input']}'"

    return {
        "result": response,
        "history": state["history"] + [response],
        "action": "end",  # 响应后结束一轮对话
    }


# ============================================
# 🔥🔥🔥 条件边定义
# ============================================

def should_continue(state: AgentState) -> ActionType:
    """
    条件函数：返回下一步动作类型

    🔥🔥🔥 面试常考：条件边的判断函数
    返回值会映射到对应的节点路径
    """
    return state["action"]


def create_conditional_graph():
    """
    创建带条件边的 StateGraph
    """
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("route", route_node)
    graph.add_node("search", search_node)
    graph.add_node("calculate", calculate_node)
    graph.add_node("respond", respond_node)

    # 🔥🔥🔥🔥🔥 面试最高频：条件边语法
    # add_conditional_edges(源节点, 条件函数, 路径映射)
    graph.add_conditional_edges(
        START,
        should_continue,
        {
            "search": "search",
            "calculate": "calculate",
            "respond": "respond",
            "end": END,
        }
    )

    # 动作节点到响应节点
    graph.add_edge("search", "respond")
    graph.add_edge("calculate", "respond")

    # 响应节点的条件边
    graph.add_conditional_edges(
        "respond",
        should_continue,
        {
            "search": "search",
            "calculate": "calculate",
            "respond": "respond",
            "end": END,
        }
    )

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_examples():
    """运行多个示例展示条件边"""
    app = create_conditional_graph()

    test_inputs = [
        "帮我搜索一下天气",
        "计算一下 123 + 456",
        "你好，随便聊聊",
        "结束对话",
    ]

    print("\n" + "="*60)
    print("条件边示例运行")
    print("="*60 + "\n")

    for input_text in test_inputs:
        print(f"\n>>> 用户输入: {input_text}")

        initial_state = {
            "user_input": input_text,
            "action": "respond",  # 初始动作
            "result": "",
            "history": [],
        }

        result = app.invoke(initial_state)

        print(f"最终结果: {result['result']}")
        print(f"历史记录: {len(result['history'])} 步")


if __name__ == "__main__":
    run_examples()