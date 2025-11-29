def _hp_line(label: str, cur: int, maxv: int) -> str:
    return f"{label}: {cur}/{maxv}"


def _enemy_defense_effect(base_def: int, down_amt: int, down_turns: int) -> int:
    return max(0, base_def - (down_amt if down_turns > 0 else 0))


def _clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))
