# Marker spacing and temporal smoothing in two-point fixture heading estimates

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Research working paper

### Abstract

A camera can estimate fixture heading from two marks, but the available robot reference also depends on the camera calibration. At 32 held-out stops of one robot, widening the pair from 28.5 to 85.5 mm reduced mean absolute apparent-heading disagreement from 0.377° to 0.140°. Widening it again to 199.5 mm gave 0.111°. Two checks put those gains in context. Removing a training block and refitting the calibration changed the reference heading by 0.026° on average. An optical reference fitted using 40 other board corners differed from the robot reference by 0.074°. Both references showed the large short-to-medium spacing benefit. Their disagreement and the diminishing gain at the longest tested span limit claims about very small filter effects or wider fixtures.

## How a small yaw error reaches the target

A fixture registered from two marks may be used to place a tool well beyond them. A heading error of one degree swings a target 36 mm from the midpoint by about 0.63 mm. Fiducial localization and target-registration error are distinct quantities [1]. The setup decision studied here is whether to increase marker spacing or borrow heading information from neighboring fixtures.

For two planar points observed a distance B apart in the same coordinate frame, independent isotropic localization errors of standard deviation σ give a first-order angular variance of 2σ²/B². In an image B is the projected separation in pixels. Foreshortening, distortion and correlated errors can break inverse scaling with physical board spacing. The midpoint and full observed heading are the equal-weight rigid fit. A tracker can reduce noise if neighboring poses have similar yaw, but a fixture arriving with a new yaw inherits an error from its predecessor. This comparison first measures heading on a physical robot sequence, then isolates translation, yaw and timing in a simulation.

## How the reference heading was estimated

Tabb and Ahmad Yousef studied camera–robot calibration from measured robot poses and images [2]. Their public dataset DS1 records 88 stops of a Denso VS-6577GM-B arm with a Sony camera, 640 × 480 pixels, and a checkerboard with 28.5 mm spacing [3]. Two corners in the same row were used as fiducials, with separations of one, three or seven cells. The endpoint is the axial heading of the projected segment in the image plane.

Frame numbers were grouped in eleven consecutive blocks of eight. Zero-indexed blocks 2, 5, 8 and 10 were withheld. The remaining 56 stops provided camera intrinsics, distortion, two fixed rigid transforms, and estimator weights. The two transforms map the observed robot pose and the known board grid into the camera frame. Their fit minimizes corner reprojection error over training images. For a held-out stop, projecting its robot pose and known marker coordinates gives the reference without using any pixels from that stop. The held-out robot projection uses no pixels from the test stop. Its fixed calibration still shares the camera and board with the observations under test.

Full-board reprojection RMS was 1.60 px on the 56 fitting stops and 1.69 px on the 32 test stops. A common pixel shift affects a pair’s midpoint but leaves its heading unchanged, so neither RMS is itself an angular uncertainty. To measure calibration sensitivity in degrees, we separately omitted each of the seven training blocks. We refitted camera intrinsics, distortion and both rigid transforms on the remaining 48 stops. Every fit predicted the same 32 withheld stops. The mean absolute shift from the full-fit reference was 0.026° at each span. Across the seven fits, the one-cell mean shift ranged from 0.011° to 0.042°. These are sensitivity measures over overlapping fits.

For a second reference, we estimated board pose independently at each held-out image using the 40 corners outside the tested row. We projected the known row through that pose with the original training intrinsics. This reference uses neither the robot at that stop nor either marker used to measure heading. Shared lens calibration, board geometry and within-image errors can still affect both reference routes. They disagreed by 0.074° on average across held-out stops at each span. A calibrated rotary stage or independently surveyed poses would be needed to measure absolute reference error.

## Spacing dominated filtering on the held-out blocks

The raw estimator uses the angle of the vector between the two observed corners. The static estimator shrinks it toward the mean training heading, using the weight minimizing training squared axial error. The sequence estimator uses a scalar Kalman update [4]. Its measurement variance and marginal heading spread come from the training residuals and reference headings. Lag-one persistence is fitted on consecutive training stops. A second tracker is deliberately set to 0.95. All tracks restart at the first stop of a disjoint test block. Angles are compared modulo 180°.

At one-cell spacing, the 0.003° difference between fitted tracking and raw heading changed sign across blocks. Two blocks improved and two worsened. Widening from one to three cells improved all four blocks by 0.055° to 0.544°. Using the other 40 corners as the reference, raw errors at one, three and seven cells were 0.390°, 0.110° and 0.081°. Omitting a training block gave raw-to-robot errors of 0.351–0.405°, 0.131–0.153° and 0.091–0.132°, respectively. The short-to-medium gain survived the reference choices. At 28.5 mm the filter ranking depended on the reference. Static shrinkage increased error from 0.377° to 0.393° against the robot estimate, but reduced it from 0.390° to 0.371° against the optical estimate.


