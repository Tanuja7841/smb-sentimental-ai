from services.memory_service import load_memory


def show_memory():

    memory = load_memory()

    print("\n=========== AGENT MEMORY ===========\n")

    for item in memory:

        print(item)