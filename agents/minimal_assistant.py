import asyncio
import logging
import requests  # Added for API call
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero
import re

load_dotenv()
logger = logging.getLogger("voice-assistant")

# Define Flask API endpoint
FLASK_SERVER_URL = "https://7f01-27-4-44-174.ngrok-free.app/validate_audio"

async def extract_text_from_stream(stream):
    """Extract text from async generator"""
    text = ""
    async for chunk in stream:
        text += chunk
    return text

def estimate_audio_length(text):
    """
    Estimate audio duration based on text length.
    Assumption: 150 words = 60 seconds.
    """
    words_per_second = 150 / 60  # Approximate speaking rate
    words = len(text.split())
    estimated_duration = words / words_per_second  # Estimated seconds

    return estimated_duration

async def before_tts_cb(agent, text_stream):
    """
    Before sending text to TTS, extract the text (if it's an async generator),
    estimate audio length, and validate via API.
    """
    if isinstance(text_stream, str):
        text = text_stream  # If it's already a string, use it directly
    else:
        text = await extract_text_from_stream(text_stream)  # Extract text from async generator

    estimated_length = estimate_audio_length(text)

    # Debug print before sending to API
    print(f"[DEBUG] Original text before validation: {text}")

    # Send estimated length to Flask API
    response = requests.post(FLASK_SERVER_URL, json={"length": estimated_length, "text": text})

    if response.status_code == 200:
        modified_text = response.json().get("message", text)  # Use modified text if provided

        # Debug print after validation
        print(f"[DEBUG] Modified text after validation: {modified_text}")

        return modified_text
    else:
        return text  # Default to original text if API fails

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    dg_model = "nova-3-general"
    if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
        # use a model optimized for telephony
        dg_model = "nova-2-phonecall"

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model=dg_model),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        before_tts_cb=before_tts_cb,  #New callback for validation
    )

    agent.start(ctx.room, participant)

    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def _on_metrics_collected(mtrcs: metrics.AgentMetrics):
        metrics.log_metrics(mtrcs)
        usage_collector.collect(mtrcs)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: ${summary}")

    ctx.add_shutdown_callback(log_usage)

    # listen to incoming chat messages, only required if you'd like the agent to
    # answer incoming messages from Chat
    chat = rtc.ChatManager(ctx.room)

    async def answer_from_text(txt: str):
        chat_ctx = agent.chat_ctx.copy()
        chat_ctx.append(role="user", text=txt)
        stream = agent.llm.chat(chat_ctx=chat_ctx)
        await agent.say(stream)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if msg.message:
            asyncio.create_task(answer_from_text(msg.message))

    await agent.say("Hey, how can I help you today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )