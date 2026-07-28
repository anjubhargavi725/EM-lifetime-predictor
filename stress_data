"""
Without lab access, this script generates data that behaves the way real EM failure data behaves:
  - failure times follow a LOGNORMAL distribution (this is standard)
  - the MEDIAN failure time follows Black's Equation
  - I added random noise so it looks like real messy lab data, not a perfect curve

Later scripts will take this data and try to recover the true A, n, Ea
values by fitting Black's Equation to it.
"""

import numpy as np

# Boltzmann constant in eV/K
K_BOLTZMANN = 8.617e-5

# ---- "TRUE" underlying material parameters ----
# In real life you don't know these - you're trying to discover them from
# the data. I'm setting them here just so I can generate realistic fake
# data and later check if my fitting code recovers them correctly.
TRUE_A = 1.0e5      # prefactor (arbitrary units, depends on wire geometry)
TRUE_N = 2.0         # current density exponent (~2 is typical for EM)
TRUE_EA = 0.8        # activation energy in eV (typical for Cu interconnects)


def black_equation(J, T, A=TRUE_A, n=TRUE_N, Ea=TRUE_EA):
    """
    This is Black's Equation itself.

    J  = current density (A/cm^2)
    T  = temperature (Kelvin)

    Returns the MEDIAN time to failure (MTTF) in hours.
    """
    return A * (J ** -n) * np.exp(Ea / (K_BOLTZMANN * T))


def generate_stress_test_data(J_list, T_list, samples_per_condition=8, seed=42):
    """
    For each (J, T) stress condition, simulate a batch of wires failing.

    Real failure data is lognormal - meaning most wires fail near the
    median time, but a few fail early and a few survive much longer.
    That's why I sample from a lognormal distribution around the Black's
    Equation prediction, instead of just returning one number.
    """
    rng = np.random.default_rng(seed)
    records = []

    for J in J_list:
        for T in T_list:
            median_life = black_equation(J, T)

            # sigma = spread of the lognormal distribution.
            # 0.3-0.5 is a realistic value for EM failure data.
            sigma = 0.35
            failure_times = rng.lognormal(mean=np.log(median_life), sigma=sigma,
                                           size=samples_per_condition)

            for t in failure_times:
                records.append({"J": J, "T": T, "failure_time_hr": t})

    return records


if __name__ == "__main__":
    # Example stress plan: 3 current densities x 3 temperatures
    # These are much harsher than real chip operating conditions -
    # that's the whole point of "accelerated" testing.
    J_conditions = [1e6, 2e6, 4e6]      # A/cm^2
    T_conditions = [400, 425, 450]       # Kelvin (~127C to 177C)

    data = generate_stress_test_data(J_conditions, T_conditions)

    print(f"Generated {len(data)} simulated failure events")
    print("First few rows:")
    for row in data[:5]:
        print(row)
