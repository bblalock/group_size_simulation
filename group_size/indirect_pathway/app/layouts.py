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
                html.Label("Target Average Rate (per 100,000):"),
                dcc.Slider(
                    id='target-rate-slider',
                    min=100, max=1000, step=50, value=500,
                    marks={i: str(i) for i in range(100, 1001, 200)},
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
                    [dbc.Tab(label='Position Distribution Mechanism',
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
                                     )
                                 ])
                             ]
                             ),
                     dbc.Tab(label='Position-to-Rate Mechanism',
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
                                     )
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
                                     )
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
            html.P([
                "This interactive tool demonstrates how disparities emerge through an indirect pathway mechanism. ",
                "Social stratification places disadvantaged groups in more vulnerable positions, which then translate to higher incarceration rates through a non-linear function. ",
                "The model shows that even with identical treatment at each position level, substantial disparities can emerge due to structural factors."
            ]),
            html.P([
                html.Strong("Key concepts: "),
                "1) Position distributions represent social stratification, ",
                "2) The γ parameter controls how strongly position affects incarceration risk, ",
                "3) Group size (proportion disadvantaged) affects the magnitude of observed disparities."
            ])
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
            html.H4("Parameter Space Analysis"),
            html.P(
                "Explore how different parameters correlate and interact across the parameter space.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P([
                "This analysis examines thousands of simulations across the parameter space to reveal patterns and relationships. ",
                "The visualizations show how group size, stratification parameters, and incarceration function parameters interact to produce varying levels of disparity."
            ]),
            html.P([
                html.Strong("Key insights: "),
                "1) Disparity ratios follow predictable patterns based on group proportions, ",
                "2) The γ parameter amplifies disparities non-linearly, ",
                "3) Position gaps between groups have stronger effects when γ is higher, ",
                "4) Floor rates can significantly reduce extreme disparities."
            ])
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
                "Higher floor rates tend to reduce extreme disparities by establishing a minimum risk level."
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
                        html.P([
                            "These heatmaps show correlations between model parameters and outcome metrics. ",
                            "Stronger colors indicate stronger relationships. Examine which parameters most strongly influence disparity measures."
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
                        ])
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
                                    "This stacked area plot shows the probability of observing different disparity levels as group size changes. ",
                                    "Notice how the likelihood of extreme disparities increases as the disadvantaged group becomes smaller."
                                ], className="text-muted mb-2"),
                                dcc.Graph(
                                    id='disparity-probability-plot',
                                )
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
                                    "This 3D visualization maps the relationship between group proportion, stratification parameter (γ), and disparity ratio. ",
                                    "Use the selectors below to choose different variables for the z-axis and color scale."
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
                                )
                            ])
                        ], color="secondary", outline=False),
                        lg=7, md=12
                    )
                ])
            ], gap=2)
        ])
    ])

    return dbc.Tab(
        label="Parameter Space Analysis",
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
            html.H1("Group Size Effects in Measures of Disparity",
                    className="display-1"),
            html.P(
                "Explore how group sizes and social stratification interact to produce disparities in criminal justice outcomes.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P([
                "This interactive dashboard demonstrates how structural factors can generate significant disparities in incarceration rates ",
                "even without explicit discrimination at the individual level. The model shows that smaller disadvantaged groups tend to experience ",
                "more extreme disparities due to the mathematical properties of the indirect pathway mechanism."
            ]),
            html.P([
                html.Strong("Two exploration modes: "),
                "1) The Mechanism Explorer allows you to manipulate individual parameters and observe their effects in real-time. ",
                "2) The Parameter Space Analysis provides a bird's-eye view of patterns across thousands of simulations."
            ])
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
