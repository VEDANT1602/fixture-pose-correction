# Marker spacing and temporal smoothing in two-point fixture heading estimates

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Robot-camera measurement report · November 24, 2026

### Abstract

The apparent heading of a checkerboard row can be estimated from either two adjacent corners or a wider pair in the same image. On a Denso robot with a Sony camera, extending the span from 28.5 to 85.5 mm reduced mean absolute disagreement with a robot-pose reference from 0.377° to 0.140°. The wider pair improved on the shorter one at 25 of 32 held-out stops. An optical reference fitted to the other board rows favored the wider pair at 26 stops. Extending the span to 199.5 mm yielded a smaller mean gain, about 0.03° against either reference. At 28.5 mm, changing references reversed the ranking of raw and statically smoothed headings. For this rig the reference choice preserved the spacing result and changed the smoothing decision.

## Projected heading on a calibration board

A fixture registered from two marks may be used to place a tool well beyond them. A heading error of one degree swings a target 36 mm from the midpoint by about 0.63 mm. Fiducial localization and target-registration error are distinct quantities [1]. Here the measured quantity is the projected direction of a marker pair on the board. The question is whether the same-image spacing comparison and the ranking of smoothing methods survive a change in the reference heading.

For two planar points observed a distance B apart in the same coordinate frame, independent isotropic localization errors of standard deviation σ give a first-order angular variance of 2σ²/B². In an image B is the projected separation in pixels. Foreshortening, distortion and correlated errors can break inverse scaling with physical board spacing. The midpoint and full observed heading are the equal-weight rigid fit. A tracker can reduce noise if neighboring poses have similar yaw, but a fixture arriving with a new yaw inherits an error from its predecessor. All three spacings can be evaluated on the same held-out images, so changing spacing keeps the robot pose and camera view fixed. Each span uses a different pair of corner locations, which also changes which localization errors enter the estimate.

## Two references for the same 32 stops

Tabb and Ahmad Yousef studied camera–robot calibration from measured robot poses and images [2]. Their public dataset DS1 records 88 stops of a Denso VS-6577GM-B arm with a Sony camera, 640 × 480 pixels, and a checkerboard with 28.5 mm spacing [3]. Two corners in the same row were used as fiducials, with separations of one, three or seven cells. The endpoint is the axial heading of the projected segment in the image plane.

Frame numbers were grouped in eleven consecutive blocks of eight. Zero-indexed blocks 2, 5, 8 and 10 were withheld. The remaining 56 stops provided camera intrinsics, distortion, two fixed rigid transforms, and estimator weights. The two transforms map the observed robot pose and the known board grid into the camera frame. Their fit minimizes corner reprojection error over training images. For a held-out stop, projecting its robot pose and known marker coordinates gives the reference without using any pixels from that stop. Its fixed calibration still shares the camera and board with the observations under test.

Full-board reprojection RMS was 1.60 px on the 56 fitting stops and 1.69 px on the 32 test stops. A common pixel shift affects a pair’s midpoint but leaves its heading unchanged, so neither RMS is itself an angular uncertainty. To measure calibration sensitivity in degrees, the analysis separately omitted each of the seven training blocks. Each calibration refit estimated camera intrinsics, distortion and both rigid transforms on the remaining 48 stops. Every fit predicted the same 32 withheld stops. The mean absolute shift from the full-fit reference was 0.026° at each span. Across the seven fits, the one-cell mean shift ranged from 0.011° to 0.042°. The seven refits share training images. The spread measures sensitivity to the omitted block.

For a second reference, the optical procedure estimated board pose separately in each held-out image using the 40 corners outside the tested row. It projected the known row through that pose with the original training intrinsics. This reference uses neither the robot at that stop nor either marker used to measure heading. Shared lens calibration, board geometry and within-image errors can still affect both reference routes. They disagreed by 0.074° on average across held-out stops at each span. A calibrated rotary stage or independently surveyed poses would be needed to measure absolute reference error.

## Paired spacing differences and filter rankings

The raw estimator uses the angle of the vector between the two observed corners. The static estimator shrinks it toward the mean training heading, using the weight minimizing training squared axial error. The sequence estimator uses a scalar Kalman update [4]. Its measurement variance and marginal heading spread come from the training residuals and reference headings. Lag-one persistence is fitted on consecutive training stops. A second tracker is deliberately set to 0.95. All tracks restart at the first stop of a disjoint test block. Angles are compared modulo 180°.

At one-cell spacing, the 0.003° difference between fitted tracking and raw heading changed sign across blocks. Two blocks improved and two worsened. Widening from one to three cells improved all four blocks by 0.055° to 0.544°. Using the other 40 corners as the reference, mean absolute raw disagreements at one, three and seven cells were 0.390°, 0.110° and 0.081°. Omitting a training block gave raw-to-robot errors of 0.351–0.405°, 0.131–0.153° and 0.091–0.132°, respectively. The short-to-medium gain survived the reference choices. At 28.5 mm the filter ranking depended on the reference. Static shrinkage increased error from 0.377° to 0.393° against the robot estimate, but reduced it from 0.390° to 0.371° against the optical estimate.


