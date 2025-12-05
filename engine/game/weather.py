# engine/game/weather.py
import time

class Weather:
    TYPES = ["Sunny", "Rainy", "Stormy", "Foggy", "Snowy"]

    def __init__(self):
        self.current = self._choice(self.TYPES)

    def _choice(self, items):
        # Simple pseudo-random choice using time
        t = int(time.time() * 1000)
        idx = t % len(items)
        return items[idx]

    def change(self):
        self.current = self._choice(self.TYPES)

    def effect(self):
        # Return a dict of effects based on current weather
        effects = {
            "Sunny": {},
            "Rainy": {"visibility": 0.2},
            "Stormy": {"encounter_rate": +0.2},
            "Foggy": {"visibility": 0.4},
            "Snowy": {"movement_penalty": +1},
        }
        return effects.get(self.current, {})

    def stuck_message(self):
        messages = {
            "Snowy": "Snowdrifts block your path ",
        }
        return messages.get(self.current, "The weather is unusual.")

    def describe(self):
        descriptions = {
            "Sunny": "The sun is shining brightly.",
            "Rainy": "It's raining steadily.",
            "Stormy": "A fierce storm is raging.",
            "Foggy": "Thick fog reduces visibility.",
            "Snowy": "Snow is falling gently.",
        }
        return descriptions.get(self.current, "The weather is indescribable.")