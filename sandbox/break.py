#! /usr/bin/env python
"""This is a basic example of the pooltool API"""

import numpy as np

import pooltool as pt


def main(args):
    if not args.no_viz:
        interface = pt.ShotViewer()

    if args.seed:
        np.random.seed(args.seed)

    shot = pt.System(
        cue=pt.Cue(cue_ball_id="cue"),
        table=(table := pt.Table.pocket_table()),
        balls=pt.get_nine_ball_rack(
            table, ordered=True, spacing_factor=args.spacing_factor
        ),
    )

    # Aim at the head ball then strike the cue ball
    shot.aim_at_ball(ball_id="1")
    shot.strike(V0=args.V0)

    # Evolve the shot
    shot = pt.simulate(shot)

    if not args.no_viz:
        interface.show(shot)

    if args.save:
        shot.save(args.save)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser("A good old 9-ball break")
    ap.add_argument(
        "--no-viz", action="store_true", help="If set, the break will not be visualized"
    )
    ap.add_argument(
        "--spacing-factor",
        type=float,
        default=1e-3,
        help="What fraction of the ball radius should each ball be randomly separated by in the rack?",
    )
    ap.add_argument(
        "--V0",
        type=float,
        default=8,
        help="With what speed should the cue stick strike the cue ball?",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Provide a random seed if you want reproducible results",
    )
    ap.add_argument(
        "--save", type=str, default=None, help="Filepath that shot will be saved to"
    )

    args = ap.parse_args()

    main(args)
