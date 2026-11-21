# Marker spacing and temporal smoothing in two-point fixture heading estimates

Research working paper by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana, USA.

A camera can estimate fixture heading from two marks, but the available robot reference also depends on the camera calibration. At 32 held-out stops of one robot, widening the pair from 28.5 to 85.5 mm reduced mean absolute apparent-heading disagreement from 0.377° to 0.140°. Widening it again to 199.5 mm gave 0.111°. Two checks put those gains in context. Removing a training block and refitting the calibration changed the reference heading by 0.026° on average. An optical reference fitted using 40 other board corners differed from the robot reference by 0.074°. Both references showed the large short-to-medium spacing benefit. Their disagreement and the diminishing gain at the longest tested span limit claims about very small filter effects or wider fixtures.

[Paper (PDF)](manuscript.pdf) · [Editable text](manuscript.md) · [Methods and study files](study/README.md) · [Manuscript history](study/VERSION.md)

[Author-owned software license](LICENSE) · [Third-party terms](LICENSING.md) · [Previous version](https://github.com/VEDANT1602/fixture-pose-correction/tree/0f605edeb06fb7f8874fab52b3896616c5f6af44)
