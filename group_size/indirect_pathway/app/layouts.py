import dash_bootstrap_components as dbc
from dash import dcc, html
from constants import PLOT_HEIGHT, PLOT_CARD_WIDTH


def create_controls_card():
    return dbc.Card([
        dbc.CardHeader("Controls"),
        dbc.CardBody(
            dbc.Stack([
                # Position distribution controls
                html.H5("Population Parameters"),
                html.Label("Sample Size:"),
                dcc.Slider(
                    id='sample-size-slider',
                    min=100, max=10000, step=100, value=1000,
                    marks={i: str(i) for i in range(0, 10001, 2000)},
                ),
                html.Label("Proportion Disadvantaged (p):"),
                dcc.Slider(
                    id='p-slider',
                    min=0.01, max=0.99, step=0.01, value=0.3,
                    marks={i/10: str(i/10) for i in range(0, 11, 2)},
                ),
                html.Label("Population Average Rate:"),
                dcc.Slider(
                    id='population-average-rate-slider',
                    min=100, max=1000, step=50, value=500,
                    marks={i: str(i) for i in range(100, 1001, 200)},
                ),

                # Distribution controls
                html.H5("Distribution Parameters"),
                html.Label("Mean Position (Disadvantaged):"),
                dcc.Slider(
                    id='mu-disadv-slider',
                    min=0.01, max=0.9, step=0.01, value=0.2,
                    marks={i/10: str(i/10) for i in range(0, 10, 2)},
                ),
                html.Label("Position Gap:"),
                dcc.Slider(
                    id='z-position-gap-slider',
                    min=0, max=0.8, step=0.01, value=0.3,
                    marks={i/10: str(i/10) for i in range(0, 9, 2)},
                ),
                html.Label("Concentration (Disadvantaged):"),
                dcc.Slider(
                    id='c-disadv-slider',
                    min=1, max=50, step=1, value=20,
                    marks={i: str(i) for i in range(0, 51, 10)},
                ),
                html.Label("Concentration (Advantaged):"),
                dcc.Slider(
                    id='c-adv-slider',
                    min=1, max=50, step=1, value=20,
                    marks={i: str(i) for i in range(0, 51, 10)},
                ),
                # Incarceration rate parameters
                html.H5("Incarceration Rate Parameters"),
                html.Label("Shape Parameter (γ):"),
                dcc.Slider(
                    id='gamma-slider',
                    min=0, max=5, step=0.1, value=1,
                    marks={i: str(i) for i in range(0, 6)},
                ),
                html.Label("Incarceration Rate Floor (per 100,000):"),
                dcc.Slider(
                    id='floor-rate-slider',
                    min=0, max=200, step=10, value=0,
                    marks={i: str(i) for i in range(0, 201, 50)},
                ),
            ], gap=2))
    ],
        style=dict(height='100%'))


