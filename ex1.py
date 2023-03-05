from pathlib import Path
import sys

import pygame

from auraboros.gamescene import Scene, SceneManager
from auraboros import global_
from auraboros.global_ import init  # noqa
from auraboros.schedule import IntervalCounter
from auraboros.gametext import TextSurfaceFactory
from auraboros.utilities import AssetFilePath

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

pygame.init()

clock = pygame.time.Clock()

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))


class TitleMenuScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("hello_world", "Hello, World!")

    def update(self, dt):
        pass

    def draw(self, screen):
        textfactory.render("hello_world", screen, (16, 0))


def run(fps_num=60):
    global fps
    fps = fps_num
    running = True
    scene_manager = SceneManager()
    scene_manager.push(TitleMenuScene(scene_manager))
    while running:
        dt = clock.tick(fps)/1000  # dt means delta time

        global_.screen.fill((0, 0, 0))
        for event in pygame.event.get():
            running = scene_manager.event(event)

        scene_manager.update(dt)
        scene_manager.draw(global_.screen)
        pygame.transform.scale(global_.screen, global_.w_size_unscaled,
                               pygame.display.get_surface())
        pygame.display.update()
        IntervalCounter.tick(dt)
    pygame.quit()
