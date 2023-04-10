from pathlib import Path
from tkinter import filedialog, messagebox
import sys
import json

import pygame

from auraboros import global_  # noqa
from auraboros.gamescene import Scene, SceneManager
from auraboros.gametext import TextSurfaceFactory
from auraboros.utilities import AssetFilePath
from auraboros import engine
from auraboros.gameinput import Keyboard
from auraboros.ui import GameMenuSystem, GameMenuUI, MsgWindow

from dungeongen2 import GameDungeonMap, print_2dlist, int_to_str_in_2dlist

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


# def prepare_filedialog():
#     with tk.Tk() as root:
#         root.withdraw()


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
        self.generate_dungeon()
        self.minimap_x = global_.w_size[0] // 3
        self.minimap_y = global_.w_size[1] // 3
        self.minimap_square_size = 3
        self.square_size = 32
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_scroll_speed = {"left": 1, "up": 1, "right": 1, "down": 1}
        self.camera_scroll_accel = 1
        self.camera_scroll_max_speed = 24
        self.map_surface = pygame.Surface(
            (self.square_size*self.dungeon_map.width,
             self.square_size*self.dungeon_map.height))
        self.minimap_surface = pygame.Surface(global_.w_size)
        self.minimap_surface.set_colorkey((0, 0, 0))
        menusystem = GameMenuSystem()
        menusystem.add_menu_item(
            "resume_edit_mode", self.activate_edit_mode, text="Resume")
        menusystem.add_menu_item(
            "save_map_data", self.save_map_data_with_filedialog, text="Save")
        menusystem.add_menu_item(
            "load_map_data", self.load_map_data_with_filedialog, text="Load")
        menusystem.add_menu_item(
            "edit_terrain_map",
            lambda: self.switch_layer_of_map_data_to_edit("terrain"),
            text="Edit terrain_map")
        menusystem.add_menu_item(
            "edit_area_map",
            lambda: self.switch_layer_of_map_data_to_edit("area"),
            text="Edit area_map")
        self.keyboard["menu"] = Keyboard()
        self.keyboard["menu"].register_keyaction(
            pygame.K_a,
            0, 0, self.activate_edit_mode)
        self.keyboard["menu"].register_keyaction(
            pygame.K_UP,
            0, 8, menusystem.menu_cursor_up)
        self.keyboard["menu"].register_keyaction(
            pygame.K_DOWN,
            0, 8, menusystem.menu_cursor_down)
        self.keyboard["menu"].register_keyaction(
            pygame.K_z,
            0, 0, menusystem.do_selected_action)
        self.menuui = GameMenuUI(menusystem, textfactory)
        self.menuui.padding = 4
        self.playermenu_surface = pygame.Surface(global_.w_size)
        self.playermenu_surface.set_colorkey((0, 0, 0))
        self.msgbox = MsgWindow(textfactory.font())
        self.msgbox.padding = 4
        self.keyboard["edit"] = Keyboard()
        self.keyboard["edit"].register_keyaction(
            pygame.K_s,
            0, 0, self.show_menu)
        self.keyboard["edit"].register_keyaction(
            pygame.K_UP,
            0, 0, self.go_up_camera, self.decelerate_camera_speed_up)
        self.keyboard["edit"].register_keyaction(
            pygame.K_DOWN,
            0, 0, self.go_down_camera, self.decelerate_camera_speed_down)
        self.keyboard["edit"].register_keyaction(
            pygame.K_RIGHT,
            0, 0, self.go_right_camera, self.decelerate_camera_speed_right)
        self.keyboard["edit"].register_keyaction(
            pygame.K_LEFT,
            0, 0, self.go_left_camera, self.decelerate_camera_speed_left)
        self.activate_edit_mode()
        self.switch_layer_of_map_data_to_edit("terrain")
        self.calculate_square_selector_pos()
        self.pen_square_id = 0
        self.dragging_camera = False

    def save_map_data_with_filedialog(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", ".json")])
        if file_path:
            data_to_restore = {}
            data_to_restore["terrain"] = self.dungeon_map.terrain_map
            data_to_restore["area"] = self.dungeon_map.area_map
            with open(file_path, 'w') as f:
                json.dump(data_to_restore, f)

    def load_map_data_with_filedialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON", ".json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data_to_restore = json.load(f)
                    self.dungeon_map.terrain_map = data_to_restore["terrain"]
                    self.dungeon_map.area_map = data_to_restore["area"]
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to load map data.")

    def generate_dungeon(self):
        self.dungeon_map = GameDungeonMap(56, 34)

    def switch_layer_of_map_data_to_edit(self, layer_to_switch: str):
        if layer_to_switch == "terrain":
            self.current_layer_to_edit = "terrain"
        if layer_to_switch == "area":
            self.current_layer_to_edit = "area"

    def map_data_by_current_layer(self) -> list[list]:
        if self.current_layer_to_edit == "terrain":
            map_data = self.dungeon_map.terrain_map
        elif self.current_layer_to_edit == "area":
            map_data = self.dungeon_map.area_map
        return map_data

    def edit_map_data_of_current_layer(self, x, y, square):
        if self.current_layer_to_edit == "terrain":
            self.dungeon_map.terrain_map[y][x] = square
        elif self.current_layer_to_edit == "area":
            self.dungeon_map.area_map[y][x] = square

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

    def activate_edit_mode(self):
        self.control_mode = "edit"
        self.keyboard.set_current_setup("edit")

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

    def show_menu(self):
        self.control_mode = "menu"
        self.keyboard.set_current_setup("menu")

    def calculate_square_selector_pos(self):
        self.square_selector_pos = [
            self.square_size *
            ((pygame.mouse.get_pos()[0] + self.camera_offset_x)
             // self.square_size)
            - self.camera_offset_x,
            self.square_size *
            ((pygame.mouse.get_pos()[1] + self.camera_offset_y)
             // self.square_size)
            - self.camera_offset_y]

    def paint_map_data_by_mousepos(self):
        if self.is_pos_on_map(pygame.mouse.get_pos()):
            self.edit_map_data_of_current_layer(
                (pygame.mouse.get_pos()[0] + self.camera_offset_x)
                // self.square_size,
                (pygame.mouse.get_pos()[1] + self.camera_offset_y)
                // self.square_size,
                self.pen_square_id)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.paint_map_data_by_mousepos()
            if event.button == 2:
                self.dragging_camera = True
                self.drag_start_pos = pygame.mouse.get_pos()
            elif event.button == 4:
                self.pen_square_id += 1
            elif event.button == 5:
                if self.pen_square_id > 0:
                    self.pen_square_id -= 1
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                self.dragging_camera = False
                self.drag_start_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                self.paint_map_data_by_mousepos()
            if self.dragging_camera:
                dx = event.pos[0] - self.drag_start_pos[0]
                dy = event.pos[1] - self.drag_start_pos[1]
                self.camera_offset_x -= dx
                self.camera_offset_y -= dy
                self.drag_start_pos = event.pos
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
        self.menuui.set_pos_to_center()
        if self.control_mode == "menu":
            self.msgbox.text = "(press a to close menu)"
        elif self.control_mode == "edit":
            self.msgbox.text = "control camera with ←↑→↓" + \
                "(press s for menu) | " + \
                str(self.current_layer_to_edit) + " | " + \
                str(self.pen_square_id)
        # right_stick_axis_x = self.joystick_.get_axis(2)
        # right_stick_axis_y = self.joystick_.get_axis(3)
        # if self.camera_mode:
        #     self.keyboard = self.keyboard["camera"]
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
        #     self.keyboard = self.keyboard["player"]
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_s, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_a, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_z, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_LEFT, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_UP, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_RIGHT, True)
        self.keyboard.current_setup.do_action_by_keyinput(pygame.K_DOWN, True)

    def is_pos_on_map(self, pos) -> bool:
        map_x = pos[0] + self.camera_offset_x
        map_y = pos[1] + self.camera_offset_y
        bool_x = 0 <= map_x < self.dungeon_map.width*self.square_size
        bool_y = 0 <= map_y < self.dungeon_map.height*self.square_size
        return bool_x and bool_y

    def draw(self, screen):
        self.calculate_square_selector_pos()
        char_size = textfactory.font().size(" ")
        self.map_surface.fill((0, 0, 0))
        self.minimap_surface.fill((0, 0, 0))
        self.playermenu_surface.fill((0, 0, 0))
        pygame.draw.rect(
            self.map_surface, (255, 255, 255),
            (0, 0, self.square_size*self.dungeon_map.width,
             self.square_size*self.dungeon_map.height,),
            1)
        for y, line in enumerate(self.map_data_by_current_layer()):
            for x, square in enumerate(line):
                if square > 0:
                    pygame.draw.rect(
                        self.map_surface, (0, 122, 0),
                        (self.square_size*x,
                         self.square_size*y,
                         self.square_size,
                         self.square_size), 1)
                    square_surface = textfactory.font().render(
                        str(square), True, (144, 0, 144))
                    self.map_surface.blit(
                        square_surface,
                        (self.square_size*x+char_size[0]//3,
                         self.square_size*y+char_size[1]//3))
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
        if self.control_mode == "menu":
            self.menuui.draw(self.playermenu_surface)
            screen.blit(self.playermenu_surface, (0, 0))
        self.msgbox.draw(screen)
        # pygame.draw.rect(
        #     screen, (0, 255, 255),
        #     (pygame.mouse.get_pos()[0]-self.square_size//3,
        #      pygame.mouse.get_pos()[1]-self.square_size//3,
        #      self.square_size,
        #      self.square_size), 1)
        # if 0+self.camera_offset_x <= pygame.mouse.get_pos()[0] \
        #         <= self.square_size+self.camera_offset_x:
        #     pygame.draw.rect(
        #         screen, (255, 255, 0),
        #         (0,
        #          0,
        #          self.square_size,
        #          self.square_size), 1)
        # print("camera_pos", self.camera_offset_x, self.camera_offset_y)
        # print("mouse_pos", pygame.mouse.get_pos())
        # print("selected_x", pygame.mouse.get_pos()[0] // self.square_size)
        # print("selected_y", pygame.mouse.get_pos()[1] // self.square_size)
        if self.is_pos_on_map(pygame.mouse.get_pos()):
            pygame.draw.rect(
                screen, (0, 255, 255),
                self.square_selector_pos
                + [self.square_size, self.square_size], 1)


scene_manager = SceneManager()
scene_manager.push(DungeonScene(scene_manager))

if __name__ == "__main__":
    engine.run(scene_manager=scene_manager)
