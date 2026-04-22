"""
阶段2：Agent Handoff（Agent 移交/切换）
================================

知识点：
1. Agent Handoff - Agent 间的任务移交机制
2. LiveKit 方式 - 工具返回新 Agent
3. LangGraph 方式 - 条件边路由到不同 Agent
4. 状态继承 - 新 Agent 如何继承上下文

🔥🔥🔥🔥🔥 面试高频：Agent 切换怎么实现？

参考源码：livekit-agents/examples/voice_agents/multi_agent.py
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


# ============================================
# 🔥🔥🔥🔥🔥 Agent Handoff 状态定义
# ============================================

class HandoffState(TypedDict):
    """Agent Handoff 状态"""
    messages: Annotated[list[BaseMessage], add_messages]
    current_agent: str  # 当前活跃的 Agent 名
    user_data: dict  # 用户数据（跨 Agent 共享）
    task_complete: bool  # 任务是否完成


# ============================================
# 🔥🔥🔥🔥🔥 模拟不同的 Agent 类
# ============================================

class AgentInfo:
    """Agent 信息类"""
    def __init__(self, name: str, instructions: str, tools: list = None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []


# 定义不同的 Agent
AGENTS = {
    "greeter": AgentInfo(
        name="greeter",
        instructions="欢迎用户，收集基本信息（姓名、目的）",
    ),
    "assistant": AgentInfo(
        name="assistant",
        instructions="帮助用户解决问题",
    ),
    "surveyor": AgentInfo(
        name="surveyor",
        instructions="收集用户反馈，结束对话",
    ),
}


# ============================================
# 🔥🔥🔥🔥🔥 Agent 节点定义（模拟 LiveKit Handoff）
# ============================================

def greeter_node(state: HandoffState) -> dict:
    """
    🔥🔥🔥🔥🔥 欢迎 Agent：收集基本信息

    LiveKit 方式的 Handoff：
    - Agent 执行任务
    - 通过工具调用触发 Handoff
    - 工具返回新 Agent 对象
    """
    print(f"\n[Greeter Agent] 欢迎用户...")

    # 模拟收集信息
    user_data = {
        "name": "用户A",
        "purpose": "咨询产品",
    }

    msg = AIMessage(content=f"欢迎！我是 Greeter Agent。您的姓名：{user_data['name']}")

    return {
        "messages": [msg],
        "current_agent": "greeter",
        "user_data": user_data,
    }


def assistant_node(state: HandoffState) -> dict:
    """
    🔥🔥🔥🔥🔥 助手 Agent：处理用户请求

    面试要点：
    - 接收 Greeter Agent 收集的用户数据
    - 继承对话历史
    """
    print(f"\n[Assistant Agent] 处理请求...")

    user_data = state["user_data"]
    purpose = user_data.get("purpose", "未知")

    # 模拟处理
    response = f"好的 {user_data.get('name')}, 我来帮您处理：{purpose}"
    user_data["resolved"] = True  # 标记已处理

    return {
        "messages": [AIMessage(content=response)],
        "current_agent": "assistant",
        "user_data": user_data,
    }


def surveyor_node(state: HandoffState) -> dict:
    """
    🔥🔥🔥🔥🔥 调查 Agent：收集反馈并结束

    面试要点：
    - 最后一个 Agent
    - 结束对话
    """
    print(f"\n[Surveyor Agent] 收集反馈...")

    user_data = state["user_data"]

    response = f"感谢您的使用！请对本次服务评分（1-5星）"
    user_data["feedback_requested"] = True

    return {
        "messages": [AIMessage(content=response)],
        "current_agent": "surveyor",
        "user_data": user_data,
        "task_complete": True,
    }


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 Handoff 路由
# ============================================

def handoff_router(state: HandoffState) -> str:
    """
    🔥🔥🔥🔥🔥🔥🔥🔥🔥 Agent Handoff 路由函数

    面试最高频！

    两种实现方式对比：
    ┌─────────────────────────────────────────────┐
    │ LiveKit 方式：                               │
    │   工具返回新 Agent 对象                       │
    │   return StoryAgent(name, location)          │
    │                                             │
    │ LangGraph 方式：                             │
    │   条件边路由到不同 Agent 节点                  │
    │   graph.add_conditional_edges(node, router)  │
    └─────────────────────────────────────────────┘
    """
    current = state["current_agent"]
    user_data = state["user_data"]

    # 🔥🔥🔥🔥🔥 Handoff 逻辑
    if current == "greeter":
        # Greeter 完成后移交给 Assistant
        return "assistant"

    elif current == "assistant":
        # Assistant 处理完成后移交给 Surveyor
        if user_data.get("resolved"):
            return "surveyor"
        return "assistant"  # 继续处理

    elif current == "surveyor":
        # Surveyor 完成后结束
        if state["task_complete"]:
            return "end"
        return "surveyor"

    return "end"


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 创建 Handoff 图
# ============================================

def create_handoff_graph():
    """
    🔥🔥🔥🔥🔥🔥🔥🔥🔥 Agent Handoff 流程图

    流程：
    Greeter → Assistant → Surveyor → END

    这模拟了 LiveKit 的 multi_agent.py 示例：
    IntroAgent → StoryAgent → 结束
    """
    graph = StateGraph(HandoffState)

    # 添加 Agent 节点
    graph.add_node("greeter", greeter_node)
    graph.add_node("assistant", assistant_node)
    graph.add_node("surveyor", surveyor_node)

    # 入口
    graph.add_edge(START, "greeter")

    # 🔥🔥🔥🔥🔥🔥🔥🔥🔥 Handoff 条件边
    graph.add_conditional_edges(
        "greeter",
        handoff_router,
        {
            "assistant": "assistant",
            "surveyor": "surveyor",
            "end": END, 
        }
    )

    graph.add_conditional_edges(
        "assistant",
        handoff_router,
        {
            "assistant": "assistant",
            "surveyor": "surveyor",
            "end": END,
        }
    )

    graph.add_conditional_edges(
        "surveyor",
        handoff_router,
        {
            "surveyor": "surveyor",
            "end": END,
        }
    )

    return graph.compile()


# ============================================
# 运行示例
# ============================================

def run_handoff():
    """运行 Agent Handoff 示例"""
    app = create_handoff_graph()

    print("\n" + "="*60)
    print("🔥🔥🔥🔥🔥🔥🔥🔥🔥 Agent Handoff 示例")
    print("="*60)
    print("\n流程：Greeter → Assistant → Surveyor → END")
    print("（模拟 LiveKit multi_agent.py 的 IntroAgent → StoryAgent）")

    initial_state = {
        "messages": [HumanMessage(content="你好，我想咨询产品")],
        "current_agent": "",
        "user_data": {},
        "task_complete": False,
    }

    result = app.invoke(initial_state)

    print("\n" + "="*60)
    print("执行完成")
    print("="*60)
    print(f"\n最终 Agent: {result['current_agent']}")
    print(f"用户数据: {result['user_data']}")
    print(f"\n【对话历史】")
    for msg in result["messages"]:
        print(f"  [{msg.type}] {msg.content}")


# ============================================
# 🔥🔥🔥🔥🔥🔥🔥🔥🔥 LiveKit vs LangGraph 对比
# ============================================

"""
🔥🔥🔥🔥🔥🔥🔥🔥🔥 Agent Handoff 实现对比：

