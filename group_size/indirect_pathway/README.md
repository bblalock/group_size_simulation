# Indirect Pathway Simulation

This simulation explores the indirect causal pathway where race affects incarceration rate through economic position. In this model, group membership influences economic position, which in turn determines incarceration rate.

## Model Specification

The indirect pathway model uses a function where expected incarceration rates are determined by position in the stratification dimension, controlled by a shape parameter γ. We implement two versions of this model:

### Non-Normalized Model
$$\text{IncarcerationRate}(maxRate, z, \gamma) = maxRate \cdot \text{PositionEffect}(z, \gamma)$$

### Normalized Model
$$\text{IncarcerationRate}(targetAvgRate, z, \gamma) = targetAvgRate \cdot \frac{\text{PositionEffect}(z, \gamma)}{\mathbb{E}[\text{PositionEffect}(Z, \gamma)]}$$

Where in both cases:

$$\text{PositionEffect}(z, \gamma) = (1-z)^{\gamma}$$

- $z \in Z = \{z \in \mathbb{R} \mid 0 \leq z \leq 1\}$ represents position in the stratification dimension
- $\gamma \in \mathbb{R}^+$ controls the shape of the relationship between stratification position and incarceration rate
- $\mathbb{E}[\text{PositionEffect}(Z, \gamma)]$ is the expected value of the position effect across the entire population

The normalization ensures that the population-average incarceration rate remains constant at the target rate regardless of changes in γ or group distributions, allowing for more controlled comparisons.

The position effect function has the following properties:
- It equals 1 at the lowest position ($z = 0$) and approaches 0 at the highest position ($z = 1$)
- When $\gamma = 1$: Linear relationship (constant rate of decrease)
- When $0 < \gamma < 1$: Convex curve (steeper drops at higher positions)
- When $\gamma > 1$: Concave curve (steeper drops at lower positions)

## Simulation Approach

Let $p$ be proportion of the population represented by $G_{\text{disadv}}$; i.e. 
$$p = \frac{|G_{\text{disadv}}|}{|G|}$$

The simulation systematically varies several key parameters to explore how group size and the shape of the economic position-incarceration relationship affect measured inequality.

1. Group proportion: $p \in (0.01, 0.99)$ with increments of 0.05
   - This represents the proportion of the disadvantaged group in the population

2. Position distribution parameters:
   - Mean position of disadvantaged group: $\mu_{\text{disadv}} = 0.2$
   - Position gap between groups: $z_{\text{position\_gap}} \in \{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6\}$
     - The mean position of the advantaged group is calculated as $\mu_{\text{adv}} = \mu_{\text{disadv}} + z_{\text{position\_gap}}$
   - Concentration parameters: $c_{\text{disadv}} = c_{\text{adv}} = 20$
     - These control the spread of the beta distributions for each group
     - Higher values create more peaked, narrower distributions

3. Incarceration risk parameters:
   - Shape parameter: $\gamma \in [0, 5]$ with 20 evenly spaced values
     - Controls the relationship between stratification position and incarceration risk
   - Target average incarceration rate: $\text{targetAvgRate} = 500$ (per 100,000)
     - Used in the normalized model to maintain a constant population-average rate

4. Simulation size:
   - Sample size: $N = 10,000$ individuals per simulation run

For each combination of these parameters, we:

