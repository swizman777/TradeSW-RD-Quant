"""Phase 2.A Hurst metrics: 5 harmonised metrics (CONTRAT section 3 / Annexe A.3).

The 5 obligatoires:
    1. Information Coefficient (IC) : corr(signal_t, ret_{t+1})
    2. Sharpe net (already net of fees+slippage at compute_pnl_hurst stage)
    3. AIC parsimony
    4. Diebold-Mariano test vs buy-and-hold (p-value)
    5. Bootstrap 1000x CI on Sharpe and IC

All bootstrap RNG paths are seeded (np.random.default_rng(42)) for
reproducibility (CONTRAT "Reproductibilite" clause).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.metrics import sharpe

BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 42
TRADING_DAYS = 252


@dataclass(frozen=True)
class BootstrapCI:
    """95% percentile confidence interval."""

    mean: float
    lower: float
    upper: float


def information_coefficient(signal: pd.Series, future_returns: pd.Series) -> float:
    """IC = Pearson corr(signal_t, ret_{t+1}).

    Caller passes the t-aligned signal and the SAME-index t-aligned
    future returns (the shift to t+1 is the caller's responsibility - we
    only correlate the two series as given to keep the function pure).
    """
    aligned = pd.concat([signal, future_returns], axis=1, join="inner").dropna()
    if len(aligned) < 3:
        return float("nan")
    s = aligned.iloc[:, 0]
    r = aligned.iloc[:, 1]
    if s.std(ddof=1) < 1e-12 or r.std(ddof=1) < 1e-12:
        return float("nan")
    return float(s.corr(r))


def aic_strategy(ret_strategy_net: pd.Series, n_params: int) -> float:
    """Simple AIC = 2k - 2 log L on a Gaussian-likelihood approximation.

    n_params for Phase 2.A overlay binaire = 3 (window, refit_step, H threshold).
    """
    r = ret_strategy_net.dropna()
    n = len(r)
    if n < 2:
        return float("nan")
    sigma2 = float(r.var(ddof=1))
    if sigma2 <= 0 or not np.isfinite(sigma2):
        return float("nan")
    log_lik = -0.5 * n * (np.log(2 * np.pi * sigma2) + 1.0)
    return float(2 * n_params - 2 * log_lik)


def diebold_mariano(
    err_a: pd.Series,
    err_b: pd.Series,
    horizon: int = 1,
) -> tuple[float, float]:
    """Diebold-Mariano test on squared-error loss differential.

    Returns (DM statistic, two-sided p-value). Newey-West variance with
    `horizon - 1` lags (=0 for horizon=1, i.e. plain variance).

    Convention: positive DM means model A has HIGHER loss than B,
    i.e. B forecasts better.
    """
    aligned = pd.concat([err_a, err_b], axis=1, join="inner").dropna()
    if len(aligned) < 10:
        return float("nan"), float("nan")
    d = (aligned.iloc[:, 0] ** 2 - aligned.iloc[:, 1] ** 2).values
    n = len(d)
    mean_d = float(np.mean(d))
    # Newey-West with horizon-1 lags
    var_d = float(np.var(d, ddof=1))
    for lag in range(1, horizon):
        cov = float(np.cov(d[:-lag], d[lag:], ddof=1)[0, 1])
        weight = 1.0 - lag / horizon
        var_d += 2.0 * weight * cov
    if var_d <= 0 or not np.isfinite(var_d):
        return float("nan"), float("nan")
    dm = mean_d / np.sqrt(var_d / n)
    # Two-sided p-value via normal approximation
    from math import erf, sqrt  # noqa: PLC0415

    p = 2.0 * (1.0 - 0.5 * (1.0 + erf(abs(dm) / sqrt(2.0))))
    return float(dm), float(p)


def bootstrap_ci(
    series: pd.Series,
    statistic: str = "sharpe",
    n_boot: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
    ci: float = 0.95,
) -> BootstrapCI:
    """Bootstrap percentile CI on `statistic` of a series.

    `statistic` in {"sharpe", "mean"}. Reproducible via fixed seed.
    """
    arr = series.dropna().values
    n = len(arr)
    if n < 10:
        return BootstrapCI(mean=float("nan"), lower=float("nan"), upper=float("nan"))
    rng = np.random.default_rng(seed)
    stats = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        if statistic == "sharpe":
            std = sample.std(ddof=1)
            if std < 1e-12:
                stats[i] = np.nan
            else:
                stats[i] = sample.mean() / std * np.sqrt(TRADING_DAYS)
        else:
            stats[i] = float(sample.mean())
    stats = stats[np.isfinite(stats)]
    if len(stats) < 10:
        return BootstrapCI(mean=float("nan"), lower=float("nan"), upper=float("nan"))
    lo_q = (1.0 - ci) / 2.0
    hi_q = 1.0 - lo_q
    return BootstrapCI(
        mean=float(np.mean(stats)),
        lower=float(np.quantile(stats, lo_q)),
        upper=float(np.quantile(stats, hi_q)),
    )


def summarise_hurst(
    df: pd.DataFrame,
    n_params: int = 3,
) -> dict[str, float]:
    """One-shot summary for the verdict (5 metrics + raw sharpes + spread).

    Expects `df` columns: ret_strategy_net, ret_bh, h_value, weight.
    """
    sharpe_net = sharpe(df["ret_strategy_net"])
    sharpe_bh = sharpe(df["ret_bh"])
    # IC: align signal_t (h_value or weight) with ret_{t+1}
    ic_signal = df["h_value"]
    future_ret = df["ret_decimal"].shift(-1)
    ic = information_coefficient(ic_signal, future_ret)
    aic = aic_strategy(df["ret_strategy_net"], n_params=n_params)
    # DM: error vs realized return; null model = always-long (ret_bh)
    err_strat = df["ret_strategy_net"] - df["ret_bh"]
    err_bh = pd.Series(0.0, index=df.index)
    dm_stat, dm_p = diebold_mariano(err_bh, err_strat, horizon=1)
    boot_sharpe = bootstrap_ci(df["ret_strategy_net"], statistic="sharpe")
    boot_ic_series = (ic_signal - ic_signal.mean()) * (
        future_ret - future_ret.mean()
    )
    boot_ic = bootstrap_ci(boot_ic_series.dropna(), statistic="mean")
    return {
        "sharpe_net": sharpe_net,
        "sharpe_bh": sharpe_bh,
        "sharpe_spread": sharpe_net - sharpe_bh,
        "ic": ic,
        "aic": aic,
        "dm_stat": dm_stat,
        "dm_pvalue": dm_p,
        "sharpe_boot_mean": boot_sharpe.mean,
        "sharpe_boot_lo": boot_sharpe.lower,
        "sharpe_boot_hi": boot_sharpe.upper,
        "ic_boot_lo": boot_ic.lower,
        "ic_boot_hi": boot_ic.upper,
    }
