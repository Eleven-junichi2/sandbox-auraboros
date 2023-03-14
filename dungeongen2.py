# 0 = air
# 1 = room square
# 2 = wall
# 3 = water
# 4 = pathway square
# from collections import UserList
# from random import randint
# from typing import Tuple
# import sys
# import traceback

def generate_2dlist(size_1d, size_2d, item) -> list[list]:
    """return two dimensional list filled given item"""
    return [[item for _ in range(size_2d)] for _ in range(size_1d)]


class GameDungeonMap:
    """
    area_map: ダンジョン生成において部屋の割当や通路引きのために番号で区画分けしたマップ
    """

    def __init__(self):
        self.width = 56
        self.height = 34

    def generate_area_map(self):
        pass


def fill_mapdata(list_2d: list[list],
                 from_x: int, from_y: int, width: int, height: int,
                 item_to_fill_square):
    for y in range(from_y, from_y+height):
        for x in range(from_x, from_x+width):
            list_2d[y][x] = item_to_fill_square


def fill_mapdata_pos_to_pos(list_2d: list[list],
                            from_x: int, from_y: int, to_x: int, to_y: int,
                            item_to_fill_square):
    for y in range(from_y, to_y+1):
        for x in range(from_x, to_x+1):
            list_2d[y][x] = item_to_fill_square


def convert_map_to_display(
        list_2d: list[list[int]],
        conversion_dict: dict[int:str]) -> list[list[str]]:
    map_to_display = []
    for line in list_2d:
        map_to_display.append([conversion_dict[square] for square in line])
    return map_to_display


def print_matrix(list_2d: list[list], with_frame=False,
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
    conversion_dict = {0: " ", 1: ".", 2: "#", 3: "~", 4: ":"}
