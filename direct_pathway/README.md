# Direct Pathway Simulation

This simulation explores different models of the direct causal pathway where race affects incarceration rate, independent of economic position. We implement and compare three alternative formulations to understand how group size affects measured inequality.

## Model Specifications

The direct pathway models use simplified approaches where incarceration rates are determined solely by group membership. In each model the level of disparity is controlled by a parameter.

### Standard Model
The Standard Model conceptualizes discrimination in punishment as a function of group membership while maintaining a constant population-wide incarceration rate. It introduces a parameter d that directly represents the disparity ratio between disadvantaged and advantaged groups (i.e., the disadvantaged group's incarceration rate is exactly d times that of the advantaged group). This approach ensures that the total "amount" of punishment in the system remains fixed, with changes in the disparity ratio d only affecting how that punishment is allocated across groups, not the overall incarceration level.

$$\text{IncarcerationRate}(avgRate, g, d, p) = \frac{avgRate}{\text{GroupEffect}(g, d, p)}$$

Where:

$$\text{GroupEffect}(g, d, p) = 
\begin{cases} 
d \cdot p + (1-p) & \text{if } g \in G_{\text{adv}} \\
\frac{1}{d \cdot (d \cdot p + (1-p))} & \text{if } g \in G_{\text{disadv}}
\end{cases}$$

Which simplifies to:

$$\text{Rate}\_{\text{adv}} = \frac{avgRate}{d \cdot p + (1-p)}$$

$$\text{Rate}\_{\text{disadv}} = d \cdot \text{Rate}\_{\text{adv}}$$

Where:
- $g \in G$ represents an individual's group membership
- $d \geq 1$ is the disparity ratio between groups
- $p$ is the proportion of the population in the disadvantaged group
- $avgRate$ is the population average incarceration rate

This model maintains a constant population average incarceration rate for any value of $d$, as demonstrated by:

$$p \cdot \text{Rate}\_{\text{disadv}} + (1-p) \cdot \text{Rate}\_{\text{adv}} = avgRate$$

When we substitute the rate equations:

$$p \cdot d \cdot \frac{avgRate}{d \cdot p + (1-p)} + (1-p) \cdot \frac{avgRate}{d \cdot p + (1-p)} = avgRate$$

Factoring out common terms:

$$\frac{avgRate}{d \cdot p + (1-p)} \cdot (p \cdot d + (1-p)) = avgRate$$

This simplifies to:

$$avgRate \cdot \frac{d \cdot p + (1-p)}{d \cdot p + (1-p)}$$

Therefore:

$$avgRate = avgRate$$

Which confirms that the population-weighted average incarceration rate equals $avgRate$ for any value of $d$.

### Alternative Model 1: Bias-Controlled Redistribution Model

Similar to the Standard Model, this conceptualizes a criminal justice system with a fixed total amount of punishment, where discrimination redistributes punishment rather than creating additional punishment overall. However, instead of directly setting the disparity ratio between groups, this model introduces a bias parameter b that controls the degree to which punishment is shifted from the advantaged to the disadvantaged group. When b=0, punishment is equally distributed; as b approaches 1, more punishment is transferred to the disadvantaged group, reaching complete inequality when b=1 (where the advantaged group receives no punishment). This approach provides an alternative way to model how discrimination manifests while still maintaining a constant population-wide incarceration rate.

$$\text{IncarcerationRate}(avgRate, g, b, p) = avgRate \cdot \text{GroupEffect}(g, b, p)$$

Where:

$$\text{GroupEffect}(g, b, p) = 
\begin{cases} 
1 + b \cdot \frac{1 - p}{p} & \text{if } g \in G_{\text{disadv}} \\
1 - b & \text{if } g \in G_{\text{adv}}
\end{cases}$$

Where:
- $g \in G$ represents an individual's group membership
- $b \in [0,1]$ controls how punishment is redistibuted between groups
- $p$ is the proportion of the population in the disadvantaged group

This function has the following properties:
- When $b = 0$: Both groups have the same effect (1), equal to the population average
- When $b = 1$: The advantaged group has an effect of 0, while the disadvantaged group has an effect of $1 + \frac{1-p}{p} = \frac{1}{p}$
- For any value of $b$, the population-weighted average effect remains 1:

$$p \cdot \left(1 + b \cdot \frac{1-p}{p}\right) + (1-p) \cdot (1-b) = 1$$

This ensures that the population average remains constant at avgRate regardless of group size or discrimination level.

### Alternative Model 2: Non-Redistributive Disparity Model

Unlike the previous models which maintain a fixed total amount of punishment that gets redistributed, this model conceptualizes discrimination as adding punishment to the system. The disparity parameter d directly sets the ratio between group incarceration rates, but the advantaged group's baseline rate remains constant regardless of the level of discrimination. This means that as disparity increases, the total amount of punishment in the system grows rather than being redistributed. 

$$\text{IncarcerationRate}(baseRate, g, d) = 
\begin{cases} 
baseRate & \text{if } g \in G_{\text{adv}} \\
d \cdot baseRate & \text{if } g \in G_{\text{disadv}} 
\end{cases}$$

Where:
- $g \in G$ represents an individual's group membership
- $d \geq 1$ is the direct disparity ratio between groups
- $baseRate$ is the incarceration rate of the advantaged group

This function has the following properties:
- When $d = 1$: Both groups have the same rate, equal to $baseRate$ (no discrimination)
- When $d > 1$: The disadvantaged group's rate is exactly $d$ times that of the advantaged group
- The population average incarceration rate varies with group size:

$$\text{PopulationAverage} = baseRate \cdot (1 + p \cdot (d-1))$$

## Simulation Approach

The simulations systematically vary multiple parameters to understand how group size affects measured inequality across all three models:

1. **Parameter Selection**:
   * Set population proportions: p ∈ [0, 1], number of values = $n_p$
   * Choose average/base incarceration rates: range from 100 to 1000 per 100,000, number of values = $n_r$
   * Define disparity parameters for Standard Model and Non-Redistributive Disparity Model: d > 1, number of values = $n_d$
   * Define bias parameters for Bias-Controlled Redistribution Model: b ∈ [0, 1], number of values = $n_b$

2. **Factorial Design**:
   * Create a factorial design by systematically combining all selected parameter values for each model
        * This yields $n_p \times n_r \times n_d$ total simulation runs for the Standard and Non-Redistributive models
        * And $n_p \times n_r \times n_b$ total simulation runs for the Bias-Controlled Redistribution model
   * This systematic approach ensures we capture the interactions between parameters across the parameter space

3. **For Each Scenario**:
   * Calculate group-specific incarceration rates according to each model
   * Calculate disparity measures:
      * DisparityRatio = Rate_disadv / Rate_adv
      * DisparityDifference = Rate_disadv - Rate_adv
      * Population average incarceration rate
      * Other inequality metrics as needed

4. **Regression Analysis**:
   * Analyze how group size ($p$) affects disparity measures under different model assumptions by using multiple linear regression to __decompose__ variation across simulation runs
   * Quantify the proportion of variance in disparity measures explained by group size ($p$)
        * Calculate $\Delta R^2 = R^2_{\text{full}} - R^2_{\text{reduced}}$ between regression models with and without $p$ as a regressor to quantify variance uniquely explained by group size
   * Test for interaction effects to understand when group size has the largest impact
   * Compare results across all three models to identify robust patterns

## Expected Insights

1. How group size ($p$) affects measured inequality even when the underlying disparity parameter remains constant
2. The mathematical relationship between group size, disparity parameter, and resulting inequality metrics
3. The trade-offs between different conceptual models of how race affects incarceration