from swarm import Agent
from typing import List, Dict
import os
import chainlit as cl


class DeveloperAgent:
    def __init__(self, test_agent):
        self.test_agent = test_agent
        self.orchestrator_agent = None

    @cl.step(type="tool")
    async def transfer_to_test_agent(self, unused: str = "") -> str:
        """Transfer to test agent when code changes need validation

        Args:
            unused: Placeholder parameter to satisfy function schema
        """
        display_name = "🔄 Transfer to Testing Agent"
        cl.Step(name=display_name, type="tool")
        return self.test_agent

    @cl.step(type="tool")
    async def transfer_to_orchestrator(self, unused: str = "") -> str:
        """Transfer back to orchestrator after development is complete

        Args:
            unused: Placeholder parameter to satisfy function schema
        """
        display_name = "🔄 Transfer to Orchestrator"
        cl.Step(name=display_name, type="tool")
        return self.orchestrator_agent

    @cl.step(type="tool")
    async def read_component(self, path: str) -> str:
        """Read a component file's contents"""
        display_name = f"📖 Reading Component: {path}"
        cl.Step(name=display_name, type="tool")

        try:
            with open(path, "r") as file:
                return file.read()
        except Exception as e:
            return f"Error reading component: {str(e)}"

    @cl.step(type="tool")
    async def write_component(self, path: str, content: str) -> str:
        """Write changes to a component file"""
        display_name = f"✍️ Writing Component: {path}"
        cl.Step(name=display_name, type="tool")

        try:
            with open(path, "w") as file:
                file.write(content.encode("utf-8").decode("unicode_escape"))
            return f"Successfully updated {path}"
        except Exception as e:
            return f"Error writing component: {str(e)}"

    # Create wrapper functions for non-async calls
    def _transfer_to_test_agent(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.transfer_to_test_agent(unused))

    def _transfer_to_orchestrator(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.transfer_to_orchestrator(unused))

    def _read_component(self, path: str) -> str:
        import asyncio

        return asyncio.run(self.read_component(path))

    def _write_component(self, path: str, content: str) -> str:
        import asyncio

        return asyncio.run(self.write_component(path, content))

    def create_agent(self) -> Agent:
        return Agent(
            name="Developer",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a TypeScript/React developer agent specialized in web development.
            
            Key capabilities:
            1. Read and understand React component structure
            2. Make precise code modifications while preserving functionality
            3. Ensure type safety in TypeScript
            4. Follow React best practices
            
            After making changes, transfer to Testing Agent for validation.""",
            functions=[
                self._transfer_to_test_agent,
                self._read_component,
                self._write_component,
                self._transfer_to_orchestrator,
            ],
        )
