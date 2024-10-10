from typing import Tuple

import numpy as np
from numpy import sqrt, dot, array
import pooltool.constants as const
import pooltool.ptmath as ptmath
from pooltool.objects.ball.datatypes import Ball, BallState
from pooltool.physics.resolve.ball_ball.core import CoreBallBallCollision


def _resolve_ball_ball(rvw1, rvw2, R, m):
    r_i, v_i, omega_i = rvw1.copy()
    r_j, v_j, omega_j = rvw2.copy()

    r_i[2], r_i[1] = r_i[1], r_i[2]
    v_i[2], v_i[1] = v_i[1], 0
    omega_i[2], omega_i[1] = omega_i[1], omega_i[2]

    r_j[2], r_j[1] = r_j[1], r_j[2]
    v_j[2], v_j[1] = v_j[1], 0
    omega_j[2], omega_j[1] = omega_j[1], omega_j[2]

    v_i1, omega_i1, v_j1, omega_j1 = _collide_balls(r_i, v_i, omega_i, r_j, v_j, omega_j, R, m)

    omega_i1[1], omega_i1[2] = omega_i1[2], omega_i1[1]
    omega_j1[1], omega_j1[2] = omega_j1[2], omega_j1[1]

    rvw1[1,:2] = v_i1[::2]
    rvw1[2] = omega_i1
    rvw2[1,:2] = v_j1[::2]
    rvw2[2] = omega_j1
    return rvw1, rvw2


class FrictionalMathavan(CoreBallBallCollision):
    """
    Implements the ball-ball collision model described in: ::
      NUMERICAL SIMULATIONS OF THE FRICTIONAL COLLISIONS
      OF SOLID BALLS ON A ROUGH SURFACE
      S. Mathavan,  M. R. Jackson,  R. M. Parkin
      DOI: 10.1007/s12283-014-0158-y
      International Sports Engineering Association
      2014
    """
    def solve(self, ball1: Ball, ball2: Ball) -> Tuple[Ball, Ball]:
        rvw1, rvw2 = _resolve_ball_ball(
            ball1.state.rvw.copy(),
            ball2.state.rvw.copy(),
            ball1.params.R,
            ball1.params.m
        )

        ball1.state = BallState(rvw1, const.sliding)
        ball2.state = BallState(rvw2, const.sliding)

        return ball1, ball2


INF = float('inf')


