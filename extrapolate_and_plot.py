"""
We take the (A, n, Ea) we fitted from the harsh stress data, plug in
the real operating J and T, and predict the real-world lifetime. This
step is why accelerated testing is useful at all - you get an answer in
days that would otherwise take years to observe directly.

I also make two standard reliability-engineering plots:

1. Arrhenius plot: ln(MTTF) vs 1/T -> should be a straight line, slope
   related to Ea. This is the classic plot used to visually sanity check
   an activation energy extraction.

2. Failure time distribution: histogram of raw failure times at one
   condition, showing the lognormal spread.
"""

import numpy as np
import matplotlib.pyplot as plt

from stress_data import generate_stress_test_data, black_equation, K_BOLTZMANN
from black_eq_fit import compute_median_life_per_condition, fit_black_equation


def extrapolate_lifetime(A, n, Ea, J_use, T_use):
    #Plug fitted parameters into black's eq at real operating conditions to predict field lifetime.
    return black_equation(J_use, T_use, A=A, n=n, Ea=Ea)


def plot_arrhenius(conditions, median_lives, savepath="arrhenius_plot.png"):
    
    """Classic reliability plot: ln(MTTF) vs 1/T.
    A straight line here is visual sign of a clean Ea extraction"""
    
    J_vals = np.array([c[0] for c in conditions])
    T_vals = np.array([c[1] for c in conditions])

    plt.figure(figsize=(6, 5))
    for J in sorted(set(J_vals)):
        mask = J_vals == J
        inv_T = 1.0 / T_vals[mask]
        ln_life = np.log(median_lives[mask])
        # sort by 1/T so the line draws cleanly
        order = np.argsort(inv_T)
        plt.plot(inv_T[order], ln_life[order], "o-", label=f"J = {J:.0e} A/cm²")

    plt.xlabel("1 / T (1/K)")
    plt.ylabel("ln(Median Failure Time)")
    plt.title("Arrhenius Plot: Electromigration Failure Data")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(savepath, dpi=150)
    print(f"Saved {savepath}")


def plot_failure_distribution(data, J_target, T_target, savepath="failure_distribution.png"):
    
    """Show the raw (lognormal) spread of failure times at one stress
    condition - this is what you'd actually see in raw lab data, before
    it gets reduced down to a single median value."""
    times = [row["failure_time_hr"] for row in data
             if row["J"] == J_target and row["T"] == T_target]

    plt.figure(figsize=(6, 5))
    plt.hist(times, bins=8, color="steelblue", edgecolor="black", alpha=0.8)
    plt.axvline(np.median(times), color="red", linestyle="--",
                label=f"Median = {np.median(times):.0f} hr")
    plt.xlabel("Failure Time (hours)")
    plt.ylabel("Count")
    plt.title(f"Failure Time Distribution @ J={J_target:.0e} A/cm², T={T_target}K")
    plt.legend()
    plt.tight_layout()
    plt.savefig(savepath, dpi=150)
    print(f"Saved {savepath}")


if __name__ == "__main__":
    # 1: harsh accelerated stress conditions (lab) 
    J_conditions = [1e6, 2e6, 4e6]     # A/cm^2 - much higher than real use
    T_conditions = [400, 425, 450]      # Kelvin - much hotter than real use

    data = generate_stress_test_data(J_conditions, T_conditions)
    conditions, median_lives = compute_median_life_per_condition(data)

    A_fit, n_fit, Ea_fit = fit_black_equation(conditions, median_lives)
    print(f"Fitted parameters: A={A_fit:,.1f}, n={n_fit:.3f}, Ea={Ea_fit:.3f} eV\n")

    # 2: real chip operating conditions (much gentler)
    J_use = 5e4      # A/cm^2  - typical real interconnect current density
    T_use = 358       # Kelvin  - ~85C, typical chip junction temp

    predicted_life_hrs = extrapolate_lifetime(A_fit, n_fit, Ea_fit, J_use, T_use)
    predicted_life_years = predicted_life_hrs / (24 * 365)

    print(f"Predicted field lifetime at J={J_use:.0e} A/cm², T={T_use}K:")
    print(f"  {predicted_life_hrs:,.0f} hours  (~{predicted_life_years:,.1f} years)")

    #3: make the standard reliability plots 
    plot_arrhenius(conditions, median_lives)
    plot_failure_distribution(data, J_target=J_conditions[0], T_target=T_conditions[0])
