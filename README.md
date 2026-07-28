
# Electromigration Lifetime Predictor

A mini project simulating the standard workflow used in silicon reliability
characterization:stress test -- extract failure model-- extrapolate to real operating lifetime.

I built this without lab access, so the "stress test data" is simulated —
but the statistics (lognormal failure times), the physics (Black's
Equation), and the fitting method (log-linear regression / Arrhenius
analysis) are all the real methodology used in industry EM characterization.

## Background

Electromigration (EM) is the gradual movement of metal atoms in an
interconnect caused by momentum transfer from flowing electrons ("electron
wind"). Over time, this creates voids or hillocks in the
wire. It's one of the dominant long-term reliability failure mechanisms in
chip interconnects.

Since chips need to last years, one can't just run it at real operating
conditions and wait to see when it fails. Instead, reliability engineers
accelerate failure by stressing test structures at much higher current
density and temperature than real use conditions, and then use a model 
Black's Equation to extrapolate back down to realistic lifetime at
normal operating conditions:

MTTF = A * J^(-n) * exp(Ea / kT)


- J = current density
- T = temperature (K)
- Ea = activation energy of the diffusion process
- n = current density exponent (~2 for EM)
- A = geometry/material-dependent prefactor

## What this project does

1. **stress_data.py** - simulates accelerated stress test data across
   multiple (J, T) conditions with realistic noise added.

2. **black_equation_fit.py** - takes the noisy failure data and fits it
   back to Black's Equation using log-linear regression, recovering A, n, and Ea from data alone.

3. **extrapolate_and_plot.py** - uses the fitted parameters to predict
   lifetime at realistic chip operating conditions, and generates two
   standard reliability plots:
   - **Arrhenius plot** (ln(MTTF) vs 1/T) - a straight line is the visual
     check that the activation energy extraction is clean
   - **Failure distribution histogram** - shows the raw lognormal spread at
     one stress condition, before it's reduced to a single median value

## Sample result

Fitting recovered the "true" simulated parameters closely, even with
lognormal noise added:

| Parameter | True value | Fitted value |
|---|---|---|
| A  | 100,000 | ~136,000 |
| n  | 2.00 | ~2.04 |
| Ea | 0.80 eV | ~0.81 eV |

## An honest caveat (worth knowing)

When I extrapolate down to real chip operating conditions (low J, ~85°C),
the predicted lifetime comes out to an enormous, unrealistic number
(centuries). This isn't a bug; it's a well known pitfall in real EM
extrapolation:

- Black's Equation is fit from data taken far outside the real
  operating regime, so extrapolating that far introduces large uncertainty.
- Real characterization work reports lifetime with confidence intervals,
  not a single number, and cross-checks it against multiple stress
  conditions and known material data - not just one fitted curve.
- Also, in industry, EM lifetime specs are usually stated at a target
  failure percentile (e.g., 0.1% cumulative failures by X years), not
  the median - because a chip failing is defined by the first wire
  failing, not the typical one.

I'm noting this explicitly because recognizing where a model's assumptions
break down is as important as building the model in the first place.

## Why I built this

I have hands-on experience automating impedance measurements (Python +
PyVISA, function generator + oscilloscope) and wanted to extend that into
characterization domain relevant to silicon characterization
roles. Coming from a
materials science background, electromigration is a natural bridge: it's
fundamentally atomic diffusion along grain boundaries and interfaces under
electrical/thermal stress, and grain structure and texture directly affect
activation energy and lifetime - the same underlying physics as diffusion
and reaction-rate problems in materials science, just applied to
interconnect reliability.

## Requirements

```
numpy
scipy
matplotlib
```

## Run it

```bash
python3 stress_data.py        # generate & preview simulated stress data
python3 black_eq_fit.py     # fit Black's Equation, compare to true values
python3 extrapolate_and_plot.py   # extrapolate lifetime & generate plots
```
## After you run, these are plots you will get 
## Failure distribution:
<img width="500" height="400" alt="failure_distribution" src="https://github.com/user-attachments/assets/d51e2b58-bb73-4504-a8c3-1bd0b913402d" />

## Arrhenius plot:
<img width="500" height="400" alt="arrhenius_plot" src="https://github.com/user-attachments/assets/401f379a-b230-4b87-854e-c77ccee3ff3c" />
