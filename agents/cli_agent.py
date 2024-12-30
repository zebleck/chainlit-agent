import chainlit as cl
from swarm import Agent
from typing import Dict, List, Any, Optional
import subprocess
import threading
import queue
import asyncio
import time
import re
import os


class CLIAgent:
    def __init__(self):
        """Initialize CLI Agent"""
        self.processes: Dict[str, subprocess.Popen] = {}
        self.output_queues: Dict[str, queue.Queue] = {}
        self.output_threads: Dict[str, threading.Thread] = {}
        self.latest_output: Dict[str, List[str]] = {}
        self.current_dir = os.getcwd()  # Track current directory

    def _read_output(self, process_id: str, process: subprocess.Popen):
        """Read output from process and store in queue"""
        queue = self.output_queues[process_id]
        while True:
            if process.poll() is not None:  # Process finished
                break
            output = process.stdout.readline()
            if output:
                queue.put(output.strip())

    @cl.step(type="tool")
    async def start_process(self, command: str) -> str:
        """Start a new process with the given command

        Args:
            command: Command to execute (e.g., 'npm start')
        """
        display_name = f"▶️ Start Process: {command}"
        cl.Step(name=display_name, type="tool")

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=self.current_dir,
            )

            process_id = f"process_{len(self.processes)}"
            self.processes[process_id] = process
            self.output_queues[process_id] = queue.Queue()
            self.latest_output[process_id] = []

            thread = threading.Thread(
                target=self._read_output, args=(process_id, process), daemon=True
            )
            self.output_threads[process_id] = thread
            thread.start()

            return f"Process started with ID: {process_id} in directory: {self.current_dir}"
        except Exception as e:
            return f"Error starting process: {str(e)}"

    @cl.step(type="tool")
    async def get_latest_output(self, process_id: str) -> str:
        """Get the latest output from a running process

        Args:
            process_id: ID of the process to get output from
        """
        display_name = f"📋 Get Output: {process_id}"
        cl.Step(name=display_name, type="tool")

        if process_id not in self.processes:
            return f"No process found with ID: {process_id}"

        # Get all available output from queue
        output = []
        try:
            while True:
                line = self.output_queues[process_id].get_nowait()
                output.append(line)
        except queue.Empty:
            pass

        if not output and process_id in self.latest_output:
            output = self.latest_output[process_id]

        return "\n".join(output) if output else "No new output"

    @cl.step(type="tool")
    async def stop_process(self, process_id: str) -> str:
        """Stop a running process

        Args:
            process_id: ID of the process to stop
        """
        display_name = f"⏹️ Stop Process: {process_id}"
        cl.Step(name=display_name, type="tool")

        if process_id not in self.processes:
            return f"No process found with ID: {process_id}"

        try:
            self.processes[process_id].terminate()
            self.processes[process_id].wait(timeout=5)
            return f"Process {process_id} stopped"
        except Exception as e:
            return f"Error stopping process: {str(e)}"

    @cl.step(type="tool")
    async def run_command(self, command: str) -> str:
        """Execute a one-off command and return its output

        Args:
            command: Command to execute (e.g., 'ls -la', 'git status', 'cd /path/to/dir')
        """
        display_name = f"🔧 Run Command: {command}"
        cl.Step(name=display_name, type="tool")

        command = command.encode("utf-8").decode("unicode_escape")

        try:
            # Handle cd commands specially
            if command.strip().startswith("cd "):
                new_dir = command.strip()[3:].strip()
                # Handle relative paths
                if not os.path.isabs(new_dir):
                    new_dir = os.path.join(self.current_dir, new_dir)
                new_dir = os.path.abspath(new_dir)

                if os.path.exists(new_dir):
                    self.current_dir = new_dir
                    return f"Changed directory to: {self.current_dir}"
                else:
                    return f"Directory not found: {new_dir}"

            # For all other commands, run them in the current directory
            process = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
                cwd=self.current_dir,  # Use current directory
            )

            output = process.stdout
            error = process.stderr

            if process.returncode != 0:
                return f"Command failed with error:\n{error}"

            return output if output else "Command executed successfully (no output)"

        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @cl.step(type="tool")
    async def get_current_dir(self, unused_param: str = None) -> str:
        """Get the current working directory"""
        display_name = "📂 Get Current Directory"
        cl.Step(name=display_name, type="tool")
        return self.current_dir

    # Create wrapper functions for non-async calls
    def _start_process(self, command: str) -> str:
        return asyncio.run(self.start_process(command))

    def _get_latest_output(self, process_id: str) -> str:
        return asyncio.run(self.get_latest_output(process_id))

    def _stop_process(self, process_id: str) -> str:
        return asyncio.run(self.stop_process(process_id))

    def _run_command(self, command: str) -> str:
        return asyncio.run(self.run_command(command))

    def _get_current_dir(self, unused_param: str = None) -> str:
        return asyncio.run(self.get_current_dir(unused_param))

    def create_agent(self) -> Agent:
        """Create and return a Swarm Agent with CLI capabilities"""
        return Agent(
            name="CLI Helper",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a helpful AI assistant for managing CLI processes and executing commands.
            You can:
            1. Start long-running processes (like servers) and monitor their output
            2. Execute one-off commands and get their results
            3. Stop running processes when needed
            4. Change and track the current working directory
            
            You understand common development commands and can help with:
            - Git operations
            - File system operations
            - Package management (npm, pip, etc)
            - Development servers
            - Build processes
            - Directory navigation
            
            When running commands that need a specific directory:
            1. First check the current directory with get_current_dir
            2. Use 'cd' to change to the needed directory
            3. Then run your command
            
            Always provide clear feedback about command execution and any errors encountered.
            Be careful with destructive commands and ask for confirmation when needed.""",
            functions=[
                self._start_process,
                self._get_latest_output,
                self._stop_process,
                self._run_command,
                self._get_current_dir,
            ],
        )

    def close(self):
        """Stop all running processes"""
        for process_id in list(self.processes.keys()):
            self._stop_process(process_id)

    def __del__(self):
        """Cleanup processes"""
        self.close()
