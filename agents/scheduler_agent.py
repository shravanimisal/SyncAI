def suggest_meeting_time(task):

    if "meeting" in task.get("task", "").lower():

        return "I am available tomorrow between 10 AM - 2 PM. Please confirm your preferred time."

    return None