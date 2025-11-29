from datetime import datetime

class GameLog:
    def __init__(self, max_size=10):
        self.entries = []
        self.max_size = max_size

    def add_entry(self, entry):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entries.append((timestamp, entry))
        if len(self.entries) > self.max_size:
            self.entries.pop(0)
        return entry

    def get_recent_entries(self, count=10):
        return [f"{ts} - {msg}" for ts, msg in self.entries[-count:]]

    def clear(self):
        self.entries.clear()

    def __str__(self):
        return "\n".join(f"{ts} - {msg}" for ts, msg in self.entries)
