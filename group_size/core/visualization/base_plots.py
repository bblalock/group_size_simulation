from core.visualization.style import plotly_theme_decorator
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


@plotly_theme_decorator
def create_3d_scatter(df, 
                      x_col, 
                      y_col, 
                      z_col, 
                      color_col=None, 
                      height=800,
                      width=1000,
                      **kwargs
                      ):
    """
    Generic 3D scatter plot function.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame
    x_col : str
        Column name for x-axis
    y_col : str
        Column name for y-axis
    z_col : str
        Column name for z-axis
    color_col : str, optional
        Column name for color coding points
    **kwargs : dict
        Additional arguments passed to px.scatter_3d
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.scatter_3d(
        df,
        x=x_col,
        y=y_col,
        z=z_col,
        color=color_col,
        **kwargs
    )
    return fig

@plotly_theme_decorator
def create_line_plot(df, 
                     x_col, 
                     y_col, 
                     color_col=None, 
                     error_y=None, 
                     **kwargs
                     ):
    """
    Generic line plot function with optional error bars.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame
    x_col : str
        Column name for x-axis
    y_col : str
        Column name for y-axis
    color_col : str, optional
        Column name for color coding lines
    error_y : str, optional
        Column name for y-axis error bars
    **kwargs : dict
        Additional arguments passed to px.line
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        error_y=error_y,
        **kwargs
    )
    return fig

@plotly_theme_decorator
def create_box_plot(df, 
                    x_col, 
                    y_col, 
                    color_col=None, 
                    height=700,
                    width=1200,
                    **kwargs
                    ):
    """
    Generic box plot function.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame
    x_col : str
        Column name for x-axis categories
    y_col : str
        Column name for y-axis values
    color_col : str, optional
        Column name for color coding boxes
    **kwargs : dict
        Additional arguments passed to px.box
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        **kwargs
    )
    return fig

@plotly_theme_decorator
def create_scatter_plot(df, x_col, y_col, color_col=None, size_col=None, **kwargs):
    """
    Generic scatter plot function.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame
    x_col : str
        Column name for x-axis
    y_col : str
        Column name for y-axis
    color_col : str, optional
        Column name for color coding points
    size_col : str, optional
        Column name for point sizes
    **kwargs : dict
        Additional arguments passed to px.scatter
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        **kwargs
    )
    return fig