1. Generate positions from beta distributions for each group:
   - For disadvantaged group: $z_i \sim \text{Beta}(\alpha_{disadv}, \beta_{disadv})$ for $i \in \{1, 2, ..., n_{disadv}\}$
   - For advantaged group: $z_j \sim \text{Beta}(\alpha_{adv}, \beta_{adv})$ for $j \in \{1, 2, ..., n_{adv}\}$
   
   Where the beta distribution parameters are derived using the mean-concentration approach:
      - $\alpha_{group} = \mu_{group} \cdot c_{group}$
      - $\beta_{group} = (1 - \mu_{group}) \cdot c_{group}$
   
   This parameterization follows from the standard properties of the beta distribution:
      - The mean of a beta distribution is $\mathbb{E}[X] = \frac{\alpha}{\alpha + \beta}$
      - By defining the concentration parameter $c = \alpha + \beta$, we get $\mu = \frac{\alpha}{c}$
      - Solving for $\alpha$ gives $\alpha = \mu \cdot c$
      - Similarly, $\beta = (1-\mu) \cdot c$
   
   The variance of the resulting distribution is $\text{Var}[X] = \frac{\mu(1-\mu)}{c+1}$, showing that:
   - Higher concentration values create more peaked, narrower distributions
   - Lower concentration values create more spread-out distributions
   - For a fixed concentration, the variance is maximized when $\mu = 0.5$

2. Calculate individual expected incarceration rates using the normalized model:
   - Calculate the average position effect across the entire population: $\mathbb{E}[\text{PositionEffect}(Z, \gamma)]$
   - Compute the normalization factor: $\text{normFactor} = \frac{1}{\mathbb{E}[\text{PositionEffect}(Z, \gamma)]}$
   - For each individual $i$ with position $z_i$: $\text{Rate}_i = targetAvgRate \cdot (1-z_i)^{\gamma} \cdot \text{normFactor}$

3. Aggregate to calculate group-level rates:
   - For disadvantaged group: $\text{GroupRate}\_{disadv} = \frac{1}{n_{disadv}} \sum_{i=1}^{n_{disadv}} \text{Rate}_i$
   - For advantaged group: $\text{GroupRate}\_{adv} = \frac{1}{n_{adv}} \sum_{j=1}^{n_{adv}} \text{Rate}_j$

4. Calculate disparity measures:
   - Basic measures:
     - DisparityRatio = $d = \frac{\text{GroupRate}_{disadv}}{\text{GroupRate}_{adv}}$
     - DisparityDifference = $\text{GroupRate}_{disadv} - \text{GroupRate}_{adv}$
   - Normalized Disparity Index: $\eta = \frac{d - 1}{d + \frac{1 - p}{p}}$ Where $d$ is the disparity ratio calculated above

6. Analyze how these measures vary with:
   - Group size proportions ($p$)
   - Stratification-incarceration relationship shape ($\gamma$)
   - Economic distribution parameters (means, variances, overlap)
   - Focus particularly on how η behaves compared to raw disparity measures

## Expected Insights

This simulation will demonstrate:

1. How the shape of the stratification-incarceration relationship affects the sensitivity of inequality measures to group size
2. Why non-linear relationships (especially concave, γ > 1) make cross-national comparisons problematic
3. The mathematical relationship between group size, position distributions, and resulting inequality metrics
4. How the Normalized Disparity Index (η) may provide a more comparable measure across different demographic contexts
5. The impact of normalizing the population-average incarceration rate versus using a fixed maximum rate

## Relationship to Direct Pathway Analysis

While the direct pathway model performs a mathematical decomposition of how group size affects the relationship between population-average incarceration rates and group-specific rates, this indirect pathway model takes a fundamentally different approach through simulation.

In this model, disparities emerge organically from three interacting components:
1. The shape parameter γ that determines how position in the stratification dimension affects incarceration risk
2. The distributions of advantaged and disadvantaged groups in the stratification space
3. The relative size of the groups (p)

Rather than directly controlling the disparity ratio d, we observe how it emerges from these underlying mechanisms. This allows us to explore questions like:
- How does the shape of the stratification-incarceration relationship (γ) affect resulting disparities?
- How do different distributions of groups in stratification space translate into incarceration disparities?
- How does group size p interact with these mechanisms to produce observed disparities?
- How does normalizing to maintain a constant population-average rate affect the relationship between group size and disparity measures?

The Normalized Disparity Index η here serves as an emergent metric rather than a direct decomposition - it helps us understand how the underlying mechanisms produce disparities that may or may not be comparable across different demographic contexts.