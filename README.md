# When two fixture markers justify a rotational correction

Two markers can locate a fixture well enough to correct its translation while giving a poor estimate of its rotation. A small angular error matters at the end of a long part. This experiment asks when a robot should rotate its taught positions and how to recognize a pair of markers that is too close together to support the full correction.

**Maintainer** · Vedant Thaker  
**Research materials** · [Manuscript (PDF)](manuscript.pdf) · [Editable manuscript](manuscript.md) · [Condition-level results](results.csv)

## Experiment

The simulated fixture has three operations. The outer two are 36 mm from the center. Each has a different placement tolerance, and one local retry is available for the entire cycle. Six policies share the fixture poses, marker noise, endpoint errors and time allowance. One uses translation alone. Another estimates the full rigid transformation. A third reduces its angular correction according to marker separation and a fixed prior on fixture rotation.

The setup condition allows translations up to 2 mm per axis and rotations up to one degree. The challenge increases these to 4.5 mm and four degrees and raises marker noise to 0.45 mm per coordinate. A further condition adds a common 0.8 mm offset to both readings on the same challenge fixtures. The experiment crosses these conditions with three marker spans and three deadlines.

## What changed with marker span?

Each cell counts completed three-operation cycles out of the same 1,000 challenge starts at a 1.85 s deadline.

| Marker span | Translation only | Full rotation | Shrunk rotation | Full rotation with common bias |
|---|---:|---:|---:|---:|
| 12 mm | 497 | 444 | 680 | 367 |
| 36 mm | 497 | 895 | 918 | 692 |
| 72 mm | 497 | 981 | 981 | 762 |

At 12 mm, full rotation performed worse than translation alone. Shrinkage gained 342 paired cycles and lost 106 relative to full rotation, for a net gain of 236 cycles. At 72 mm, the two angle estimators finished tied. The wider span reduced the angular error caused by the same marker noise. A common shift still moved the estimated fixture center.

## Reproduce and check

From the repository root, use Python 3.11 and install the version of NumPy listed in [requirements.txt](requirements.txt).

```shell
python -m pip install -r requirements.txt
python run.py
python verify.py
```

[run.py](run.py) generates all inputs from seed 1705 and writes 162 condition-policy rows. [verify.py](verify.py) uses the Python standard library to read the CSV independently. It checks the complete condition grid, completion bounds, paired gain/loss accounting and the table above. You can run it directly against the archived CSV before installing NumPy. Re-running the simulation overwrites the local results file.

## Interpretation

These are simulation counts. The time and recovery constants are assigned. An aborted cycle can be short because a stage failed. The geometry covers planar motion, independent reading noise and one common bias. A bench test needs an independently measured endpoint, several marker baselines and actual recovery times to establish how the effect transfers to an assembly cell.
