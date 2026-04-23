"""
Phase 3: Complete LiveKit Voice Agent
================================

Key concepts:
1. Agent class definition (instructions, tools)
2. @function_tool tool definition
3. AgentSession configuration (STT/LLM/TTS/VAD)
4. Interruption mechanism
5. Run commands (dev/console/start)

Reference: livekit-agents/examples/voice_agents/basic_agent.py

Prerequisites:
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero livekit-plugins-cartesia livekit-plugins-turn-detector
"""

import logging
import os

# Try imports
try:
    from dotenv import load_dotenv
    from livekit.agents import (
        Agent,
        AgentServer,
        AgentSession,
        JobContext,
        JobProcess,
        RunContext,
        cli,
        inference,
    )
    from livekit.agents.llm import function_tool
    from livekit.plugins import silero
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    print("[WARN] LiveKit not installed. Run:")
    print("pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero")

logger = logging.getLogger("voice-agent")

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()


# ============================================
# Agent Class Definition
# ============================================

class VoiceAgent(Agent):
    """
    LiveKit Agent Class

    Key points:
    - Inherit from Agent
    - instructions: Agent's role definition
    - tools: tool list
    - on_enter: callback when entering
    - @function_tool: define tool functions
    """

    def __init__(self) -> None:
        super().__init__(
            # instructions: Agent's role
            instructions=(
                "Your name is Assistant, built with LiveKit. "
                "You interact with users via voice. "
                "Keep your responses concise. "
                "Do not use emojis or markdown. "
                "You are helpful and friendly."
            ),
            # Tool list
            tools=[],
        )

    async def on_enter(self) -> None:
        """
        Callback when Agent enters session
        Usually used to generate welcome message
        """
        self.session.generate_reply(
            instructions="greet the user and ask how you can help"
        )

    # ============================================
    # Tool Definition Example
    # ============================================

    @function_tool
    async def get_weather(
        self,
        context: RunContext,
        location: str,
    ) -> str:
        """
        Get weather tool

        Args:
            location: The location user asks about
        """
        logger.info(f"Getting weather for: {location}")

        # Mock weather data
        weather_data = {
            "Beijing": "Sunny, 25C",
            "Shanghai": "Cloudy, 22C",
            "Guangzhou": "Rain, 28C",
        }
        return weather_data.get(location, f"No weather data for {location}")

    @function_tool
    async def get_time(
        self,
        context: RunContext,
    ) -> str:
        """
        Get current time - no parameter tool example
        """
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Current time: {now}"


# ============================================
# AgentServer Configuration
# ============================================

server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """
    Prewarm function - runs before Agent starts
    Used to load models (like VAD)
    """
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model loaded")


server.setup_fnc = prewarm


# ============================================
# Entry Point
# ============================================

@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """
    Agent entry point

    Steps:
    1. Create AgentSession (configure STT/LLM/TTS/VAD)
    2. Create Agent
    3. Start session
    """

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # AgentSession configuration
    session = AgentSession(
        # STT (Speech-to-Text)
        stt=inference.STT(
            "deepgram/nova-3",
            language="multi",
        ),

        # LLM (Large Language Model)
        llm=inference.LLM(
            "openai/gpt-4.1-mini",
        ),

        # TTS (Text-to-Speech)
        tts=inference.TTS(
            "cartesia/sonic-3",
            voice="your_voice_id",
        ),

        # VAD (Voice Activity Detection)
        vad=ctx.proc.userdata["vad"],
    )

    # Start session
    await session.start(
        agent=VoiceAgent(),
        room=ctx.room,
    )

    logger.info("Agent session started")


# ============================================
# Run Commands
# ============================================

"""
LiveKit Agent run modes:

[console mode]
python voice_agent.py console
- Terminal mode, local audio input/output
- No LiveKit Server needed
- Quick testing

[dev mode]
python voice_agent.py dev
- Development mode, connects to LiveKit Server
- Hot reload support
- Recommended for development

[start mode]
python voice_agent.py start
- Production mode
- Performance optimized
- Recommended for deployment

[connect mode]
python voice_agent.py connect --room xxx --identity yyy
- Connect to existing room
- For testing or debugging
"""


# ============================================
# Interview Key Points
# ============================================

"""
Interview Key Points:

Q1: How to define Agent class?
A:
1. Inherit from Agent
2. super().__init__(instructions, tools)
3. Define on_enter callback
4. Use @function_tool for tools

Q2: What to configure in AgentSession?
A:
- stt: Speech recognition (Deepgram)
- llm: Language model (OpenAI)
- tts: Speech synthesis (Cartesia)
- vad: Voice activity detection (Silero)
- turn_detection: Turn detection

Q3: How to configure interruption?
A:
In turn_handling:
- turn_detection: MultilingualModel()
- interruption: resume_false_interruption, false_interruption_timeout

Q4: How to write @function_tool?
A:
@function_tool
async def tool_name(self, context: RunContext, param: str) -> str:
    '''Tool description'''
    return "result"

Q5: What are the run commands?
A:
- console: Local test, no Server needed
- dev: Development mode, hot reload
- start: Production mode
"""

if __name__ == "__main__":
    if LIVEKIT_AVAILABLE:
        cli.run_app(server)
    else:
        print("[ERROR] Please install LiveKit dependencies first")
        print("pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-silero")