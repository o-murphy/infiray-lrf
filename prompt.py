import threading
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt


# Function for the log thread
def log_thread(console):
    while True:
        # Simulate fetching logs (replace this with your actual log retrieval logic)
        logs = f"[cyan]Debug:[/cyan] Log message at {time.strftime('%H:%M:%S')}"

        # Display logs in the top panel
        console.print(Panel(logs, title="Logs", expand=False))

        # Sleep for a short duration (simulating some time passing between logs)
        time.sleep(2)


# Function for the input thread
def input_thread(console):
    while True:
        # Get user input in the bottom panel
        user_input = Prompt.ask("Enter something:", )

        # Display user input
        console.print(f"User Input: {user_input}", style="bold green")


# Create a console with a custom layout
console = Console()

# Create a layout with two rows: one for logs and one for input
layout = Layout()

# Add a panel for logs at the top
layout.split_row(
    Layout(name="logs", ratio=2),
)

# Add a panel for input at the bottom
layout.split_row(
    Layout(name="input", ratio=1),
)

# Add the layout to the console
console.layout = layout

# Start the log thread
log_thread = threading.Thread(target=log_thread, args=(console,))
log_thread.daemon = True
log_thread.start()

# Start the input thread
input_thread = threading.Thread(target=input_thread, args=(console,))
input_thread.daemon = True
input_thread.start()

# Wait for both threads to finish (not really applicable in this example)
log_thread.join()
input_thread.join()
