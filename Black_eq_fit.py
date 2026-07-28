"""
Now that we have (noisy, realistic) failure data, the job of a
characterization engineer is to work BACKWARDS: figure out A, n, and Ea
from the data, so we can predict lifetime at real operating conditions.

The trick: Black's Equation is not linear, but if you
take the log of both sides, it becomes linear:

    ln(MTTF) = ln(A) - n*ln(J) + (Ea/k) * (1/T)

That means ln(MTTF) is just a linear combination of ln(J) and (1/T).
So instead of a complicated nonlinear fit, we can use simple multi-variable
linear regression (numpy's least squares) to pull out n and Ea directly
from the slopes.

This mirrors what's actually done in reliability labs when they build an
"Arrhenius plot" or a "Black's plot" from stress test data.
"""

import numpy as np
from stress_data_sim import generate_stress_test_data, K_BOLTZMANN, TRUE_A, TRUE_N, TRUE_EA


def compute_median_life_per_condition(data):
    """
    Group the raw failure times by (J, T) condition and take the median.
    Black's Equation predicts the MEDIAN life, so this is the right
    statistic to compare against - not the mean, since the distribution
    is lognormal (skewed).
    """
    from collections import defaultdict

    grouped = defaultdict(list)
    for row in data:
        grouped[(row["J"], row["T"])].append(row["failure_time_hr"])

    conditions = []
    median_lives = []
    for (J, T), times in grouped.items():
        conditions.append((J, T))
        median_lives.append(np.median(times))

    return conditions, np.array(median_lives)


def fit_black_equation(conditions, median_lives):
    
    #Linear regression on the log-transformed Black's Equation.
    #We solve for [ln(A), -n, Ea/k] using least squares.
    
    J_vals = np.array([c[0] for c in conditions])
    T_vals = np.array([c[1] for c in conditions])

    y = np.log(median_lives)
    x1 = np.log(J_vals)
    x2 = 1.0 / T_vals

    # Build the design matrix: [1, ln(J), 1/T] for each data point
    # (the "1" column is for the ln(A) intercept term)
    X = np.column_stack([np.ones_like(x1), x1, x2])

    # Least squares solve: X @ coeffs = y
    coeffs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)

    ln_A, neg_n, Ea_over_k = coeffs

    A_fit = np.exp(ln_A)
    n_fit = -neg_n
    Ea_fit = Ea_over_k * K_BOLTZMANN

    return A_fit, n_fit, Ea_fit


if __name__ == "__main__":
    # Same stress plan as before
    J_conditions = [1e6, 2e6, 4e6]
    T_conditions = [400, 425, 450]

    data = generate_stress_test_data(J_conditions, T_conditions)
    conditions, median_lives = compute_median_life_per_condition(data)

    A_fit, n_fit, Ea_fit = fit_black_equation(conditions, median_lives)

    print("---- Fit results vs true values ----")
    print(f"A  : fitted = {A_fit:,.1f}   true = {TRUE_A:,.1f}")
    print(f"n  : fitted = {n_fit:.3f}    true = {TRUE_N:.3f}")
    print(f"Ea : fitted = {Ea_fit:.3f} eV   true = {TRUE_EA:.3f} eV")
