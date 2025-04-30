def plotly_theme_decorator(func):
    """
    Decorator that applies a consistent theme to plotly figures.
    """
    def wrapper(*args, **kwargs):
        height = kwargs.pop('height', 800) if 'height' in kwargs else None
        width = kwargs.pop('width', 1000) if 'width' in kwargs else None

        fig = func(*args, **kwargs)
        fig.update_layout(
            template="plotly_white",
            font=dict(
                family="Times New Roman",
                size=12,
                color="black"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                title=dict(
                    side='top',
                    font=dict(size=12)
                )
            ),
            title=dict(
                font=dict(size=16),
                x=0.5,
                xanchor='center'
            ),
            height=height,
            width=width,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0),
        )
        return fig
    return wrapper