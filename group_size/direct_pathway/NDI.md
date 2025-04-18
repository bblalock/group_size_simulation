# The Normalized Disparity Index (η): A New Metric for Measuring Group Disparities

## Definition

The **Normalized Disparity Index** (η, eta) is defined as:

$$\eta = \frac{d - 1}{d + \frac{1 - p}{p}}$$

Where:
* $d$: Disparity ratio — the ratio of rates between two groups (e.g., $\frac{\text{Rate}_\text{Black}}{\text{Rate}_\text{White}}$)
* $p$: Proportion of the disadvantaged group in the population

## Interpretation

The Normalized Disparity Index can be understood as a fraction of two meaningful components:

$$\eta = \frac{\text{Excess Disparity}}{\text{Disparity + Group Size Imbalance}} = \frac{d - 1}{d + \frac{1 - p}{p}}$$

* **Excess Disparity** $(d - 1)$: Measures how much the disparity ratio exceeds equality (where equality would be $d = 1$)
* **Disparity + Group Size Imbalance** $\left(d + \frac{1 - p}{p}\right)$: Accounts for both the magnitude of disparity and the population imbalance between groups

Thus, **η measures the severity of disparity adjusted for population balance**:
* A value close to 1 implies high disparity with a meaningful population impact
* A lower η suggests either modest disparity or limited population exposure
* η = 0 indicates no disparity (perfect parity between groups)


## Derivation from Outcome Model

The Normalized Disparity Index can be derived from a model of group outcomes:

$$\text{Outcome}_g = \text{avgRate} \cdot \text{GroupEffect}(g, \eta, p)$$

Where:

$$\text{GroupEffect}(g) = 
\begin{cases} 
1 + \eta \cdot \frac{1 - p}{p}, & \text{if }g\text{ is disadvantaged} \\
1 - \eta, & \text{if }g\text{ is advantaged} 
\end{cases}$$

This model:
* Reconstructs group-level outcome rates using η
* Ensures that **both disparity and population share are incorporated into interpretation**
* Maintains the overall average rate across the population

## η as a Discount/Uplift Factor

The Normalized Disparity Index (η) functions as:
* A **discount factor** on the advantaged group's outcome rate
* A corresponding **uplift factor** on the disadvantaged group's rate

This interpretation makes η particularly intuitive:

* **Advantaged group** receives a discount: $\text{GroupEffect} = 1 - \eta$
  
  Their outcome is reduced by a factor of η relative to the average.

* **Disadvantaged group** receives an uplift: $\text{GroupEffect} = 1 + \eta \cdot \frac{1 - p}{p}$
  
  Their outcome is increased proportionally to both η and the population size imbalance.

## Properties of the Model

This structure ensures that the **weighted average of group outcomes equals the overall outcome rate**:

$$\text{avgRate} = p \cdot \text{Outcome}_\text{disadv} + (1 - p) \cdot \text{Outcome}_\text{adv}$$

The Normalized Disparity Index η thus represents:
1. The severity of disparity between groups
2. The share of the average rate that's reallocated between groups
3. A measure that inherently accounts for both magnitude of disparity and population composition

## Applications

The Normalized Disparity Index is useful for:
* Comparing disparities across different contexts, time periods, or populations
* Prioritizing interventions based on both disparity magnitude and population impact
* Tracking progress in reducing disparities over time
* Standardizing reporting of disparities in a way that accounts for population composition

## Example Calculation

Consider a scenario where:
* The disparity ratio $d = 2.5$ (disadvantaged group has 2.5 times the rate of the advantaged group)
* The disadvantaged group comprises 30% of the population ($p = 0.3$)

The Normalized Disparity Index would be:

$$\eta = \frac{2.5 - 1}{2.5 + \frac{1 - 0.3}{0.3}} = \frac{1.5}{2.5 + 2.33} = \frac{1.5}{4.83} \approx 0.31$$

This indicates a moderate level of disparity when accounting for both the ratio difference and the population composition.