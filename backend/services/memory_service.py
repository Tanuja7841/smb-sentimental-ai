import json
from pathlib import Path

MEMORY_FILE = Path("backend/data/agent_memory.json")


def load_memory():

    if not MEMORY_FILE.exists():

        return []

    with open(MEMORY_FILE, "r") as file:

        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:

        json.dump(memory, file, indent=4)


def add_memory(agent, customer, event, severity):

    memory = load_memory()

    # CHECK DUPLICATES

    for item in reversed(memory):

        if (
            item["agent"] == agent
            and item["customer"] == customer
            and item["event"] == event
        ):

            print("Duplicate memory detected. Skipping.")

            return

    # ADD NEW MEMORY

    memory.append({
        "agent": agent,
        "customer": customer,
        "event": event,
        "severity": severity
    })

    with open(MEMORY_FILE, "w") as file:

        json.dump(memory, file, indent=4)