"""Independent planar fixture reconstruction. All observations are generated."""
import csv
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
TARGETS = np.array([[-36., 0.], [0., 16.], [36., 0.]])
TOLS = np.array([1.30, 1.60, 0.90])
POLICIES = ["replay", "translation", "rigid", "gated", "shrunk", "oracle"]


def rotate(points, angles):
    cos, sin = np.cos(angles)[:, None], np.sin(angles)[:, None]
    x, y = points.T
    return np.stack((cos * x - sin * y, sin * x + cos * y), axis=-1)


def draw_fixtures(seed, n, setup=False):
    rng = np.random.default_rng(seed)
    trans_bound, yaw_bound = (2., 1.) if setup else (4.5, 4.)
    return dict(translation=rng.uniform(-trans_bound, trans_bound, (n, 2)),
                angle=np.radians(rng.uniform(-yaw_bound, yaw_bound, n)),
                marker_z=rng.normal(size=(n, 2, 2)),
                bias_angle=rng.uniform(0, 2*np.pi, n),
                tracking=rng.normal(0, .12, (n, 3, 2)),
                recovery=rng.normal(0, .27, (n, 3, 2)))


def estimate(f, span, noise, bias):
    markers = np.array([[-span / 2, 0.], [span / 2, 0.]])
    ideal = rotate(markers, f["angle"]) + f["translation"][:, None]
    obs = ideal + noise * f["marker_z"]
    obs += bias * np.stack([np.cos(f["bias_angle"]), np.sin(f["bias_angle"])], axis=1)[:, None]
    delta = obs[:, 1] - obs[:, 0]
    return obs.mean(axis=1), np.arctan2(delta[:, 1], delta[:, 0])


def cycle(f, span, noise, bias, deadline, policy, prior_deg=2.):
    truth = rotate(TARGETS, f["angle"]) + f["translation"][:, None]
    mid, heading = estimate(f, span, noise, bias)
    if policy == "oracle":
        planned = truth.copy()
    elif policy == "replay":
        planned = np.broadcast_to(TARGETS, truth.shape)
    elif policy == "translation":
        planned = TARGETS + mid[:, None]
    else:
        if policy == "shrunk":
            prior = np.radians(prior_deg)**2
            heading *= prior / (prior + 2 * .45**2 / span**2)
        planned = rotate(TARGETS, heading) + mid[:, None]
        if policy == "gated":
            apply = np.linalg.norm(planned - TARGETS, axis=-1) > .75 * TOLS
            planned = np.where(apply[:, :, None], planned, TARGETS)
    n = len(truth)
    elapsed = np.full(n, .10)
    active = np.ones(n, dtype=bool)
    retry = np.zeros(n, dtype=bool)
    first_error = np.linalg.norm(planned + f["tracking"] - truth, axis=-1)
    retry_error = np.linalg.norm(f["recovery"], axis=-1)
    for k, tol in enumerate(TOLS):
        displacement = np.linalg.norm(planned[:, k] - TARGETS[k], axis=1)
        cost = .32 + np.where(displacement > 1e-12, .06 + displacement/55., 0.)
        elapsed[active] += cost[active]
        active &= elapsed <= deadline
        missed = active & (first_error[:, k] > tol)
        eligible = missed & ~retry & (elapsed + .36 <= deadline)
        elapsed[eligible] += .36
        retry |= eligible
        active[missed] = False
        active[eligible] = retry_error[eligible, k] <= tol
    return active, active & ~retry, retry, np.minimum(elapsed, deadline)


def comparison(rows, rigid):
    success, fast, retry, elapsed = rows
    difference = success.astype(int) - rigid.astype(int)
    return dict(n=len(success), completed=int(success.sum()), first_pass=int(fast.sum()),
                retry_count=int(retry.sum()), mean_elapsed=round(elapsed.mean(), 6),
                gains_vs_rigid=int((difference == 1).sum()), losses_vs_rigid=int((difference == -1).sum()),
                difference_pp=round(100*difference.mean(), 4),
                se_pp=round(100*difference.std(ddof=1)/np.sqrt(len(difference)), 4))


def save(name, data):
    with (OUT / name).open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0])
        writer.writeheader()
        writer.writerows(data)


def main():
    baseline = []
    for group in ["setup", "challenge", "challenge_bias"]:
        setup = group == "setup"
        f = draw_fixtures(51705 + int(setup), 1000, setup)
        bias, noise = .8 * (group == "challenge_bias"), .25 if setup else .45
        mid, heading = estimate(f, 36, 0, 0)
        assert np.allclose(mid, f["translation"]) and np.allclose(heading, f["angle"])
        for span in [12, 36, 72]:
            for deadline in [1.55, 1.85, 2.20]:
                outcomes = {p: cycle(f, span, noise, bias, deadline, p) for p in POLICIES}
                for p, outcome in outcomes.items():
                    baseline.append(dict(condition=group, span_mm=span, deadline_s=deadline,
                                         policy=p, **comparison(outcome, outcomes["rigid"][0])))
    save("independent_results.csv", baseline)
    # Distinct seed and 10,000 new fixtures; pair all variants within fixture.
    f = draw_fixtures(71354, 10000)
    sensitivity = []
    for span in [12, 36, 72]:
        for noise in [.25, .45, .65]:
            rigid = cycle(f, span, noise, 0, 1.85, "rigid")[0]
            for prior in [1., 2., 4.]:
                outcome = cycle(f, span, noise, 0, 1.85, "shrunk", prior)
                sensitivity.append(dict(span_mm=span, marker_sd_mm=noise, prior_sd_deg=prior,
                                        **comparison(outcome, rigid)))
    save("sensitivity.csv", sensitivity)


if __name__ == "__main__":
    main()
