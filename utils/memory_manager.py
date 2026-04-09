import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            # ✅ FIX: ensure it's always dict
            if isinstance(data, dict):
                return data
            else:
                return {}

    except:
        return {}


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user_preferences(user_id):
    memory = load_memory()
    return memory.get(user_id, {})


def save_user_preferences(user_id, tone, language):
    memory = load_memory()

    if user_id not in memory:
        memory[user_id] = {}

    memory[user_id]["tone"] = tone
    memory[user_id]["language"] = language

    save_memory(memory)


def save_email_history(user_id, email):
    memory = load_memory()

    if user_id not in memory:
        memory[user_id] = {}

    history = memory[user_id].get("history", [])

    if not isinstance(history, list):
        history = []

    history.append(email)

    memory[user_id]["history"] = history[-5:]

    save_memory(memory)