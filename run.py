"""Reproduce the planar assembly experiment. Requires Python 3.10+ and NumPy."""
import csv
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
N = 1000
TARGETS = np.array([[-36., 0.], [0., 16.], [36., 0.]])
TOLS = np.array([1.30, 1.60, 0.90])
POLICIES = ("replay", "translation", "rigid", "gated", "shrink", "oracle")


def rotate(points, angles):
    c, s = np.cos(angles)[:, None], np.sin(angles)[:, None]
    return np.stack((c * points[:, 0] - s * points[:, 1],
                     s * points[:, 0] + c * points[:, 1]), axis=-1)


def run_policy(correct, truth, tracking, recovery, limit):
    n = len(truth)
    elapsed = np.full(n, 0.10)
    live = np.ones(n, dtype=bool)
    attempts = np.zeros(n, dtype=int)
    adjusted = np.zeros(n, dtype=int)
    failures = np.zeros(n, dtype=int)
    first = np.ones(n, dtype=bool)
    for j in range(len(TARGETS)):
        displacement = np.linalg.norm(correct[:, j], axis=1)
        adjust = displacement > 1e-12
        adjusted += live & adjust
        elapsed += live * (0.32 + np.where(adjust, 0.060 + displacement / 55., 0.))
        err = np.linalg.norm(correct[:, j] + tracking[:, j] - truth[:, j], axis=1)
        missed = live & (err > TOLS[j])
        failures += missed
        first &= ~missed
        room = elapsed + 0.36 <= limit + 1e-12
        retry = missed & room & (attempts == 0)
        attempts += retry
        elapsed += 0.36 * retry
        recovered = np.linalg.norm(recovery[:, j], axis=1) <= TOLS[j]
        live &= (~missed | (retry & recovered)) & (elapsed <= limit + 1e-12)
    return live, first & live, attempts, adjusted, np.minimum(elapsed, limit), failures


def main():
    rng = np.random.default_rng(1705)
    rows = []
    base = None
    for case, trans, yaw, sigma, bias in (
        ("setup", 2.0, 1.0, 0.25, 0.0),
        ("released", 4.5, 4.0, 0.45, 0.0),
        ("biased", 4.5, 4.0, 0.45, 0.8),
    ):
        # The two challenge regimes share all draws, including localization bias direction.
        if case == "released":
            base = rng.bit_generator.state
        if case == "biased":
            rng.bit_generator.state = base
        translation = rng.uniform(-trans, trans, (N, 2))
        theta = np.deg2rad(rng.uniform(-yaw, yaw, N))
        error = rng.normal(0, sigma, (N, 2, 2))
        direction = rng.uniform(-np.pi, np.pi, N)
        error += bias * np.column_stack((np.cos(direction), np.sin(direction)))[:, None, :]
        track = rng.normal(0, 0.12, (N, 3, 2))
        recovery = rng.normal(0, 0.27, (N, 3, 2))
        true_delta = rotate(TARGETS, theta) - TARGETS + translation[:, None, :]
        for span in [12., 36., 72.]:
            markers = np.array([[-span / 2, 0], [span / 2, 0]])
            observed = rotate(markers, theta) + translation[:, None, :] + error
            midpoint = np.repeat(observed.mean(axis=1)[:, None, :], 3, axis=1)
            delta = observed[:, 1] - observed[:, 0]
            angle = np.arctan2(delta[:, 1], delta[:, 0])
            rigid = midpoint + rotate(TARGETS, angle) - TARGETS
            prior_var = np.deg2rad(2.)**2
            weight = prior_var / (prior_var + 2 * .45**2 / span**2)
            shrunk = midpoint + rotate(TARGETS, weight * angle) - TARGETS
            assert np.allclose(rotate(markers, theta).mean(axis=1), 0.)
            exact_angle = np.arctan2(np.sin(theta) * span, np.cos(theta) * span)
            assert np.max(np.abs(exact_angle - theta)) < 1e-14
            corrections = [np.zeros_like(rigid), midpoint, rigid,
                           rigid * (np.linalg.norm(rigid, axis=2) > 0.75*TOLS)[:, :, None],
                           shrunk, true_delta]
            for limit in [1.55, 1.85, 2.2]:
                results = [run_policy(x, true_delta, track, recovery, limit) for x in corrections]
                ref = results[2][0]
                for policy, (done, first, ret, adj, elapsed, misses) in zip(POLICIES, results):
                    rows.append(dict(case=case, span_mm=span, deadline_s=limit, policy=policy,
                        trials=N, completed=int(done.sum()), first_pass=int(first.sum()),
                        retries=int(ret.sum()), adjustments=int(adj.sum()),
                        first_attempt_misses=int(misses.sum()), mean_cycle_s=round(elapsed.mean(), 6),
                        gains_vs_rigid=int(np.sum(done & ~ref)),losses_vs_rigid=int(np.sum(ref & ~done))))
    with (HERE/"results.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(len(rows), "condition-policy rows written.")


if __name__ == "__main__":
    main()
