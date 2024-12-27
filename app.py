import chainlit as cl
from swarm import Swarm
from agents.file_agent import FileAgent
from agents.sql_agent import SQLAgent
from agents.selenium_agent import SeleniumAgent
from agents.cli_agent import CLIAgent
import os

# Initialize Swarm client
client = Swarm()

# Create agents
cli_agent = CLIAgent()

# Choose which agent to use (you can modify this based on your needs)
agent = cli_agent.create_agent()

# Store conversation history
conversation_history = {}


@cl.on_chat_start
async def on_chat_start():
    conversation_history[cl.user_session.get("id")] = []


@cl.on_message
async def main(message: cl.Message):
    session_id = cl.user_session.get("id")
    messages = conversation_history[session_id]
    messages.append({"role": "user", "content": message.content})

    try:
        response = client.run(agent=agent, messages=messages)
        messages.extend(response.messages)
        conversation_history[session_id] = messages
        await cl.Message(content=response.messages[-1]["content"]).send()
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


@cl.on_stop
def on_stop():
    cli_agent.close()
