from abc import ABC, abstractmethod

import pooltool.ani.tasks as tasks
from pooltool.ani.action import Action
from pooltool.utils.strenum import StrEnum, auto


class Mode(StrEnum):
    aim = auto()
    ball_in_hand = auto()
    calculate = auto()
    call_shot = auto()
    cam_load = auto()
    cam_save = auto()
    game_over = auto()
    menu = auto()
    pick_ball = auto()
    purgatory = auto()
    shot = auto()
    stroke = auto()
    view = auto()
    none = auto()


class BaseMode(ABC):
    keymap = None
    name = None

    def __init__(self):
        if self.keymap is None:
            raise NotImplementedError(
                "Subclasses of BaseMode must have 'keymap' attribute"
            )

        if self.name is None:
            raise NotImplementedError(
                "Subclasses of BaseMode must have 'name' attribute"
            )

        tasks.add(self.shared_task, "shared_task")
        tasks.add(self.cam_save_watch, "cam_save_watch")
        tasks.add(self.cam_load_watch, "cam_load_watch")
        tasks.add(self.help_watch, "help_watch")

    def shared_task(self, task):
        if self.keymap.get(Action.quit):
            self.keymap[Action.quit] = False
            self.close_scene()
            self.change_mode(Mode.menu)
        elif self.keymap.get(Action.introspect):
            self.keymap[Action.introspect] = False
            import pooltool as pt

            shot = self.shots.active
            import pdb

            pdb.set_trace()

        return task.cont

    def cam_save_watch(self, task):
        if self.keymap.get(Action.cam_save) and self.mode != Mode.cam_save:
            self.change_mode(Mode.cam_save)

        return task.cont

    def cam_load_watch(self, task):
        if self.keymap.get(Action.cam_load) and self.mode != Mode.cam_load:
            self.change_mode(Mode.cam_load)

        return task.cont

    def help_watch(self, task):
        if self.keymap.get(Action.show_help):
            self.keymap[Action.show_help] = False
            if self.help_node.is_hidden():
                self.help_node.show()
            else:
                self.help_node.hide()

        return task.cont

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass
