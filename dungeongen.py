# 0 = air
# 1 = room square
# 2 = wall
# 3 = water
# 4 = pathway square
from random import randint
import traceback
import sys


def generate_mapdata(width, height, square=0) -> list[list[int]]:
    """return list[y][x]"""
    return [[square for _ in range(width)] for _ in range(height)]


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


def make_room_at_random_on_mapdata(
        list_2d: list[list[int]], how_many: int, square,
        room_size_limit=None, try_limit=99, ) -> dict:
    """try_limit 部屋を作る際、既に作った部屋と重複した場合の再試行を行える回数"""
    map_width = len(list_2d[0])
    map_height = len(list_2d)
    making_log_list = []
    for _ in range(how_many):
        current_try = 0
        while True:
            retry = False
            current_try += 1
            # print("try: ", current_try)
            room_info = {"from_x": 0, "from_y": 0, "width": 0, "height": 0}
            room_info["from_x"] = randint(0, map_width-1)
            if room_size_limit:
                room_info["width"] = randint(
                    0, room_size_limit)
            else:
                room_info["width"] = randint(
                    0, map_width-1-room_info["from_x"])
            if room_info["from_x"]+room_info["width"] > map_width-1:
                room_info["width"] = 0
            room_info["from_y"] = randint(0, map_height-1)
            if room_size_limit:
                room_info["height"] = randint(
                    0, room_size_limit)
            else:
                room_info["height"] = randint(
                    0, map_height-1-room_info["from_y"])
            if room_info["from_y"]+room_info["height"] > map_height-1:
                room_info["height"] = 0
            for making_log in making_log_list:
                if (making_log["from_x"] <=
                    room_info["from_x"]+room_info["width"]
                    <= making_log["from_x"]+making_log["width"] or
                    making_log["from_y"] <=
                    room_info["from_y"]+room_info["height"]
                        <= making_log["from_y"]+making_log["height"]):
                    # print("reload")
                    retry = True
                else:
                    # print("ok")
                    retry = False
            if retry:
                if current_try < try_limit:
                    continue
                else:
                    break
            else:
                break
        fill_mapdata(list_2d, room_info["from_x"], room_info["from_y"],
                     room_info["width"], room_info["height"], square)
        making_log_list.append(
            {"from_x": room_info["from_x"], "from_y": room_info["from_y"],
             "width": room_info["width"], "height": room_info["height"]})
    return making_log_list


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
    # ---


def split_map_to_area(list_2d: list[list], num_of_area: int, area_min_size=3):
    # TODO implement when num of area >= 5
    height = len(list_2d)
    width = len(list_2d[0])
    area_map = generate_mapdata(width, height, 0)
    # v_split_pos = randint(0, height-1)  # pos of vertical split line
    v_split_pos = height-1
    # pos of horizontal split line
    h_split_pos = randint(area_min_size, width-1-area_min_size)
    home_pos = [0, 0]
    # recursion = 0
    for area_num in range(1, num_of_area+1):
        if area_num % 3 == 0:
            v_split_pos = randint(area_min_size, v_split_pos-area_min_size)
            fill_mapdata_pos_to_pos(
                area_map, home_pos[0], home_pos[1],
                width-1, v_split_pos, 3)
            # 右辺
            fill_mapdata(
                area_map, width-1, home_pos[1], 1, v_split_pos, 0)
            # 下底
            fill_mapdata(
                area_map, home_pos[0], v_split_pos,
                width-home_pos[0], 1, 0)
            h_split_pos = randint(
                h_split_pos+area_min_size, width-1-area_min_size)
        else:
            if area_num % 2 == 0:
                fill_mapdata_pos_to_pos(
                    area_map, h_split_pos+1, 0, width-1, v_split_pos, area_num)
                # 右辺
                fill_mapdata(
                    area_map, width-1, home_pos[1], 1, v_split_pos+1, 0)
                # 下底
                fill_mapdata(
                    area_map, h_split_pos, v_split_pos,
                    width-h_split_pos, 1, 0)
                home_pos[0] = h_split_pos+1
            else:
                fill_mapdata(area_map, home_pos[0], home_pos[0], h_split_pos+1,
                             v_split_pos+1, area_num)
                # 右辺
                fill_mapdata(
                    area_map, h_split_pos, home_pos[1], 1, v_split_pos+1, 0)
                # 下底
                fill_mapdata(
                    area_map, home_pos[0], v_split_pos, width, 1, 0)
            if area_num % 4 == 0:
                fill_mapdata(
                    area_map, h_split_pos, home_pos[1], 1, v_split_pos, 0)
        print("area:", area_num)
        print("home_pos:", home_pos)
        print("h_split_pos, v_split_pos:", h_split_pos, v_split_pos)
    return area_map


if __name__ == "__main__":
    conversion_dict = {0: " ", 1: ".", 2: "#", 3: "~", 4: ":"}
    conversion_dict_debug = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4"}
    dungeon_map_data = generate_mapdata(56, 34, 0)
    dungeon_area_data = split_map_to_area(dungeon_map_data, 4)
    # make_room_at_random_on_mapdata(dungeon_map_data, 4, 1, 10)
    map_to_display = convert_map_to_display(dungeon_map_data, conversion_dict)

    # print(map_to_display)
    # print_matrix(map_to_display)
    print_matrix(convert_map_to_display(
        dungeon_area_data, conversion_dict_debug))
