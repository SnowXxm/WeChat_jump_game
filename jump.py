from __future__ import print_function, division
import os
import sys
import time
import math
import random
# import cv2 as cv
from PIL import Image

if_first_jump = True


def start_game(im):
    rgb_button_start = (0, 199, 119, 255)
    region_start_x = int(im.size[0])
    region_start_y = int(im.size[1])
    pixel_imgaine = im.load()  # 从PIL Load

    status_break = False
    for y in range(int(region_start_y * 1 / 2), region_start_y, 5):
        global pos_button_start
        if status_break:
            break
        for x in range(0, int(region_start_x * 1 / 2), 3):
            if im.getpixel((x, y)) == rgb_button_start:
                pos_button_start = (x, y)
                break

    os.system('adb shell input tap {x} {y}'.format(
        x=pos_button_start[0],
        y=pos_button_start[1]
    ))
    time.sleep(1.5)
    print('开始游戏！')


def find_target_board(im):
    pos_data = {
        'chessman_x': 0,
        'chessman_y': 0,
        'target_x': 0,
        'target_y': 0,
    }

    def get_chessman(im):
        chessman_x = [10000, 0]  # 最小值和最大值
        chessman_y = 0
        bounds_x = (int(im.size[0] * 1 / 7), int(im.size[0] * 6 / 7))
        bounds_y = (int(im.size[1] * 1 / 3), int(im.size[1] * 2 / 3))

        for y in range(bounds_y[0], bounds_y[1]):
            for x in range(bounds_x[0], bounds_x[1]):
                if ((50 < im.getpixel((x, y))[0] < 60) & \
                        (50 < im.getpixel((x, y))[1] < 60) & \
                        (50 < im.getpixel((x, y))[2] < 60)):
                    if x < chessman_x[0]:
                        chessman_x[0] = x
                        chessman_y = y
                    elif x > chessman_x[1]:
                        chessman_x[1] = x

        chessman_x = int(sum(chessman_x) / 2)
        return (chessman_x, chessman_y)

    def get_board(im):
        board_x = 0
        board_y = [10000, 0]
        bounds_y = (int(im.size[1] * 1 / 3), int(im.size[1] * 2 / 3))
        if pos_data['chessman_x'] > im.size[0] * 1 / 2:  # 棋子在屏幕右边,扫描左边
            bounds_x = (int(im.size[0] * 1 / 7), int(im.size[0] * 1 / 2))
        else:  # 棋子在屏幕左边，扫描右边
            bounds_x = (int(im.size[0] * 1 / 2), int(im.size[0] * 6 / 7))

        for x in range(bounds_x[0], bounds_x[1]):
            for y in range(bounds_y[0], bounds_y[1]):
                if (im.getpixel((x, y)) == im.getpixel((x, y + 200))) | (
                        im.getpixel((x, y)) == im.getpixel((x, y - 200))):
                    if (pos_data['chessman_x'] - 30 < x) | (x > pos_data['chessman_x'] + 30)| (y < pos_data['chessman_y'] - 60):
                        if y < board_y[0]:
                            board_y[0] = y
                            board_x = x
                        elif y > board_y[1]:
                            board_y[1] = y

        board_y = int(sum(board_y) / 2)
        return (board_x, board_y)

    def get_white_point(im):
        rgb_white_point = (245, 245, 245)
        bounds_x = (int(im.size[0] * 1 / 7), int(im.size[0] * 6 / 7))
        bounds_y = (int(im.size[1] * 1 / 3),(int(im.size[1] * 2 / 3)))

        for y in range(bounds_y[0], bounds_y[1]):
            for x in range(bounds_x[0], bounds_x[1]):
                if im.getpixel((x, y))[:3] == rgb_white_point:
                    return (x + 15, y)

        return None

    # 第一次开始的话，减少不必要的推算。
    if if_first_jump == True:
        chessman = get_chessman(im)
        board = get_board(im)
        pos_data['chessman_x'] = chessman[0]
        pos_data['chessman_y'] = chessman[1]
        pos_data['target_x'] = board[0]
        pos_data['target_y'] = board[1]
        return pos_data
    else:
        chessman = get_chessman(im)
        white_point = get_white_point(im)
        pos_data['chessman_x'] = chessman[0]
        pos_data['chessman_y'] = chessman[1]
        if white_point == None:
            board = get_board(im)
            pos_data['target_x'] = board[0]
            pos_data['target_y'] = board[1]
        else:
            pos_data['target_x'] = white_point[0]
            pos_data['target_y'] = white_point[1]
        return pos_data


def leap_of_faith(distance, press_pos):
    global if_first_jump
    #print(distance)
    press_coefficient = 1.636  # 按压时间系数，可能需要调节
    press_time = max(int(distance * press_coefficient), 300)  # 设置 300ms 是最小的按压时间
    os.system('adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=press_pos[0],
        y1=press_pos[1],
        x2=press_pos[0],
        y2=press_pos[1],
        duration=press_time
    ))
    if_first_jump = False if if_first_jump == True else None
    time.sleep(random.uniform(0.7, 1.2))


def check_screenshot():
    if os.path.isfile('jump.png'):
        os.remove('jump.png')
    pull_screenshot()
    Image.open('./1.png').load()


def pull_screenshot():
    os.system('adb shell screencap -p /sdcard/jump.png')
    os.system('adb pull /sdcard/jump.png')


def main():
    pull_screenshot()
    start_game(Image.open('./jump.png'))
    while True:
        pull_screenshot()
        im = Image.open('./jump.png')
        data = find_target_board(im)
        print(data)
        leap_of_faith(abs((abs(data['chessman_x'] - data['target_x']) ** 2) - (
                    abs(data['chessman_y'] - data['target_y']) ** 2)) ** 0.5,
                      (int(im.size[0] / 2), int(im.size[1] / 2)))


main()
