from swarm import Agent
from typing import List, Dict
import os
import chainlit as cl


class OrchestratorAgent:
    def __init__(self, dev_agent, test_agent):
        self.dev_agent = dev_agent
        self.test_agent = test_agent
        self.readme_path = "IF_YOURE_AN_LLM_README.md"

    @cl.step(type="tool")
    async def transfer_to_dev_agent(self, unused: str = "") -> str:
        """Transfer task to developer agent when code changes are needed"""
        display_name = "🔄 Transfer to Developer Agent"
        cl.Step(name=display_name, type="tool")
        return self.dev_agent

    @cl.step(type="tool")
    async def transfer_to_test_agent(self, unused: str = "") -> str:
        """Transfer task to test agent when testing is needed"""
        display_name = "🔄 Transfer to Testing Agent"
        cl.Step(name=display_name, type="tool")
        return self.test_agent

    @cl.step(type="tool")
    async def read_readme(self, unused: str = "") -> str:
        """Read the project README file for context"""
        display_name = "📖 Reading Project README"
        cl.Step(name=display_name, type="tool")

        try:
            with open(self.readme_path, "r") as file:
                return file.read()
        except Exception as e:
            return f"Error reading README: {str(e)}"

    @cl.step(type="tool")
    async def get_cwd(self, unused: str = "") -> str:
        """Get current working directory"""
        display_name = "📂 Getting Current Directory"
        cl.Step(name=display_name, type="tool")
        return os.getcwd()

    @cl.step(type="tool")
    async def change_cwd(self, path: str) -> str:
        """Change current working directory"""
        display_name = f"📂 Changing Directory to: {path}"
        cl.Step(name=display_name, type="tool")
        try:
            os.chdir(path)
            return f"Changed directory to {path}"
        except Exception as e:
            return f"Error changing directory: {str(e)}"

    # Create wrapper functions for non-async calls
    def _transfer_to_dev_agent(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.transfer_to_dev_agent(unused))

    def _transfer_to_test_agent(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.transfer_to_test_agent(unused))

    def _read_readme(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.read_readme(unused))

    def _get_cwd(self, unused: str = "") -> str:
        import asyncio

        return asyncio.run(self.get_cwd(unused))

    def _change_cwd(self, path: str) -> str:
        import asyncio

        return asyncio.run(self.change_cwd(path))

    def create_agent(self) -> Agent:
        return Agent(
            name="Orchestrator",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are the orchestrator of a web development system.
            
            Core Capabilities:
            1. Understand TypeScript/React project structure from README
            2. Coordinate between Developer and Testing agents
            3. Make informed decisions about task requirements
            
            Approach:
            - Read project documentation first using read_readme() (if the user wants to develop something)
            - Understand which components might be affected
            - Read files for more detail
            - Transfer to appropriate agent based on task type
            
            Remember:
            - Always check README for project structure
            - Do not transfer before knowing which files need to change
            - Keep focus on relevant files only
            - Coordinate between agents effectively""",
            functions=[
                self._transfer_to_dev_agent,
                self._transfer_to_test_agent,
                self._read_readme,
                self._get_cwd,
                self._change_cwd,
            ],
        )
