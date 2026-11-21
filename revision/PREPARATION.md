# Preparation record

Two-marker pose correction under independent and slowly drifting fixture yaw

Vedant Thaker · 21 November 2026

## Original work

Vedant Thaker is the sole author. He designed the original two-marker fixture correction study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

The author reports that the research project began on 2 August 2026. The previous versions and the new revision represent different stages of the work.

## Revision activities

OpenAI Codex assisted with the registration and serial-estimator comparisons, sensitivity implementation, extraction and analysis of measured calibration-board geometry, and verification of numerical results, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Computational checks

In the revision, a fresh execution of the pinned code produced a byte-identical results.csv, and the grid, paired gains and losses, and headline counts passed the repository verifier. The added implementation independently generated the sensitivity results and checked noise-free reconstruction. The added comparisons checked equality of least-squares and direct heading on paired inputs, used separate noise calibration and evaluated both serial regimes. The board result is a reanalysis of public photographs.

## Data and version records

The baseline repository contains the simulator and its 162-row table. At that revision, run python run.py followed by python verify.py. The companion supplement supplies fixture_sensitivity.py, its environment and both generated CSVs. Run python fixture_sensitivity.py to reproduce the additional fixtures and the 27 sensitivity contrasts. The original fixture observations are generated. The supplement includes separate Linux x86_64 environment locks for the baseline and revision. Run python registration_baselines.py for the serial comparison, then python board_check.py for the measured marker check. The supplement includes the derived image coordinates, per-image source hashes, unaggregated chord estimates and sequence-level differences. Optional image extraction uses commit 49486f61fb25722cbcf586b7f4320921d46fb38e of opencv/opencv.

[Original pinned software](https://github.com/VEDANT1602/fixture-pose-correction/tree/be91e32b7e57c2c81a5308da8345031aa1474588) · [Revision code and data](https://github.com/VEDANT1602/fixture-pose-correction/tree/main/revision/supplement)

The reported checks are computational. No independent personal rerun or line-by-line review of these revisions by the author is asserted here.
