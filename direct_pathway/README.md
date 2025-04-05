# Direct Pathway Simulation

This simulation explores the direct causal pathway where race directly affects incarceration risk, independent of economic position. In this model, group membership has a direct effect on expected incarceration rate.

## Model Specification

The direct pathway model uses a simplified approach where incarceration rates are determined solely by group membership, controlled by a disparity parameter θ. The population average incarceration rate is preserved across different group proportions.



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

## Simulation Approach

Let $\pi$ be proportion of the population represented by $G_{\text{disadv}}$; i.e. 
$$\pi = \frac{|G_{\text{disadv}}|}{|G|}$$

The simulation systematically varies $\pi$ and $\theta$ to explore how group size and direct discrimination affect measured inequality.

1. Define the population proportion of the disadvantaged group: $\pi \in (0,1)$

2. Set the disparity parameter $\theta \in [0,1]$ that controls the strength of direct discrimination

3. Calculate group-level incarceration rates directly:
   - For disadvantaged group: $\text{GroupRate}_{disadv} = \text{avgRate} \cdot \left(1 + \theta \cdot \frac{1-\pi}{\pi}\right)$
   - For advantaged group: $\text{GroupRate}_{adv} = \text{avgRate} \cdot (1-\theta)$

4. Calculate disparity measures:
   - Rate-based measures:
   
   DisparityRatio = 

   $$\frac{\text{GroupRate}_{\text{disadv}}}{\text{GroupRate}_{\text{adv}}} = \frac{1 + \theta \cdot \frac{1-\pi}{\pi}}{1-\theta}$$

   DisparityDifference = 

   $$\text{GroupRate}_{disadv} - \text{GroupRate}_{adv} = \text{avgRate} \cdot \left(\theta \cdot \frac{1-\pi}{\pi} + \theta\right)$$
   
   - Odds-based measures (converting rates to probabilities if necessary):
   
   Odds for disadvantaged group:

   $$\text{Odds}_{disadv} = \frac{\text{GroupRate}_{disadv}}{1 - \text{GroupRate}_{disadv}}$$

   Odds for advantaged group:

   $$\text{Odds}_{adv} = \frac{\text{GroupRate}_{adv}}{1 - \text{GroupRate}_{adv}}$$

   OddsRatio = 

   $$\frac{\text{Odds}_{disadv}}{\text{Odds}_{adv}}$$

5. Analyze how disparity measures vary with:
   - Group size proportions ($\pi$)
   - Disparity parameter ($\theta$)
   - Average incarceration rate ($\text{avgRate}$)

## Expected Insights

1. How group size (π) affects measured inequality even when the underlying disparity parameter remains constant
3. The mathematical relationship between group size, disparity parameter, and resulting inequality metrics
