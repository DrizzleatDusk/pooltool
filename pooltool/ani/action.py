#! /usr/bin/env python

from pooltool.utils.strenum import StrEnum, auto


class Action(StrEnum):
    aim = auto()
    rotate_cue_left = auto()
    rotate_cue_right = auto()
    exit = auto()
    power = auto()
    elevation = auto()
    english = auto()
    fine_control = auto()
    exec_shot = auto()
    call_shot = auto()
    ball_in_hand = auto()
    adjust_head = auto()
    move = auto()
    prev_shot = auto()
    next_shot = auto()
    show_help = auto()
    new_game = auto()
    toggle_pause = auto()
    restart_ani = auto()
    undo_shot = auto()
    cam_save = auto()
    cam_load = auto()
    slow_down = auto()
    speed_up = auto()
    rewind = auto()
    regain_control = auto()
    fast_forward = auto()
    stroke = auto()
    pick_ball = auto()
    quit = auto()
    close_scene = auto()
    view = auto()
    zoom = auto()
    introspect = auto()
    hide_cue = auto()
    parallel = auto()
    scroll_up = auto()
    scroll_down = auto()
