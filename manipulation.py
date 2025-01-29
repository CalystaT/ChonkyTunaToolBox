import pandas as pd
import plotly.graph_objects as go

def fix_piecewise(df, column) -> tuple:
    """
    Identifies and corrects discontinuities in a specified column of a DataFrame by dividing the data into continuous regions 
    and leveling the regions to create a smooth transition between them.
    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column (str): The name of the column to be processed.
    Returns:
    tuple: A tuple containing:
        - continuous_regions (list of lists): A list of continuous regions identified in the data.
        - corrected_values (list): A list of values with corrected discontinuities.
    """
    values = df[column].values
    diffs = df[column].diff().abs()  # Compute differences between neighboring points
    avg_diff = diffs[:10].mean()  # Compute average difference of first 10 points
    
    # Define threshold for discontinuity
    continuous_regions = []
    current_region = [values[0]]  # Start first region with the first value
    
    for i in range(1, len(values)):
        if abs(values[i] - values[i-1]) <= avg_diff*200:  # Check if the difference is greater than the average:
            current_region.append(values[i])  # Add value to current region
        else:
            if current_region:
                continuous_regions.append(current_region)  # Save previous region
            current_region = [values[i]]  # Start new region
    
    if current_region:
        continuous_regions.append(current_region)  # Append last region

    def level_regions(reg1, reg2):  # function to level one region to another by adding the difference between the last value of the first region and the first value of the second region to all values of the second region
        leveled = reg1.copy()
        offset = reg1[-1] - reg2[0]
        for val in reg2:
            leveled.append(val + offset)
        return leveled

    def connect(regions):  # function to level a leveled region to the next region
        corrected = regions[0]
        for i in range(1, len(regions)):
            corrected = level_regions(corrected, regions[i])
        return corrected

    return continuous_regions, connect(continuous_regions)



def background_corrector(df, column, window_size=10) -> list:
    """
    Corrects background drift in a given column of a DataFrame by applying a moving average filter and subtracting it from the original data.
    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column (str): The name of the column to be processed.
    window_size (int): The size of the moving average window.
    threshold (float): The threshold for detecting background drift.
    Returns:
    list: A list of corrected values with background drift removed.
    """
    values = df[column].values
    ma = pd.Series(values).rolling(window=window_size).mean().values  # Compute moving average
    drift = values - ma  # Compute background drift
    corrected_values = values - drift  # Corrected values

    return corrected_values

