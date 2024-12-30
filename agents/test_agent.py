from swarm import Agent
from agents.selenium_agent import SeleniumAgent
from typing import List, Dict
import chainlit as cl


class TestAgent(SeleniumAgent):
    def __init__(self, orchestrator_agent):
        super().__init__()
        self.orchestrator_agent = orchestrator_agent

    @cl.step(type="tool")
    async def transfer_to_orchestrator(self, unused: str = "") -> str:
        """Transfer back to orchestrator after testing is complete

        Args:
            unused: Placeholder parameter to satisfy function schema
        """
        display_name = "🔄 Transfer to Orchestrator"
        cl.Step(name=display_name, type="tool")
        return self.orchestrator_agent

    # Create wrapper function for non-async call
    def _transfer_to_orchestrator(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.transfer_to_orchestrator(unused))

    def create_agent(self) -> Agent:
        selenium_agent = super().create_agent()

        # Add transfer function
        selenium_agent.functions.append(self._transfer_to_orchestrator)

        selenium_agent.instructions += """
        After completing tests or taking screenshots, transfer results back to the Orchestrator.
        Focus on validating recent changes and providing clear visual evidence."""

        return selenium_agent
