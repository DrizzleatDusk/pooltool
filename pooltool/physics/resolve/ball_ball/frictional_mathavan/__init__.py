"""An implementation of the Mathavan et al. (2014) ball-ball collision model.

The model "uses general theories of dynamics of spheres rolling on a flat surface and
general frictional impact dynamics under the assumption of point contacts between the
balls under collision and that of the table."

The authors compare the model predictions to experimental exit velocities and angles
measured with a high speed camera system and illustrate marked improvement over previous
theories, which unlike this model, fail to account for spin.

References:
    Mathavan, S., Jackson, M.R. & Parkin, R.M. Numerical simulations of the frictional
    collisions of solid balls on a rough surface. Sports Eng 17, 227–237 (2014).
    https://doi.org/10.1007/s12283-014-0158-y

    Available at
    https://billiards.colostate.edu/physics_articles/Mathavan_Sports_2014.pdf
"""

from typing import Tuple
from numpy.typing import NDArray

from numba import jit
import numpy as np
from numpy import sqrt, dot, array
import pooltool.constants as const
from pooltool.objects.ball.datatypes import Ball, BallState
from pooltool.physics.resolve.ball_ball.core import CoreBallBallCollision


def _resolve_ball_ball(rvw1, rvw2, *args, **kwargs):
    r_i, v_i, w_i = rvw1.copy()
    r_j, v_j, w_j = rvw2.copy()

    v_i1, w_i1, v_j1, w_j1 = collide_balls(r_i, v_i, w_i, r_j, v_j, w_j, *args, **kwargs)

    rvw1[1,:2] = v_i1[:2]
    rvw2[1,:2] = v_j1[:2]
    rvw1[2] = w_i1
    rvw2[2] = w_j1
    return rvw1, rvw2


class FrictionalMathavan(CoreBallBallCollision):
    def solve(self, ball1: Ball, ball2: Ball) -> Tuple[Ball, Ball]:
        rvw1, rvw2 = _resolve_ball_ball(
            ball1.state.rvw.copy(),
            ball2.state.rvw.copy(),
            ball1.params.R,
            ball1.params.m,
            u_s1=ball1.params.u_s,
            u_s2=ball2.params.u_s,
            # Assume the interaction coefficients are the average of the two balls
            u_b=(ball1.params.u_b + ball2.params.u_b) / 2,
            e_b=(ball1.params.e_b + ball2.params.e_b) / 2,
        )

        ball1.state = BallState(rvw1, const.sliding)
        ball2.state = BallState(rvw2, const.sliding)

        return ball1, ball2


INF = float('inf')
z_loc = array([0, 0, 1], dtype=np.float64)

