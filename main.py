import chainlit as cl
from swarm import Swarm
from agents.orchestrator_agent import OrchestratorAgent
from agents.developer_agent import DeveloperAgent
from agents.test_agent import TestAgent
import os
import logging

# Initialize Swarm client
client = Swarm()

# Store conversation history and agents
conversation_history = {}
agent_instances = {}


def setup_agents():
    # Create agents (note: circular references handled through init)
    test_agent = TestAgent(orchestrator_agent=None)
    dev_agent = DeveloperAgent(test_agent=test_agent)
    orchestrator_agent = OrchestratorAgent(dev_agent=dev_agent, test_agent=test_agent)
    dev_agent.orchestrator_agent = orchestrator_agent

    # Set orchestrator reference in test agent
    test_agent.orchestrator_agent = orchestrator_agent

    # Create the actual agents
    test_agent = test_agent.create_agent()
    dev_agent = dev_agent.create_agent()
    orchestrator_agent = orchestrator_agent.create_agent()

    return orchestrator_agent, dev_agent, test_agent


@cl.on_chat_start
async def on_chat_start():
    # Setup agents for this session
    session_id = cl.user_session.get("id")
    orchestrator_agent, dev_agent, test_agent = setup_agents()

    # Store all agents for this session
    agent_instances[session_id] = {
        "orchestrator": orchestrator_agent,
        "developer": dev_agent,
        "tester": test_agent,
        "current": orchestrator_agent,  # Start with orchestrator
    }

    # Initialize conversation history
    conversation_history[session_id] = []

    # Send welcome message
    await cl.Message(
        content="I'm ready to help with web development tasks. I'll coordinate between development and testing as needed."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    session_id = cl.user_session.get("id")
    messages = conversation_history[session_id]
    current_agent_name = agent_instances[session_id]["current"].name
    messages.append(
        {"role": "user", "content": f"{message.content}\nYou're {current_agent_name}"}
    )

    try:
        # Get current agent
        current_agent = agent_instances[session_id]["current"]

        # Run the agent
        response = client.run(
            agent=current_agent, messages=messages, debug=True  # Enable debug logging
        )

        logging.warning(f"Full response object: {response}")
        logging.warning(f"Response messages: {response.messages}")

        # Check if agent wants to transfer control
        last_tool_calls = None
        for msg in response.messages:
            if msg.get("tool_calls"):
                last_tool_calls = msg["tool_calls"]
                logging.warning(f"Found tool calls: {last_tool_calls}")

        # Handle agent transfers
        if last_tool_calls:
            for tool_call in last_tool_calls:
                name = tool_call["function"]["name"]
                logging.warning(f"Processing tool call: {name}")

                if name == "_transfer_to_dev_agent":
                    agent_instances[session_id]["current"] = agent_instances[
                        session_id
                    ]["developer"]
                    await cl.Message(
                        content="🔄 Transferring to Developer Agent..."
                    ).send()

                elif name == "_transfer_to_test_agent":
                    agent_instances[session_id]["current"] = agent_instances[
                        session_id
                    ]["tester"]
                    await cl.Message(
                        content="🔄 Transferring to Testing Agent..."
                    ).send()

                elif name == "_transfer_to_orchestrator":
                    agent_instances[session_id]["current"] = agent_instances[
                        session_id
                    ]["orchestrator"]
                    await cl.Message(
                        content="🔄 Transferring back to Orchestrator..."
                    ).send()

        # Update conversation history
        messages.extend(response.messages)
        conversation_history[session_id] = messages

        # Send all response messages
        if response.messages:
            for message in response.messages:
                if message.get("content"):
                    await cl.Message(content=message["content"]).send()
        else:
            await cl.Message(content="No response received").send()

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logging.error(error_msg)
        await cl.Message(content=error_msg).send()


@cl.on_stop
def on_stop():
    # Cleanup for the session
    session_id = cl.user_session.get("id")
    if session_id in agent_instances:
        # Close any resources if needed
        del agent_instances[session_id]
    if session_id in conversation_history:
        del conversation_history[session_id]
