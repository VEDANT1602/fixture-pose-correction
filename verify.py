"""Check the archived fixture study's CSV without invoking the simulator."""
import csv
from itertools import product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    with Path(__file__).with_name("results.csv").open(newline="") as stream:
        records = list(csv.DictReader(stream))
    indexed = {
        (r["case"], float(r["span_mm"]), float(r["deadline_s"]), r["policy"]): r
        for r in records
    }
    expected = set(product(
        ("setup", "released", "biased"), (12., 36., 72.), (1.55, 1.85, 2.20),
        ("replay", "translation", "rigid", "gated", "shrink", "oracle"),
    ))
    require(len(records) == len(expected) and indexed.keys() == expected, "Condition grid differs")
    for (case, span, deadline, policy), record in indexed.items():
        count = int(record["completed"])
        first = int(record["first_pass"])
        trials = int(record["trials"])
        gain = int(record["gains_vs_rigid"])
        loss = int(record["losses_vs_rigid"])
        rigid = int(indexed[case, span, deadline, "rigid"]["completed"])
        require(trials == 1000 and 0 <= first <= count <= trials, f"Completion count: {record}")
        require(count - rigid == gain - loss, f"Paired difference: {case}, {span}, {deadline}, {policy}")
        require(0 <= gain <= min(count, trials - rigid), f"Invalid gain: {record}")
        require(0 <= loss <= min(rigid, trials - count), f"Invalid loss: {record}")
    for span, expected_counts in [
        (12, [497, 444, 680, 367]), (36, [497, 895, 918, 692]), (72, [497, 981, 981, 762]),
    ]:
        counts = [
            int(indexed[case, span, 1.85, policy]["completed"])
            for case, policy in [
                ("released", "translation"), ("released", "rigid"),
                ("released", "shrink"), ("biased", "rigid"),
            ]
        ]
        require(counts == expected_counts, f"Headline counts for {span} mm: {counts}")
    short_span = indexed["released", 12, 1.85, "shrink"]
    require((int(short_span["gains_vs_rigid"]), int(short_span["losses_vs_rigid"])) == (342, 106),
            "Short-span paired comparison differs")
    print("Verified 162 conditions, the three marker-span comparisons and the net gain of 236 cycles.")


if __name__ == "__main__":
    main()
