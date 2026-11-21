# Two-marker pose correction under independent and slowly drifting fixture yaw

**Vedant Thaker**  
Independent Researcher, Jeffersonville, Indiana, United States  
Correspondence: vthaker1@asu.edu  
21 November 2026

## Abstract

With two symmetric markers, least-squares rigid registration uses the marker midpoint and the full observed heading. A short baseline can magnify heading noise enough that a distant assembly target misses tolerance. In the original 1,000 simulated challenge cycles at 12 mm spacing, translation completed 497, rigid registration 444 and fixed yaw shrinkage 680. A separate comparison calibrated yaw and camera variances from duplicate views. On 10,000 new cycles at 12 mm spacing, calibrated shrinkage completed 6,792 cycles under independent yaw. A Kalman filter assuming persistent yaw completed 6,041. With the same marginal yaw spread but slowly drifting poses, the corresponding counts were 6,683 and 8,128. In 13 calibration-board photographs, widening the baseline from two to eight squares reduced angular RMS discrepancy from 0.147° to 0.085°. Held-out target discrepancy stayed near 0.04 board squares. The photographs test geometric consistency, while the timing and completion counts come from simulation.

## Fiducial registration at the tool target

A camera can locate the midpoint of a fixture accurately and still place a taught target outside tolerance. The angular error applies over the lever arm from the midpoint to the tool, and the outermost stage here allows only 0.90 mm. Classical point-based registration distinguishes fiducial error from error at a separate target [1]. Demonstration-based assembly and task-parameterized control address how to teach and execute a sequence [2, 3]. This experiment takes the sequence as given and tests the consequence of two-marker registration at the actual stage endpoints.

Each candidate correction receives the same two marker observations. Holding the sensing budget fixed lets the experiment isolate a choice the controller must make: translate the taught frame, rotate it through the entire estimated yaw, or discount that yaw. Completion by the deadline is the primary outcome because an improvement in geometric accuracy can still cost enough motion time to exhaust the single retry.

## Two-marker pose and angular shrinkage

The taught target centers are (−36, 0), (0, 16) and (36, 0) mm. Their radial tolerances are 1.30, 1.60 and 0.90 mm in that order. A planar rotation about the origin and a translation locate the true fixture. Two markers straddle the origin at half-span b/2. Each observed coordinate has independent Gaussian error with standard deviation s. A bias condition adds the same vector of length 0.8 mm, with a uniformly sampled direction, to both markers.

The setup distribution has independent uniform translation coordinates in [−2, 2] mm, uniform yaw in [−1°, 1°] and s = 0.25 mm. The challenge distribution uses [−4.5, 4.5] mm, [−4°, 4°] and s = 0.45 mm. Each has 1,000 fixtures. The biased challenge uses the same fixtures and noise draws as the unbiased challenge. Spans of 12, 36 and 72 mm, the policies and the deadline variants share each regime’s draws.

Translation uses the observed midpoint. Full rigid correction also rotates each target by the angle of the observed marker difference vector. Gated correction applies the rigid displacement only at stages where it exceeds 75% of tolerance. Shrinkage multiplies the observed angle by w = v/(v + 2s₀²/b²). Here v = (2π/180)² rad² and s₀ = 0.45 mm are fixed estimator settings. Linearizing the marker difference gives angle-error variance 2s²/b². Under independent, zero-mean angle and error this weight minimizes mean squared angular error among linear weights if their variances match the assumed inputs. It need not optimize deadline completion. The nominal weights are 0.302, 0.796 and 0.940 at increasing spans. Two controls replay the taught target and apply the true fixture transform.

For a least-squares planar rigid transform [4], minimizing the summed squared marker residuals first sets translation to the observed centroid because the nominal pair is centered. With no scale change and positive determinant, the minimizing rotation maps the direction of the nominal difference vector onto the direction of the observed vector. Its angle is atan2(Δy, Δx). An SVD Procrustes fit on all 180,000 simulated two-marker inputs in the serial comparison agreed with the direct angle to 1.12 × 10⁻¹⁶ radians. These are equivalent baselines under equal coordinate weights. They give no information about a common positional offset.

