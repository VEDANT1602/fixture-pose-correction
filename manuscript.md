# When two fixture markers justify a rotational correction

**Vedant Thaker**  
Working paper · 18 November 2026

## Abstract

A robot can estimate a fixture's translation from the mean position of two markers. Estimating rotation from the same pair introduces a lever-arm effect. A small difference between nearby marker readings can put a distant tool target outside tolerance. Six policies face the same readings, motion budget and one opportunity for recovery in a simulated three-stage planar assembly. On 1,000 challenge fixtures with a 1.85 s deadline and markers 12 mm apart, full rigid correction completed 444 cycles. Translation alone completed 497. Shrinking the estimated rotation toward the taught orientation raised the count to 680. With markers 72 mm apart, full and shrunk rotation each completed 981 cycles. Adding a common localization bias of 0.8 mm reduced full-correction completions to 762 even at the wider separation. Greater marker spacing helps with differential noise. A shift shared by both readings calls for an independent reference.

## From a demonstrated pose to an assembly decision

Consider a fixture that supports three operations. The first and third sit at opposite ends of the part. An operator teaches the robot once. On the next cycle, two optical markers show that the fixture has moved. Translating every taught position together is easy. Rotating the trajectory can also recover the true part frame, but a noisy angle applies a large correction at the outer operations, precisely where the placement tolerance may be smallest.

Singh, Chang and Yu combine task-level sequencing with primitive execution learned from demonstrations, including tests in simulation and on a physical setup [1]. Calinon, Bruno and Caldwell relate motion reproduction to task frames and position-dependent control [2]. Point-registration work by Fitzpatrick, West and Maurer distinguishes error at the fiducials from the error at the target [3]. The present study takes these observations down to a small decision that can be audited end to end. The sequence is already known. The trajectory endpoints are given. Under what marker geometry is an estimated fixture rotation good enough to improve completion before the deadline?

A useful comparison must pay for failed attempts. A method could appear fast simply because it stops on the first miss. It could also rely on an unlimited supply of local measurements during recovery. Here each cycle has a common fixed budget and at most one local retry. Results distinguish first-pass completion, eventual completion and time consumed across all starts.

## Fixture, observations and controls

Three nominal target centers lie at (-36,0), (0,16) and (36,0) mm in their taught work frame, with circular tolerances of 1.30, 1.60 and 0.90 mm, respectively. The actual part undergoes one planar rotation about its center, followed by a translation. Two nominal marker centers sit on the horizontal axis at half the marker span on each side of the origin. Each transformed marker receives independent Gaussian localization error on both coordinates. In the bias condition, both markers also receive a common displacement of 0.8 mm in a direction sampled uniformly for each fixture.

The setup set draws each translation coordinate uniformly in [-2,2] mm and yaw uniformly in [-1,1] degree, with 0.25 mm marker noise per coordinate. A separately generated challenge set draws translation coordinates in [-4.5,4.5] mm and yaw in [-4,4] degrees, with 0.45 mm marker noise. The bias test reuses every draw from the challenge set and adds only the common displacement. Each set has 1,000 fixtures. Marker spans of 12, 36 and 72 mm share the fixture poses, errors and recovery draws within a set. No assembly outcome is used to estimate a policy parameter.

Translation-only correction moves all targets by the observed marker midpoint. Rigid correction also rotates each taught target by the direction of the measured marker-to-marker vector. The gated policy applies the full rigid correction at a stage only when its estimated displacement exceeds 75% of that stage's tolerance. This deadband can avoid a small adjustment and its time cost. It makes no allowance for marker span.

The shrinkage alternative uses the same translation and attenuates the angle. With independent marker noise of standard deviation s and span b, the first-order angular variance around a horizontal baseline is 2s²/b². If the fixture yaw prior has variance v, the minimum mean-square linear weighting under independent zero-mean yaw and noise is v/(v + 2s²/b²). The test freezes v at the square of two degrees in radians and s at 0.45 mm in every condition. It multiplies the measured angle by that weight before forming the rotation matrix. This linearization is a control derived for small perturbations. Its settings need not be optimal for the broader challenge poses.

Two further controls use the taught positions unchanged and the true fixture transform, respectively. All six policies reserve the same 0.10 s observation slot. Each stage costs 0.32 s. An adjustment adds 0.06 s plus the correction length divided by 55 mm/s. The realized first-attempt endpoint has independent isotropic 0.12 mm standard deviation per axis. A miss is discovered by an ideal stage-completion check. If the single retry is unused and at least 0.36 s remains, a local correction consumes that interval and leaves a fresh residual with standard deviation 0.27 mm per axis. A failed recovery or exhausted deadline ends the cycle. A stopped cycle contributes its elapsed time, capped at the deadline. Thus the comparison charges the same local recovery to any policy that needs it.

