import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as py

BASELINE_DISTANCE = 5
START_DATE = "2024-01-01"


def main():
    df = load_and_preprocess_data()
    create_running_pic(df)
    create_running_time_pic(df)


def load_and_preprocess_data():
    """
    This function loads the data from the csv file and preprocesses it.

    Returns:
        pd.DataFrame: preprocessed DataFrame
    """    
    df = pd.read_csv(
        "data/Activities.csv",
        decimal=".",
        delimiter=",",
        parse_dates=["Date"],
        date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"),
    )
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")

    df = df.sort_values(by="Date", ascending=True)

    df = df[df["Date"] >= pd.to_datetime(START_DATE)]
    df = df[df["Activity Type"] == "Running"]

    def convert_time(time):
        # convert "HH:MM:SS" to seconds
        hours, minutes, seconds = time.split(":")
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

    df["ElapsedTimeSeconds"] = df["Elapsed Time"].apply(lambda x: convert_time(x))
    df["ElapsedTimeHours"] = df["ElapsedTimeSeconds"] / 3600

    df["Date"] = df["Date"].dt.date

    # Sort the DataFrame by 'Date'
    df = df.sort_values("Date", ascending=True)

    # Calculate the cumulative sum of the 'Distance' column
    df["Cumulative Distance"] = df["Distance"].cumsum()

    # Create a new DataFrame with all dates from the specific start date to the end date
    start_date = pd.to_datetime(START_DATE)
    end_date = df["Date"].max()
    all_dates = pd.date_range(start=start_date, end=end_date)
    df_dates = pd.DataFrame(all_dates, columns=["Date"])
    df_dates["Date"] = df_dates["Date"].dt.date

    # Merge the new DataFrame with the original one, filling missing values with the last valid observation
    plot_df = df_dates.merge(df, on="Date", how="left")
    plot_df["Cumulative Distance"].fillna(method="ffill", inplace=True)
    plot_df["Cumulative Distance"].fillna(
        0, inplace=True
    )  # fill NaNs at the start with 0

    # Calculate the constant distance per day
    constant_distance_per_day = BASELINE_DISTANCE

    # Create a new column for the cumulative sum of this constant distance
    plot_df["Goal"] = np.arange(len(plot_df)) * constant_distance_per_day

    # Create a new column for the cumulative time in hours
    plot_df["CumulativeTime"] = plot_df["ElapsedTimeHours"].cumsum()
    plot_df["CumulativeTime"].fillna(method="ffill", inplace=True)
    plot_df["CumulativeTime"].fillna(0, inplace=True)  # fill NaNs at the start with 0

    return plot_df


def create_running_pic(plot_df: pd.DataFrame):
    """
    This function creates and saves a plotly figure showing the cumulative running distance and daily values.

    Parameters:
    plot_df (pd.DataFrame): A DataFrame containing the data to be plotted. It should have 'Date', 'Cumulative Distance', 'Daily Values', and 'Constant Cumulative Distance' columns.

    Returns:
    None
    """
    # Create initial line chart for cumulative sum
    fig = go.Figure()

    # Add lines
    fig.add_trace(
        go.Scatter(
            x=plot_df["Date"],
            y=plot_df["Cumulative Distance"],
            name="Cumulative Distance",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=plot_df["Date"], y=plot_df["Goal"], name="5km/Day", line=dict(dash="dash")
        )
    )
    # Add bar chart for daily values
    fig.add_trace(
        go.Bar(
            x=plot_df["Date"],
            y=plot_df["Distance"],
            name="Daily Values",
            opacity=0.5,
            yaxis="y2",
        )
    )

    # Create secondary y-axis
    fig.update_layout(
        title=dict(text="Running distance", x=0.5, xanchor="center"),
        yaxis=dict(title="Cumulative km"),
        yaxis2=dict(title="Daily km", overlaying="y", side="right"),
        legend=dict(x=0.5, y=-0.1, xanchor="center", yanchor="top", orientation="h"),
    )

    # fig.show()
    # Save the figure as a png file
    py.write_image(fig, "running_distance.png", scale=2)


def create_running_time_pic(plot_df: pd.DataFrame):
    """
    This function creates and saves a plotly figure showing the cumulative running time and daily values.

    Parameters:
    plot_df (pd.DataFrame): A DataFrame containing the data to be plotted. It should have 'Date', 'CumulativeTime', and 'ElapsedTimeHours' columns.

    Returns:
    None
    """
    # Create initial line chart for cumulative sum
    fig = go.Figure()

    # Add lines
    fig.add_trace(
        go.Scatter(
            x=plot_df["Date"], y=plot_df["CumulativeTime"], name="Cumulative Time"
        )
    )
    # Add bar chart for daily values
    fig.add_trace(
        go.Bar(
            x=plot_df["Date"],
            y=plot_df["ElapsedTimeHours"],
            name="Daily Values",
            opacity=0.5,
            yaxis="y2",
        )
    )

    # Create secondary y-axis
    fig.update_layout(
        title=dict(text="Running time", x=0.5, xanchor="center"),
        yaxis=dict(title="Cumulative H"),
        yaxis2=dict(title="Daily H", overlaying="y", side="right"),
        legend=dict(x=0.5, y=-0.1, xanchor="center", yanchor="top", orientation="h"),
    )

    # fig.show()
    # Save the figure as a png file
    py.write_image(fig, "running_time.png", scale=2)


if __name__ == "__main__":
    main()
