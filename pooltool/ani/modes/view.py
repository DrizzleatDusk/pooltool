#! /usr/bin/env python

import pooltool.ani.utils as autils

from pooltool.ani.modes import Mode, action

import numpy as np


class ViewMode(Mode):
    keymap = {
        action.aim: False,
        action.fine_control: False,
        action.move: True,
        action.quit: False,
        action.zoom: False,
    }


    def enter(self):
        self.mouse.hide()
        self.mouse.relative()
        self.mouse.track()

        self.task_action('escape', action.quit, True)
        self.task_action('mouse1', action.zoom, True)
        self.task_action('mouse1-up', action.zoom, False)
        self.task_action('a', action.aim, True)
        self.task_action('v', action.move, True)
        self.task_action('v-up', action.move, False)

        self.add_task(self.view_task, 'view_task')
        self.add_task(self.quit_task, 'quit_task')


    def exit(self):
        self.remove_task('view_task')
        self.remove_task('quit_task')


    def view_task(self, task):
        if self.keymap[action.aim]:
            enter_kwargs = dict(
                load_prev_cam = True
            )
            self.change_mode('aim', enter_kwargs=enter_kwargs)
        elif self.keymap[action.zoom]:
            self.zoom_camera_view()
        elif self.keymap[action.move]:
            self.move_camera_view()
        else:
            self.rotate_camera_view()

        return task.cont


    def zoom_camera_view(self):
        with self.mouse:
            s = -self.mouse.get_dy()*0.3

        self.cam.node.setPos(autils.multiply_cw(self.cam.node.getPos(), 1-s))


    def move_camera_view(self):
        with self.mouse:
            dxp, dyp = self.mouse.get_dx(), self.mouse.get_dy()

        # NOTE This conversion _may_ depend on how I initialized self.cam.focus
        h = self.cam.focus.getH() * np.pi/180 + np.pi/2
        dx = dxp * np.cos(h) - dyp * np.sin(h)
        dy = dxp * np.sin(h) + dyp * np.cos(h)

        f = 0.6
        self.cam.focus.setX(self.cam.focus.getX() + dx*f)
        self.cam.focus.setY(self.cam.focus.getY() + dy*f)


    def fix_cue_stick_to_camera(self):
        self.cue_stick.get_node('cue_stick_focus').setH(self.cam.focus.getH())


    def rotate_camera_view(self):
        if self.keymap[action.fine_control]:
            fx, fy = 2, 0
        else:
            fx, fy = 13, 3

        with self.mouse:
            alpha_x = self.cam.focus.getH() - fx * self.mouse.get_dx()
            alpha_y = max(min(0, self.cam.focus.getR() + fy * self.mouse.get_dy()), -90)

        self.cam.focus.setH(alpha_x) # Move view laterally
        self.cam.focus.setR(alpha_y) # Move view vertically


