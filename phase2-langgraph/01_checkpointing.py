"""
阶段2：Checkpointing（状态持久化）
================================

知识点：
1. Checkpointer - 状态持久化机制
2. MemorySaver - 内存持久化（LangGraph 内置，推荐用于开发）
3. Redis 连接测试 - 验证 Redis 可用性
4. 时间旅行调试 - 回溯历史状态

面试要点：
- LangGraph 内置只有 MemorySaver
- 生产环境持久化需要自己实现或使用第三方库
- 自定义 Checkpointer 需要匹配 LangGraph 内部格式（复杂）

前置条件（可选）：
pip install redis
"""

from typing import TypedDict, Annotated, Any, Optional, List, Tuple
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# 尝试导入 redis（用于连接测试）
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[WARN] redis 未安装，请运行: pip install redis")


# ============================================
# 状态定义
# ============================================

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    count: int
    finished: bool


# ============================================
# 简单节点
# ============================================

def process_node(state: AgentState) -> dict:
    count = state["count"] + 1
    msg = AIMessage(content=f"第 {count} 次处理")
    print(f"[Process] 计数: {count}")

    if count >= 3:
        return {"messages": [msg], "count": count, "finished": True}

    return {"messages": [msg], "count": count, "finished": False}


def should_continue(state: AgentState) -> str:
    if state["finished"]:
        return "end"
    return "continue"


# ============================================
# Redis 连接测试
# ============================================

def test_redis_connection(redis_url: str = "redis://localhost:6379") -> bool:
    """
    测试 Redis 连接是否可用

    Returns:
        True: Redis 可用
        False: Redis 不可用
    """
    if not REDIS_AVAILABLE:
        print("[WARN] redis 库未安装")
        return False

    try:
        client = redis.from_url(redis_url, decode_responses=True)
        result = client.ping()
        if result:
            print(f"[OK] Redis 连接成功: {redis_url}")
            return True
    except redis.ConnectionError as e:
        print(f"[WARN] Redis 连接失败: {e}")
        print("请确保 Redis 服务已启动（redis-server.exe）")

    return False


# ============================================
# Checkpointing 示例（使用 MemorySaver）
# ============================================

def create_checkpointed_graph():
    """
    创建带 Checkpointer 的图

    面试要点：
    - LangGraph 内置 MemorySaver（内存存储）
    - 生产环境需要自己实现持久化方案
    - 自定义 Checkpointer 需要继承 BaseCheckpointSaver 并实现多个方法
    """
    graph = StateGraph(AgentState)

    graph.add_node("process", process_node)
    graph.add_edge(START, "process")

    graph.add_conditional_edges(
        "process",
        should_continue,
        {"continue": "process", "end": END}
    )

    # 使用 MemorySaver（内置，稳定可靠）
    checkpointer = MemorySaver()
    print("[OK] 使用 MemorySaver（LangGraph 内置）")

    app = graph.compile(checkpointer=checkpointer)
    return app, checkpointer


def run_with_checkpoint():
    """演示 Checkpointer 的能力"""

    # 先测试 Redis 连接（可选）
    print("\n>>> Redis 连接测试")
    redis_ok = test_redis_connection()
    if redis_ok:
        print("[INFO] Redis 可用，但 LangGraph 需要自定义 Checkpointer 才能使用")
        print("[INFO] 自定义实现需要匹配 LangGraph 内部格式，较复杂")

    # 使用 MemorySaver 进行演示
    print("\n>>> 使用 MemorySaver 演示 Checkpointing")
    app, checkpointer = create_checkpointed_graph()

    config = {"configurable": {"thread_id": "demo-session-1"}}

    print("\n" + "="*60)
    print("Checkpointing 示例")
    print("="*60 + "\n")

    # 第一阶段：初始运行
    print("\n>>> 第一阶段：初始运行")
    initial_state = {
        "messages": [HumanMessage(content="开始处理")],
        "count": 0,
        "finished": False,
    }

    result = app.invoke(initial_state, config)
    print(f"完成! 计数: {result['count']}")
    print(f"消息数: {len(result['messages'])}")

    # 第二阶段：查看历史
    print("\n>>> 第二阶段：查看历史 Checkpoints")
    checkpoints = list(app.get_state_history(config))
    print(f"Checkpoint 数量: {len(checkpoints)}")
    for i, cp in enumerate(checkpoints):
        state = cp.values
        print(f"  Checkpoint {i}: count={state.get('count', 0)}, finished={state.get('finished')}")

    # 第三阶段：回溯
    print("\n>>> 第三阶段：时间旅行 - 回溯")
    if len(checkpoints) > 1:
        target = checkpoints[1]
        print(f"回溯到: count={target.values.get('count')}")
        app.update_state(config, target.values)
        result = app.invoke(None, config)
        print(f"恢复后继续运行完成! 计数: {result['count']}")

    # 第四阶段：新会话
    print("\n>>> 第四阶段：新会话")
    new_config = {"configurable": {"thread_id": "demo-session-2"}}
    result = app.invoke(
        {"messages": [HumanMessage(content="新会话")], "count": 0, "finished": False},
        new_config
    )
    print(f"新会话计数: {result['count']}")

    return app


# ============================================
# 面试要点总结
# ============================================

"""
Checkpointing 面试要点：

Q1: Checkpointer 有什么用？
A:
1. 持久化状态 - Agent 状态不会丢失
2. 暂停-恢复 - 支持 Agent 中断后继续（生产必备）
3. 时间旅行调试 - 可以回溯历史状态
4. 多轮对话 - 支持跨会话对话

Q2: LangGraph 内置哪些 Checkpointer？
A:
[OK] MemorySaver - 内置，内存存储，开箱即用
[WARN] RedisSaver - 不存在，需自己实现
[WARN] SqliteSaver - 不存在，需自己实现

Q3: 生产环境怎么实现持久化？
A:
方案1：自己实现 Redis Checkpointer（继承 BaseCheckpointSaver）
  - 需要实现: get_tuple, put, put_writes, list 等方法
  - 需要匹配 LangGraph 内部 checkpoint 格式（包含版本等字段）
  - 实现复杂，建议参考 LangGraph 源码

方案2：使用第三方持久化库（如有）

Q4: MemorySaver 的局限？
A:
- 重启后数据丢失
- 无法多实例共享
- 仅适合开发测试

Q5: Redis 在生产环境的作用？
A:
- 用于持久化 Agent 状态
- 支持分布式部署（多实例共享状态）
- 支持暂停-恢复功能
"""


if __name__ == "__main__":
    run_with_checkpoint()