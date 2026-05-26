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

    memory.append({
        "agent": agent,
        "customer": customer,
        "event": event,
        "severity": severity
    })

    save_memory(memory)