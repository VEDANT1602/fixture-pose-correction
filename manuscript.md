# Marker spacing and temporal smoothing in two-point fixture heading estimates

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

21 November 2026

### Abstract

Two markers can register a fixture even when their separation is too short to estimate heading accurately. A robot–camera benchmark with 88 physical stops lets marker span and temporal smoothing be tested against the same sequence. Calibration used 56 stops. On the other 32, increasing separation from 28.5 to 85.5 mm cut the mean absolute difference between the measured heading and the robot-predicted heading from 0.377° to 0.140°. All four test blocks showed the reduction. At 28.5 mm, a tracker fitted on the calibration stops changed the error to 0.373°, while a tracker assuming strong persistence raised it to 0.463°. Separate simulated fixture sequences show where smoothing helps a downstream target and where it introduces lag. Across these physical views, a wider marker pair gave the more consistent gain.

## How a small yaw error reaches the target

A fixture registered from two marks may be used to place a tool well beyond them. A heading error of one degree swings a target 36 mm from the midpoint by about 0.63 mm. Fiducial localization and target-registration error are distinct quantities [1]. The setup decision studied here is whether to increase marker spacing or borrow heading information from neighboring fixtures.

For a planar pair a distance B apart, independent isotropic localization errors of standard deviation σ give a first-order angular variance of 2σ²/B². The midpoint and full observed heading are the equal-weight rigid fit. A tracker can reduce noise if neighboring poses have similar yaw, but a fixture arriving with a new yaw inherits an error from its predecessor. This comparison first measures heading on a physical robot sequence, then isolates translation, yaw and timing in a simulation.

## A physical reference from held-out robot poses

Tabb and Ahmad Yousef studied camera–robot calibration from measured robot poses and images [2]. Their public dataset DS1 records 88 stops of a Denso VS-6577GM-B arm with a Sony camera, 640 × 480 pixels, and a checkerboard with 28.5 mm spacing [3]. Two corners in the same row were used as fiducials, with separations of one, three or seven cells. The endpoint is the axial heading of the projected segment in the image plane.

Frame numbers were grouped in eleven consecutive blocks of eight. Zero-indexed blocks 2, 5, 8 and 10 were withheld. The remaining 56 stops provided camera intrinsics, distortion, two fixed rigid transforms, and estimator weights. The two transforms map the observed robot pose and the known board grid into the camera frame. Their fit minimizes corner reprojection error over training images. For a held-out stop, projecting its robot pose and known marker coordinates gives the reference without using any pixels from that stop. All 32 held-out images are used only to estimate the competing headings and to score the reprojection check.

The full-board root-mean-square reprojection discrepancy of the robot reference was 1.60 px on the fitting stops and 1.69 px on the held-out stops. This includes robot-to-camera calibration error. Small differences between the filters are therefore weak evidence for a method ranking. These measurements concern apparent heading on one physical rig. They contain no contact outcome, surveyed fixture yaw in the work plane, or execution time.

## Spacing dominated filtering on the held-out blocks

The raw estimator uses the angle of the vector between the two observed corners. The static estimator shrinks it toward the mean training heading, using the weight minimizing training squared axial error. The sequence estimator uses a scalar Kalman update [4]. Its measurement variance and marginal heading spread come from the training residuals and reference headings. Lag-one persistence is fitted on consecutive training stops. A second tracker is deliberately set to 0.95. All tracks restart at the first stop of a disjoint test block. Angles are compared modulo 180°.

With a one-cell span, fitting temporal persistence (about 0.655) yielded a mean absolute improvement of 0.003° over raw heading. It improved two held-out blocks and worsened two. By comparison, increasing the raw span from one to three cells improved each block, by 0.055° to 0.544°. Increasing to seven cells lowered the overall raw error again, from 0.140° to 0.111°. The strong-persistence filter gave the largest overall error at every span.


| Span (mm) | Raw | Static | Fitted tracker | Tracker, ϕ = 0.95 |
| --- | --- | --- | --- | --- |
| 28.5 | 0.377 | 0.393 | 0.373 | 0.463 |
| 85.5 | 0.140 | 0.143 | 0.145 | 0.173 |
| 199.5 | 0.111 | 0.111 | 0.115 | 0.130 |
Table 1. Mean absolute apparent-heading disagreement in degrees across the same 32 held-out physical stops. The supplementary tables give 90th percentiles and individual stop errors.

## When persistence is wrong

