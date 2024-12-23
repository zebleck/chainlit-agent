import chainlit as cl
from swarm import Swarm
from agents.file_agent import FileAgent
from agents.sql_agent import SQLAgent
import os
import json

# Initialize Swarm client
client = Swarm()

# Create SQL agent
sql_agent = SQLAgent(os.environ["ODBC_CONNECTION_STRING"])
agent = sql_agent.create_agent()

# Store conversation history
conversation_history = {}


@cl.on_chat_start
async def on_chat_start():
    # Initialize empty conversation history for new session
    conversation_history[cl.user_session.get("id")] = []


@cl.on_message
async def main(message: cl.Message):
    # Get session ID
    session_id = cl.user_session.get("id")

    # Get conversation history for this session
    messages = conversation_history[session_id]

    # Add new user message
    messages.append({"role": "user", "content": message.content})

    # Add debug prints
    print("Calling Swarm with messages:", messages)
    response = client.run(agent=agent, messages=messages)
    print("Swarm response:", response)
    print("Response messages:", response.messages)

    # Update conversation history with assistant's response
    messages.extend(response.messages)
    conversation_history[session_id] = messages

    # Send the response back to Chainlit
    await cl.Message(content=response.messages[-1]["content"]).send()
