# Marker spacing and temporal smoothing in two-point fixture heading estimates

Robot-camera measurement report by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana, USA. Revised November 24, 2026.

The apparent heading of a checkerboard row can be estimated from either two adjacent corners or a wider pair in the same image. On a Denso robot with a Sony camera, extending the span from 28.5 to 85.5 mm reduced mean absolute disagreement with a robot-pose reference from 0.377° to 0.140°. The wider pair improved on the shorter one at 25 of 32 held-out stops. An optical reference fitted to the other board rows favored the wider pair at 26 stops. Extending the span to 199.5 mm yielded a smaller mean gain, about 0.03° against either reference. At 28.5 mm, changing references reversed the ranking of raw and statically smoothed headings. For this rig the reference choice preserved the spacing result and changed the smoothing decision.

[Paper (PDF)](manuscript.pdf) · [Editable text](manuscript.md) · [Methods and study files](study/README.md) · [Manuscript history](study/VERSION.md)

[Author-owned software license](LICENSE) · [Third-party terms](LICENSING.md) · [Previous version](https://github.com/VEDANT1602/fixture-pose-correction/tree/64e2d55e15131c088588c1c377115ac360749915)
