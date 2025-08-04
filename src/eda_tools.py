from src.plot_data_basic import Plotter
from src.plot_data_bivariate import PlotNumericalVsNumericalScatter, PlotCorrHeatmap, PlotCategoricalVsNumericalBox
from src.load_data import DataLoaderFactory
from src.plot_data_basic import Plotter, PlotStrategy
from src.plot_data_basic import PlotAverageSessionTimes, PlotNumberOfSessions, PlotUserFrequencyDistribution
from src.plot_data_univariate import PlotCategoricalDistribution, PlotNumericalDistribution
from src.plot_data_bivariate import PlotNumericalVsNumericalScatter, PlotCorrHeatmap, PlotCategoricalVsNumericalBox

from src.plot_tools import add_enriched_datetime_columns, get_daily_session_stats
import matplotlib.pyplot as plt


import pandas as pd

def plot_bivariate_plots(plotter: Plotter, df: pd.DataFrame):
    plotter.set_strategy(PlotCorrHeatmap())
    plotter.plot(df,features=["start_time", "end_time", "duration_minutes","total_energy"])
    plt.show()

    fig, axs = plt.subplots(1, 3, figsize=(14, 5))

    plotter.set_strategy(PlotNumericalVsNumericalScatter())
    plotter.plot(df, feature1="start_time", feature2="end_time", ax=axs[0], time_of_day_settings_flag = (True, True), gridsize=100)
    plotter.plot(df, feature1="start_time", feature2="duration_minutes", ax=axs[1], time_of_day_settings_flag = (True, True), gridsize=100)
    plotter.plot(df, feature1="end_time", feature2="duration_minutes", ax=axs[2], time_of_day_settings_flag = (True, True), gridsize=100)

    fig.suptitle("Time Distributions")
    fig.tight_layout()

    fig, axs = plt.subplots(1, 3, figsize=(14, 5))

    plotter.set_strategy(PlotNumericalVsNumericalScatter())
    plotter.plot(df, feature1="start_time", feature2="total_energy", ax=axs[0], time_of_day_settings_flag = (True, False), gridsize=100)
    plotter.plot(df, feature1="end_time", feature2="total_energy", ax=axs[1], time_of_day_settings_flag = (True, False), gridsize=100)
    plotter.plot(df, feature1="duration_minutes", feature2="total_energy", ax=axs[2], time_of_day_settings_flag = (True, False), gridsize=100)

    fig.suptitle("Time Distributions")
    fig.tight_layout()
    plt.show()
    plt.show()

    fig, axs = plt.subplots(1, 3, figsize=(14, 5))

    plotter.set_strategy(PlotCategoricalVsNumericalBox())
    plotter.plot(df, categorical_col="month", numerical_col="start_time", ax=axs[0], time_of_day_settings_flag = True, gridsize=100)
    plotter.plot(df, categorical_col="month", numerical_col="end_time", ax=axs[1], time_of_day_settings_flag = True, gridsize=100)
    plotter.plot(df, categorical_col="month", numerical_col="duration_minutes", ax=axs[2], time_of_day_settings_flag = True, gridsize=100)

    fig.suptitle("Time Distributions")
    fig.tight_layout()
    plt.show()

    fig, axs = plt.subplots(1, 3, figsize=(14, 5))

    plotter.set_strategy(PlotCategoricalVsNumericalBox())
    plotter.plot(df, categorical_col="day_of_week", numerical_col="start_time", ax=axs[0], time_of_day_settings_flag = True, gridsize=100)
    plotter.plot(df, categorical_col="day_of_week", numerical_col="end_time", ax=axs[1], time_of_day_settings_flag = True, gridsize=100)
    plotter.plot(df, categorical_col="day_of_week", numerical_col="duration_minutes", time_of_day_settings_flag = True, ax=axs[2], gridsize=100)

    fig.suptitle("Time Distributions")
    fig.tight_layout()
    plt.show()

def plot_univariate_plots(plotter: Plotter, df: pd.DataFrame):
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    plotter.set_strategy(PlotCategoricalDistribution())
    plotter.plot(df, column="month", ax=axs[0]) # Month plot
    plotter.plot(df, column="day_of_week", ax=axs[1]) # Weekday plot

    fig.suptitle("Categorical Distributions: Month and Day of Week")
    fig.tight_layout()

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    plotter.set_strategy(PlotNumericalDistribution(kde=True))
    plotter.plot(df, column="start_time", ax=axs[0], time_of_day_settings_flag=True)
    plotter.plot(df, column="end_time", ax=axs[1], time_of_day_settings_flag=True)
    plotter.plot(df, column="duration_minutes", bins=60, ax=axs[2])

    fig.suptitle("Time Distributions")
    fig.tight_layout()

    duration_hours = (df['end_datetime'] - df['start_datetime']).dt.total_seconds() / 3600
    df['average_power_kW'] = df['total_energy'] / duration_hours

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    plotter.plot(df, column="total_energy", ax=axs[0])
    plotter.plot(df, column="average_power_kW", ax=axs[1])
    axs[0].set_xlabel("Energy Demand (kWh)")
    plt.show()