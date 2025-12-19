import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore
import seaborn as sns
import matplotlib.dates as mdates
import datetime
import os
from typing import List
import numpy as np
from calendar import monthrange


def plot_all(files: List[str], output_dir: str = "plots"):
    """
    Create yearly plots from multiple monthly data files.
    Displays all months from January to the last month in the data.
    
    Parameters:
    -----------
    files : List[str]
        List of file paths, each containing data for one month
    output_dir : str
        Directory to save the plots
    """
    
    # Read and combine all data from all files
    all_data = []
    for file in files:
        df_month = pd.read_excel(file)
        df_month = df_month[["Name", "t_stamp", "EnvAvg", "CaskAvg"]]
        df_month = df_month[(df_month["CaskAvg"] > 0) & (df_month["EnvAvg"] > 0)]
        df_month = df_month.dropna()
        all_data.append(df_month)
    
    # Combine all monthly data
    df = pd.concat(all_data, ignore_index=True)
    
    # Sort by timestamp
    df = df.sort_values(by="t_stamp")
    
    if df["t_stamp"].empty:
        print("No data available")
        return None
    
    # Get the actual date range from the data
    start_date = df["t_stamp"].min()
    end_date = df["t_stamp"].max()
    year = start_date.year
    
    # Always start from January 1st
    plot_start_date = datetime.datetime(year, 1, 1)
    
    # End at the last day of the last month in the data
    last_month = end_date.month
    last_day = monthrange(year, last_month)[1]
    plot_end_date = datetime.datetime(year, last_month, last_day, 23, 59, 59)
    
    print(f"Plotting data from January to {plot_end_date.strftime('%B')} {year}")
    
    # Step 1: Apply zscore within each group (for each cask)
    df[["EnvAvg_z", "CaskAvg_z"]] = df.groupby("Name")[["EnvAvg", "CaskAvg"]].transform(zscore)
    
    # Step 2: Filter out the outliers
    z_score_threshold = 2
    df_filtered = df[
        (df["EnvAvg_z"].abs() <= z_score_threshold)
        & (df["CaskAvg_z"].abs() <= z_score_threshold)
    ]
    
    # Drop the z-score columns
    df_filtered = df_filtered.drop(columns=["EnvAvg_z", "CaskAvg_z"])
    
    # Set the style of the visualization
    sns.set_theme(style="whitegrid")
    
    # Get all unique cask names
    all_names = df_filtered["Name"].unique()
    
    # Create a plot for each cask
    for name in all_names:
        plt.figure(figsize=(20, 10))
        
        # Get data for this specific cask
        cask_data = df_filtered[df_filtered["Name"] == name]
        
        if not cask_data.empty:
            # Plot delta temperature
            plt.plot(
                cask_data["t_stamp"],
                cask_data["CaskAvg"] - cask_data["EnvAvg"],
                label=f"Holtec/Casks/{name}/Delta Temp",
                color='blue',
                alpha=0.7,
                linewidth=1.5
            )
            
            # Plot environment temperature
            plt.plot(
                cask_data["t_stamp"],
                cask_data["EnvAvg"],
                label=f"Holtec/Environment/TIA/Value",
                color='green',
                alpha=0.7,
                linewidth=1.5
            )
            
            # Plot cask average temperature
            plt.plot(
                cask_data["t_stamp"],
                cask_data["CaskAvg"],
                label=f"Holtec/Casks/{name}/Average Temp",
                color='red',
                alpha=0.7,
                linewidth=1.5
            )
        
        # Set titles and labels
        if last_month == 12:
            plt.title(f"{name} - Year {year}", fontsize=16, fontweight='bold')
        else:
            last_month_name = plot_end_date.strftime('%B')
            plt.title(f"{name} - January to {last_month_name} {year}", 
                     fontsize=16, fontweight='bold')
        
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Temperature [°C]", fontsize=12)
        
        # Set y-axis limits
        plt.ylim(0, 100)
        plt.yticks(range(0, 101, 10))
        
        # Create grid for better readability
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Set x-axis to show from January to last month
        ax = plt.gca()
        ax.set_xlim([plot_start_date, plot_end_date])
        
        # Always show all months from January to the last month
        if last_month <= 6:
            # Show every month if 6 or fewer months
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        else:
            # For more than 6 months, show every month (we have space for 12 months)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_minor_locator(mdates.MonthLocator())
        
        # Add minor grid for weeks
        ax.grid(True, which='minor', alpha=0.2, linestyle=':')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add legend
        plt.legend(loc='upper left', fontsize=10)
        
        # Adjust layout
        plt.tight_layout()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save the plot with appropriate filename
        if last_month == 12:
            filename = f"{output_dir}/{name}_Year_{year}.png"
        else:
            filename = f"{output_dir}/{name}_Jan_to_{plot_end_date.strftime('%b')}_{year}.png"
        
        plt.savefig(filename, dpi=300, format="png", bbox_inches='tight')
        
        # Close the plot
        plt.close()
    
    # Also create a summary plot showing all casks
    create_summary_plot(df_filtered, plot_start_date, plot_end_date, output_dir)
    
    if last_month == 12:
        return f"01.{year} to 12.{year}"
    else:
        return f"01.{year} to {last_month:02d}.{year}"


