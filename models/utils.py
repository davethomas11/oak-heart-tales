# models/utils.py
from dataclasses import dataclass

def clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))

def xp_to_next_level(level: int) -> int:
    # Simple quadratic curve
    return 50 + (level * level * 25)