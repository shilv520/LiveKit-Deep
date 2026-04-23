# 阶段3 学习笔记：LiveKit 实时语音 Agent

## 核心知识点

### 1. LiveKit 核心架构 🔥🔥🔥🔥🔥🔥🔥🔥🔥

```
┌─────────────────────────────────────────────────────────┐
│                    用户端                                │
│  LiveKit Room ← WebRTC 实时音频传输                     │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                  AgentServer                             │
│  - 任务调度、进程管理                                     │
│  - prewarm（预热模型）                                    │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                  JobContext                              │
│  - 连接 LiveKit Room                                     │
│  - 管理会话生命周期                                       │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                  AgentSession                            │
│  STT → LLM → TTS                                         │
│  VAD + Turn Detection + 打断机制                         │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent                                 │
│  - instructions（指令）                                  │
│  - tools（工具）                                         │
│  - @function_tool                                        │
└─────────────────────────────────────────────────────────┘
```

---

### 2. 核心组件详解

| 组件 | 作用 | 推荐 |
|-----|------|-----|
| **AgentServer** | 任务调度、进程管理 | LiveKit 内置 |
| **JobContext** | 会话上下文、房间连接 | LiveKit 内置 |
| **AgentSession** | STT/LLM/TTS/VAD 管理 | 配置各组件 |
| **Agent** | 定义行为、指令、工具 | 继承 Agent 类 |

---

### 3. STT/LLM/TTS 🔥🔥🔥🔥🔥

```python
session = AgentSession(
    # STT（语音识别）
    stt=inference.STT("deepgram/nova-3", language="multi"),

    # LLM（大模型）
    llm=inference.LLM("openai/gpt-4.1-mini"),

    # TTS（语音合成）
    tts=inference.TTS("cartesia/sonic-3", voice="..."),
)
```

| 组件 | 作用 | 推荐服务 |
|-----|------|---------|
| STT | 语音转文本 | Deepgram（低延迟、多语言） |
| LLM | 生成回复 | OpenAI GPT-4 / Anthropic Claude |
| TTS | 文本转语音 | Cartesia（低延迟、音质好） |

---

### 4. VAD + 打断机制 🔥🔥🔥🔥🔥🔥🔥🔥🔥

**面试最高频！**

```
VAD（Voice Activity Detection）
────────────────────────────
作用：检测用户是否在说话

Turn Detection（轮次检测）
────────────────────────────
作用：判断用户何时结束说话（语义分析）

打断流程：
────────────────────────────
1. VAD 检测到用户开始说话
2. 立即停止 TTS 播放
3. 开始处理用户新输入
```

**源码配置：**
```python
vad = silero.VAD.load()  # 加载 VAD 模型

# 轮次检测
from livekit.plugins.turn_detector.multilingual import MultilingualModel
turn_detection = MultilingualModel()
```

---

### 5. Agent 类定义 🔥🔥🔥🔥🔥

```python
class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Your name is Kelly...",  # 指令
            tools=[EndCallTool()],                 # 工具
        )

    async def on_enter(self):
        # 进入时生成欢迎语
        self.session.generate_reply()

    @function_tool
    async def lookup_weather(self, context, location):
        """查询天气（LLM 会理解 docstring）"""
        return "sunny, 25°C"
```

---

### 6. LangGraph + LiveKit 集成 🔥🔥🔥🔥🔥🔥🔥🔥🔥

**分工：**

| 层 | 职责 |
|---|------|
| **LiveKit** | 音频传输、语音处理（STT/TTS）、打断机制 |
| **LangGraph** | 业务逻辑、Agent 编排、工具调用 |

**关键：LLMAdapter**
```python
from livekit.plugins.langchain import LLMAdapter

# 1. 创建 LangGraph 图
graph = StateGraph(State)
graph.add_node("chatbot", chatbot_node)
compiled_graph = graph.compile()

# 2. 用 LLMAdapter 包装
llm_adapter = LLMAdapter(compiled_graph)

# 3. Agent 使用 LLMAdapter
agent = Agent(
    instructions="",
    llm=llm_adapter,  # 🔥🔥🔥🔥🔥 关键
)

# 4. AgentSession 只配语音层
session = AgentSession(
    stt=inference.STT("deepgram/nova-3"),
    tts=inference.TTS("cartesia/sonic-3"),
    vad=vad,
)
```

---

### 7. 运行命令 🔥🔥🔥

| 命令 | 说明 |
|-----|------|
| `python agent.py console` | 终端模式，本地测试（无需 Server） |
| `python agent.py dev` | 开发模式，热重载 |
| `python agent.py start` | 生产模式 |
| `python agent.py connect` | 连接已有房间 |

---

## 阶段3 文件结构

```
phase3-livekit-voice/
├── 01_livekit_basics.py       # 架构解析
├── 02_voice_agent.py          # 完整语音 Agent
├── 03_langgraph_integration.py # LangGraph + LiveKit
└── NOTES.md                   # 本笔记
```

---

## 面试高频问答

### Q1: LiveKit 延迟为什么低？

> 1. **WebRTC 原生传输**（UDP）
> 2. **流式处理**（边说边处理）
> 3. **无需等待完整音频**

---

### Q2: VAD 是什么？为什么重要？

> - **Voice Activity Detection**（语音活动检测）
> - 判断用户是否在说话
> - 区分"说话"和"静音"
> - **打断机制的基础**

---

### Q3: 用户打断 Agent 怎么实现？

> 1. VAD 检测到用户开始说话
> 2. 立即停止 TTS 播放
> 3. 开始处理用户新输入
> 4. **LiveKit 原生支持**

---

### Q4: @function_tool 怎么写？

```python
@function_tool
async def tool_name(self, context: RunContext, param: str) -> str:
    """工具描述（LLM 会理解）"""
    return "结果"
```

---

### Q5: LangGraph + LiveKit 怎么集成？

> **LLMAdapter 桥接：**
> ```python
> llm_adapter = LLMAdapter(graph)
> agent = Agent(llm=llm_adapter)
> ```
>
> - LangGraph 处理业务逻辑
> - LiveKit 处理语音层

---

### Q6: Agent 和 AgentSession 的区别？

| 组件 | 作用 |
|-----|------|
| Agent | 定义行为（指令、工具） |
| AgentSession | 管理组件（STT/LLM/TTS/VAD） |

---

## 与源码对照

| 知识点 | 源码位置 |
|-------|---------|
| Basic Agent | [basic_agent.py](../livekit-agents/examples/voice_agents/basic_agent.py) |
| LangGraph 集成 | [langgraph_agent.py](../livekit-agents/examples/voice_agents/langgraph_agent.py) |
| Multi-Agent | [multi_agent.py](../livekit-agents/examples/voice_agents/multi_agent.py) |

---

## 运行前置条件

```bash
# 安装依赖
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero livekit-plugins-cartesia livekit-plugins-turn-detector

# LangGraph 集成额外需要
pip install langgraph langchain-openai livekit-plugins-langchain

# 配置 .env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
OPENAI_API_KEY=sk-xxx
DEEPGRAM_API_KEY=xxx
CARTESIA_API_KEY=xxx

# 启动 LiveKit Server
docker run -d -p 7880:7880 livekit/livekit-server
```

---

## 下一步

阶段4 将学习：
- MCP（Model Context Protocol）集成
- 工具标准化
- 与外部服务的连接