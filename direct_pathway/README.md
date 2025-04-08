# Direct Pathway Simulation

This simulation explores two different models of the direct causal pathway where race affects incarceration rate, independent of economic position. We implement and compare two alternative formulations to understand how group size affects measured inequality.

## Model Specifications

The direct pathway model uses a simplified approach where incarceration rates are determined solely by group membership. In each model the level of disparity is controlled by a parameter. 

### Model 1: Finite Punishment Allocation Model (or Constant Population Average Approach)

The Finite Punishment Allocation Model conceptualizes a criminal justice system with limited capacity, where discrimination doesn't create additional punishment but rather redistributes it unequally between groups.

$$\text{IncarcerationRate}(avgRate, g, \theta, \pi) = avgRate \cdot \text{GroupEffect}(g, \theta, \pi)$$

Where:

$$\text{GroupEffect}(g, \theta, \pi) = 
\begin{cases} 
\left(1 + \theta \cdot \frac{1 - \pi}{\pi}\right) & \text{if } g \in G_{\text{disadv}} \\
\left(1 - \theta\right) & \text{if } g \in G_{\text{adv}}
\end{cases}$$

Where:
- $g \in G$ represents an individual's group membership
- $\theta \in [0,1]$ controls the disparity between groups
- $\pi$ is the proportion of the population in the disadvantaged group

This function has the following properties:
- When $\theta = 0$: Both groups have the same effect (1), equal to the population average
- When $\theta = 1$: The advantaged group has an effect of 0, while the disadvantaged group has an effect of $1 + \frac{1-\pi}{\pi} = \frac{1}{\pi}$
- For any value of $\theta$, the population-weighted average effect remains 1:
$$\pi \cdot \left(1 + \theta \cdot \frac{1-\pi}{\pi}\right) + (1-\pi) \cdot (1-\theta) = 1$$

This ensures that the population average remains constant at avgRate regardless of group size or discrimination level.

### Model 2: Multiplicative Disparity Model (or Constant Disparity Ratio Approach)

The Multiplicative Disparity Model captures discrimination as a direct risk multiplier, where the disadvantaged group faces a consistently higher rate of punishment compared to the advantaged group. This approach mirrors how disparities are typically measured and discussed in policy contexts—as relative risks, treating discrimination as a factor that amplifies punishment rather than redistributes it (i.e. the population weighted average will increase with D).

$$\text{IncarcerationRate}(baseRate, g, D) = 
\begin{cases} 
baseRate & \text{if } g \in G_{\text{adv}} \\
D \cdot baseRate & \text{if } g \in G_{\text{disadv}} 
\end{cases}$$

Where:
- $g \in G$ represents an individual's group membership
- $D \geq 1$ is the direct disparity ratio between groups
- $baseRate$ is the incarceration rate of the advantaged group

This function has the following properties:
- When $D = 1$: Both groups have the same rate, equal to $baseRate$ (no discrimination)
- When $D > 1$: The disadvantaged group's rate is exactly $D$ times that of the advantaged group
- The population average incarceration rate varies with group size:
$$\text{PopulationAverage} = baseRate \cdot (1 + \pi \cdot (D-1))$$

This model directly encodes the disparity ratio, making it constant regardless of group size, while allowing the total incarceration rate to increase with both the proportion of the disadvantaged group ($\pi$) and the magnitude of discrimination ($D$).

## Simulation Approach

The simulations systematically varies multiple parameters to understand how group size affects measured inequality:

### For the Finite Punishment Allocation Model

1. **Parameter Selection**:
   * Choose population average incarceration rate: avgRate ∈ {100, 200, 500, 1000} per 100,000
   * Set population proportions to examine: π ∈ {0.05, 0.1, 0.25, 0.5, 0.75, 0.9}
   * Define discrimination parameters: θ ∈ {0, 0.25, 0.5, 0.75, 0.9}

2. **Factorial Design**:
   * Run simulations for all combinations of (avgRate, π, θ) 
   * This produces a total of 4 × 6 × 5 = 120 simulation scenarios

3. **For Each Scenario**:
   * Calculate incarceration rates:
      * GroupRate_disadv = avgRate · (1 + θ · (1-π)/π)
      * GroupRate_adv = avgRate · (1-θ)
   * Calculate disparity measures:
      * DisparityRatio = GroupRate_disadv / GroupRate_adv
      * DisparityDifference = GroupRate_disadv - GroupRate_adv
      * OddsRatio and other inequality metrics (optional)

4. **Regression Analysis**:
   * Primary regression: DisparityRatio ~ π + θ + interactions
   * Quantify the proportion of variance in disparity measures explained by group size (π)
        * Calculate $\Delta R^2 = R^2_{\text{full}} - R^2_{\text{reduced}}$ between models with and without $\pi$ to quantify variance uniquely explained by group size
   * Test for interaction effects to understand when group size has the largest impact

### For the Multiplicative Disparity Model

1. **Parameter Selection**:
   * Choose baseline incarceration rates: baseRate ∈ {100, 200, 500, 1000} per 100,000
   * Set population proportions to examine: π ∈ {0.05, 0.1, 0.25, 0.5, 0.75, 0.9}
   * Define disparity ratios: D ∈ {1, 2, 5, 10, 20}

2. **Factorial Design**:
   * Run simulations for all combinations of (baseRate, π, D) 
   * This produces a total of 4 × 6 × 5 = 120 simulation scenarios

3. **For Each Scenario**:
   * Calculate incarceration rates:
      * GroupRate_disadv = D × baseRate
      * GroupRate_adv = baseRate
   * Calculate system-level metrics:
      * DisparityRatio = D (constant by definition)
      * DisparityDifference = baseRate × (D-1) (independent of group size)
      * PopulationAverage = baseRate × (1 + π × (D-1))
      * Total incarceration burden = PopulationAverage × TotalPopulation

4. **Regression Analysis**:
   * Primary regression: PopulationAverage ~ π + D + baseRate + interactions
   * Quantify the proportion of variance in population average explained by group size (π)
        * Calculate $\Delta R^2 = R^2_{\text{full}} - R^2_{\text{reduced}}$ between models with and without $\pi$ to quantify variance uniquely explained by group size
   * Analyze interaction effects between D and π to understand when group size has the largest impact
   * Compare the explanatory power of group size across different disparity levels

This model demonstrates that even when countries have identical disparity ratios (D), differences in demographic composition (π) lead to different system-level incarceration rates

## Expected Insights

1. How group size (π) affects measured inequality even when the underlying disparity parameter remains constant
2. The mathematical relationship between group size, disparity parameter, and resulting inequality metrics
3. The trade-offs between maintaining a constant population average (Model 1) versus a constant disparity ratio (Model 2)
