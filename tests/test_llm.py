from swarm import Swarm, Agent

client = Swarm()

agent = Agent(
    name="Agent",
    model="gemini/gemini-2.0-flash-exp",
    instructions="You are a helpful agent.",
)

messages = [{"role": "user", "content": "Hi!"}]
response = client.run(agent=agent, messages=messages)

print(response.messages[-1]["content"])
