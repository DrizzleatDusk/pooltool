#! /usr/bin/env python
"""This illustrates how shots can be visualized multiple times in a single script"""

import numpy as np

import pooltool as pt

get_pos = lambda table, ball: (
    (table.w - 2 * ball.params.R) * np.random.rand() + ball.params.R,
    (table.l - 2 * ball.params.R) * np.random.rand() + ball.params.R,
    ball.params.R,
)


def place_ball(i, balls, table):
    ball = pt.Ball(i)
    while True:
        new_pos = get_pos(table, ball)
        ball.state.rvw[0] = new_pos

        for other in balls.values():
            if pt.physics.is_overlapping(
                ball.state.rvw, other.state.rvw, ball.params.R, other.params.R
            ):
                break
        else:
            return ball


def main(args):
    if not args.no_viz:
        interface = pt.ShotViewer()
    while True:
        # Setup the system
        table = pt.Table.from_table_specs(pt.PocketTableSpecs(l=4, w=2))
        balls = {}
        balls["cue"] = place_ball("cue", balls, table)
        for i in range(args.N):
            balls[str(i)] = place_ball(str(i), balls, table)
        cue = pt.Cue(cue_ball_id="cue")
        shot = pt.System(cue=cue, table=table, balls=balls)

        # Aim at the head ball then strike the cue ball
        shot.aim_at_ball("1")
        shot.strike(V0=40)

        # Evolve the shot
        try:
            pt.simulate(shot, continuize=False, quiet=False)
        except KeyboardInterrupt:
            break

        if not args.no_viz:
            interface.show(shot)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser("A large arena with many balls")
    ap.add_argument("-N", type=int, default=50, help="The number of balls")
    ap.add_argument(
        "--no-viz", action="store_true", help="If set, the break will not be visualized"
    )
    args = ap.parse_args()
    main(args)
