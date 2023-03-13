# 0 = air
# 1 = room square
# 2 = wall
# 3 = water
# 4 = pathway square
from random import randint
from typing import Tuple
import sys
import traceback


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


def split_map_to_area(
        list_2d: list[list],
        num_of_area: int,
        area_min_size=3) -> Tuple[list[list[int]], list[dict]]:
    # TODO implement when num of area >= 5
    if num_of_area > 4:
        raise ValueError("num_of_area must be smaller than or equal to 4.")
    height = len(list_2d)
    width = len(list_2d[0])
    area_map = generate_mapdata(width, height, 0)
    # v_split_pos = randint(0, height-1)  # pos of vertical split line
    v_split_pos = height-1
    # pos of horizontal split line
    if num_of_area <= 2:
        h_split_pos = randint(area_min_size, width-1-area_min_size)
    else:
        h_split_pos = randint(
            area_min_size, width-2-area_min_size*(num_of_area-1))
    home_pos = [0, 0]
    area_list = []
    for area_num in range(1, num_of_area+1):
        if area_num % 3 == 0:
            v_split_pos = randint(area_min_size, v_split_pos-area_min_size-1)
            print("area_min_size, v_split_pos-area_min_size",
                  area_min_size, v_split_pos-area_min_size)
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
            try:
                h_split_pos = randint(
                    h_split_pos+area_min_size, width-2-area_min_size)
            except ValueError:
                traceback.print_exc()
                print("h_split_pos+area_min_size", h_split_pos+area_min_size)
                print("width-1-area_min_size", width-1-area_min_size)
                sys.exit(1)
        else:
            if area_num % 2 == 0:
                home_pos[0] = h_split_pos+1
                fill_mapdata_pos_to_pos(
                    area_map, home_pos[0], 0, width-1, v_split_pos, area_num)
                # 右辺
                fill_mapdata(
                    area_map, width-1, home_pos[1], 1, v_split_pos+1, 0)
                # 下底
                fill_mapdata(
                    area_map, h_split_pos, v_split_pos,
                    width-h_split_pos, 1, 0)
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
                # 左辺
                fill_mapdata(
                    area_map, h_split_pos, home_pos[1], 1, v_split_pos, 0)
    # -- collect area list --
    for area_num in range(1, num_of_area+1):
        # print(area_num)
        home_pos_was_found = False
        end_x_was_found = False
        for y, line in enumerate(area_map):
            for x, square in enumerate(line):
                if not home_pos_was_found and square == area_num:
                    home_pos_was_found = True
                    area_home_pos = (x, y)
                if not end_x_was_found and home_pos_was_found and square == 0:
                    end_x_was_found = True
                    end_x = x-1
                if end_x_was_found:
                    if x == end_x:
                        break
        for y, line in enumerate(area_map):
            if y >= area_home_pos[1]:
                if line[area_home_pos[0]] == 0:
                    # print("end_y", y-1)
                    end_y = y-1
                    break
        area_list.append(
            {"id": area_num, "home_pos": area_home_pos,
                "end_pos": (end_x, end_y)})
    return area_map, area_list


def make_room_in_area_map(
        area_map: list[list[int]], area_list: list[dict],
        min_room_width=2, min_room_height=2) -> list[list[int]]:
    map_width = len(area_map[0])
    map_height = len(area_map)
    new_area_map = generate_mapdata(map_width, map_height, 0)
    for area in area_list:
        try:
            from_x = randint(area["home_pos"][0],
                             area["end_pos"][0]-min_room_width)
            to_x = randint(from_x+min_room_width, area["end_pos"][0])
            from_y = randint(area["home_pos"][1],
                             area["end_pos"][1]-min_room_height)
            to_y = randint(from_y+min_room_height, area["end_pos"][1])
        except ValueError:
            traceback.print_exc()
            print("The area size is smaller than the given minimum room size.")
            print(area["home_pos"][1], area["end_pos"][1]-min_room_height)
            sys.exit(1)
        fill_mapdata_pos_to_pos(
            new_area_map, from_x, from_y, to_x, to_y, area["id"])
    return new_area_map


if __name__ == "__main__":
    conversion_dict = {0: " ", 1: ".", 2: "#", 3: "~", 4: ":"}
    conversion_dict_debug = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4"}
    dungeon_map_data = generate_mapdata(56, 34, 0)
    dungeon_area_data, area_list = split_map_to_area(dungeon_map_data, 4)
    dungeon_area_data = make_room_in_area_map(dungeon_area_data, area_list)
    map_to_display = convert_map_to_display(dungeon_map_data, conversion_dict)

    # print(map_to_display)
    # print_matrix(map_to_display)
    print_matrix(convert_map_to_display(
        dungeon_area_data, conversion_dict_debug))
    print(area_list)