## Counting completions against the cycle deadline

Every policy pays 0.10 s for sensing and 0.32 s per attempted stage. A nonzero adjustment adds 0.06 s plus its length divided by 55 mm/s. Independent tracking error has standard deviation 0.12 mm per coordinate. An ideal check detects a miss. A cycle can buy one local retry for 0.36 s if time remains. Its residual error has standard deviation 0.27 mm per axis. A failed retry or deadline terminates the cycle. Elapsed time is capped at the deadline, and failures stay in the denominator.

Table 1 shows why elapsed time alone rewards the wrong behavior. Taught replay consumes the least time because most cycles stop early. At 36 mm, shrinkage completes 23 more challenge cycles than full rotation. Relative to full rotation, the gated policy avoids 107 commanded adjustments; it completes one previously failed cycle and loses two that previously completed.

| Correction | First pass | Completed | Retries | Mean time (s) |
| --- | --- | --- | --- | --- |
| Taught replay | 8 | 44 | 992 | 1.142 |
| Translation | 290 | 497 | 669 | 1.659 |
| Full rigid | 705 | 895 | 244 | 1.525 |
| Gated rigid | 703 | 894 | 246 | 1.518 |
| Shrunk angle | 727 | 918 | 232 | 1.517 |
| True transform | 1,000 | 1,000 | 0 | 1.436 |

Table 1. Challenge fixtures at 36 mm and 1.85 s. Counts use all 1,000 starts per policy. First pass counts cycles completed without a retry.

## Differential marker noise versus common displacement

At 12 mm the differential-noise approximation predicts a yaw standard deviation of 3.04°. At the outer targets this corresponds to 1.91 mm of lateral error before tracking and translation error, against a final-stage tolerance of 0.90 mm. Shrinkage gains 342 paired successes and loses 106 relative to full rotation. The net difference is 23.6 percentage points. A pointwise 95% normal interval, using the sample standard error of −1/0/+1 fixture-level differences, spans 19.7 to 27.5 points. This interval describes draws from this generator and this contrast.

At 72 mm the predicted yaw-induced lateral error falls to 0.32 mm. Shrinkage and full rotation exchange three successes in each direction. A displacement shared by both markers cancels in their difference and remains in their midpoint. At 72 mm it lowers rigid first-pass completions from 922 to 424 and eventual completions from 981 to 762. With an unbiased 36 mm span, rigid completion ranges from 675 at 1.55 s to 895 at 1.85 s and 949 at 2.20 s. In the easier setup at 36 mm and 1.85 s, translation and rigid correction both finish every cycle, using 17 and 36 retries respectively.

| Span (mm) | Translation | Full rigid | Shrunk angle | Rigid, biased |
| --- | --- | --- | --- | --- |
| 12 | 497 | 444 | 680 | 367 |
| 36 | 497 | 895 | 918 | 692 |
| 72 | 497 | 981 | 981 | 762 |

Table 2. Completed cycles out of 1,000 challenge starts by 1.85 s. The last column adds a 0.8 mm shift to both marker observations.

## A yaw weight calibrated for the wrong localization noise

A separate implementation drew 10,000 additional challenge fixtures, using seed 71354, and paired all 27 combinations of three spans, three true localization noise levels (0.25, 0.45 and 0.65 mm) and three assumed yaw standard deviations (1°, 2° and 4°). The estimator continued to use s₀ = 0.45 mm. All comparisons use a 1.85 s deadline and zero common bias.

With 12 mm spacing and the 2° prior, shrinkage changes completion relative to full rotation by −3.82, +18.90 and +25.76 percentage points as actual noise increases. The Monte Carlo standard errors are 0.62, 0.64 and 0.60 points. At 36 mm those effects are −0.39, +2.37 and +6.25 points. At 72 mm they are 0.00, +0.19 and +0.57 points. At short spacing and 0.25 mm noise, simply changing the assumed yaw spread from 1° to 4° changes the paired difference from −18.57 to +10.26 points. These finite comparisons demonstrate that a fixed weight can suppress useful yaw information. They do not estimate optimal settings for a production fixture.

