"""Cross-check the angular reference on USDA DS1. Output tables appear beside this file."""
import argparse
import csv
from pathlib import Path

import cv2 as cv
import numpy as np

from robot_bench import angle, fit_geometry, load_dataset, wrap, write


SPANS = [(1, 3, 4), (3, 2, 5), (7, 0, 7)]
TEST_BLOCKS = [2, 5, 8, 10]


def headings(points):
    return np.column_stack([
        angle(points[:, 2, right] - points[:, 2, left])
        for cells, left, right in SPANS
    ])


def optical_heading(geometry, grids, camera, distortion):
    # Each target has known physical board coordinates.
    # All three evaluated pairs belong to row 2, which is absent from fitting.
    support = np.repeat(np.arange(6) != 2, 8)
    projections = []
    for image_grid in grids:
        corners = image_grid.reshape(-1, 2)
        ok, rotation, position = cv.solvePnP(
            geometry[support], corners[support], camera, distortion,
            flags=cv.SOLVEPNP_ITERATIVE,
        )
        if not ok:
            raise RuntimeError("Board-only pose fit failed")
        projected, _ = cv.projectPoints(geometry.astype(float), rotation, position, camera, distortion)
        projections.append(projected.reshape(6, 8, 2))
    return headings(np.stack(projections))


def abs_difference(first, second):
    return np.abs(np.degrees(wrap(first - second)))


def compare(dataset, errors_csv):
    ids, geometry, grids, robot = load_dataset(dataset)
    block = ids // 8
    test = np.isin(block, TEST_BLOCKS)
    train = ~test
    camera, distortion, _, _, projected = fit_geometry(geometry, grids, robot, train)
    base = headings(projected[test])
    raw = headings(grids[test])
    optical = optical_heading(geometry, grids[test], camera, distortion)
    # Re-score the originally fitted estimators without fitting their weights to a new target.
    with errors_csv.open(newline="") as stream:
        estimates = {(int(rec["frame"]), int(rec["cells"]), rec["method"]): float(rec["residual_deg"])
                     for rec in csv.DictReader(stream)}
    tracked = {}
    for method in ("static", "trained", "assume_095"):
        offsets = [[estimates[(int(frame), cells, method)] for cells, _, _ in SPANS] for frame in ids[test]]
        tracked[method] = base + np.radians(offsets)
    rows = []
    def append(label, omitted, values):
        for j, frame in enumerate(ids[test]):
            for k, (cells, _, _) in enumerate(SPANS):
                rows.append(dict(frame=int(frame), test_block=int(frame//8), cells=cells,
                                 comparison=label, omitted_train_block=omitted,
                                 abs_difference_deg=values[j,k]))
    append("raw_to_full_robot", "none", abs_difference(raw, base))
    append("optical_to_full_robot", "none", abs_difference(optical, base))
    append("raw_to_optical", "none", abs_difference(raw, optical))
    for method, values in tracked.items():
        append(method + "_to_optical", "none", abs_difference(values, optical))
    for omit in np.unique(block[train]):
        subset = train & (block != omit)
        _, _, _, inverted, pr = fit_geometry(geometry, grids, robot, subset)
        if inverted:
            raise RuntimeError("Refit switched kinematic transform direction")
        alternative = headings(pr[test])
        append("refit_robot_to_full_robot", int(omit), abs_difference(alternative, base))
        append("raw_to_refit_robot", int(omit), abs_difference(raw, alternative))
        for method, values in tracked.items():
            append(method + "_to_refit_robot", int(omit), abs_difference(values, alternative))
    write("reference_sensitivity.csv", rows)
    summary = []
    for label in dict.fromkeys(x["comparison"] for x in rows):
        for cells, _, _ in SPANS:
            selected = [r for r in rows if r["cells"] == cells and r["comparison"] == label]
            values = np.array([r["abs_difference_deg"] for r in selected])
            by_fit = {}
            for r in selected:
                by_fit.setdefault(r["omitted_train_block"], []).append(r["abs_difference_deg"])
            means = [np.mean(v) for v in by_fit.values()]
            summary.append(dict(comparison=label,cells=cells,n_fits=len(means),n_distinct_stops=32,
                                n_predictions=len(values),mae_deg=values.mean(),
                                p90_deg=np.quantile(values,.90),min_fit_mae_deg=min(means),
                                max_fit_mae_deg=max(means)))
    write("reference_summary.csv", summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--errors", type=Path, default=Path(__file__).with_name("robot_bench_errors.csv"))
    args=parser.parse_args()
    compare(args.dataset, args.errors)