| Span (mm) | Raw | Static | Fitted tracker | Tracker, ϕ = 0.95 |
| --- | --- | --- | --- | --- |
| 28.5 | 0.377 | 0.393 | 0.373 | 0.463 |
| 85.5 | 0.140 | 0.143 | 0.145 | 0.173 |
| 199.5 | 0.111 | 0.111 | 0.115 | 0.130 |
Table 1. Mean absolute apparent-heading disagreement in degrees across the same 32 held-out physical stops. The supplementary tables give 90th percentiles and individual stop errors.

Scaling the three-cell robot-reference error purely by inverse span predicts 0.060° at seven cells (0.140° × 3/7); the observed error was 0.111°. The optical comparison also exceeded its inverse-span extrapolation, 0.081° versus 0.047°. Reference disagreement is one plausible contribution to a nonvanishing error floor. Three spans on one rig cannot identify a limiting floor or establish an optimum beyond 199.5 mm.

## When persistence is wrong

The target calculation uses 80 independent calibration sequences and 120 fresh test sequences per regime, each 96 fixtures long. Marginal yaw standard deviation is 4/√3 degrees, the spread of a uniform ±4° operating envelope. The innovation scale preserves that variance. A two-state process switches with probability 0.12 per fixture between independent yaw and autoregressive yaw with persistence 0.90. Neither regime is revealed to the filter. Calibration uses mixed Gaussian sequences and duplicate noisy marker readings to estimate measurement variance, yaw variance and lag covariance. The fitted fixed coefficient is 0.458 at a 12 mm span. Test data include independent, persistent, mixed and mixed heavy-tailed sequences; the latter use variance-standardized Student t innovations with five degrees of freedom.

Translation is uniform within ±4.5 mm on each axis. The primary endpoint is average radial registration error at a target 36 mm from the marker midpoint, before tracking or retry noise. The camera-coordinate noise used for calibration is 0.45 mm per coordinate. Held-out noise ranges from 0.25 to 0.70 mm and marker span from 12 to 72 mm. These are assigned design settings. The physical camera data do not supply the simulator’s stochastic law.

Static shrinkage provides the stronger comparison for deciding whether to track a sequence. On the heavy-tailed switching fixtures, the fitted tracker reduced mean target error from 1.021 to 0.990 mm relative to static shrinkage, a paired gain of 0.032 mm (Monte Carlo SE 0.003 mm over 120 sequences). Relative to the unsmoothed angle the gain was 0.593 mm. The additional tracking gain was 0.088 mm for persistent yaw, 0.034 mm for Gaussian switching, and −0.022 mm for independent yaw. Widening the raw pair from 12 to 36 mm reduced the heavy-tailed target error from 1.582 to 0.666 mm.

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

On this rig, moving from 28.5 to 85.5 mm gave a consistent reduction in apparent-heading disagreement with both reference constructions. The 199.5 mm pair yielded a smaller gain than inverse-span extrapolation. A tighter claim about temporal filtering requires an independently calibrated angular reference. Any throughput claim also requires observed placement outcomes and workstation cycle times.

## Data and code availability

The supplement includes the robot-bench calibration and projection code, the seven calibration refits, withheld-row optical check, simulator, paired static-tracker comparisons, per-stop physical errors and full sensitivity tables. The 88 source images and indexed robot stops are available in the USDA DS1 archive [3]. Instructions identify the direct official download and SHA-256. Related project repository: https://github.com/VEDANT1602/fixture-pose-correction.

[Study files, software and source records](https://github.com/VEDANT1602/fixture-pose-correction/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with processing the public robot-pose benchmark, implementing the calibration refits, optical reference and filter comparisons, and drafting the results.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] J. M. Fitzpatrick, J. B. West and C. R. Maurer Jr. Predicting error in rigid-body point-based registration. IEEE Transactions on Medical Imaging 17, 694–702 (1998). <https://doi.org/10.1109/42.736021>

[2] A. Tabb and K. M. Ahmad Yousef. Solving the robot-world hand-eye(s) calibration problem with iterative methods. Machine Vision and Applications (2017). <https://doi.org/10.1007/s00138-017-0841-7>

[3] A. Tabb and K. M. Ahmad Yousef. Data from: Solving the Robot-World Hand-Eye(s) Calibration Problem with Iterative Methods. USDA Ag Data Commons, dataset DS1. <https://doi.org/10.15482/USDA.ADC/1340592>

[4] R. E. Kalman. A new approach to linear filtering and prediction problems. Journal of Basic Engineering 82, 35–45 (1960). <https://doi.org/10.1115/1.3662552>
