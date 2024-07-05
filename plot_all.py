import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import datetime
import os


def plot_all(file: str):
    """Plots all the data from the given file

    Args:
        file (str): file path
    """
    df = pd.read_excel(file)
    df = df.dropna()
    HISTORM_list = df["Name"].drop_duplicates().tolist()

    # Get the maximum date from the 't_stamp' column and format it as 'MM.YYYY'
    month_year = df["t_stamp"].max().strftime("%m.%Y")

    # Calculate the mode temperature excluding zero and negative values
    cask_mode_temp = df[df["CaskAvg"] > 0]["CaskAvg"].mode()[0]

    # Replace zero temperature values with the mode
    df["CaskAvg"] = df["CaskAvg"].replace(0, cask_mode_temp)

    # Calculate the mode environment temperature excluding zero and negative values
    env_mode_temp = df[df["EnvAvg"] > 0]["EnvAvg"].mode()[0]
    df["EnvAvg"] = df["EnvAvg"].replace(0, env_mode_temp)

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

            plt.figure(figsize=(16, 9), facecolor="white")
            plt.title(f"{HISTORM}")
            plt.plot(
                HI["t_stamp"],
                HI["CaskAvg"] - HI["EnvAvg"],
                label=f"Holtec/Casks/{HISTORM}/Delta Temp",
            )
            plt.plot(HI["t_stamp"], HI["EnvAvg"],
                     label=f"Holtec/Environment/TIA/Value")
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
            ax.xaxis.set_major_locator(
                mdates.DayLocator(interval=1)
            )  # set xticks to every day
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter("%d/%m/%y %H:%M")
            )  # format xticks as 'day/month/year'

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
            # set x-axis limits to first and last day
            ax.set_xlim([start_date, end_date])

            plt.xticks(rotation=90)
            plt.ylabel("Temperatura [°C]")
            plt.ylim(0, 100)
            plt.yticks(range(0, 101, 10))

            # Save the plot as a high-quality image
            plt.tight_layout()

            # Check if the directory exists and create it if it doesn't
            if not os.path.exists("plots"):
                os.makedirs("plots")

            plt.savefig(f"plots/{HISTORM}.png", dpi=300, format="png")

            # close the plot
            plt.close()

            # plt.show()
    return month_year