## Does rotation earn its time?

Table 1 uses the challenge fixtures, a 36 mm marker span and a 1.85 s deadline. Each row has the same 1,000 starts. First pass means that all three stages finished before the deadline without a retry. Retries counts cycles that actually attempted the one permitted recovery.

| Correction | First pass | Completed | Retries | Mean elapsed, s |
|---|---|---|---|---|
| Taught replay | 8 | 44 | 992 | 1.142 |
| Translation | 290 | 497 | 669 | 1.659 |
| Rigid | 705 | 895 | 244 | 1.525 |
| Gated rigid | 703 | 894 | 246 | 1.518 |
| Shrunk angle | 727 | 918 | 232 | 1.517 |
| True transform | 1000 | 1000 | 0 | 1.436 |

The short mean elapsed time for replay reflects early failures. Full rigid correction completed 398 more cycles on balance than translation. At this span the deadband removed 107 commanded adjustments across the 1,000 starts. It changed the final outcome on only three paired fixtures, gaining one and losing two. The more consequential decision was how confidently to estimate orientation.

Table 2 holds the fixture draws and deadline fixed and varies the sensing geometry. The translation estimate is independent of marker span because the noise draws are held fixed and the two exact marker positions average to the fixture center.

| Span, mm | Translation completed | Rigid completed | Shrunk angle completed | Rigid with bias |
|---|---|---|---|---|
| 12 | 497 | 444 | 680 | 367 |
| 36 | 497 | 895 | 918 | 692 |
| 72 | 497 | 981 | 981 | 762 |

At 12 mm the differential-noise approximation predicts roughly 3.04 degrees of angular standard deviation. A target 36 mm away amplifies that to about 1.91 mm of lateral error before translation and tracking error. The end target permits 0.90 mm. Shrinkage gained 342 completions and lost 106 compared with full rotation on the paired trials, a net 23.6 percentage points. A normal interval using the sample variance of the paired binary difference gives approximately 19.7 to 27.5 points at 95%. This is sampling uncertainty for the constructed fixture distribution. At 72 mm the same calculation predicts roughly 0.51 degrees or 0.32 mm at the end target. Full and shrunk rotation traded three successes in each direction and finished tied.

The wider marker pair cannot diagnose a common shift. The shift cancels in the difference vector used to compute yaw and survives in the midpoint. At 72 mm it reduced full-correction first-pass completions from 922 to 424. The time budget matters separately. For the 36 mm unbiased challenge, rigid correction completed 675, 895 and 949 cycles at 1.55, 1.85 and 2.20 s. Additional time primarily makes a local retry useful. Under the easy setup conditions at 36 mm and 1.85 s, translation and full rotation each completed all 1,000 cycles, but translation needed 17 retries and rotation needed 36.

## Limits and replication

The marker model excludes occlusion, wrong correspondences, perspective distortion, joint compliance and out-of-plane fixture pitch. The local recovery and inspection rules are deliberately favorable, and none of the timing constants came from a production line. Consequently the measured quantities here are simulation counts and assigned cycle times. A physical trial could begin with a rigid fixture on a rotary stage, randomized translations, several marker spans and an independent position measurement at the tight end target. Recording residuals and retry durations would test the angular-noise model and the operational consequence separately.

Run python run.py with Python 3.10 or newer and NumPy. The script writes 162 grouped condition-policy rows to results.csv from generator seed 1705. It checks the exact midpoint identity and noise-free heading reconstruction. A failed cycle remains in the reported denominator, and the CSV includes paired gains and losses against full rotation. In this benchmark it was worth correcting rotation when either the marker baseline or the prior made that angle sufficiently precise. A wider baseline helped with differential reading noise. Independent position information would still be needed to resolve a shared frame error.

## Research and writing assistance

Vedant Thaker supplied the research brief and source materials. OpenAI Codex assisted with study design, implementation, execution, literature review and drafting. Clever Humanizer suggested edits to the abstract. The final wording was checked against the analysis.

## References

[1] S. Singh, Q. Chang and T. Yu. Hierarchical learning for robotic assembly tasks leveraging learning from demonstration. Advanced Robotics Research, 2025. https://doi.org/10.1002/adrr.202400024

[2] S. Calinon, D. Bruno and D. G. Caldwell. A task-parameterized probabilistic model with minimal intervention control. IEEE International Conference on Robotics and Automation, 2014. https://doi.org/10.1109/ICRA.2014.6907339

[3] J. M. Fitzpatrick, J. B. West and C. R. Maurer Jr. Predicting error in rigid-body point-based registration. IEEE Transactions on Medical Imaging 17, 694–702, 1998. https://doi.org/10.1109/42.736021
