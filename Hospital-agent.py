import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import openai, silero,azure
from livekit.agents import JobContext, WorkerOptions, cli, Agent, AgentSession
from livekit.agents import metrics, MetricsCollectedEvent

THIS_DIR = Path(__file__).parent.parent
sys.path.insert(0,str(THIS_DIR))

load_dotenv(f"{THIS_DIR}/envs/.env.saas")

logger = logging.getLogger("Hospital-Agent")
logger.setLevel(logging.INFO)

from utils.helper_functions import get_text_from_google_doc 
instructions = get_text_from_google_doc("1TJVfrDAy3IQRehb8T6ihwizS_E1AHiGOYBBy5IFn0sE")[1]
                                         
print(instructions)

stt=azure.STT(
            speech_key="2g5a2Fe1x2LbXPDNgNeJBOh3xLFe9G0Fh511A2JTMfP6poNR7qFJJQQJ99BEACHYHv6XJ3w3AAAAACOGj0Gx",
            speech_region="eastus2",
        )
tts=azure.TTS(
        speech_key="2g5a2Fe1x2LbXPDNgNeJBOh3xLFe9G0Fh511A2JTMfP6poNR7qFJJQQJ99BEACHYHv6XJ3w3AAAAACOGj0Gx",
        speech_region="eastus2",
        voice="ta-IN-PallaviNeural",
        language="ta-IN-PallaviNeural "
    )   

class HospitalAgent(Agent):
    """A LiveKit agent that used for hospital Appointment booking"""

    def __init__(self):
        super().__init__(
            instructions=instructions,

        stt =stt,
        llm=openai.LLM.with_azure(azure_deployment="gpt-4o-mini"),
        tts = tts,
        vad=silero.VAD.load(),
        allow_interruptions=True
        )
    async def on_enter(self):
        await self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the LiveKit agent application."""

    agent = HospitalAgent()

    await ctx.connect()

    session = AgentSession()

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        #logger.info(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    # At shutdown, generate and log the summary from the usage collector
    ctx.add_shutdown_callback(log_usage)

    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            #agent_name="hospital-agent",
            entrypoint_fnc=entrypoint
        )
    )
