__version__ = "0.2.0"

from pooltool import terminal
from pooltool.ani.animate import FrameStepper, Game, ShotViewer
from pooltool.ani.image import (
    GzipArrayImages,
    HDF5Images,
    ImageZip,
    NpyImages,
    image_stack,
    save_images,
)
from pooltool.events import (
    Agent,
    AgentType,
    Event,
    EventType,
    ball_ball_collision,
    ball_circular_cushion_collision,
    ball_linear_cushion_collision,
    ball_pocket_collision,
    filter_ball,
    filter_time,
    filter_type,
    get_next_transition_event,
    null_event,
    resolve_event,
    rolling_spinning_transition,
    rolling_stationary_transition,
    sliding_rolling_transition,
    spinning_stationary_transition,
    stick_ball_collision,
)
from pooltool.evolution import simulate
from pooltool.layouts import (
    get_eight_ball_rack,
    get_nine_ball_rack,
    get_three_cushion_rack,
)
from pooltool.objects import (
    Ball,
    BallHistory,
    BallOrientation,
    BallParams,
    BallState,
    BilliardTableSpecs,
    CircularCushionSegment,
    Cue,
    CueSpecs,
    CushionDirection,
    CushionSegments,
    LinearCushionSegment,
    Pocket,
    PocketTableSpecs,
    Table,
    TableModelDescr,
    TableType,
)
from pooltool.system import MultiSystem, System, SystemController, multisystem, visual

run = terminal.Run()
progress = terminal.Progress()


__all__ = [
    "get_eight_ball_rack",
    "get_nine_ball_rack",
    "get_three_cushion_rack",
    "System",
    "MultiSystem",
    "multisystem",
    "SystemController",
    "visual",
    "filter_ball",
    "filter_time",
    "filter_type",
    "FrameStepper",
    "resolve_event",
    "null_event",
    "ball_ball_collision",
    "ball_linear_cushion_collision",
    "ball_circular_cushion_collision",
    "ball_pocket_collision",
    "stick_ball_collision",
    "spinning_stationary_transition",
    "rolling_stationary_transition",
    "rolling_spinning_transition",
    "sliding_rolling_transition",
    "get_next_transition_event",
    "Event",
    "EventType",
    "AgentType",
    "Agent",
    "Ball",
    "BallState",
    "BallParams",
    "BallHistory",
    "BallOrientation",
    "CueSpecs",
    "Cue",
    "Pocket",
    "LinearCushionSegment",
    "CircularCushionSegment",
    "CushionSegments",
    "CushionDirection",
    "ImageZip",
    "HDF5Images",
    "GzipArrayImages",
    "NpyImages",
    "Table",
    "TableModelDescr",
    "TableType",
    "PocketTableSpecs",
    "BilliardTableSpecs",
    "Game",
    "save_images",
    "image_stack",
    "ShotViewer",
    "simulate",
]
