import json
import os

FILE = "analytics.json"


def load_data():
    if not os.path.exists(FILE):
        return {
            "total_emails": 0,
            "replies_sent": 0,
            "skipped": 0,
            "meetings": 0
        }

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "total_emails": 0,
            "replies_sent": 0,
            "skipped": 0,
            "meetings": 0
        }


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# 🔥 IMPORTANT FUNCTION (this was missing)
def increment(field):
    data = load_data()

    if field not in data:
        data[field] = 0

    data[field] += 1

    save_data(data)


def get_analytics():
    return load_data()