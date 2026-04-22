"""
阶段2：多 Agent 协作（Multi-Agent Collaboration）
================================

知识点：
1. 多 Agent 图结构 - 多个节点协同工作
2. Agent 间通信 - 通过共享状态传递信息
3. 协作模式 - 串行、并行、层级协作
4. Agent Handoff - Agent 切换机制

🔥🔥🔥🔥🔥 面试高频：如何实现多 Agent 协作？
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


# ============================================
# 🔥🔥🔥🔥🔥 多 Agent 状态定义
# ============================================

class MultiAgentState(TypedDict):
    """多 Agent 协作状态"""
    messages: Annotated[list[BaseMessage], add_messages]
    # 🔥🔥🔥🔥🔥 关键：共享状态实现 Agent 间通信
    research_result: str  # 研究结果
    critique_feedback: str  # 批评反馈
    final_output: str  # 最终输出
    current_agent: str  # 当前活跃 Agent
    iteration: int  # 迭代次数
    approved: bool  # 是否通过审核


# ============================================
# 🔥🔥🔥🔥🔥 Agent 节点定义
# ============================================

def researcher_node(state: MultiAgentState) -> dict:
    """
    🔥🔥🔥 研究员 Agent：收集和整理信息

    面试要点：
    - 每个 Agent 有独立的职责
    - 通过状态字段传递工作结果
    """
    print(f"\n[Researcher Agent] 正在研究...")

    last_msg = state["messages"][-1].content if state["messages"] else ""

    # 模拟研究过程
    research_result = f"关于 '{last_msg}' 的研究结果："
    research_result += "\n1. 基础概念已梳理"
    research_result += "\n2. 关键要点已提取"
    research_result += "\n3. 相关资料已收集"

    return {
        "research_result": research_result,
        "current_agent": "researcher",
        "messages": [AIMessage(content=f"[Researcher] 研究完成：\n{research_result}")],
    }


def critic_node(state: MultiAgentState) -> dict:
    """
    🔥🔥🔥🔥🔥 批评家 Agent：审核和改进建议

    面试要点：
    - 接收上游 Agent 的输出
    - 提供反馈和改进建议
    """
    print(f"\n[Critic Agent] 正在审核...")

    iteration = state["iteration"] + 1

    # 模拟批评过程
    research = state["research_result"]

    # 前2轮提出改进建议，第3轮批准
    if iteration < 3:
        critique = f"审核反馈（第{iteration}轮）："
        critique += "\n- 需要更深入的细节"
        critique += "\n- 建议补充实例说明"
        approved = False
    else:
        critique = "审核通过！内容已完善"
        approved = True

    return {
        "critique_feedback": critique,
        "current_agent": "critic",
        "iteration": iteration,
        "approved": approved,
        "messages": [AIMessage(content=f"[Critic] {critique}")],
    }


def writer_node(state: MultiAgentState) -> dict:
    """
    🔥🔥🔥🔥🔥 写作 Agent：生成最终输出

    面试要点：
    - 整合所有 Agent 的工作
    - 生成最终结果
    """
    print(f"\n[Writer Agent] 正在写作...")

    research = state["research_result"]
    critique = state["critique_feedback"]

    # 整合并生成最终输出
    final_output = f"=== 最终报告 ===\n\n"
    final_output += f"【研究结果】\n{research}\n\n"
    final_output += f"【审核反馈】\n{critique}\n\n"
    final_output += f"【结论】\n经过 {state['iteration']} 轮迭代，已完成最终报告。"

    return {
        "final_output": final_output,
        "current_agent": "writer",
        "messages": [AIMessage(content=final_output)],
    }


# ============================================
# 🔥🔥🔥🔥🔥 条件路由函数
# ============================================

def route_after_research(state: MultiAgentState) -> str:
    """研究后路由：去批评家"""
    return "critic"


def route_after_critique(state: MultiAgentState) -> str:
    """
    🔥🔥🔥🔥🔥 批评后路由：决定是否需要重新研究

    面试要点：
    - 条件边实现 Agent 间循环
    - 审核不通过则返回研究员改进
    """
    if state["approved"]:
        return "writer"  # 通过 -> 写作
    return "researcher"  # 不通过 -> 重新研究


def route_after_writer(state: MultiAgentState) -> str:
    """写作后路由：结束"""
    return "end"


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 创建多 Agent 图
# ============================================

def create_multi_agent_graph():
    """
    🔥🔥🔥🔥🔥🔥🔥🔥🔥 面试最高频：多 Agent 协作图

    流程：
    ┌─────────────────────────────────────────────┐
    │  START                                       │
    │    ↓                                         │
    │  Researcher（研究员）                         │
    │    ↓                                         │
    │  Critic（批评家）                             │
    │    ↓ ←─────────────────┐                    │
    │  通过?                  │ 未通过              │
    │    ↓ 是                 └───────────────────→│
    │  Writer（写作）                              │
    │    ↓                                         │
    │  END                                         │
    └─────────────────────────────────────────────┘

    这种 researcher -> critic -> (循环) -> writer 的模式
    是经典的多 Agent 协作流程！
    """
    graph = StateGraph(MultiAgentState)

    # 🔥🔥🔥🔥🔥 添加多个 Agent 节点
    graph.add_node("researcher", researcher_node)
    graph.add_node("critic", critic_node)
    graph.add_node("writer", writer_node)

    # 定义边
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "critic")

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 条件边：批评后的路由（核心！）
    graph.add_conditional_edges(
        "critic",
        route_after_critique,
        {
            "researcher": "researcher",  # 未通过 -> 回到研究员改进
            "writer": "writer",  # 通过 -> 写作
        }
    )

    graph.add_edge("writer", END)

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_multi_agent():
    """运行多 Agent 协作"""
    app = create_multi_agent_graph()

    print("\n" + "="*60)
    print("🔥🔥🔥🔥🔥🔥🔥🔥🔥 多 Agent 协作示例")
    print("="*60)
    print("\n流程：Researcher → Critic → (循环改进) → Writer")

    initial_state = {
        "messages": [HumanMessage(content="请帮我研究 LangGraph 的核心概念")],
        "research_result": "",
        "critique_feedback": "",
        "final_output": "",
        "current_agent": "",
        "iteration": 0,
        "approved": False,
    }

    result = app.invoke(initial_state)

    print("\n" + "="*60)
    print("执行完成")
    print("="*60)
    print(f"\n总迭代次数: {result['iteration']}")
    print(f"最终通过审核: {result['approved']}")
    print(f"\n【最终输出】")
    print(result["final_output"])


# ============================================
# 🔥🔥🔥🔥🔥 面试要点总结
# ============================================

"""
🔥🔥🔥🔥🔥🔥🔥🔥🔥 多 Agent 协作面试要点：

Q1: 多 Agent 如何通信？
A: 通过共享状态（State）传递信息。每个 Agent 读写状态中的特定字段。

Q2: Agent Handoff（移交）怎么实现？
A:
方式1：条件边路由到不同 Agent（LangGraph 方式）
方式2：工具返回新 Agent 对象（LiveKit 方式）

Q3: 常见的协作模式？
A:
1. 串行协作：Agent1 → Agent2 → Agent3
2. 循环协作：Agent1 → Agent2 → (条件判断) → Agent1/Agent3
3. 层级协作：Manager Agent 分配任务给 Worker Agents
4. 并行协作：多个 Agent 同时处理不同任务

Q4: 多 Agent 的优势？
A:
- 职责分离，每个 Agent 更专注
- 可复用，同一 Agent 可服务多个流程
- 可扩展，新增 Agent 不影响现有结构
"""


if __name__ == "__main__":
    run_multi_agent()