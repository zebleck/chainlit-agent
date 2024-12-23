import chainlit as cl
import matplotlib.pyplot as plt
import io


@cl.step(type="tool")
async def tool():
    # Fake tool
    await cl.sleep(2)
    return "#Response from the tool!"


async def create_plot():
    # Create a simple plot
    plt.figure(figsize=(10, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.title("Sample Plot")
    plt.xlabel("X axis")
    plt.ylabel("Y axis")
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Close the figure to free memory
    
    return buf


@cl.on_message
async def main(message: cl.Message):
    """
    This function is called every time a user inputs a message in the UI.
    It sends back a message with both text and a plot.

    Args:
        message: The user's message.

    Returns:
        None.
    """
    # Create a plot and get its bytes
    plot_bytes = await create_plot()
    
    # Create an image element from the plot bytes
    image = cl.Image(
        content=plot_bytes.getvalue(),
        name="plot",
        display="inline",
        size="large"
    )

    # Call the tool
    tool_res = await tool()

    # Send a message with both text and plot
    await cl.Message(
        content=f"{tool_res}\nHere's a plot for you!",
        elements=[image]
    ).send()