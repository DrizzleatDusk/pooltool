#! /usr/bin/env python
"""Constants and other

All units are SI unless otherwise stated.
"""

import numpy as np

numba_cache = True
np.set_printoptions(precision=10, suppress=True)
# tol = np.finfo(np.float).eps * 100
tol = 1e-12

# Ball states
stationary = 0
spinning = 1
sliding = 2
rolling = 3
pocketed = 4

state_dict = {
    0: "stationary",
    1: "spinning",
    2: "sliding",
    3: "rolling",
    4: "pocketed",
}

nontranslating = {stationary, spinning, pocketed}
energetic = {spinning, sliding, rolling}

# Taken from https://billiards.colostate.edu/faq/physics/physical-properties/
g = 9.8  # gravitational constant
m = 0.170097  # ball mass
R = 0.028575  # ball radius
u_s = 0.2  # sliding friction
u_r = 0.01  # rolling friction
u_sp = 10 * 2 / 5 * R / 9  # spinning friction
e_c = 0.85  # cushion coeffiient of restitution
f_c = 0.2  # cushion coeffiient of friction

english_fraction = 0.5

table_length = 1.9812  # 7-foot table (78x39 in^2 playing surface)
table_width = 1.9812 / 2  # 7-foot table (78x39 in^2 playing surface)
table_height = 0.708
lights_height = 1.99  # relative to playing surface
cushion_width = 2 * 2.54 / 100  # 2 inches x 2.54 cm/inch x 1/100 m/cm
cushion_height_fraction = 0.64
cushion_height = cushion_height_fraction * 2 * R
corner_pocket_width = 0.118
corner_pocket_angle = 5.3  # degrees
corner_pocket_depth = 0.0398
corner_pocket_radius = 0.124 / 2
corner_jaw_radius = 0.0419 / 2
side_pocket_width = 0.137
side_pocket_angle = 7.14  # degrees
side_pocket_depth = 0.00437
side_pocket_radius = 0.129 / 2
side_jaw_radius = 0.0159 / 2
