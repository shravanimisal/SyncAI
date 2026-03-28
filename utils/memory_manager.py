import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def add_to_memory(sender, email, reply):
    memory = load_memory()
    memory.append({
        "sender": sender,
        "email": email,
        "reply": reply
    })
    save_memory(memory)


def get_context(sender, limit=3):
    memory = load_memory()
    user_memory = [m for m in memory if m["sender"] == sender]
    return user_memory[-limit:]