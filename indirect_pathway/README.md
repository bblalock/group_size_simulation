# Indirect Pathway Simulation

This simulation explores the indirect causal pathway where race affects incarceration risk through economic position. In this model, group membership influences economic position, which in turn determines incarceration risk.

## Model Specification

The indirect pathway model uses a function where incarceration rates are determined by economic position, controlled by a shape parameter γ:

$$\text{IncarcerationRate}(maxRate, p, \gamma) = maxRate \cdot \text{PositionEffect}(p, \gamma)$$

Where:

$$\text{PositionEffect}(p, \gamma) = \left(1-\frac{p}{100}\right)^{\gamma}$$


- $p \in P = \{p \in \mathbb{R} \mid 0 \leq p \leq 100\}$ represents the economic percentile
- $\gamma \in \mathbb{R}^+$ controls the shape of the relationship between economic position and incarceration risk

This function has the following properties:
- It equals 1 at the lowest economic position ($p = 0$) and approaches 0 at the highest position ($p = 100$)
- When $\gamma = 1$: Linear relationship (constant rate of decrease)
- When $0 < \gamma < 1$: Convex curve (steeper drops at higher economic positions)
- When $\gamma > 1$: Concave curve (steeper drops at lower economic positions)


## Simulation Approach

Let $\pi$ be proportion of the population represented by $G_{\text{disadv}}$; i.e. 
$$\pi = \frac{|G_{\text{disadv}}|}{|G|}$$

The simulation systematically varies $\pi$ and $\gamma$ to explore how group size and the shape of the economic position-incarceration relationship affect measured inequality.

1. Define the population proportion of the disadvantaged group: $\pi \in (0,1)$

2. Generate economic positions from distributions for each group:
   - For disadvantaged group: $p_i \sim F_{disadv}$ for $i \in \{1, 2, ..., n_{disadv}\}$
   - For advantaged group: $p_j \sim F_{adv}$ for $j \in \{1, 2, ..., n_{adv}\}$
   
   Where:
   - $F_{disadv}$ and $F_{adv}$ are probability distributions over $P$
   - $n_{disadv} = \pi \cdot N$ and $n_{adv} = (1-\pi) \cdot N$ for total population size $N$
   - Distributions can be parameterized to control overlap, variance, and shape

3. Calculate individual expected incarceration rates:
   - For each individual $i$ with economic position $p_i$: $\text{Rate}_i = \text{IncarcerationRate}(maxRate, p_i, \gamma)$

4. Aggregate to calculate group-level rates:
   - $\text{GroupRate}_{disadv} = \frac{1}{n_{disadv}} \sum_{i=1}^{n_{disadv}} \text{Rate}_i$
   - $\text{GroupRate}_{adv} = \frac{1}{n_{adv}} \sum_{j=1}^{n_{adv}} \text{Rate}_j$

5. Calculate disparity measures:
   - Rate-based measures:
     - $\text{DisparityRatio} = \frac{\text{GroupRate}_{disadv}}{\text{GroupRate}_{adv}}$
     - $\text{DisparityDifference} = \text{GroupRate}_{disadv} - \text{GroupRate}_{adv}$
   
   - Odds-based measures (converting rates to probabilities if necessary):
     - $\text{Odds}_{disadv} = \frac{\text{GroupRate}_{disadv}}{1 - \text{GroupRate}_{disadv}}$
     - $\text{Odds}_{adv} = \frac{\text{GroupRate}_{adv}}{1 - \text{GroupRate}_{adv}}$
     - $\text{OddsRatio} = \frac{\text{Odds}_{disadv}}{\text{Odds}_{adv}}$

6. Analyze how disparity measures vary with:
   - Group size proportions ($\pi$)
   - Class-incarceration relationship shape ($\gamma$)
   - Economic distribution parameters (means, variances, overlap)


## Expected Insights

This simulation will demonstrate:

1. How the shape of the class-incarceration relationship affects the sensitivity of inequality measures to group size
2. Why non-linear relationships (especially concave, γ > 1) make cross-national comparisons problematic
3. The mathematical relationship between group size, economic position distributions, and resulting inequality metrics
