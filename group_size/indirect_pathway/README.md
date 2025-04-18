# Indirect Pathway Simulation

This simulation explores the indirect causal pathway where race affects incarceration rate through economic position. In this model, group membership influences economic position, which in turn determines incarceration rate.

 ## Model Specification

The indirect pathway model uses a function where expected incarceration rates are determined by position in the stratification dimension, controlled by a shape parameter γ:

$$\text{IncarcerationRate}(maxRate, z, \gamma) = maxRate \cdot \text{PositionEffect}(z, \gamma)$$

Where:

$$\text{PositionEffect}(z, \gamma) = (1-z)^{\gamma}$$

- $z \in Z = \{z \in \mathbb{R} \mid 0 \leq z \leq 1\}$ represents position in the stratification dimension
- $\gamma \in \mathbb{R}^+$ controls the shape of the relationship between stratification position and incarceration rate

This function has the following properties:
- It equals 1 at the lowest position ($z = 0$) and approaches 0 at the highest position ($z = 1$)
- When $\gamma = 1$: Linear relationship (constant rate of decrease)
- When $0 < \gamma < 1$: Convex curve (steeper drops at higher positions)
- When $\gamma > 1$: Concave curve (steeper drops at lower positions)

## Simulation Approach

Let $p$ be proportion of the population represented by $G_{\text{disadv}}$; i.e. 
$$p = \frac{|G_{\text{disadv}}|}{|G|}$$

The simulation systematically varies $p$ and $\gamma$ to explore how group size and the shape of the economic position-incarceration relationship affect measured inequality.

1. Define the population proportion of the disadvantaged group: $p \in (0,1)$

2. Generate positions from distributions for each group:
   - For disadvantaged group: $z_i \sim F_{disadv}$ for $i \in \{1, 2, ..., n_{disadv}\}$
   - For advantaged group: $z_j \sim F_{adv}$ for $j \in \{1, 2, ..., n_{adv}\}$
   
   Where:
   - $F_{disadv}$ and $F_{adv}$ are probability distributions over $Z$
   - $n_{disadv} = p \cdot N$ and $n_{adv} = (1-p) \cdot N$ for total population size $N$
   - Distributions can be parameterized to control overlap, variance, and shape

3. Calculate individual expected incarceration rates:
   - For each individual $i$ with position $z_i$: $\text{Rate}_i = \text{IncarcerationRate}(maxRate, z_i, \gamma)$

4. Aggregate to calculate group-level rates:
   - For disadvantaged group: $\text{GroupRate}\_{disadv} = \frac{1}{n_{disadv}} \sum_{i=1}^{n_{disadv}} \text{Rate}_i$
   - For advantaged group: $\text{GroupRate}\_{adv} = \frac{1}{n_{adv}} \sum_{j=1}^{n_{adv}} \text{Rate}_j$

5. Calculate disparity measures:
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

The Normalized Disparity Index η here serves as an emergent metric rather than a direct decomposition - it helps us understand how the underlying mechanisms produce disparities that may or may not be comparable across different demographic contexts.