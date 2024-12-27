import subprocess
import threading
import queue
import time

def test_process_output():
    print("Starting test...")
    
    # Create a queue for output
    output_queue = queue.Queue()
    
    # Function to read output
    def read_output(process):
        while True:
            if process.poll() is not None:  # Process finished
                break
            output = process.stdout.readline()
            if output:
                line = output.strip()
                print(f"Got output: {line}")
                output_queue.put(line)

    # Start a long-running process (e.g., npm start)
    print("Starting process...")
    process = subprocess.Popen(
        "npm run swall",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd="/home/zebleck/github/Cosmos/Cosmos-FrontEnd"  # Change this to your project path
    )
    
    # Start output reading thread
    thread = threading.Thread(target=read_output, args=(process,), daemon=True)
    thread.start()
    
    # Monitor output for a while
    try:
        print("Monitoring output...")
        for _ in range(30):  # Monitor for 30 seconds
            try:
                # Try to get output with timeout
                line = output_queue.get(timeout=1)
                print(f"Main thread got: {line}")
            except queue.Empty:
                print("No output in last second...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted...")
    finally:
        print("Cleaning up...")
        process.terminate()
        process.wait(timeout=5)
        print("Test finished!")

if __name__ == "__main__":
    test_process_output() 