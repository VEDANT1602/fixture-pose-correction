"""Compare the trained tracker with static shrinkage on paired simulator sequences."""
import csv
from pathlib import Path

import numpy as np

from mixed_fixture import TARGETS, calib, filterseq, fixtures, measure, rotate


def main():
    span = 12
    noise = 0.45
    variance, observation_variance, fitted = calib(fixtures(19051, "mixed", 80), span)
    rows = []
    for k, regime in enumerate(["iid", "drift", "mixed", "mixed-t"]):
        trials = fixtures(29111+k, regime)
        yaw, translation = trials[:2]
        truth = (rotate(TARGETS, yaw)+translation[..., None, :])[..., 2, :]
        observed, mid = measure(trials, span, noise)
        run_mae = []
        for persistence in [0., fitted]:
            angles = filterseq(observed, variance, observation_variance, persistence)
            placed = (rotate(TARGETS, angles)+mid[..., None, :])[..., 2, :]
            run_mae.append(np.linalg.norm(placed-truth, axis=-1).mean(axis=1))
        difference = run_mae[0]-run_mae[1]
        rows.append(dict(regime=regime, n_sequences=len(difference), span_mm=span,
                         coordinate_noise_mm=noise, static_mae_mm=run_mae[0].mean(),
                         tracked_mae_mm=run_mae[1].mean(), static_minus_tracked_mm=difference.mean(),
                         paired_sequence_mcse_mm=difference.std(ddof=1)/np.sqrt(len(difference))))
    with Path(__file__).with_name("strong_comparator.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__=="__main__":
    main()
