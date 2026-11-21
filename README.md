# Two-marker pose correction under independent and slowly drifting fixture yaw

Vedant Thaker · November 21, 2026

With two symmetric markers, least-squares rigid registration uses the marker midpoint and the full observed heading. A short baseline can magnify heading noise enough that a distant assembly target misses tolerance.

- [Revised manuscript (PDF)](manuscript.pdf) · [Editable manuscript](manuscript.md)
- [Revision code, results and reproduction instructions](revision/supplement/) · [Preparation record](revision/PREPARATION.md)
- [Baseline software and results at the study commit](https://github.com/VEDANT1602/fixture-pose-correction/tree/be91e32b7e57c2c81a5308da8345031aa1474588) · [Software license](LICENSE) · [Third-party terms](LICENSING.md)

## Earlier study and reproduction instructions

The following instructions and results describe the original study. The revised paper and its supplemental tests are linked above.

### When to trust the angle between two fixture markers

Two landmarks can locate a fixture's center while giving a poor estimate of its angle. At a short baseline, small independent errors in their positions create a large error in measured rotation. The simulated tool then applies that rotation to operations up to 36 mm from the center.

With the markers 12 mm apart, translation alone finished 497 of 1,000 challenge fixtures by the 1.85 s deadline. Applying the full measured angle finished 444. Shrinking the angle toward zero, using marker separation and a fixed angular prior, finished 680. On the same starts it rescued 342 failures of the full adjustment and lost 106 of its successes. The net difference is 236 completed cycles. [Paired results](results.csv?plain=1#L63) · [Angular weighting rule](run.py#L77)

| Marker separation | Translation only | Full angle | Shrunk angle |
| --- | ---: | ---: | ---: |
| 12 mm | 497 | 444 | 680 |
| 36 mm | 497 | 895 | 918 |
| 72 mm | 497 | 981 | 981 |

Each column counts completed three-operation cycles under the same challenge noise and deadline. The full-angle and shrunk-angle counts coincide at 72 mm. A wider baseline helps estimate rotation, but it cannot remove a shared translation error: adding a common 0.8 mm reading bias lowered the full-angle result there to 762. Cycle durations and retries are simulated. Independent endpoint measurements would be needed to transfer the choice of baseline to a physical fixture. [All six policies](results.csv) · [Study design](https://github.com/VEDANT1602/fixture-pose-correction/blob/be91e32b7e57c2c81a5308da8345031aa1474588/manuscript.md) · [Paper PDF](https://github.com/VEDANT1602/fixture-pose-correction/blob/be91e32b7e57c2c81a5308da8345031aa1474588/manuscript.pdf)

## Reproduce and check

From the repository root, use Python 3.11 and install the version of NumPy listed in [requirements.txt](requirements.txt).

```shell
python -m pip install -r requirements.txt
python run.py
python verify.py
```

[run.py](run.py) generates all inputs from seed 1705 and writes 162 condition-policy rows. [verify.py](verify.py) uses the Python standard library to read the CSV independently. It checks the complete condition grid, completion bounds, paired gain/loss accounting and the table above. You can run it directly against the archived CSV before installing NumPy. Re-running the simulation overwrites the local results file.

Maintained by Vedant Thaker.
