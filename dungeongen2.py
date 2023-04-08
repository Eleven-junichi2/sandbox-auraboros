# 0 = air
# 1 = room square
# 2 = pathway square
# 3 = water
# 4 = pathway square
# from collections import UserList
# from random import randint
# from typing import Tuple
# import sys
# import traceback

def generate_2dlist(size_1d, size_2d, item) -> list[list]:
    """Return two dimensional list filled given item."""
    return [[item for _ in range(size_2d)] for _ in range(size_1d)]


def fill_2dlist(list_2d: list[list],
                from_x: int, from_y: int, to_x: int, to_y: int,
                item_to_fill):
    for y in range(from_y, to_y+1):
        for x in range(from_x, to_x+1):
            list_2d[y][x] = item_to_fill


def convert_items_of_2dlist(
        list_2d: list[list],
        dict_to_convert: dict) -> list[list]:
    """
    Convert each items in the given list using the provided dictionary.

    Args:
        list_2d (list[list]): The 2D list to be converted.
        dict_to_convert (dict)

    Returns:
        list[list]

    Examples:
        >>> list_2d = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        >>> dict_to_convert = {0: "wall", 1: "path", 2: "room"}
        >>> convert_items_of_2dlist(list_2d, dict_to_convert)
        [["wall", "path", "room"],
         ["path", "room", "wall"],
         ["room", "wall", "path"]]
    """
    converted_2dlist = []
    for line in list_2d:
        converted_2dlist.append([dict_to_convert[item] for item in line])
    return converted_2dlist


def int_to_str_in_2dlist(list_2d: list[list[int]]) -> list[list[str]]:
    """
    Args:
        list_2d (list[list]): The 2D list to be converted.
        dict_to_convert (dict)

    Returns:
        list[list]

    Examples:
        >>> list_2d = [[1, 1, 2], [1, 1, 2], [1, 2, 2]]
        >>> convert_int_to_str_in_2dlist(list_2d)
        [["1", "1", "2"],
         ["1", "1", "2"],
         ["1", "2", "2"]]
    """
    converted_2dlist = []
    for line in list_2d:
        converted_2dlist.append([str(item) for item in line])
    return converted_2dlist


def convert_2dlist_to_print(
        list_2d: list[list[int]],
        conversion_dict: dict[int:str]) -> list[list[str]]:
    map_to_display = []
    for line in list_2d:
        map_to_display.append([conversion_dict[square] for square in line])
    return map_to_display


class GameDungeonMap:
    """
    マップを表すlistはlist[y][x]の形式
    area_map: 部屋の割当や通路引き等に使うダンジョン生成用の二次元list
    """

    def __init__(self, width=56, height=34):
        self.width = width
        self.height = height
        self.map_square_dict = {}
        self.map_object_dict = {}
        # self.area_map = []
        self._init_area_map()
        self._init_terrain_map()

    def _init_area_map(self):
        self.area_map = generate_2dlist(self.height, self.width, 0)

    def _init_terrain_map(self):
        self.terrain_map = generate_2dlist(self.height, self.width, 0)

    def fill_area_map(
            self, from_x: int, from_y: int,
            to_x: int, to_y: int, square_to_fill):
        fill_2dlist(
            self.area_map, from_x, from_y, to_x, to_y, square_to_fill)

    def fill_terrain_map(
            self, from_x: int, from_y: int,
            to_x: int, to_y: int, square_to_fill):
        fill_2dlist(
            self.terrain_map, from_x, from_y, to_x, to_y, square_to_fill)


def print_2dlist(list_2d: list[list], with_frame=False,
                 frame_vertical="-", frame_horizontal="|"):
    def print_frame_vertical(num_of_digit_vertical,
                             frame_vertical, frame_size_vertical, ):
        space_str = " "*(num_of_digit_vertical+1)
        print(space_str+frame_vertical *
              (frame_size_vertical*num_of_digit_vertical-3))
        space_str = " "
        print(space_str+frame_vertical*frame_size_vertical)
    if with_frame:
        frame_size_vertical = len(list_2d[0]) + 2
    else:
        frame_vertical = ""
        frame_horizontal = ""
    # -process to print-
    num_of_digit_vertical = len(str(len(list_2d[0])))
    num_of_digit_horizontal = len(str(len(list_2d)))
    if with_frame:
        print(" ", end="")
    print(" "*(num_of_digit_vertical), end="")
    if len(list_2d[0]) < 10:
        measure_vertical = "".join([str(i)
                                    for i in range(len(list_2d[0]))])
    else:
        measure_vertical = "".join(
            [str(i).ljust(num_of_digit_vertical)
                for i in range(len(list_2d[0]))])
    print(" "+measure_vertical)

    if with_frame:
        print_frame_vertical(num_of_digit_vertical,
                             frame_vertical, frame_size_vertical)
    for y_num, line in enumerate(list_2d):

        measure_horizontal = str(y_num).rjust(num_of_digit_horizontal)
        print(measure_horizontal, end="")
        print(frame_horizontal+" ", end="")
        print((" "*(num_of_digit_vertical-1)).join(line), end="")
        print(" "+frame_horizontal)
    if with_frame:
        print_frame_vertical(num_of_digit_vertical,
                             frame_vertical, frame_size_vertical)


if __name__ == "__main__":
    # conversion_dict = {0: " ", 1: ".", 2: "#", 3: "~", 4: ":"}
    dungeon_map = GameDungeonMap()
    print_2dlist(int_to_str_in_2dlist(dungeon_map.area_map))
