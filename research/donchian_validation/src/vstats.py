"""Statistics used by the validation (pure Python)."""
import itertools
import math
import random
import statistics


def _betacf(a, b, x):
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def _betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1 - bt * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """One-sided P(T > t)."""
    p2 = _betai(df / 2.0, 0.5, df / (df + t * t))
    return p2 / 2 if t > 0 else 1 - p2 / 2


def chi2_sf(x, k):
    """P(X > x) for chi-square with k degrees of freedom (regularized upper incomplete gamma)."""
    a, x = k / 2.0, x / 2.0
    if x <= 0:
        return 1.0
    if x < a + 1:
        s, term, n = 1.0 / a, 1.0 / a, 0
        while abs(term) > 1e-14 * abs(s) and n < 1000:
            n += 1
            term *= x / (a + n)
            s += term
        return 1 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = b + an / c
        c = c if abs(c) > 1e-300 else 1e-300
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def summary(rs):
    n = len(rs)
    if n == 0:
        return {"trades": 0}
    m = statistics.mean(rs)
    sd = statistics.stdev(rs) if n > 1 else 0.0
    wins, losses = [r for r in rs if r > 0], [r for r in rs if r <= 0]
    eq = peak = 1.0
    mdd = cum = cpeak = mdd_r = 0.0
    streak = worst = 0
    for r in rs:
        eq *= 1 + 0.005 * r
        peak = max(peak, eq)
        mdd = max(mdd, 1 - eq / peak)
        cum += r
        cpeak = max(cpeak, cum)
        mdd_r = max(mdd_r, cpeak - cum)
        streak = streak + 1 if r <= 0 else 0
        worst = max(worst, streak)
    t = m / (sd / math.sqrt(n)) if sd > 0 else None
    gl = -sum(losses)
    return {"trades": n, "win_rate_pct": len(wins) / n * 100, "profit_factor": sum(wins) / gl if gl > 0 else None,
                "expectancy_r": m, "sd_r": sd, "t_stat": t, "p_one_sided": t_sf(t, n - 1) if t is not None else None, "total_r": sum(rs),
                "max_drawdown_r": mdd_r, "max_drawdown_pct_at_0_5pct_risk": mdd * 100, "return_pct_at_0_5pct_risk": (eq - 1) * 100,
                "longest_losing_streak": worst, "avg_win_r": statistics.mean(wins) if wins else None,
                "avg_loss_r": statistics.mean(losses) if losses else None, "median_r": statistics.median(rs)}


def iid_bootstrap_ci(rs, runs, seed, level=0.95):
    rnd = random.Random(seed)
    n = len(rs)
    means = sorted(sum(rnd.choices(rs, k=n)) / n for _ in range(runs))
    a = (1 - level) / 2
    return means[int(a * runs)], means[int((1 - a) * runs) - 1]


def stationary_bootstrap_indices(n, mean_block, rnd):
    """Politis-Romano stationary bootstrap: blocks of geometric length with the given mean (circular)."""
    p = 1.0 / mean_block
    out, i = [], rnd.randrange(n)
    while len(out) < n:
        out.append(i)
        i = rnd.randrange(n) if rnd.random() < p else (i + 1) % n
    return out


def block_bootstrap_mean_ci(groups, runs, seed, mean_block, level=0.95):
    """CI of the per-trade mean when trades are resampled in blocks of consecutive calendar groups (months).

    ``groups`` is a list (one entry per month, in order) of lists of trade results; empty months allowed.
    """
    rnd = random.Random(seed)
    n = len(groups)
    means = []
    for _ in range(runs):
        idx = stationary_bootstrap_indices(n, mean_block, rnd)
        tot = cnt = 0
        for i in idx:
            tot += sum(groups[i])
            cnt += len(groups[i])
        if cnt:
            means.append(tot / cnt)
    means.sort()
    a = (1 - level) / 2
    return means[int(a * len(means))], means[int((1 - a) * len(means)) - 1], means


def ljung_box(xs, lags):
    n = len(xs)
    m = statistics.mean(xs)
    d = [x - m for x in xs]
    c0 = sum(v * v for v in d) / n
    acf, q = [], 0.0
    for k in range(1, lags + 1):
        ck = sum(d[i] * d[i - k] for i in range(k, n)) / n
        r = ck / c0
        acf.append(r)
        q += r * r / (n - k)
    q *= n * (n + 2)
    return {"lags": lags, "q": q, "p_value": chi2_sf(q, lags), "acf": acf}


def runs_test(signs):
    """Wald-Wolfowitz runs test on a sequence of booleans (wins). Returns z and two-sided p."""
    n1 = sum(signs)
    n2 = len(signs) - n1
    runs = 1 + sum(1 for a, b in itertools.pairwise(signs) if a != b)
    mu = 2 * n1 * n2 / (n1 + n2) + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
    z = (runs - mu) / math.sqrt(var)
    return {"runs": runs, "expected": mu, "z": z, "p_two_sided": 2 * norm_sf(abs(z))}