| Span (mm) | Raw | Static | Fitted tracker | Tracker, ϕ = 0.95 |
| --- | --- | --- | --- | --- |
| 28.5 | 0.377 | 0.393 | 0.373 | 0.463 |
| 85.5 | 0.140 | 0.143 | 0.145 | 0.173 |
| 199.5 | 0.111 | 0.111 | 0.115 | 0.130 |
Table 1. Mean absolute apparent-heading disagreement in degrees across the same 32 held-out physical stops. The supplementary tables give 90th percentiles and individual stop errors.

Increasing the span from 85.5 to 199.5 mm reduced mean disagreement by 0.0283° against the robot reference and 0.0292° against the optical reference. Both gains had the same sign in every held-out block. At 199.5 mm the references themselves differed by 0.0738°, or 66% of the 0.1114° raw-to-robot disagreement. This ratio compares magnitudes. Without independently measured headings, it cannot partition the error between the references and the marker pair.

Scaling the three-cell robot-reference error purely by inverse span predicts 0.060° at seven cells (0.140° × 3/7); the observed error was 0.111°. The optical comparison also exceeded its inverse-span extrapolation, 0.081° versus 0.047°. Reference disagreement is one plausible contribution to a nonvanishing error floor. Three spans on one rig cannot identify a limiting floor or establish an optimum beyond 199.5 mm.

Table 2 reports the comparisons within each stop. The short-to-medium improvement was large in block 5 and smaller in block 10. A mean gain in all four blocks still allows individual stops to favor the shorter pair.

| Reference | Span increase (mm) | Mean gain (°) | Median gain (°) | Stops improved / 32 | Range of the four block means (°) |
| --- | --- | --- | --- | --- | --- |
| Robot pose | 28.5 to 85.5 | 0.237 | 0.095 | 25 | 0.055 to 0.544 |
| Other board rows | 28.5 to 85.5 | 0.279 | 0.298 | 26 | 0.171 to 0.551 |
| Robot pose | 85.5 to 199.5 | 0.028 | 0.021 | 19 | 0.007 to 0.057 |
| Other board rows | 85.5 to 199.5 | 0.029 | 0.044 | 21 | 0.015 to 0.047 |

Table 2. Gain is the absolute angular disagreement of the shorter pair minus that of the longer pair at the same stop. Each block contains eight consecutive stops on this rig.

## Measurement limits

The optical reference shares image conditions with the measured pair. The robot reference shares its fitted camera calibration. Agreement between the two comparisons strengthens the observed spacing result on this board, but neither reference measures absolute projected heading independently. Distinguishing a small smoothing gain from reference error requires independently surveyed board poses or a calibrated angular stage, with mount alignment and projection into the image plane included in the uncertainty budget.

The physical sequence ends at image acquisition. It records no tool placement, deadline or retry. The separate simulation in the supplement uses an assigned 12 mm marker spacing for its main comparison, below the 28.5 mm physical minimum. Its 0.032 mm mean tracking gain over static shrinkage applies to the specified heavy-tailed switching model. The assigned cycle times provide no estimate of workstation throughput.

## Data and code availability

The study files provide the calibration and refit scripts, per-stop robot and optical discrepancies, simulation parameters and derived tables. In `study/`, run `python verify.py` to reproduce both physical tables from the released stop-level results. To regenerate them from images and poses, follow `study/README.md` and use the identified USDA DS1 archive [3].

Project repository and study directory: <https://github.com/VEDANT1602/fixture-pose-correction/tree/main/study>.

## Author and disclosures

Vedant Thaker is the sole author. He set the fixture-heading question, identified the risk of testing a tracker under its own assumed dynamics and requested a check on reference-heading error. OpenAI Codex assisted with processing the public robot-pose benchmark, implementing the calibration refits, optical reference and filter comparisons, and drafting the results. The paired stop summaries and their verification also used this assistance.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] J. M. Fitzpatrick, J. B. West and C. R. Maurer Jr. Predicting error in rigid-body point-based registration. IEEE Transactions on Medical Imaging 17, 694–702 (1998). <https://doi.org/10.1109/42.736021>

[2] A. Tabb and K. M. Ahmad Yousef. Solving the robot-world hand-eye(s) calibration problem with iterative methods. Machine Vision and Applications (2017). <https://doi.org/10.1007/s00138-017-0841-7>

[3] A. Tabb and K. M. Ahmad Yousef. Data from: Solving the Robot-World Hand-Eye(s) Calibration Problem with Iterative Methods. USDA Ag Data Commons, dataset DS1. <https://doi.org/10.15482/USDA.ADC/1340592>. DS1 download: <https://ndownloader.figshare.com/files/44531195>

[4] R. E. Kalman. A new approach to linear filtering and prediction problems. Journal of Basic Engineering 82, 35–45 (1960). <https://doi.org/10.1115/1.3662552>
