import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import datetime
import os


def plot_all(file: str):
    """
    Generates and saves temperature difference plots for each unique 'Name' in the dataset.

    This function reads a dataset from an Excel file, filters out rows with non-positive 'CaskAvg' or 'EnvAvg' values,
    and generates a plot for each unique 'Name' in the dataset. The plots show the temperature difference between 'CaskAvg'
    and 'EnvAvg', alongside the individual 'CaskAvg' and 'EnvAvg' temperatures over time. Each plot is saved in a 'plots'
    directory with the 'Name' as part of the filename.

    Args:
        file (str): The path to the Excel file containing the dataset.

    Returns:
        str: The maximum date found in the 't_stamp' column of the dataset, formatted as 'MM.YYYY'.

    Note:
        - The function assumes the Excel file has columns 'Name', 't_stamp', 'CaskAvg', and 'EnvAvg'.
        - Rows with non-positive values for 'CaskAvg' or 'EnvAvg' are excluded from the analysis.
        - Plots are saved in the 'plots' directory, which is created if it does not exist.
    """

    # Read the dataset from the Excel file
    df = pd.read_excel(file)

    # Drop rows with missing values
    df = df.dropna()

    # Filter out rows where 'CaskAvg' or 'EnvAvg' are less than or equal to zero
    df = df[(df["CaskAvg"] > 0) & (df["EnvAvg"] > 0)]

    # Get the unique 'Name' values in the dataset
    HISTORM_list = df["Name"].drop_duplicates().tolist()

    # Get the maximum date from the 't_stamp' column and format it as 'MM.YYYY'
    month_year = df["t_stamp"].max().strftime("%m.%Y")

    # Generate and save plots for each unique 'Name' in the dataset
    for HISTORM in HISTORM_list:
        if HISTORM not in [
            "HI80",
            "HI70",
            "HI60",
            "HI50",
            "HI40",
            "HI30",
            "HI20",
            "HI10",
            "HI81",
            "HI71",
            "HI61",
            "HI51",
            "HI41",
            "HI31",
            "HI21",
            "HI82",
            "HI72",
            "HI62",
            "HI52",
            "HI42",
            "HI83",
            "HI73",
            "HI63",
        ]:
            pass
        else:
            HI = df.loc[df["Name"] == HISTORM]

            # Create a plot for the current 'Name'
            plt.figure(figsize=(16, 9), facecolor="white")
            plt.title(f"{HISTORM}")
            plt.plot(
                HI["t_stamp"],
                HI["CaskAvg"] - HI["EnvAvg"],
                label=f"Holtec/Casks/{HISTORM}/Delta Temp",
            )
            plt.plot(HI["t_stamp"], HI["EnvAvg"], label=f"Holtec/Environment/TIA/Value")
            plt.plot(
                HI["t_stamp"],
                HI["CaskAvg"],
                label=f"Holtec/Casks/{HISTORM}/Average Temp",
                color="grey",
            )
            plt.legend()
            plt.grid(alpha=0.6, linestyle="--")
            plt.xlabel("Data")

            # Set xticks to every day at 00:00
            ax = plt.gca()
            # set xticks to every day
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            # format xticks as 'day/month/year'
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y %H:%M"))

            # set x-axis limits to first and last day
            start_date = datetime.datetime(
                df["t_stamp"].dt.year.max(),
                df["t_stamp"].dt.month.max(),
                df["t_stamp"].dt.day.min(),
            )
            end_date = datetime.datetime(
                df["t_stamp"].dt.year.max(),
                df["t_stamp"].dt.month.max(),
                df["t_stamp"].dt.day.max(),
                12,
                00,
                00,
            )
            ax.set_xlim([start_date, end_date])

            # Rotate xticks for better readability
            plt.xticks(rotation=90)

            # Set y-axis labels and limits
            plt.ylabel("Temperatura [°C]")
            plt.ylim(0, 100)
            plt.yticks(range(0, 101, 10))

            # Save the plot as a high-quality image
            plt.tight_layout()

            # Check if the directory exists and create it if it doesn't
            if not os.path.exists("plots"):
                os.makedirs("plots")

            # Save the plot
            plt.savefig(f"plots/{HISTORM}.png", dpi=300, format="png")

            # close the plot
            plt.close()

    # Return the maximum date in the 't_stamp' column, to be used in the report
    return month_year
