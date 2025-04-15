from __future__ import annotations

from typing import TYPE_CHECKING
import lzma
import pickle

import numpy
from tcod.console import Console
from tcod.map import compute_fov

from src.message_log import MessageLog
from src import (
    exceptions,
    render_functions
)

if TYPE_CHECKING:
    from entity import Actor
    from src.map.game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )

        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

        self.game_map.tiles["dark"]["ch"] = numpy.select(
            condlist=[(self.game_map.visible|self.game_map.explored) & self.game_map.tiles["wallglyph"]],
            choicelist=[self.game_map.wall_glyph()],
            default=self.game_map.tiles["dark"]["ch"],
        )
        self.game_map.tiles["light"]["ch"] = numpy.select(
            condlist=[(self.game_map.visible|self.game_map.explored) & self.game_map.tiles["wallglyph"]],
            choicelist=[self.game_map.wall_glyph()],
            default=self.game_map.tiles["light"]["ch"],
        )

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
