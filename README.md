# LangGraph + LiveKit 学习项目

> 基于 livekit/agents 源码的系统性学习笔记和示例代码

## 项目结构

```
LangGraph-LiveKit/
├── phase1-quickstart/       # 阶段1：环境准备与快速上手 ✅
├── phase2-langgraph/        # 阶段2：LangGraph 基础与 Agent 编排 ✅
├── phase3-livekit-voice/    # 阶段3：LiveKit 实时语音 Agent
├── phase4-mcp-deepagents/   # 阶段4：MCP Skill + DeepAgents
├── phase5-rl-advanced/      # 阶段5：Agentic RL 进阶（可选）
├── phase6-final-project/    # 阶段6：完整实战项目
├── livekit-agents/          # 源码（仅参考，不提交）
├── LEARNING_PLAN.md         # 学习计划
└── README.md                # 本文件
```

## 学习进度

| 阶段 | 状态 | 核心内容 |
|-----|------|---------|
| Phase 1 | ✅ 完成 | StateGraph、条件边、ReAct循环 |
| Phase 2 | ✅ 完成 | Checkpointing、工具调用、多Agent协作 |
| Phase 3 | 🚧 待开始 | LiveKit 实时语音、VAD、打断机制 |
| Phase 4 | 🚧 待开始 | MCP Skill 集成 |
| Phase 5 | 🚧 待开始 | Agentic RL（可选） |
| Phase 6 | 🚧 待开始 | 完整实战项目 |

## 快速开始

```bash
# 安装依赖
pip install langgraph langchain-core

# 运行阶段1示例
python phase1-quickstart/01_stategraph_basics.py
python phase1-quickstart/02_conditional_edges.py
python phase1-quickstart/03_react_loop.py

# 运行阶段2示例
python phase2-langgraph/01_checkpointing.py
python phase2-langgraph/02_tools.py
python phase2-langgraph/03_multi_agent.py
python phase2-langgraph/04_agent_handoff.py
```

## 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [源码仓库](https://github.com/livekit/agents)