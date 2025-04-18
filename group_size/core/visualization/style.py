def plotly_theme_decorator(func):
    """
    Decorator that applies a consistent theme to plotly figures.
    """
    def wrapper(*args, **kwargs):
        height = kwargs.pop('height', 800) if 'height' in kwargs else 800
        width = kwargs.pop('width', 1000) if 'width' in kwargs else 1000

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
            width=width
        )
        return fig
    return wrapper