def create_visualization_section():
    return dbc.Stack(children=[
        # Statistics card on top
        dbc.Card([
            dbc.CardHeader("Statistics"),
            dbc.CardBody(id='stats-container')
        ]),
        # Visualization card below
        dbc.Card([
            dbc.CardHeader("Visualization"),
            dbc.CardBody([
                dbc.Tabs(
                    [dbc.Tab(label='Social Stratification Mechanism',
                             tab_id='position-distribution-tab',
                             children=[
                                 html.Div([
                                     html.P([
                                         "This plot shows how individuals from advantaged and disadvantaged groups are distributed across social positions. ",
                                         "The x-axis represents social position (0-1), where higher values indicate more privileged positions. ",
                                         "Adjust the distribution parameters to see how changes in group means, concentration, and position gap affect stratification."
                                     ], className="text-muted mb-2"),
                                     dcc.Graph(
                                         id='position-distribution-plot',
                                         style={'height': '100%', 'width': '100%'}
                                     ),
                                     dbc.Card([
                                         dbc.CardBody([
                                             dcc.Markdown('''
### Social Stratification Model

We model social stratification by generating different position distributions for advantaged and disadvantaged groups using beta distributions:

- For disadvantaged group: $z_i \sim \\text{Beta}(\\alpha_{\\text{disadv}}, \\beta_{\\text{disadv}})$
- For advantaged group: $z_j \sim \\text{Beta}(\\alpha_{\\text{adv}}, \\beta_{\\text{adv}})$

Where the beta distribution parameters are derived using the mean-concentration approach:
- $\\alpha_{\\text{group}} = \\mu_{\\text{group}} \\cdot c_{\\text{group}}$
- $\\beta_{\\text{group}} = (1 - \\mu_{\\text{group}}) \\cdot c_{\\text{group}}$

The mean position of the disadvantaged group ($\\mu_{\\text{disadv}}$) is lower than that of the advantaged group ($\\mu_{\\text{adv}}$), with the difference controlled by the position gap parameter:

$\\mu_{\\text{adv}} = \\mu_{\\text{disadv}} + z_{\\text{position\\_gap}}$

The concentration parameters ($c_{\\text{disadv}}$ and $c_{\\text{adv}}$) control how tightly each group clusters around its mean position, with higher values creating more peaked, narrower distributions.
''', mathjax=True, style={'color': 'white'})
                                         ])
                                     ], color="dark", inverse=True, className="mt-3")
                                 ])
                             ]
                             ),
                     dbc.Tab(label='Position-to-Incarceration Mechanism',
                             tab_id='position-to-rate-tab',
                             children=[
                                 html.Div([
                                     html.P([
                                         "This plot demonstrates how social position translates to incarceration risk through a power function. ",
                                         "The shape parameter (γ) controls the steepness of the curve - higher values create more extreme disparities between top and bottom positions. ",
                                         "The normalization factors ensure the population average matches the target rate while maintaining the floor rate."
                                     ], className="text-muted mb-2"),
                                     dcc.Graph(
                                         id='position-to-rate-plot',
                                         style={'height': '100%', 'width': '100%'}
                                     ),
                                     dbc.Card([
                                         dbc.CardBody([
                                             dcc.Markdown('''
### Basic Position-to-Incarceration Relationship

The core mechanism of the model is a power function that translates position to incarceration risk:

$$\\text{PositionEffect}(z, \\gamma) = (1-z)^{\\gamma}$$

Where:
- $z \\in Z = \\{z \\in \\mathbb{R} \\mid 0 \\leq z \\leq 1\\}$ represents position in the stratification dimension
- $\\gamma \\in \\mathbb{R}^+$ controls the shape of the relationship between position and incarceration risk

### Function Properties

The position effect function has the following properties:
- It equals 1 at the lowest position ($z = 0$) and approaches 0 at the highest position ($z = 1$)
- When $\\gamma = 1$: Linear relationship (constant rate of decrease)
- When $0 < \\gamma < 1$: Convex curve (steeper drops at higher positions)
- When $\\gamma > 1$: Concave curve (steeper drops at lower positions)

### Normalized Incarceration Rate Model

To enable controlled comparisons across simulations, we implement a normalized model that maintains a constant population-average incarceration rate:

$$\\text{IncarcerationRate}(\\text{targetAvgRate}, z, \\gamma) = \\text{targetAvgRate} \\cdot \\frac{(1-z)^{\\gamma}}{E[(1-Z)^{\\gamma}]}$$

Where:
- targetAvgRate is the desired population-average incarceration rate
- $E[(1-Z)^{\\gamma}]$ is the expected value of the position effect across the entire population
- The fraction normalizes the position effect so that its average equals 1

### Normalized Model with Floor Rate

We further extend the model by introducing a minimum incarceration rate (floor) in a three-step process:

1. Calculate initial rates using the normalized model
2. Apply floor rate constraint: $\\text{RateWithFloor}(z) = \\max(\\text{floorRate}, \\text{InitialRate}(z))$
3. Apply second normalization to maintain target average: $\\text{FinalRate}(z) = \\text{RateWithFloor}(z) \\cdot \\frac{\\text{targetAvgRate}}{E[\\text{RateWithFloor}(Z)]}$

This two-step normalization process is critical for maintaining comparable scenarios across simulation runs. When we add a floor, we potentially increase the average rate, so the second normalization factor adjusts all rates proportionally downward to maintain the target average.
''', mathjax=True, style={'color': 'white'})
                                         ])
                                     ], color="dark", inverse=True, className="mt-3")
                                 ])
                             ]
                             ),
                     dbc.Tab(label='Disparity Generation Mechanism',
                             tab_id='disparity-generation-tab',
                             children=[
                                 html.Div([
                                     html.P([
                                         "This plot shows the resulting incarceration rates for each group. ",
                                         "The disparity ratio (disadvantaged/advantaged) and normalized disparity index (η) quantify the level of inequality. ",
                                         "Observe how group size (proportion disadvantaged) interacts with stratification parameters to produce disparities."
                                     ], className="text-muted mb-2"),
                                     dcc.Graph(
                                         id='incarceration-plot',
                                         style={'height': '100%', 'width': '100%'}
                                     ),
                                     dbc.Card([
                                         dbc.CardBody([
                                             dcc.Markdown('''
### Disparity Generation Mechanism

The indirect pathway model simulates how social stratification affects incarceration rates through a two-step process:

1. **Social Stratification**: Advantaged and disadvantaged groups have different distributions along a socioeconomic position dimension Z
2. **Position-to-Incarceration Function**: An individual's position in Z determines their incarceration risk through a power function

Our analysis reveals an important distinction between unconstrained and constrained models:

- In the **unconstrained model**, disparity ratios remain largely independent of group size, with disparities primarily determined by the position gap between groups and the shape parameter of the position-to-incarceration function.

- When we introduce empirically realistic constraints—specifically a minimum incarceration rate (floor)—the relationship changes significantly. With this floor constraint applied, smaller disadvantaged groups show higher measured disparities than larger disadvantaged groups.
''', mathjax=True, style={'color': 'white'})
                                         ])
                                     ], color="dark", inverse=True, className="mt-3")
                                 ])
                             ]
                             ),
                     ],
                    active_tab='disparity-generation-tab',
                    className="nav-justified"
                )
            ])
        ])
    ], gap=2)


