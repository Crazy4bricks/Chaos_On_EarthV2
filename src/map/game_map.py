from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator, Optional
from unittest import case

from tcod.console import Console
import numpy as np

from src.entity import Actor, Item
from src.map import tile_types

if TYPE_CHECKING:
    from src.engine import Engine
    from src.entity import Entity


class GameMap:
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((width, height), fill_value=False, order="F")  # Tiles the player has seen before

        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (entity for entity in self.entities if isinstance(entity, Actor) and entity.is_alive)

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_revealed_and_wall(self):
        """Return True if the tile is revealed and it's a wall."""
        wall = (self.tiles["wallglyph"] == True)
        is_revealed = self.visible | self.explored

        return wall & is_revealed

    def wall_glyph(self) -> np.ndarray:
        """Return the glyph for the wall at the given location."""
        revealed_wall = self.is_revealed_and_wall()

        north = np.roll(revealed_wall, 1, axis=1)
        south = np.roll(revealed_wall, -1, axis=1)
        west = np.roll(revealed_wall, 1, axis=0)
        east = np.roll(revealed_wall, -1, axis=0)

        mask = (
            (1 * north.astype(int)) + # North neighbor contributes 1
            (2 * south.astype(int)) + # South neighbor contributes 2
            (4 * west.astype(int)) + # West neighbor contributes 4
            (8 * east.astype(int))  # East neighbor contributes 8
        )

        glyph_lookup = np.array([
            ord("O"),
            ord("║"),
            ord("║"),
            ord("║"),
            ord("═"),
            ord("╝"),
            ord("╗"),
            ord("╣"),
            ord("═"),
            ord("╚"),
            ord("╔"),
            ord("╠"),
            ord("═"),
            ord("╩"),
            ord("╦"),
            ord("╬")
        ])

        wall_glyphs = glyph_lookup[mask]

        return wall_glyphs

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[
                self.visible,
                self.explored,
                ],
            choicelist=[
                self.tiles["light"],
                self.tiles["dark"],
            ],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from src.map.procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )
