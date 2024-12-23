import chainlit as cl
from swarm import Swarm
from file_agent import FileAgent
import os

# Initialize Swarm client
client = Swarm()

# Create file agent
file_agent = FileAgent()
agent = file_agent.create_agent()

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
    
    # Get response from Swarm
    response = client.run(agent=agent, messages=messages)
    
    # Update conversation history with assistant's response
    messages.extend(response.messages)
    conversation_history[session_id] = messages
    
    # Send the response back to Chainlit
    print(f"Session {session_id} - Assistant response: {response.messages[-1]['content']}")
    await cl.Message(content=response.messages[-1]["content"]).send()
