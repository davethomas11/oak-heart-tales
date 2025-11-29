from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
import random


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TILESET_FILE = os.path.join(DATA_DIR, "tileset.json")


@dataclass
class Tile:
    name: str
    description: str
    danger: float
    safe: bool = False
    ascii: Optional[str] = None  # filename of ascii art for this tile (relative to data/rooms)
    shop: bool = False  # indicates a shop is present on this tile

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "danger": self.danger,
            "safe": self.safe,
            "ascii": self.ascii,
            "shop": self.shop,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Tile":
        return Tile(
            name=d["name"],
            description=d.get("description", ""),
            danger=float(d.get("danger", 0.0)),
            safe=bool(d.get("safe", False)),
            ascii=d.get("ascii"),
            shop=bool(d.get("shop", False)),
        )


class World:
    def __init__(self, width: int, height: int, grid: List[List[Tile]], seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.grid = grid
        self.seed = seed

    def get(self, x: int, y: int) -> Tile:
        return self.grid[y][x]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "grid": [[t.to_dict() for t in row] for row in self.grid],
        }

    def get_size(self) -> int:
        return self.width  # assuming square world

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "World":
        width = int(d["width"])  # type: ignore
        height = int(d["height"])  # type: ignore
        seed = d.get("seed")
        grid = [[Tile.from_dict(td) for td in row] for row in d["grid"]]
        return World(width=width, height=height, grid=grid, seed=seed)

    @staticmethod
    def _load_tileset() -> Dict[str, Any]:
        # Provide a default tileset if file is missing
        default = {
            "village": {"name": "Oakheart Village", "description": "Your humble village. A safe haven.", "danger": 0.0, "safe": True},
            "tiles": [
                {"name": "Western Farms", "description": "Abandoned fields overrun with weeds.", "danger": 0.2},
                {"name": "Old Watchtower", "description": "A crumbling tower watches the valleys.", "danger": 0.3},
                {"name": "Frost Creek", "description": "Icy water murmurs over smooth stones.", "danger": 0.35},
                {"name": "Mire Flats", "description": "Boggy ground that sucks at your boots.", "danger": 0.45},
                {"name": "Gloomwood", "description": "Dark trees crowd the path. Eyes watch.", "danger": 0.55},
                {"name": "Ruined Keep", "description": "Broken walls hide shadows and secrets.", "danger": 0.6},
                {"name": "Northern Ridge", "description": "Wind-swept ridge with sparse pines.", "danger": 0.35},
                {"name": "Eastgate Road", "description": "A cobbled road lined with old mileposts.", "danger": 0.25},
            ]
        }
        try:
            with open(TILESET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # basic validation
                if "village" in data and "tiles" in data:
                    return data
        except FileNotFoundError:
            pass
        return default

    @staticmethod
    def generate_random(size: int, seed: Optional[int] = None) -> "World":
        # Create a world centered on a safe village, increasing danger with distance
        if seed is None:
            seed = random.randrange(1, 10_000_000)
        rng = random.Random(seed)
        tileset = World._load_tileset()
        base_tiles = tileset["tiles"]
        village_def = tileset["village"]

        width = height = size
        cx = width // 2
        cy = height // 2
        grid: List[List[Tile]] = []

        for y in range(height):
            row: List[Tile] = []
            for x in range(width):
                if x == cx and y == cy:
                    row.append(Tile.from_dict(village_def))
                    continue
                # choose a random base tile
                td = rng.choice(base_tiles)
                # scale danger by Manhattan distance from center
                dist = abs(x - cx) + abs(y - cy)
                danger = float(td.get("danger", 0.2))
                scaled = min(0.8, max(0.0, danger + dist * 0.05))
                row.append(Tile(name=td["name"], description=td.get("description", ""), danger=scaled, safe=False, ascii=td.get("ascii")))
            grid.append(row)

        # Place a few random shops deterministically based on the seed
        rng2 = random.Random(seed + 1337)
        num_shops = max(1, size // 3)
        placed = 0
        positions = [(x, y) for y in range(height) for x in range(width) if not (x == cx and y == cy)]
        rng2.shuffle(positions)
        for (sx, sy) in positions:
            if placed >= num_shops:
                break
            # Avoid clustering too close to village for variety
            dist = abs(sx - cx) + abs(sy - cy)
            if dist < 1:
                continue
            t = grid[sy][sx]
            # Convert this tile into a safe shop tile
            grid[sy][sx] = Tile(
                name="Merchant's Caravan",
                description="A traveling merchant offers wares and wisdom.",
                danger=0.0,
                safe=True,
                ascii=t.ascii,  # keep any ascii if present; renderer will fallback otherwise
                shop=True,
            )
            placed += 1

        return World(width=width, height=height, grid=grid, seed=seed)
