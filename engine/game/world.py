import math
import random

class Tile:
    def __init__(
            self,
            name: str,
            description: str,
            danger: float,
            safe: bool = False,
            ascii: str = None,
            shop: bool = False,
    ):
        self.name = name
        self.description = description
        self.danger = danger
        self.safe = safe
        self.ascii = ascii
        self.shop = shop

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "danger": self.danger,
            "safe": self.safe,
            "ascii": self.ascii,
            "shop": self.shop,
        }

    @staticmethod
    def from_dict(d: dict) -> "Tile":
        return Tile(
            name=d["name"],
            description=d["description"],
            danger=float(d["danger"] if "danger" in d else 0.0),
            safe=bool(d["safe"] if "safe" in d else False),
            ascii=d["ascii"],
            shop=bool(d["shop"] if "shop" in d else False),
        )


class World:
    def __init__(self, width: int, height: int, grid: list, seed: int = None):
        self.width = width
        self.height = height
        self.grid = grid
        self.seed = seed

    def get_tile(self, x: int, y: int) -> Tile:
        return self.grid[y][x]

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "grid": [[t.to_dict() for t in row] for row in self.grid],
        }

    def get_size(self) -> int:
        return self.width  # assuming square world

    @staticmethod
    def from_dict(d: dict) -> "World":
        width = int(d["width"])  # type: ignore
        height = int(d["height"])  # type: ignore
        seed = d.get("seed")
        grid = [[Tile.from_dict(td) for td in row] for row in d["grid"]]
        return World(width=width, height=height, grid=grid, seed=seed)

    @staticmethod
    def _default_tileset() -> dict:
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
        return default


    def _pseudoRandomSeed(seed) -> dict:
        x = math.sin(seed) * 10000
        rng = int((x - math.floor(x)) * 1000000)
        return {
            "choice": lambda lst: lst[rng % len(lst)],
            "randrange": lambda a, b: a + (rng % (b - a)),
            "shuffle": lambda lst: lst.sort(key=lambda _: rng)
        }

    @staticmethod
    def generate_random(size: int, tileset: dict, seed: int = None) -> "World":
        if tileset is None:
            tileset = World._default_tileset()
        # Create a world centered on a safe village, increasing danger with distance
        if seed is None:
            seed = random.randrange(1, 10_000_000)
        # For JS compatibility
        rng = World._pseudoRandomSeed(seed)
        #__pragma__('skip')
        rng = random.Random(seed)
        #__pragma__('noskip')
        base_tiles = tileset["tiles"]
        village_def = tileset["village"]

        width = height = size
        cx = width // 2
        cy = height // 2
        grid: list = []

        for y in range(height):
            row: list = []
            for x in range(width):
                if x == cx and y == cy:
                    row.append(Tile.from_dict(village_def))
                    continue
                # choose a random base tile
                td = rng.choice(base_tiles)
                # scale danger by Manhattan distance from center
                dist = abs(x - cx) + abs(y - cy)
                danger = float(td["danger"] if "danger" in td else 0.2)
                scaled = min(0.8, max(0.0, danger + dist * 0.05))
                row.append(Tile(name=td["name"], description=td["description"], danger=scaled, safe=False, ascii=td["ascii"]))
            grid.append(row)

        # Place a few random shops deterministically based on the seed
        # For JS compatibility
        rng2 = World._pseudoRandomSeed(seed)
        #__pragma__('skip')
        rng2 = random.Random(seed + 1337)
        #__pragma__('noskip')
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
