"""
阶段3：LiveKit 实时语音 Agent 基础架构
================================

知识点：
1. LiveKit 核心架构（Agent、AgentSession、AgentServer）
2. STT/LLM/TTS 组件
3. VAD（语音活动检测）
4. 打断机制

参考源码：livekit-agents/examples/voice_agents/basic_agent.py

前置条件：
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero
"""

# ============================================
# LiveKit 核心架构解析
# ============================================

"""
LiveKit Agents 架构：

┌─────────────────────────────────────────────────────────┐
│                    用户端                                │
│  ┌─────────────┐                                        │
│  │ LiveKit     │  ← WebRTC 实时音频传输                 │
│  │ Room        │                                        │
│  └─────────────┘                                        │
│         ↓ 音频流                                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                  AgentServer                             │
│  - 任务调度                                              │
│  - 进程管理                                              │
│  - 预热（prewarm）                                       │
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
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │ STT     │→ │ LLM     │→ │ TTS     │                 │
│  │(语音识别)│  │(大模型) │  │(语音合成)│                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
│                                                         │
│  ┌─────────────────────────────────────┐               │
│  │ VAD + Turn Detection + 打断机制     │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent                                 │
│  - instructions（指令）                                  │
│  - tools（工具）                                         │
│  - on_enter/on_exit（生命周期回调）                      │
└─────────────────────────────────────────────────────────┘
"""

# ============================================
# 核心组件详解
# ============================================

"""
1. AgentServer（服务端）
────────────────────────────
- 主进程，负责任务调度
- prewarm: 预加载模型（如 VAD）
- 监听 LiveKit 服务器的任务请求

# 源码用法：
server = AgentServer()
server.setup_fnc = prewarm  # 预热函数
@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ...

2. JobContext（任务上下文）
────────────────────────────
- 每个用户会话的上下文
- ctx.room: LiveKit 房间
- ctx.add_shutdown_callback(): 添加关闭回调

# 源码用法：
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    await session.start(agent=MyAgent(), room=ctx.room)

3. AgentSession（会话管理）
────────────────────────────
- 管理 STT、LLM、TTS 组件
- 处理语音流、打断、轮次检测

# 源码用法：
session = AgentSession(
    stt=inference.STT("deepgram/nova-3"),     # 语音识别
    llm=inference.LLM("openai/gpt-4.1-mini"), # 大模型
    tts=inference.TTS("cartesia/sonic-3"),    # 语音合成
    vad=silero.VAD.load(),                    # VAD
    turn_detection=MultilingualModel(),       # 轮次检测
)

4. Agent（智能体）
────────────────────────────
- 定义 Agent 的行为
- instructions: 指令/角色设定
- tools: 工具列表
- @function_tool: 定义工具

# 源码用法：
class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Your name is Kelly...",
            tools=[EndCallTool()],
        )

    @function_tool
    async def lookup_weather(self, context, location):
        return "sunny"
"""

# ============================================
# STT/LLM/TTS 组件详解
# ============================================

"""
STT（Speech-to-Text，语音识别）
────────────────────────────
作用：将用户语音转为文本
推荐：Deepgram（低延迟，多语言）

# 源码：
stt=inference.STT("deepgram/nova-3", language="multi")

LLM（Large Language Model，大模型）
────────────────────────────
作用：处理用户输入，生成回复
推荐：OpenAI GPT-4、Anthropic Claude

# 源码：
llm=inference.LLM("openai/gpt-4.1-mini")

TTS（Text-to-Speech，语音合成）
────────────────────────────
作用：将文本转为语音
推荐：Cartesia（低延迟，音质好）

# 源码：
tts=inference.TTS("cartesia/sonic-3", voice="...")
"""

# ============================================
# VAD + 打断机制详解（面试最高频）
# ============================================

"""
VAD（Voice Activity Detection，语音活动检测）
────────────────────────────
作用：检测用户是否在说话
原理：分析音频能量、频率等特征

# 源码：
from livekit.plugins import silero
vad = silero.VAD.load()

Turn Detection（轮次检测）
────────────────────────────
作用：判断用户何时结束说话
原理：语义分析，不只是静音检测

# 源码：
from livekit.plugins.turn_detector.multilingual import MultilingualModel
turn_detection=MultilingualModel()

打断机制（Interruption）
────────────────────────────
流程：
1. VAD 检测到用户开始说话
2. 立即停止 TTS 播放
3. 开始处理用户新输入

# 源码配置：
turn_handling=TurnHandlingOptions(
    turn_detection=MultilingualModel(),
    interruption={
        "resume_false_interruption": True,  # 恢复误判打断
        "false_interruption_timeout": 1.0,
    },
)
"""

# ============================================
# 面试要点总结
# ============================================

"""
LiveKit 面试要点：

Q1: LiveKit 延迟为什么低？
A:
1. WebRTC 原生传输（UDP）
2. 流式处理（边说边处理）
3. 无需等待完整音频

Q2: VAD 是什么？为什么重要？
A:
- Voice Activity Detection（语音活动检测）
- 判断用户是否在说话
- 区分"说话"和"静音"
- 打断机制的基础

Q3: 用户打断 Agent 怎么实现？
A:
1. VAD 检测到用户开始说话
2. 立即停止 TTS 播放
3. 开始处理用户新输入
4. LiveKit 原生支持

Q4: STT/LLM/TTS 是什么？
A:
- STT: Speech-to-Text，语音识别
- LLM: Large Language Model，大模型
- TTS: Text-to-Speech，语音合成
- 三者串联实现语音对话

Q5: Agent 和 AgentSession 的区别？
A:
- Agent: 定义行为（指令、工具）
- AgentSession: 管理组件（STT/LLM/TTS/VAD）
"""

# ============================================
# 运行命令
# ============================================

"""
运行 LiveKit Agent 需要：

1. 安装依赖：
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero

2. 配置环境变量（.env）：
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=your_key
DEEPGRAM_API_KEY=your_key

3. 启动 LiveKit Server：
docker run -d -p 7880:7880 -p 5000-5020:5000-5020 livekit/livekit-server

4. 运行 Agent：
python basic_agent.py dev
"""

if __name__ == "__main__":
    print("请查看代码注释学习 LiveKit 架构")
    print("运行完整示例请参考 phase3-livekit-voice/02_voice_agent.py")