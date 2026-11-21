# Two-marker physical and simulated heading

## Reproduce

Tested on Python 3.12.14. Install the packages in requirements.txt in an isolated environment. The CPU results use double precision for model fitting. Small numerical changes between BLAS builds may affect the final digits of optimization output.

1. Fetch [USDA Ag Data Commons DS1.zip](https://ndownloader.figshare.com/files/44531195). Its SHA-256 is 5ea8ab9b0781ea4431d5ea0316d0df695c1b0244eb7b22d6341a6f241c3a279d. Extract it; the directory DS1 contains calibration_object.txt, robot_cali.txt, ExperimentDetails.txt and images/camera0.
2. Run `python robot_bench.py /path/to/DS1`. This fits the camera and robot geometry using 56 training images. It exports robot_bench_summary.csv and robot_bench_errors.csv. Test robot poses alone predict the reference test image coordinates; the fitted camera never sees held-out images during parameter training.
3. Run `python mixed_fixture.py`. This exports fixture_results.csv and timing_results.csv. Identical test draws are shared across methods, spans and camera noise levels within a generator. Do not pool observations across these conditions as if independent.

## Definitions

The physical angle is the axial direction of the projected line between two identified points; it is periodic in 180°. The projected line uses the same two known board points as the observed line. The eight-frame test blocks have zero-based labels 2, 5, 8 and 10. Temporal estimators restart at a block boundary. The robot transforms operate on the input 4×4 pose matrix in either direction; the direction and nonlinear fit with the smaller training reprojection loss is used. A consistently oriented grid is enforced before fitting.

The simulated primary endpoint is radial error at the rightmost 36 mm target. The reported standard error uses 120 independent sequence-level means. Tracking error, deadlines, stage times and retry noise enter only the simulated completion endpoint. Physical runs do not measure those quantities.

The source data are referenced at the original host, and all distributed CSVs are outputs of the supplied programs. No third-party camera images, robot input matrices or library binaries are bundled.