def create_mechanism_explorer_tab():
    jumbotron = create_jumbotron(
        [
            html.H4("Mechanism of the Simulation"),
            html.P(
                "Explore how social stratification and position-to-incarceration functions interact to generate group disparities.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            dcc.Markdown('''
This interactive tool demonstrates how outcome differences emerge through an indirect pathway mechanism based purely on structural factors:

1. **Position Distribution**: Different groups have distinct distributions along a position dimension
2. **Position-to-Incarceration Function**: Lower positions face higher incarceration risk through a power function relationship
3. **Emergent Patterns**: The interaction of these mechanisms produces substantial group differences in outcomes

##### Key Parameters:
* **Position Gap**: The difference between mean positions of advantaged and disadvantaged groups (strongest determinant of outcome differences)
* **γ (Gamma)**: Controls the steepness of the position-to-incarceration relationship (higher values amplify differences non-linearly)
* **Group Size**: The proportion of the disadvantaged group in the population
* **Floor Rate**: Minimum incarceration rate constraint (when applied, smaller disadvantaged groups show higher measured differences)

Explore how these parameters interact to generate outcome patterns in the visualization panels.
''', className="mb-4"),
        ])

    return dbc.Tab(label="Mechanism Explorer",
                   children=[
                       jumbotron,
                       # Main row containing controls and chart
                       dbc.Row([
                               dbc.Row([
                                   # Left column - Controls card
                                   dbc.Col(create_controls_card(),
                                       md=12-PLOT_CARD_WIDTH,
                                       sm=12),
                                   # Right column - Statistics and Chart
                                   dbc.Col(create_visualization_section(),
                                       md=PLOT_CARD_WIDTH,
                                       sm=12)],
                                       justify='center')],
                               justify='center'
                               )
                   ]
                   )


def create_parameter_space_analysis_tab(simulation_results):
    jumbotron = create_jumbotron(
        [
            html.H4("Constrained vs. Unconstrained Multi-Simulation Analysis"),
            html.P(
                "Explore how floor rate constraints affect disparity patterns across the parameter space.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            dbc.Accordion([
                dbc.AccordionItem(
                    dcc.Markdown('''
Our simulation explores how key parameters affect observed disparities in incarceration rates. We focus on four critical parameters while holding others constant to isolate their effects:

1. **Group proportion**: $p \\in (0.01, 0.99)$ with increments of 0.05
   - Represents the proportion of the disadvantaged group in the population
   - Allows us to examine how group size affects disparity metrics

2. **Position gap between groups**: $z\\_position\\_gap \\in \\{0, 0.2, 0.4, 0.6, 0.8\\}$
   - The difference between mean positions of advantaged and disadvantaged groups
   - Represents structural stratification in society

3. **Shape parameter**: $\\gamma \\in [0.1, 5]$ with 20 evenly spaced values
   - Controls the steepness of the relationship between position and incarceration risk
   - Higher values create more severe penalties for lower positions

4. **Floor rate**: $floorRate \\in [0, 500]$ with 20 evenly spaced values
   - Minimum incarceration rate before second normalization
   - Introduces an empirically motivated constraint

### Constant Parameters

For parsimony and to better isolate the effects of our key variables, we hold the following parameters constant:

- Mean position of disadvantaged group: $\\mu_{\\text{disadv}} = 0.2$
- Concentration parameters: $c_{\\text{disadv}} = c_{\\text{adv}} = 20$
- Target average incarceration rate: $targetAvgRate = 500$ per 100,000
- Sample size: $N = 10,000$ individuals per simulation run

### Disparity Measures

For each simulation, we calculate several disparity measures:

1. **Disparity Ratio**: $d = \\frac{\\text{GroupRate}_{\\text{disadv}}}{\\text{GroupRate}_{\\text{adv}}}$

2. **Rate Difference**: $\\text{GroupRate}_{\\text{disadv}} - \\text{GroupRate}_{\\text{adv}}$

3. **Normalized Disparity Index**: $\\eta = \\frac{d - 1}{d + \\frac{1 - p}{p}}$
''', mathjax=True),
                    title="Simulation Approach",
                )
            ], start_collapsed=True),
            html.Br(),
            dcc.Markdown('''
Our analysis reveals an important distinction between unconstrained and constrained models. In the unconstrained model, disparity ratios remain largely independent of group size, with disparities primarily determined by the position gap between groups and the shape parameter of the position-to-incarceration function. However, when we introduce empirically realistic constraints—specifically a minimum incarceration rate (floor)—the relationship changes significantly. With this floor constraint applied, smaller disadvantaged groups show higher measured disparities than larger disadvantaged groups.

##### Comparison Between Models

The contrast between the unconstrained and constrained models reveals important insights about measuring group inequality in punishment:

- **Mathematical vs. empirical considerations**: The unconstrained model reveals the mathematical properties of disparity measures, while the constrained model better approximates empirically realistic scenarios.

- **Group size effects**: The models reveal how group size genuinely affects measured disparities under realistic constraints. When a floor rate is introduced, smaller disadvantaged groups systematically show higher disparity ratios because:
  - The floor prevents the advantaged group's rate from falling below a minimum value
  - To maintain the same population-average rate, the disadvantaged group's rate must increase to compensate
  - This mathematical relationship produces higher disparities for smaller disadvantaged groups even when all other causal factors are identical
''', mathjax=True)
        ])

    # Get unique floor rate values from simulation results
    floor_rate_values = sorted(simulation_results['min_rate'].unique())
    min_floor_rate = min(floor_rate_values)
    max_floor_rate = max(floor_rate_values)
    default_floor_rate = min_floor_rate

    # Create control panel
    controls = dbc.Card([
        dbc.CardHeader("Controls"),
        dbc.CardBody([
            html.Label("Floor Rate (per 100,000):"),
            html.P([
                "Adjust the minimum incarceration rate to see how it affects disparity patterns across the parameter space. ",
                "Higher floor rates tend to reduce extreme disparities by establishing a minimum risk level for advantaged groups, ",
                "preventing the mathematically possible but empirically unrealistic scenario of near-zero rates."
            ], className="text-muted small"),
            dcc.Slider(
                id='param-space-floor-rate-slider',
                min=min_floor_rate,
                max=max_floor_rate,
                step=None,
                value=default_floor_rate,
                marks={val: str(int(val)) for val in floor_rate_values},
            ),
        ])
    ])

    # Create layout with plots
    plots = dbc.Card([
        dbc.CardHeader("Visualizations"),
        dbc.CardBody([
            dbc.Stack([
                # Correlation plots card
                dbc.Card([
                    dbc.CardHeader("Parameter Correlations"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Correlation Method:"),
                                dbc.Switch(
                                    id='correlation-method-switch',
                                    label="Use Spearman's Correlation",
                                    value=True
                                ),
                            ], width=6),
                        ], className="mb-3"),
                        html.P([
                            "These heatmaps show correlations between model parameters and outcome metrics. ",
                            "In the unconstrained model, position gap shows the strongest positive correlation with disparity measures (>0.7), ",
                            "while group proportion (p) shows virtually no correlation with disparity ratio."
                        ], className="text-muted mb-2"),
                        dbc.Row([
                            dbc.Col(
                                dcc.Graph(
                                    id='param-metric-correlation-plot',
                                ),
                                lg=6, md=12
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id='derived-metric-correlation-plot',
                                ),
                                lg=6, md=12
                            ),
                        ]),
                        dbc.Accordion([
                            dbc.AccordionItem([
                                dcc.Markdown('''
#### Unconstrained Model
- Position gap between groups has the strongest positive correlation with disparity measures
- The shape parameter (γ) shows significant positive correlation with disparity ratio
- Group size (p) shows negligible correlation with disparity measures, confirming mathematical independence
- The relationship between parameters is consistent across different disparity metrics

#### Constrained Model
- Position gap between groups remains the strongest predictor of disparity measures
- Group size (p) shows significant negative correlation with disparity ratio when a floor is applied
- The effect of γ is moderated by the floor, but still significant
''', mathjax=True)
                            ], title="Key Findings")
                        ], start_collapsed=True)
                    ])
                ], color="secondary", outline=False),
                # Probability plot and 3D scatter plot in the same row
                dbc.Row([
                    # Probability plot card
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("Disparity Probability Distribution"),
                            dbc.CardBody([
                                html.P([
                                    "This stacked area plot shows the probability distribution of disparity ratios across different disadvantaged group proportions. ",
                                    "In the unconstrained model, these distributions largely overlap, showing that the likelihood of observing any particular disparity ratio ",
                                    "is similar regardless of group size. With a floor constraint, the probability of extreme disparities increases as the disadvantaged group becomes smaller."
                                ], className="text-muted mb-2"),
                                dcc.Graph(
                                    id='disparity-probability-plot',
                                ),
                                dbc.Accordion([
                                    dbc.AccordionItem([
                                        dcc.Markdown('''
#### Unconstrained Model
- The *probability distribution* of disparity ratios remains largely stable across different group proportions
- This stability confirms the mathematical independence of disparity ratios from group size when no empirical constraints are applied
- Disparities are primarily determined by position gap and gamma, regardless of demographic composition

#### Constrained Model
- The probability of observing extreme disparity ratios (>10:1) increases dramatically as the disadvantaged group becomes smaller, especially with lower floor rates
- As the floor rate increases, the probability distribution shifts, with extreme disparities becoming less likely
- The sensitivity to group size becomes more pronounced with higher floor rates
''', mathjax=True)
                                    ], title="Key Findings")
                                ], start_collapsed=True)
                            ])
                        ], color="secondary", outline=False),
                        lg=5, md=12
                    ),
                    
                    # 3D scatter plot card
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("Parameter Space Visualization"),
                            dbc.CardBody([
                                html.P([
                                    "This 3D visualization maps the relationship between group proportion, gamma (γ), and disparity measures. ",
                                    "In the unconstrained model, the surface remains relatively stable across different group proportions, ",
                                    "while in the constrained model, the surface shows significant variation with group size, particularly when the disadvantaged group is small."
                                ], className="text-muted mb-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Z-Axis Variable:"),
                                        dcc.Dropdown(
                                            id='z-axis-variable-dropdown',
                                            options=[
                                                {'label': 'Disparity Ratio', 'value': 'disparity_ratio'},
                                                {'label': 'Rate Difference', 'value': 'rate_difference'},
                                                {'label': 'Rate Disadvantaged', 'value': 'rate_disadv'},
                                                {'label': 'Disadvantaged Δ from Avg (%)', 'value': 'disadv_delta_from_avg_percent'},
                                                {'label': 'Rate Advantaged', 'value': 'rate_adv'},
                                                {'label': 'Advantaged Δ from Avg (%)', 'value': 'adv_delta_from_avg_percent'},
                                                {'label': 'Normalized Disparity Index (η)', 'value': 'normalized_disparity_index'}
                                            ],
                                            value='disparity_ratio',
                                            clearable=False
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Color Scale Variable:"),
                                        dcc.Dropdown(
                                            id='color-variable-dropdown',
                                            options=[
                                                {'label': 'Position Gap', 'value': 'z_position_gap'},
                                                {'label': 'Floor Rate', 'value': 'min_rate'},
                                                {'label': 'Rate Difference', 'value': 'rate_difference'},
                                                {'label': 'Disadvantaged Δ from Avg (%)', 'value': 'disadv_delta_from_avg_percent'},
                                                {'label': 'Advantaged Δ from Avg (%)', 'value': 'adv_delta_from_avg_percent'},
                                                {'label': 'Normalized Disparity Index (η)', 'value': 'normalized_disparity_index'}
                                            ],
                                            value='z_position_gap',
                                            clearable=False
                                        )
                                    ], width=6)
                                ], className="mb-3"),
                                dcc.Graph(
                                    id='simulation-3d-plot',
                                ),
                                dbc.Accordion([
                                    dbc.AccordionItem([
                                        dcc.Markdown('''
#### Unconstrained Model
- Position gap dominance: The position gap between groups is the strongest determinant of disparity levels, with higher gaps producing greater disparities
- Gamma amplification effect: Higher values of the shape parameter (γ) amplify disparities non-linearly, especially when combined with larger position gaps
- Group size-independence of disparity ratio: The disparity ratio is largely unaffected by group size when no floor constraint is applied
- Disparity ratio instability at extremes: The disparity ratio is sensitive to small values in its denominator (i.e., advantaged group's rate approaching zero)

#### Constrained Model
- Group size sensitivity: With a floor rate, the disparity ratio becomes sensitive to group size, with significantly higher disparities observed when the disadvantaged group is small
- Floor rate effects: As the floor rate increases, maximum observable disparities decrease and the sensitivity to group size becomes more pronounced
- The effects of γ are moderated by the floor rate
- When a floor rate is introduced, smaller disadvantaged groups systematically show higher disparity ratios even when all other causal factors are identical
''', mathjax=True)
                                    ], title="Key Findings")
                                ], start_collapsed=True)
                            ])
                        ], color="secondary", outline=False),
                        lg=7, md=12
                    )
                ])
            ], gap=2)
        ])
    ])

    return dbc.Tab(
        label="Constrained vs. Unconstrained Model Analysis",
        children=dbc.Row([
            dbc.Row([
                jumbotron,
                dbc.Col([
                    dbc.Stack(
                        [
                            dbc.Row([
                                dbc.Col(controls,
                                    width={"size": 12}
                                        )
                            ]),
                            dbc.Row([
                                dbc.Col(plots,
                                    width={"size": 12}
                                        )
                            ])
                        ],
                        gap=2)
                ])
            ], justify='center')
        ], justify='center')
    )


def create_jumbotron(children, className='py-3'):
    return html.Div(
        dbc.Container(
            children=children,
            fluid=True,
            className=className,
        ),
        className="p-3 bg-body-secondary mb-4",
    )


def create_layout(simulation_results):
    jumbotron = create_jumbotron(
        [
            html.H1("Indirect Pathway Simulation",
                    className="display-3"),
            html.Hr(className="my-2"),
            dcc.Markdown('''
This simulation examines how group size influences the measurement of disparities in outcomes. We developed a computational model that incorporates two key mechanisms: social stratification (different distributions of advantaged and disadvantaged groups across positions) and position-based risk (where lower positions face higher risk through a power function relationship).

Our analysis reveals an important distinction between unconstrained and constrained models. In the unconstrained model, disparity ratios remain largely independent of group size, with disparities primarily determined by the position gap between groups and the shape parameter of the position-to-risk function. However, when we introduce empirically realistic constraints—specifically a minimum rate (floor)—the relationship changes significantly. With this floor constraint applied, smaller disadvantaged groups show higher measured disparities than larger disadvantaged groups.

**Two exploration tabs:**

1. The **Mechanism Explorer** allows you to manipulate individual parameters and observe their effects in real-time.
2. The **Constrained vs. Unconstrained Multi-Simulation Analysis** provides a bird's-eye view of patterns across thousands of simulations.
            ''')
        ])

    return html.Div([
        jumbotron,
        dbc.Card([
            dbc.Tabs([
                create_mechanism_explorer_tab(),
                create_parameter_space_analysis_tab(
                    simulation_results=simulation_results)
            ], className="nav-justified")
        ])
    ])