@jit(nopython=True, cache=const.use_numba_cache)
def collide_balls(r_i, v_i, w_i,
                  r_j, v_j, w_j,
                  R, M,
                  u_s1=0.21,
                  u_s2=0.21,
                  u_b=0.05,
                  e_b=0.89,
                  deltaP=None,
                  N=1000):
    """Simulates the frictional collision between two balls.

    This function computes the post-collision linear and angular velocities of two balls
    colliding on a rough surface, taking into account both ball-to-ball friction and
    ball-to-surface friction. The collision model is based on the method described by
    Mathavan et al. (2014), which considers point contacts and frictional impact
    dynamics between the balls.

    The function transforms the velocities and angular velocities into a local
    coordinate frame defined by the line connecting the centers of the two balls at the
    point of collision. It then iteratively calculates the collision dynamics, including
    the effects of friction and restitution during the compression and restitution
    phases of the collision. Once the collision dynamics criteria are met, the updated
    velocities and angular velocities are transformed back into the global coordinate
    frame and returned.

    Args:
        r_i: Position vector of ball 1 in global coordinates. Shape: (3,).
        v_i: Velocity vector of ball 1 in global coordinates. Shape: (3,).
        w_i: Angular velocity vector of ball 1 in global coordinates. Shape: (3,).
        r_j: Position vector of ball 2 in global coordinates. Shape: (3,).
        v_j: Velocity vector of ball 2 in global coordinates. Shape: (3,).
        w_j: Angular velocity vector of ball 2 in global coordinates. Shape: (3,).
        R: Radius of the balls.
        M: Mass of the balls.
        u_s1: Coefficient of sliding friction between ball 1 and the surface.
        u_s2: Coefficient of sliding friction between ball 2 and the surface.
        u_b: Coefficient of friction between the balls during collision.
        e_b: Coefficient of restitution between the balls.
        deltaP:
            Normal impulse step size. If not passed, automatically selected according to
            equation 14 in the reference.
        N:
            If deltaP is not specified, it is calculated such that approximately this
            number of iterations are performed (see equation 14).

    Returns:
        Tuple[
            NDArray[np.float64],
            NDArray[np.float64],
            NDArray[np.float64],
            NDArray[np.float64]
        ]:
            A tuple containing:

            - Updated velocity vector of ball 1 after collision in global coordinates.
            - Updated angular velocity vector of ball 1 after collision in global
              coordinates.
            - Updated velocity vector of ball 2 after collision in global coordinates.
            - Updated angular velocity vector of ball 2 after collision in global
              coordinates.

    References:
        Mathavan, S., Jackson, M.R. & Parkin, R.M. (2014). Numerical simulations of the
        frictional collisions of solid balls on a rough surface. Sports Engineering, 17,
        227–237. https://doi.org/10.1007/s12283-014-0158-y

        Available at
        https://billiards.colostate.edu/physics_articles/Mathavan_Sports_2014.pdf
    """
    r_ij = r_j - r_i
    r_ij_mag_sqrd = dot(r_ij, r_ij)
    r_ij_mag = sqrt(r_ij_mag_sqrd)
    y_loc = r_ij / r_ij_mag
    x_loc = np.cross(y_loc, z_loc)
    G = np.vstack((x_loc, y_loc, z_loc))
    v_ix, v_iy = dot(v_i, x_loc), dot(v_i, y_loc)
    v_jx, v_jy = dot(v_j, x_loc), dot(v_j, y_loc)
    w_ix, w_iy, w_iz = dot(G, w_i)
    w_jx, w_jy, w_jz = dot(G, w_j)
    u_iR_x, u_iR_y = v_ix + R*w_iy, v_iy - R*w_ix
    u_jR_x, u_jR_y = v_jx + R*w_jy, v_jy - R*w_jx
    u_iR_xy_mag = sqrt(u_iR_x**2 + u_iR_y**2)
    u_jR_xy_mag = sqrt(u_jR_x**2 + u_jR_y**2)
    u_ijC_x = v_ix - v_jx - R*(w_iz + w_jz)
    u_ijC_z = R*(w_ix + w_jx)
    u_ijC_xz_mag = sqrt(u_ijC_x**2 + u_ijC_z**2)
    v_ijy = v_jy - v_iy
    if deltaP is None:
        deltaP = 0.5 * (1 + e_b) * M * abs(v_ijy) / N
    C = 5 / (2 * M * R)
    W_f = INF
    W_c = None
    W = 0
    niters = 0
    while v_ijy < 0 or W < W_f:
        # determine impulse deltas:
        if u_ijC_xz_mag < 1e-16:
            deltaP_1 = deltaP_2 = 0
            deltaP_ix = deltaP_iy = deltaP_jx = deltaP_jy = 0
        else:
            deltaP_1 = -u_b * deltaP * u_ijC_x / u_ijC_xz_mag
            if abs(u_ijC_z) < 1e-16:
                deltaP_2 = 0
                deltaP_ix = deltaP_iy = deltaP_jx = deltaP_jy = 0
            else:
                deltaP_2 = -u_b * deltaP * u_ijC_z / u_ijC_xz_mag
                if deltaP_2 > 0:
                    deltaP_ix = deltaP_iy = 0
                    if u_jR_xy_mag == 0:
                        deltaP_jx = deltaP_jy = 0
                    else:
                        deltaP_jx = -u_s2 * (u_jR_x / u_jR_xy_mag) * deltaP_2
                        deltaP_jy = -u_s2 * (u_jR_y / u_jR_xy_mag) * deltaP_2
                else:
                    deltaP_jx = deltaP_jy = 0
                    if u_iR_xy_mag == 0:
                        deltaP_ix = deltaP_iy = 0
                    else:
                        deltaP_ix = u_s1 * (u_iR_x / u_iR_xy_mag) * deltaP_2
                        deltaP_iy = u_s1 * (u_iR_y / u_iR_xy_mag) * deltaP_2
        # calc velocity changes:
        deltaV_ix = ( deltaP_1 + deltaP_ix) / M
        deltaV_iy = (-deltaP   + deltaP_iy) / M
        deltaV_jx = (-deltaP_1 + deltaP_jx) / M
        deltaV_jy = ( deltaP   + deltaP_jy) / M
        # calc angular velocity changes:
        deltaOm_ix = C * ( deltaP_2 + deltaP_iy)
        deltaOm_iy = C * (-deltaP_ix)
        deltaOm_iz = C * (-deltaP_1)
        deltaOm_j = C * array([( deltaP_2 + deltaP_jy),
                               (-deltaP_jx),
                               (-deltaP_1)])
        # update velocities:
        v_ix += deltaV_ix
        v_jx += deltaV_jx
        v_iy += deltaV_iy
        v_jy += deltaV_jy
        # update angular velocities:
        w_ix += deltaOm_ix
        w_iy += deltaOm_iy
        w_iz += deltaOm_iz
        w_jx += deltaOm_j[0]
        w_jy += deltaOm_j[1]
        w_jz += deltaOm_j[2]
        # update ball-table slips:
        u_iR_x, u_iR_y = v_ix + R*w_iy, v_iy - R*w_ix
        u_jR_x, u_jR_y = v_jx + R*w_jy, v_jy - R*w_jx
        u_iR_xy_mag = sqrt(u_iR_x**2 + u_iR_y**2)
        u_jR_xy_mag = sqrt(u_jR_x**2 + u_jR_y**2)
        # update ball-ball slip:
        u_ijC_x = v_ix - v_jx - R*(w_iz + w_jz)
        u_ijC_z = R*(w_ix + w_jx)
        u_ijC_xz_mag = sqrt(u_ijC_x**2 + u_ijC_z**2)
        # increment work:
        v_ijy0 = v_ijy
        v_ijy = v_jy - v_iy
        W += 0.5 * deltaP * abs(v_ijy0 + v_ijy)
        niters += 1
        if W_c is None and v_ijy > 0:
            W_c = W
            W_f = (1 + e_b**2) * W_c
            # niters_c = niters
            # _logger.debug('''
            # END OF COMPRESSION PHASE
            # W_c = %s
            # W_f = %s
            # niters_c = %s
            # ''', W_c, W_f, niters_c)
    # _logger.debug('''
    # END OF RESTITUTION PHASE
    # niters = %d
    # ''', niters)
    v_i = array((v_ix, v_iy, 0))
    v_j = array((v_jx, v_jy, 0))
    w_i = array((w_ix, w_iy, w_iz))
    w_j = array((w_jx, w_jy, w_jz))
    G_T = G.T
    return dot(G_T, v_i), dot(G_T, w_i), dot(G_T, v_j), dot(G_T, w_j)