## Noise calibration and a temporal alternative

For each camera-noise setting and marker span, 600 independently generated calibration poses supplied two images each. The variance of the between-image coordinate differences, divided by two, estimates the per-coordinate noise variance. The variance of the two-image mean heading, minus half the estimated single-image angular variance, estimates the yaw prior variance v. These calibration draws are separate from every scored fixture. Single-image calibrated shrinkage uses v/(v + R), where R is twice the calibrated coordinate variance divided by squared span. The variance subtraction uses the small-angle approximation. No completion labels determine the weight.

The temporal comparator uses the scalar state equation θₜ = ϕθₜ₋₁ + ηₜ and measurement zₜ = θₜ + εₜ [5]. Its filter assumes ϕ = 0.95, process variance (1 − ϕ²)v, and measurement variance R. The first prediction has mean zero and variance v. For ϕ = 0 the update is just the single-image calibrated rule. Every method uses the current unfiltered marker midpoint. Performance is therefore conditional on the serial structure of yaw, with no temporal advantage conferred through translation.

The test has 100 independent sequences of 100 cycles at each setting. Yaw is Gaussian with standard deviation 4/√3 degrees, matching the variance of the earlier uniform [−4°, 4°] distribution. It is independently redrawn or has lag-one correlation 0.95. The latter corresponds to a yaw correlation half-life of 13.5 fixtures. This is an illustrative production pattern. Both generators use the same independent innovations, translations, marker errors and tracker/retry draws. Uncertainty in a paired comparison uses the 100 sequence-level differences, allowing within-sequence dependence.

At 12 mm, 0.45 mm noise and independent yaw, the calibrated rule gains 22.10 percentage points over rigid correction (sequence-based Monte Carlo SE 0.67 points). With correlated yaw the temporal filter gains 35.37 points over rigid correction (SE 0.84). At 0.25 mm actual noise and independent yaw, calibrating the weight raises completions from 7,272 with the fixed rule to 8,169 of 10,000. After independent resets, retaining the previous yaw is less effective here than starting each cycle from the population prior. The direct paired difference between the temporal filter and calibrated single-image rule is −7.51 points with independent yaw (SE 0.44) and +14.45 with persistent yaw (SE 0.89).

| Method | Independent yaw | Persistent yaw | Independent RMSE (°) | Persistent RMSE (°) |
| --- | --- | --- | --- | --- |
| Translation | 5,784 | 5,684 | 2.327 | 2.399 |
| Rigid / SVD | 4,582 | 4,591 | 3.032 | 3.031 |
| Fixed shrinkage | 6,777 | 6,680 | 1.867 | 1.903 |
| Calibrated shrinkage | 6,792 | 6,683 | 1.856 | 1.888 |
| Kalman, ϕ = 0.95 | 6,041 | 8,128 | 2.171 | 1.332 |

Table 3. Completed cycles out of 10,000 and angular root-mean-square error, 12 mm spacing, 0.45 mm noise and 1.85 s deadline. The two yaw generators have the same nominal marginal variance. All methods face the same draws within each column.

## Measured fiducial geometry in calibration-board photographs

Thirteen numbered left-camera images distributed with OpenCV [6] show a photographed planar checkerboard at different orientations. Each yielded 54 subpixel intersections on a 9 × 6 grid. Eighteen corner measurements from the top and bottom rows fitted an image-to-board homography in each view. None of the marker or test-target intersections entered that fit. On each of two interior rows, a symmetric pair with separation 2, 4 or 8 squares determined yaw in the rectified board frame. Angular discrepancy is measured against the parallel board rows. Eighteen different intersections on rows 1 and 4 supplied target residuals between the two-marker rigid prediction and the rectified observed target. Each spacing uses 26 chords from the same 13 views.

At spans 2, 4 and 8 squares, angular RMS discrepancies were 0.147°, 0.110° and 0.085°. The respective target RMS discrepancies were 0.0421, 0.0386 and 0.0418 board squares. A wider pair improved angular consistency across these images. It did not improve target discrepancy monotonically. Perspective rectification, distortion and corner localization can all contribute, and the same image provides the registration and held-out measurements. No independent tracker, known physical pitch, serial pose timestamps or robot stage results are available in this check. The measured quantities therefore cannot establish a yaw prior, millimeter noise or deadline performance for the simulated fixture.

