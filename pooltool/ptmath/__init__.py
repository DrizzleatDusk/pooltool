"""Math functions"""

import pooltool.ptmath.roots as roots
from pooltool.ptmath.utils import (
    angle,
    angle_between_vectors,
    are_points_on_same_side,
    convert_2D_to_3D,
    coordinate_rotation,
    cross,
    find_intersection_2D,
    get_ball_energy,
    get_roll_time,
    get_slide_time,
    get_spin_time,
    get_u_vec,
    is_overlapping,
    norm2d,
    norm3d,
    orientation,
    point_on_line_closest_to_point,
    rel_velocity,
    solve_transcendental,
    unit_vector,
    unit_vector_slow,
    wiggle,
)

__all__ = [
    "roots",
    "angle",
    "orientation",
    "angle_between_vectors",
    "coordinate_rotation",
    "cross",
    "norm3d",
    "solve_transcendental",
    "convert_2D_to_3D",
    "norm2d",
    "point_on_line_closest_to_point",
    "find_intersection_2D",
    "are_points_on_same_side",
    "unit_vector",
    "unit_vector_slow",
    "wiggle",
    "rel_velocity",
    "get_u_vec",
    "get_slide_time",
    "get_roll_time",
    "get_spin_time",
    "get_ball_energy",
    "is_overlapping",
]