The target calculation uses 80 independent calibration sequences and 120 fresh test sequences per regime, each 96 fixtures long. Marginal yaw standard deviation is 4/√3 degrees, the spread of a uniform ±4° operating envelope. The innovation scale preserves that variance. A two-state process switches with probability 0.12 per fixture between independent yaw and autoregressive yaw with persistence 0.90. Neither regime is revealed to the filter. Calibration uses mixed Gaussian sequences and duplicate noisy marker readings to estimate measurement variance, yaw variance and lag covariance. The fitted fixed coefficient is 0.458 at a 12 mm span. Test data include independent, persistent, mixed and mixed heavy-tailed sequences; the latter use variance-standardized Student t innovations with five degrees of freedom.

Translation is uniform within ±4.5 mm on each axis. The primary endpoint is average radial registration error at a target 36 mm from the marker midpoint, before tracking or retry noise. The camera-coordinate noise used for calibration is 0.45 mm per coordinate. Held-out noise ranges from 0.25 to 0.70 mm and marker span from 12 to 72 mm. These are assigned design settings. The physical camera data do not supply the simulator’s stochastic law.

At 12 mm, the 0.95 tracker performed best among the four displayed methods with truly persistent yaw. With independent fixtures it added 0.138 mm relative to static shrinkage. At nominal noise on heavy-tailed mixed sequences, increasing raw spacing from 12 to 36 mm reduced the mean target error from 1.582 to 0.666 mm. At a fixed 12 mm, the fitted tracker reduced it to 0.990 mm. Across the independent sequences, the Monte Carlo standard error of the paired 0.593 mm reduction was 0.010 mm.


| Test yaw | Raw | Static | Fitted tracker | Tracker, ϕ = 0.95 |
| --- | --- | --- | --- | --- |
| Independent | 1.618 | 1.038 | 1.060 | 1.176 |
| Persistent (0.90) | 1.603 | 1.046 | 0.958 | 0.885 |
| Switching, Gaussian | 1.583 | 1.037 | 1.003 | 1.055 |
| Switching, heavy tails | 1.582 | 1.021 | 0.990 | 1.029 |
Table 2. Mean target error in mm at 12 mm marker span and 0.45 mm coordinate noise. Each row contains 11,520 test fixtures. Methods within a row share the same readings.

## What a time budget changes

A three-placement replay uses target radii 36, 16 and 36 mm, tolerances of 1.30, 1.60 and 0.90 mm, 0.12 mm tracking noise and one possible retry. These values define an illustrative assembly, as do the 0.10 s setup, 0.06 s correction overhead and 0.36 s retry. A sensitivity grid varies per-stage time (0.25, 0.32, 0.40 s), correction speed (40, 55, 70 mm/s) and deadline (1.60, 1.85, 2.10 s).

For the mixed heavy-tailed case at 12 mm spacing, the fitted tracker completed 71.6% at the middle clock settings, compared with 70.0% under static shrinkage. The fitted tracker’s completion fraction ranged from 4.0% to 78.0% across the 27 timing combinations. These figures measure the behavior of a timing model. Commissioning an assembly station requires observed contact outcomes and timestamped corrections from the intended fixture and controller.

The rig data support widening the pair where the registration geometry allows it. Where spacing is fixed, a proposed smoother should be checked on contiguous unseen fixture sequences with resets preserved: the short-span results show that a pooled average can hide blocks in which smoothing loses to the raw angle.

## Data and code availability

The supplement includes the robot-bench calibration and projection code, the simulator, per-stop physical errors, and full sensitivity tables. The 88 source images and indexed robot stops are available in the USDA DS1 archive [3]. Instructions identify the direct official download and SHA-256. Related project repository: https://github.com/VEDANT1602/fixture-pose-correction.

[Study files, software and source records](https://github.com/VEDANT1602/fixture-pose-correction/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with processing the public robot-pose benchmark, implementing filter stress tests and drafting the results.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] J. M. Fitzpatrick, J. B. West and C. R. Maurer Jr. Predicting error in rigid-body point-based registration. IEEE Transactions on Medical Imaging 17, 694–702 (1998). <https://doi.org/10.1109/42.736021>

[2] A. Tabb and K. M. Ahmad Yousef. Solving the robot-world hand-eye(s) calibration problem with iterative methods. Machine Vision and Applications (2017). <https://doi.org/10.1007/s00138-017-0841-7>

[3] A. Tabb and K. M. Ahmad Yousef. Data from: Solving the Robot-World Hand-Eye(s) Calibration Problem with Iterative Methods. USDA Ag Data Commons, dataset DS1. <https://doi.org/10.15482/USDA.ADC/1340592>

[4] R. E. Kalman. A new approach to linear filtering and prediction problems. Journal of Basic Engineering 82, 35–45 (1960). <https://doi.org/10.1115/1.3662552>
