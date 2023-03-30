from pathlib import Path
import sys

import pygame

from auraboros import global_  # noqa
from auraboros.gamescene import Scene, SceneManager
from auraboros.gametext import TextSurfaceFactory
from auraboros.utilities import AssetFilePath
from auraboros import engine
from auraboros.gameinput import Keyboard

import dungeongen

AssetFilePath.set_asset_root(Path(sys.argv[0]).parent / "assets")

engine.init(pixel_scale=1)

textfactory = TextSurfaceFactory()
textfactory.register_font(
    "misaki_gothic",
    pygame.font.Font(AssetFilePath.font("misaki_gothic.ttf"), 16))
textfactory.register_font(
    "ayu18mincho_9x18gm",
    pygame.font.Font(
        AssetFilePath.font("ayu18gothic-1.3a.tar/9x18gm.bdf"), 18))
textfactory.register_font(
    "k8x12S",
    pygame.font.Font(
        AssetFilePath.font("k8x12/k8x12S.ttf"), 24))


class TitleMenuScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textfactory.set_current_font("misaki_gothic")
        textfactory.register_text("hello_world", "Hello, World!")

    def update(self, dt):
        pass

    def draw(self, screen):
        textfactory.render("hello_world", screen, (16, 0))


class DungeonScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # textfactory.set_current_font("misaki_gothic")
        # textfactory.set_current_font("ayu18mincho_9x18gm")
        textfactory.set_current_font("k8x12S")
        textfactory.register_text("scout_camera", "見渡す")
        self.generate_dungeon()
        self.minimap_x = global_.w_size[0] // 3
        self.minimap_y = global_.w_size[1] // 3
        self.minimap_square_size = 3
        self.square_size = 32
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_scroll_speed = {"left": 1, "up": 1, "right": 1, "down": 1}
        self.camera_scroll_accel = 1  # constant
        self.camera_scroll_max_speed = 24
        self.map_surface = pygame.Surface(
            (self.square_size*self.map_width,
             self.square_size*self.map_height))
        self.minimap_surface = pygame.Surface(global_.w_size)
        self.minimap_surface.set_colorkey((0, 0, 0))
        self.keyboard["player"] = Keyboard()
        self.keyboard["player"].register_keyaction(
            pygame.K_s,
            0, 0, self.show_player_menu)
        self.keyboard["playermenu"] = Keyboard()
        self.keyboard["playermenu"].register_keyaction(
            pygame.K_a,
            0, 0, self.close_player_menu)
        self.keyboard["playermenu"].register_keyaction(
            pygame.K_UP,
            0, 0, self.playermenu_cursor_up)
        self.keyboard["playermenu"].register_keyaction(
            pygame.K_DOWN,
            0, 0, self.playermenu_cursor_down)
        self.keyboard.set_current_setup("player")
        # self.keyboard_setups = KeyboardSetupDict()
        # self.keyboard_setups["player"] = Keyboard()
        # self.keyboard_setups["player"].register_keyaction(
        #     pygame.K_s,
        #     0, 0, self.show_player_menu)
        # self.keyboard_setups["player"].register_keyaction(
        #     pygame.K_z,
        #     0, 0, self.activate_camera_mode)
        # self.keyboard_setups["camera"] = Keyboard()
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_UP,
        #     0, 0, self.go_up_camera, self.decelerate_camera_speed_up)
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_DOWN,
        #     0, 0, self.go_down_camera, self.decelerate_camera_speed_down)
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_RIGHT,
        #     0, 0, self.go_right_camera, self.decelerate_camera_speed_right)
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_LEFT,
        #     0, 0, self.go_left_camera, self.decelerate_camera_speed_left)
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_SPACE,
        #     2, 4, self.generate_dungeon)
        # self.keyboard_setups["camera"].register_keyaction(
        #     pygame.K_x,
        #     0, 0, self.cancel_camera_mode)
        # self.keyboard = self.keyboard_setups["player"]
        # self.joystick_ = pygame.joystick.Joystick(0)
        self.playermenu_surface = pygame.Surface(global_.w_size)
        self.playermenu_surface.set_colorkey((0, 0, 0))
        self.playermenu_is_showing = False
        self.playermenu_x = 32
        self.playermenu_y = 32
        self.playermenu_width = 32*4
        self.playermenu_height = 32*6
        self.playermenu_padding = 4
        self.menucursor_width = 10
        self.menucursor_height = 20
        self.control_mode = "player"
        self.menu_selected_index = 0
        self.menu_keys = ["inventory", "scout_camera", ]
        self.menu_actions = {"scout_camera": lambda: None}

    def generate_dungeon(self):
        self.map_width = 56
        self.map_height = 34
        dungeon_area_data, area_list = dungeongen.split_map_to_area(
            dungeongen.generate_mapdata(
                self.map_width, self.map_height, 0), 4)
        dungeon_area_data, room_list = dungeongen.make_room_in_area_map(
            dungeon_area_data, area_list)
        dungeongen.make_path_between_areas(
            dungeon_area_data, area_list, room_list, 5)
        self.map_data = dungeongen.convert_area_map_to_mapdata(
            dungeon_area_data)
        conversion_dict = {0: " ", 1: ".", 2: "#", 3: "~", 4: ":"}
        map_to_display = dungeongen.convert_map_to_display(
            self.map_data, conversion_dict)
        dungeongen.print_matrix(map_to_display)

    def go_up_camera(self):
        self.camera_offset_y -= self.camera_scroll_speed["up"]
        if self.camera_scroll_speed["up"] < self.camera_scroll_max_speed:
            self.camera_scroll_speed["up"] += self.camera_scroll_accel

    def go_down_camera(self):
        self.camera_offset_y += self.camera_scroll_speed["down"]
        if self.camera_scroll_speed["down"] < self.camera_scroll_max_speed:
            self.camera_scroll_speed["down"] += self.camera_scroll_accel

    def go_right_camera(self):
        self.camera_offset_x += self.camera_scroll_speed["right"]
        if self.camera_scroll_speed["right"] < self.camera_scroll_max_speed:
            self.camera_scroll_speed["right"] += self.camera_scroll_accel

    def go_left_camera(self):
        self.camera_offset_x -= self.camera_scroll_speed["left"]
        if self.camera_scroll_speed["left"] < self.camera_scroll_max_speed:
            self.camera_scroll_speed["left"] += self.camera_scroll_accel

    def activate_camera_mode(self):
        self.control_mode = "camera"

    def cancel_camera_mode(self):
        print("ssttoopp")
        self.control_mode = "player"

    def decelerate_camera_speed_left(self):
        if 1 < self.camera_scroll_speed["left"]:
            self.camera_scroll_speed["left"] -= self.camera_scroll_accel

    def decelerate_camera_speed_up(self):
        if 1 < self.camera_scroll_speed["up"]:
            self.camera_scroll_speed["up"] -= self.camera_scroll_accel

    def decelerate_camera_speed_right(self):
        if 1 < self.camera_scroll_speed["right"]:
            self.camera_scroll_speed["right"] -= self.camera_scroll_accel

    def decelerate_camera_speed_down(self):
        if 1 < self.camera_scroll_speed["down"]:
            self.camera_scroll_speed["down"] -= self.camera_scroll_accel

    def show_player_menu(self):
        self.control_mode = "playermenu"
        self.keyboard.set_current_setup("playermenu")

    def close_player_menu(self):
        print("cancel")
        self.control_mode = "player"
        self.keyboard.set_current_setup("player")

    def playermenu_cursor_up(self):
        if 0 < self.menu_selected_index:
            self.menu_selected_index -= 1

    def playermenu_cursor_down(self):
        if self.menu_selected_index < len(self.menu_keys)-1:
            self.menu_selected_index += 1

    def event(self, event):
        pass
        # right_stick_axis_x = self.joystick_.get_axis(2)
        # right_stick_axis_y = self.joystick_.get_axis(3)
        # if event.type == pygame.JOYAXISMOTION:
        #     if abs(right_stick_axis_x) > 0.1 or\
        #             abs(right_stick_axis_y) > 0.1:
        #         self.camera_mode = True
        #         self.close_player_menu()
        #     # if right_stick_axis_y > 0:
        #     #     self.go_down_camera()
        #   # r_stick_y = self.joystick_.get_axis(3)
        #     # print("r stick x:", right_stick_axis_x)
        # elif event.type == pygame.JOYBUTTONDOWN:
        #     print(event.button)
        # elif event.type == pygame.JOYBUTTONUP:
        #     print(event.button)
        # elif event.type == pygame.JOYHATMOTION:
        #     hat_pos = self.joystick_.get_hat(0)
        #     print(hat_pos)

    def update(self, dt):
        if self.control_mode == "player":
            pass
        elif self.control_mode == "playermenu":
            print(self.menu_selected_index)
            pass
        pass
        # right_stick_axis_x = self.joystick_.get_axis(2)
        # right_stick_axis_y = self.joystick_.get_axis(3)
        # if self.camera_mode:
        #     self.keyboard = self.keyboard_setups["camera"]
        #     self.keyboard.do_action_by_keyinput(pygame.K_UP)
        #     self.keyboard.do_action_by_keyinput(pygame.K_DOWN)
        #     self.keyboard.do_action_by_keyinput(pygame.K_RIGHT)
        #     self.keyboard.do_action_by_keyinput(pygame.K_LEFT)
        #     self.keyboard.do_action_by_keyinput(pygame.K_SPACE)
        #     self.keyboard.do_action_by_keyinput(pygame.K_x)
        #   if abs(right_stick_axis_y) > 0.1:
        #        self.keyboard.deactivate_keyup(pygame.K_UP)
        #        self.keyboard.deactivate_keyup(pygame.K_DOWN)
        #        if right_stick_axis_y > 0:
        #            self.go_down_camera()
        #        if right_stick_axis_y < 0:
        #            self.go_up_camera()
        #    else:
        #        self.keyboard.activate_keyup(pygame.K_UP)
        #        self.keyboard.activate_keyup(pygame.K_DOWN)
        #    if abs(right_stick_axis_x) > 0.1:
        #        self.keyboard.deactivate_keyup(pygame.K_RIGHT)
        #         self.keyboard.deactivate_keyup(pygame.K_LEFT)
        #       if right_stick_axis_x > 0:
        #            self.go_right_camera()
        #       if right_stick_axis_x < 0:
        #           self.go_left_camera()
        #   else:
        #      self.keyboard.activate_keyup(pygame.K_RIGHT)
        #      self.keyboard.activate_keyup(pygame.K_LEFT)
        # elif self.player_mode:
        #     print("player mode node")
        #     self.keyboard = self.keyboard_setups["player"]
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_s, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_a, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_z, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_UP, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_DOWN, True)

    def draw(self, screen):
        self.map_surface.fill((0, 0, 0))
        self.minimap_surface.fill((0, 0, 0))
        self.playermenu_surface.fill((0, 0, 0))
        pygame.draw.rect(
            self.map_surface, (255, 255, 255),
            (0, 0, self.square_size*self.map_width,
             self.square_size*self.map_height,),
            1)
        for y, line in enumerate(self.map_data):
            for x, square in enumerate(line):
                if square == 1 or square == 4:
                    pygame.draw.rect(
                        self.map_surface, (0, 122, 0),
                        (self.square_size*x,
                         self.square_size*y,
                         self.square_size,
                         self.square_size), 1)
                    pygame.draw.rect(
                        self.minimap_surface, (0, 122, 122),
                        (self.minimap_x+self.minimap_square_size*x,
                         self.minimap_y+self.minimap_square_size*y,
                         self.minimap_square_size-1,
                         self.minimap_square_size-1), 1)
        screen.blit(self.map_surface, (0, 0),
                    (self.camera_offset_x, self.camera_offset_y,
                     global_.w_size[0], global_.w_size[1]))
        screen.blit(self.minimap_surface, (0, 0))
        if self.control_mode == "playermenu":
            pygame.draw.rect(
                self.playermenu_surface, (200, 200, 255),
                (self.playermenu_x, self.playermenu_y,
                 self.playermenu_width, self.playermenu_height), 1)
            textfactory.render(
                "scout_camera", self.playermenu_surface,
                (self.menucursor_width*2+self.playermenu_x +
                 self.playermenu_padding,
                 self.playermenu_y+self.playermenu_padding))
            pygame.draw.polygon(
                self.playermenu_surface, (255, 255, 255),
                ((self.playermenu_x+self.playermenu_padding,
                  self.playermenu_y+self.playermenu_padding),
                 (self.playermenu_x +
                  self.playermenu_padding+self.menucursor_width,
                  self.playermenu_y +
                    self.playermenu_padding+self.menucursor_height//2),
                 (self.playermenu_x+self.playermenu_padding,
                  self.playermenu_y +
                  self.playermenu_padding+self.menucursor_height)))
            screen.blit(self.playermenu_surface, (0, 0))


# def run(fps_num=60):
#     global fps
#     fps = fps_num
#     running = True
#     scene_manager = SceneManager()
#     scene_manager.push(TitleMenuScene(scene_manager))
#     scene_manager.push(DungeonScene(scene_manager))
#     scene_manager.transition_to(1)
#     while running:
#         dt = clock.tick(fps)/1000  # dt means delta time

#         global_.screen.fill((0, 0, 0))
#         for event in pygame.event.get():
#             running = scene_manager.event(event)

#         scene_manager.update(dt)
#         scene_manager.draw(global_.screen)
#         pygame.transform.scale(global_.screen, global_.w_size_unscaled,
#                                pygame.display.get_surface())
#         pygame.display.update()
#         IntervalCounter.tick(dt)
#     pygame.quit()


scene_manager = SceneManager()
scene_manager.push(DungeonScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
