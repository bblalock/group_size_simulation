import os

def save_figure(fig, filename_base: str, output_dir: str):
    """
    Save a plotly figure as HTML and PNG.
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        The figure to save
    filename_base : str
        Base filename without extension
    output_dir : str
        Directory to save the figure
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as HTML
    html_path = os.path.join(output_dir, f"{filename_base}.html")
    fig.write_html(html_path)
    print(f"Figure saved as HTML: {html_path}")
    
    # Save as PNG
    png_path = os.path.join(output_dir, f"{filename_base}.png")
    fig.write_image(png_path)
    print(f"Figure saved as PNG: {png_path}")

def save_simulation_data(df, filename: str, output_dir: str):
    """
    Save simulation data to CSV.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The simulation results dataframe
    filename : str
        Filename for the CSV file
    output_dir : str
        Directory to save the data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    csv_path = os.path.join(output_dir, filename)
    df.to_csv(csv_path, index=False)
    print(f"Data saved as CSV: {csv_path}")