## Independent metrology for an assembly-station trial

The assembly simulation isolates a geometric source of error under a specified retry budget. It omits occlusion, incorrect marker matching, perspective distortion, mechanical compliance and out-of-plane pose. The time constants and localization errors are assigned. A line trial would need independent measurements of target error and common displacement, observed retry times, and spacing and yaw ranges representative of the station. The model predicts a benefit from a wider baseline when differential noise dominates, and no change in the midpoint error due to common displacement. These two predictions can be tested separately before adopting a control policy.

## Data and code availability

The baseline repository contains the simulator and its 162-row table. At that revision, run python run.py followed by python verify.py. The companion supplement supplies fixture_sensitivity.py, its environment and both generated CSVs. Run python fixture_sensitivity.py to reproduce the additional fixtures and the 27 sensitivity contrasts. The original fixture observations are generated. The supplement includes separate Linux x86_64 environment locks for the baseline and revision. Run python registration_baselines.py for the serial comparison, then python board_check.py for the measured marker check. The supplement includes the derived image coordinates, per-image source hashes, unaggregated chord estimates and sequence-level differences. Optional image extraction uses commit 49486f61fb25722cbcf586b7f4320921d46fb38e of opencv/opencv.

[Pinned baseline](https://github.com/VEDANT1602/fixture-pose-correction/tree/be91e32b7e57c2c81a5308da8345031aa1474588) · [Revision code and data](https://github.com/VEDANT1602/fixture-pose-correction/tree/main/revision/supplement) · [Preparation record](https://github.com/VEDANT1602/fixture-pose-correction/blob/main/revision/PREPARATION.md)

## Computational verification

In the revision, a fresh execution of the pinned code produced a byte-identical results.csv, and the grid, paired gains and losses, and headline counts passed the repository verifier. The added implementation independently generated the sensitivity results and checked noise-free reconstruction. The added comparisons checked equality of least-squares and direct heading on paired inputs, used separate noise calibration and evaluated both serial regimes. The board result is a reanalysis of public photographs.

## Author contribution

Vedant Thaker is the sole author. He designed the original two-marker fixture correction study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

## Use of computational assistance

OpenAI Codex assisted with the registration and serial-estimator comparisons, sensitivity implementation, extraction and analysis of measured calibration-board geometry, and verification of numerical results, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Competing interests

The author declares no competing interests.

## References

[1] J. M. Fitzpatrick, J. B. West and C. R. Maurer Jr. Predicting error in rigid-body point-based registration. IEEE Transactions on Medical Imaging 17(5), 694–702 (1998). https://doi.org/10.1109/42.736021

[2] S. Singh, Q. Chang and T. Yu. Hierarchical Learning for Robotic Assembly Tasks Leveraging Learning from Demonstration. Advanced Robotics Research 1, 2400024 (2025). https://doi.org/10.1002/adrr.202400024

[3] S. Calinon, D. Bruno and D. G. Caldwell. A task-parameterized probabilistic model with minimal intervention control. IEEE International Conference on Robotics and Automation, 3339–3344 (2014). https://doi.org/10.1109/ICRA.2014.6907339

[4] K. S. Arun, T. S. Huang and S. D. Blostein. Least-squares fitting of two 3-D point sets. IEEE Transactions on Pattern Analysis and Machine Intelligence 9(5), 698–700 (1987). https://doi.org/10.1109/TPAMI.1987.4767965

[5] R. E. Kalman. A new approach to linear filtering and prediction problems. Journal of Basic Engineering 82(1), 35–45 (1960). https://doi.org/10.1115/1.3662552

[6] OpenCV contributors. Camera Calibration, OpenCV 4.12.0, and the accompanying left-camera calibration-board images. The supplement pins the exact sample-data commit. https://docs.opencv.org/4.12.0/dc/dbb/tutorial_py_calibration.html