┌─────────────────────────────────────────────────────────┐
│                    LiveKit 方式                           │
├─────────────────────────────────────────────────────────┤
│  class IntroAgent(Agent):                                │
│      @function_tool                                      │
│      async def information_gathered(self, name, loc):    │
│          # 🔥🔥🔥 工具直接返回新 Agent                     │
│          return StoryAgent(name, location)               │
│                                                          │
│  优点：                                                   │
│  - 简洁，一个函数完成 Handoff                              │
│  - 自动继承 chat_ctx                                      │
│  - 适合语音场景                                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    LangGraph 方式                         │
├─────────────────────────────────────────────────────────┤
│  graph.add_conditional_edges(                            │
│      "agent1",                                           │
│      handoff_router,  # 🔥🔥🔥 条件函数决定下一个 Agent    │
│      {"agent2": "agent2", "end": END}                    │
│  )                                                       │
│                                                          │
│  优点：                                                   │
│  - 状态可追溯（Checkpointing）                             │
│  - 灵活，可循环改进                                        │
│  - 适合复杂工作流                                         │
└─────────────────────────────────────────────────────────┘

🔥🔥🔥🔥🔥 面试要点：
两种方式本质相同：通过某种机制决定下一个 Agent
- LiveKit：工具返回 Agent 对象
- LangGraph：条件边路由
"""


if __name__ == "__main__":
    run_handoff()