def create_summary_plot(df: pd.DataFrame, start_date: datetime.datetime, 
                       end_date: datetime.datetime, output_dir: str):
    """
    Create a summary plot showing all casks for the period.
    """
    if df.empty:
        return
    
    plt.figure(figsize=(24, 12))
    
    # Get unique cask names
    unique_names = df["Name"].unique()
    
    # Create a colormap for different casks
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_names)))
    
    for idx, name in enumerate(unique_names):
        cask_data = df[df["Name"] == name]
        if not cask_data.empty:
            plt.plot(
                cask_data["t_stamp"],
                cask_data["CaskAvg"],
                label=name,
                color=colors[idx],
                alpha=0.7,
                linewidth=1
            )
    
    # Set title based on date range
    year = start_date.year
    last_month = end_date.month
    
    if last_month == 12:
        plt.title(f"All Casks - Year {year}", fontsize=18, fontweight='bold')
    else:
        last_month_name = end_date.strftime('%B')
        plt.title(f"All Casks - January to {last_month_name} {year}", 
                 fontsize=18, fontweight='bold')
    
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Cask Temperature [°C]", fontsize=14)
    
    # Set y-axis limits
    plt.ylim(0, 100)
    
    # Format x-axis
    ax = plt.gca()
    ax.set_xlim([start_date, end_date])
    
    # Always show all months
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    
    # Add grid and legend
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save summary plot
    if last_month == 12:
        filename = f"{output_dir}/All_Casks_Summary_Year_{year}.png"
    else:
        filename = f"{output_dir}/All_Casks_Summary_Jan_to_{end_date.strftime('%b')}_{year}.png"
    
    plt.savefig(filename, dpi=300, format="png", bbox_inches='tight')
    plt.close()


# # Example usage:
# if __name__ == "__main__":
#     # Example 1: Full year (12 months)
#     full_year_files = [
#         "data/2023/01_january.xlsx",
#         "data/2023/02_february.xlsx",
#         "data/2023/03_march.xlsx",
#         "data/2023/04_april.xlsx",
#         "data/2023/05_may.xlsx",
#         "data/2023/06_june.xlsx",
#         "data/2023/07_july.xlsx",
#         "data/2023/08_august.xlsx",
#         "data/2023/09_september.xlsx",
#         "data/2023/10_october.xlsx",
#         "data/2023/11_november.xlsx",
#         "data/2023/12_december.xlsx"
#     ]
    
#     # Example 2: Partial year (Jan-Nov, 11 months)
#     partial_year_files = [
#         "data/2023/01_january.xlsx",
#         "data/2023/02_february.xlsx",
#         "data/2023/03_march.xlsx",
#         "data/2023/04_april.xlsx",
#         "data/2023/05_may.xlsx",
#         "data/2023/06_june.xlsx",
#         "data/2023/07_july.xlsx",
#         "data/2023/08_august.xlsx",
#         "data/2023/09_september.xlsx",
#         "data/2023/10_october.xlsx",
#         "data/2023/11_november.xlsx"
#     ]
    
#     # Process based on what you have
#     files_to_process = partial_year_files  # or full_year_files
    
#     date_range = plot_all(files_to_process, "plots")
#     print(f"Created plots for: {date_range}")

if __name__ == "__main__":
    # Example 2: Partial year (Jan-Nov)
    partial_year_files = [
        "D:/alexbot D/UAS/Coleta/2025-01/Jan 25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-02/FEV25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-03/mar 25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-04/abr 25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-05/MAI 25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-06/JUN25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-07/JUL25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-08/AGO25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-09/SET25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-10/OUT25.xlsx",
        "D:/alexbot D/UAS/Coleta/2025-11/NOV25.xlsx"
    ]
    
    # Process partial year
    print("\nProcessing partial year data (Jan-Nov)...")
    partial_year_range = plot_all(partial_year_files, "plots/2025_jan-nov")
    print(f"Created plots for: {partial_year_range}")