def _collide_balls(r_i, v_i, omega_i,
                   r_j, v_j, omega_j,
                   R, M,
                   mu_s=0.21,
                   mu_b=0.05,
                   e=0.89,
                   deltaP=None,
                   return_all=False):
    r_ij = r_j - r_i
    r_ij_mag_sqrd = dot(r_ij, r_ij)
    # D = 2*R
    # assert  abs(r_ij_mag_sqrd - D**2) / D**2  <  1e-8, "abs(r_ij_mag_sqrd - D**2) / D**2 = %s" % (abs(r_ij_mag_sqrd - D**2) / D**2)
    r_ij_mag = sqrt(r_ij_mag_sqrd)
    z_loc = array([0, 1, 0], dtype=np.float64)
    y_loc = r_ij / r_ij_mag
    x_loc = array((-y_loc[2], 0, y_loc[0]))
    G = np.vstack((x_loc, y_loc, z_loc))
    v_ix, v_iy = dot(v_i, x_loc), dot(v_i, y_loc)
    v_jx, v_jy = dot(v_j, x_loc), dot(v_j, y_loc)
    omega_ix, omega_iy, omega_iz = dot(G, omega_i)
    omega_jx, omega_jy, omega_jz = dot(G, omega_j)
    u_iR_x, u_iR_y = v_ix + R*omega_iy, v_iy - R*omega_ix
    u_jR_x, u_jR_y = v_jx + R*omega_jy, v_jy - R*omega_jx
    u_iR_xy_mag = sqrt(u_iR_x**2 + u_iR_y**2)
    u_jR_xy_mag = sqrt(u_jR_x**2 + u_jR_y**2)
    u_ijC_x = v_ix - v_jx - R*(omega_iz + omega_jz)
    u_ijC_z = R*(omega_ix + omega_jx)
    u_ijC_xz_mag = sqrt(u_ijC_x**2 + u_ijC_z**2)
    v_ijy = v_jy - v_iy
    if deltaP is None:
        deltaP = 0.5 * (1 + e) * M * abs(v_ijy) / 1000
    deltaP__2 = 0.5 * deltaP
    W_f = INF
    W_c = None
    W = 0
    niters = 0
    if return_all:
        v_is = [array((v_ix, v_iy, 0))]
        v_js = [array((v_jx, v_jy, 0))]
        omega_is = [array((omega_ix, omega_iy, omega_iz))]
        omega_js = [array((omega_jx, omega_jy, omega_jz))]
    while v_ijy < 0 or W < W_f:
        # determine impulse deltas:
        if u_ijC_xz_mag < 1e-16:
            deltaP_1 = deltaP_2 = 0
            deltaP_ix = deltaP_iy = deltaP_jx = deltaP_jy = 0
        else:
            deltaP_1 = -mu_b * deltaP * u_ijC_x / u_ijC_xz_mag
            if abs(u_ijC_z) < 1e-16:
                deltaP_2 = 0
                deltaP_ix = deltaP_iy = deltaP_jx = deltaP_jy = 0
            else:
                deltaP_2 = -mu_b * deltaP * u_ijC_z / u_ijC_xz_mag
                if deltaP_2 > 0:
                    deltaP_ix = deltaP_iy = 0
                    if u_jR_xy_mag == 0:
                        deltaP_jx = deltaP_jy = 0
                    else:
                        deltaP_jx = -mu_s * (u_jR_x / u_jR_xy_mag) * deltaP_2
                        deltaP_jy = -mu_s * (u_jR_y / u_jR_xy_mag) * deltaP_2
                else:
                    deltaP_jx = deltaP_jy = 0
                    if u_iR_xy_mag == 0:
                        deltaP_ix = deltaP_iy = 0
                    else:
                        deltaP_ix = mu_s * (u_iR_x / u_iR_xy_mag) * deltaP_2
                        deltaP_iy = mu_s * (u_iR_y / u_iR_xy_mag) * deltaP_2
        # calc velocity changes:
        deltaV_ix = ( deltaP_1 + deltaP_ix) / M
        deltaV_iy = (-deltaP   + deltaP_iy) / M
        deltaV_jx = (-deltaP_1 + deltaP_jx) / M
        deltaV_jy = ( deltaP   + deltaP_jy) / M
        # calc angular velocity changes:
        _ = 5/(2*M*R)
        deltaOm_ix = _ * ( deltaP_2 + deltaP_iy)
        deltaOm_iy = _ * (-deltaP_ix)
        deltaOm_iz = _ * (-deltaP_1)
        deltaOm_j = _ * array([( deltaP_2 + deltaP_jy),
                               (-deltaP_jx),
                               (-deltaP_1)])
        # update velocities:
        v_ix += deltaV_ix
        v_jx += deltaV_jx
        v_iy += deltaV_iy
        v_jy += deltaV_jy
        # update angular velocities:
        omega_ix += deltaOm_ix
        omega_iy += deltaOm_iy
        omega_iz += deltaOm_iz
        omega_jx += deltaOm_j[0]
        omega_jy += deltaOm_j[1]
        omega_jz += deltaOm_j[2]
        # update ball-table slips:
        u_iR_x, u_iR_y = v_ix + R*omega_iy, v_iy - R*omega_ix
        u_jR_x, u_jR_y = v_jx + R*omega_jy, v_jy - R*omega_jx
        u_iR_xy_mag = sqrt(u_iR_x**2 + u_iR_y**2)
        u_jR_xy_mag = sqrt(u_jR_x**2 + u_jR_y**2)
        # update ball-ball slip:
        u_ijC_x = v_ix - v_jx - R*(omega_iz + omega_jz)
        u_ijC_z = R*(omega_ix + omega_jx)
        u_ijC_xz_mag = sqrt(u_ijC_x**2 + u_ijC_z**2)
        # increment work:
        v_ijy0 = v_ijy
        v_ijy = v_jy - v_iy
        deltaW = deltaP__2 * abs(v_ijy0 + v_ijy)
        W += deltaW
        niters += 1
        if return_all:
            v_is.append(array((v_ix, v_iy, 0)))
            v_js.append(array((v_jx, v_jy, 0)))
            omega_is.append(array((omega_ix, omega_iy, omega_iz)))
            omega_js.append(array((omega_jx, omega_jy, omega_jz)))
        if W_c is None and v_ijy > 0:
            W_c = W
            W_f = (1 + e**2) * W_c
            # niters_c = niters
            # _logger.debug('''
            # END OF COMPRESSION PHASE
            # W_c = %s
            # W_f = %s
            # niters_c = %s
            # ''', W_c, W_f, niters_c)
    # _logger.debug('''
    # END OF RESTITUTION PHASE
    # niters_r = %s
    # ''', niters - niters_c)
    if return_all:
        v_is = array(v_is)
        v_js = array(v_js)
        omega_is = array(omega_is)
        omega_js = array(omega_js)
        for i in range(len(v_is)):
            dot(G.T, v_is[i], out=v_is[i])
            dot(G.T, v_js[i], out=v_js[i])
            dot(G.T, omega_is[i], out=omega_is[i])
            dot(G.T, omega_js[i], out=omega_js[i])
        return v_is, omega_is, v_js, omega_js
    v_i = array((v_ix, v_iy, 0))
    v_j = array((v_jx, v_jy, 0))
    omega_i = array((omega_ix, omega_iy, omega_iz))
    omega_j = array((omega_jx, omega_jy, omega_jz))
    G_T = G.T
    return dot(G_T, v_i), dot(G_T, omega_i), dot(G_T, v_j), dot(G_T, omega_j)
