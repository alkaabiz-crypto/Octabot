"""Trade statistics. Pure Python, including the Student-t p-value."""
import math
import random
import statistics

import protocol as P


def _betacf(a, b, x):
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
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
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_sf(t, df):
    """P(T > t) for Student's t with df degrees of freedom (one-sided)."""
    if df <= 0:
        return float("nan")
    p_two = _betai(df / 2.0, 0.5, df / (df + t * t))
    return p_two / 2.0 if t > 0 else 1.0 - p_two / 2.0


def max_drawdown_r(rs):
    peak = cum = dd = 0.0
    for r in rs:
        cum += r
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    return dd


def max_drawdown_pct(rs, risk=P.RISK_PER_TRADE):
    eq = peak = 1.0
    dd = 0.0
    for r in rs:
        eq *= 1 + risk * r
        peak = max(peak, eq)
        dd = max(dd, 1 - eq / peak)
    return dd * 100


def bootstrap_ci(rs, runs=P.BOOTSTRAP_RUNS, seed=P.SEED):
    if len(rs) < 2:
        return None, None
    rnd = random.Random(seed)
    n = len(rs)
    means = sorted(sum(rnd.choices(rs, k=n)) / n for _ in range(runs))
    return means[int(0.025 * runs)], means[int(0.975 * runs) - 1]


def summarize(rs, with_ci=True):
    """Metrics for a list of per-trade net R results, in chronological order."""
    n = len(rs)
    if n == 0:
        return dict(trades=0)
    wins, losses = [r for r in rs if r > 0], [r for r in rs if r <= 0]
    mean = statistics.mean(rs)
    sd = statistics.stdev(rs) if n > 1 else 0.0
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    streak = worst = 0
    for r in rs:
        streak = streak + 1 if r <= 0 else 0
        worst = max(worst, streak)
    gross_loss = -sum(losses)
    eq = 1.0
    for r in rs:
        eq *= 1 + P.RISK_PER_TRADE * r
    out = dict(trades=n, win_rate_pct=len(wins) / n * 100, profit_factor=(sum(wins) / gross_loss) if gross_loss > 0 else None,
               expectancy_r=mean, t_stat=t, p_one_sided=t_sf(t, n - 1) if t is not None else None, total_r=sum(rs),
               max_drawdown_r=max_drawdown_r(rs), max_drawdown_pct=max_drawdown_pct(rs), return_pct=(eq - 1) * 100,
               longest_losing_streak=worst, avg_win_r=statistics.mean(wins) if wins else None,
               avg_loss_r=statistics.mean(losses) if losses else None)
    if with_ci:
        out["ci95_low"], out["ci95_high"] = bootstrap_ci(rs)
    return out


def p_random(actual_mean, random_means):
    """Share of random-entry runs at least as good as the strategy (with the +1 correction)."""
    if not random_means:
        return None
    return (sum(m >= actual_mean for m in random_means) + 1) / (len(random_means) + 1)


def holm(pvalues):
    """Holm-Bonferroni adjusted p-values. ``pvalues`` is a dict name -> p (None entries are passed through)."""
    items = sorted(((p, k) for k, p in pvalues.items() if p is not None))
    m, adj, running = len(items), {}, 0.0
    for rank, (p, k) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        adj[k] = running
    for k, p in pvalues.items():
        if p is None:
            adj[k] = None
    return adj
