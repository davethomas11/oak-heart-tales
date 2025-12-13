class GameEvent:
    FOUND_WEAPON = "found_weapon"
    PICKED_UP_WEAPON = "weapon_picked_up"
    LEFT_WEAPON = "weapon_left"
    ENTERED_COMBAT = "entered_combat"
    EXITED_COMBAT = "exited_combat"
    ATTEMPT_MOVE = "attempt_move"
    CANT_MOVE = "cant_move"
    WEATHER_CHANGED = "weather_changed"
    DANGER_WARNING = "danger_warning"
    FOUND_SHOP = "found_shop"
    ENTERED_SHOP = "entered_shop"
    EXITED_SHOP = "exited_shop"
    SHOP_ITEM_NOT_FOUND = "shop_item_not_found"
    SHOP_NOT_ENOUGH_GOLD = "shop_not_enough_gold"
    SHOP_EMPTY = "shop_empty"
    BOUGHT_ITEM = "bought_item"
    MOVED = "moved"
    OOM = "out_of_mana"
    USED_SPELL = "used_spell"
    ATTACKED = "attacked"
    ENEMY_ATTACKED = "enemy_attacked"
    ENEMY_STUNNED = "enemy_stunned"
    ENEMY_RECOVERED = "enemy_recovered"
    USED_POTION = "used_potion"
    CAST_SPELL = "cast_spell"
    FAILED_FLEE = "failed_flee"
    HEALED = "healed"
    REGEN = "regen"
    RESTED = "rested"
    CANT_REST = "cant_rest"
    REST_INTERRUPTED = "rest_interrupted"
    LEVEL_UP = "level_up"
    INFO = "info"

    def __init__(self, event_type: str, payload: dict = None):
        self.event_type = event_type
        self.payload = payload or {}

    def __repr__(self):
        return f"<GameEvent type={self.event_type} payload={self.payload}>"


class EventManager:
    def __init__(self):
        self.listeners = []

    def subscribe(self, listener: callable):
        self.listeners.append(listener)

    def unsubscribe(self, listener: callable):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def emit(self, event: GameEvent):
        for listener in self.listeners:
            listener(event)
