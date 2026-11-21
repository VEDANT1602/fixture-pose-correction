# Marker spacing and temporal smoothing in two-point fixture heading estimates

Working paper by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana. Correspondence: vedant.thaker1602@gmail.com.

Two markers can register a fixture even when their separation is too short to estimate heading accurately. A robot–camera benchmark with 88 physical stops lets marker span and temporal smoothing be tested against the same sequence. Calibration used 56 stops. On the other 32, increasing separation from 28.5 to 85.5 mm cut the mean absolute difference between the measured heading and the robot-predicted heading from 0.377° to 0.140°. All four test blocks showed the reduction. At 28.5 mm, a tracker fitted on the calibration stops changed the error to 0.373°, while a tracker assuming strong persistence raised it to 0.463°. Separate simulated fixture sequences show where smoothing helps a downstream target and where it introduces lag. Across these physical views, a wider marker pair gave the more consistent gain.

- [Read the paper](manuscript.pdf)
- [Read the plain-text manuscript](manuscript.md)
- [Reproduce the analysis and inspect the source and data records](study/README.md)
- [Software license](LICENSE) and [third-party terms](LICENSING.md)
- [Preparation record](study/PREPARATION.md)
- [Previous manuscript and supplements](https://github.com/VEDANT1602/fixture-pose-correction/tree/d5fd89da341d942b67ea9f16422e6d1b78f1c0ff)
