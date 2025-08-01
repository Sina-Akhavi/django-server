import joblib
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import pandas.plotting


# --- Configuration ---
MODEL_FILENAME = 'arima_model.pkl'
CSV_FILENAME = 'BTC-USD.csv'
HISTORICAL_DAYS_TO_SHOW_IN_PLOT_SLICE = 30 # Number of historical days for the second plot slice
STEPS_TO_FORECAST = 7         # Number of future days to forecast (a week)
# ---------------------


def load_model(filename: str):
    """Loads a saved ARIMA model from a file."""
    loaded_model = None
    try:
        loaded_model = joblib.load(filename)
        print(f"Model '{filename}' loaded successfully.")
    except FileNotFoundError:
        print(f"Error: Model file '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred during model loading: {e}")
    return loaded_model


def load_and_prepare_historical_data(filename: str):
    """
    Loads ALL historical data from CSV, prepares it (skips rows, parses dates,
    converts 'Close' to numeric, handles NaNs), and returns the full DataFrame
    containing only the 'Close' column.
    """
    loaded_df = pd.DataFrame()
    try:
        print(f"Attempting to read CSV: {filename}...")
        # Corrected read_csv with skiprows as a list and header=0
        loaded_df = pd.read_csv(
            filename,
            skiprows=[1, 2],    # Skip row indices 1 and 2 (Lines 2 and 3 based on your CSV structure)
            header=0,           # Use the first row (index 0, Line 1) as the header
            index_col=0,        # Use the first column (Date) as index from the data rows
            parse_dates=True,   # Tell pandas to parse the index as dates
            date_format='%Y-%m-%d' # Specify the expected date format
        )
        print("CSV read successfully.")

        # Explicitly convert the index to DatetimeIndex and handle errors
        original_index_name = loaded_df.index.name if loaded_df.index.name is not None else 'Date'
        loaded_df.index = pd.to_datetime(loaded_df.index, errors='coerce')
        loaded_df.index.name = original_index_name

        if loaded_df.index.isna().any():
            print(f"Warning: Found {loaded_df.index.isna().sum()} unparseable date values in the index. Rows with NaT index will be dropped.")
            loaded_df = loaded_df.dropna(axis=0, subset=[loaded_df.index.name])


        # Ensure the 'Close' column exists and is numeric, handle errors
        if 'Close' in loaded_df.columns:
            loaded_df['Close'] = pd.to_numeric(loaded_df['Close'], errors='coerce')
            if loaded_df['Close'].isna().any():
                print(f"Warning: Found {loaded_df['Close'].isna().sum()} non-numeric values in 'Close' column after conversion. Rows with NaN will be dropped.")
                loaded_df = loaded_df.dropna(axis=0, subset=['Close'])
        else:
            print("Error: 'Close' column not found in the CSV after skipping rows. Check header row or CSV structure.")
            return pd.DataFrame() # Return empty if 'Close' is missing

        # Return only the 'Close' column as a DataFrame
        if not loaded_df.empty:
            loaded_df = loaded_df[['Close']]
            return loaded_df[:2146]
        else:
             print("Loaded DataFrame is empty after preparation.")
             return pd.DataFrame()


    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred during historical data loading/preparation: {e}.")

    return pd.DataFrame() # Return empty DataFrame if any error occurred


def generate_and_prepare_forecast(model, steps: int, full_historical_df: pd.DataFrame):
    """
    Generates a forecast using the loaded model and prepares it as a
    Pandas Series with a DatetimeIndex based on the FULL historical data.
    Requires the model and a non-empty historical DataFrame.
    """
    future_forecast_series = pd.Series(dtype=float) # Initialize as empty Series

    if model is None:
        print("Model not loaded. Cannot generate forecast.")
        return future_forecast_series
    if full_historical_df.empty:
        print("Historical data is empty. Cannot generate forecast index.")
        return future_forecast_series

    try:
        forecast_output = model.forecast(steps=steps)
        print(f"Generated forecast for the next {steps} steps.")

        # --- Convert forecast output to a Pandas Series with a DatetimeIndex ---
        if isinstance(forecast_output, np.ndarray):
             print("Forecast output is NumPy array. Creating Series with DatetimeIndex.")
             # Get necessary info from historical data to create the forecast index
             last_hist_date = full_historical_df.index.max() # Use max date of the full data
             freq = pd.infer_freq(full_historical_df.index) # Infer frequency (e.g., 'D' for daily)

             if freq:
                 # Create a DatetimeIndex starting *after* the last historical date
                 forecast_index = pd.date_range(start=last_hist_date, periods=steps + 1, freq=freq)[1:]
                 # Ensure forecast_output is 1D if needed
                 future_forecast_series = pd.Series(forecast_output.flatten(), index=forecast_index)
             else:
                 print("Could not infer frequency from full historical data index. Cannot create DatetimeIndex for forecast array. Forecast will not be plotted.")
        elif isinstance(forecast_output, pd.Series):
            print("Forecast output is Pandas Series.")
            future_forecast_series = forecast_output # Use the Series directly (it should already have an index)
            # Ensure forecast index frequency is set if possible (useful for plotting)
            if future_forecast_series.index.freq is None and not future_forecast_series.empty:
                 future_forecast_series.index.freq = pd.infer_freq(future_forecast_series.index)

        else:
             print(f"Unexpected forecast output type from model.forecast(): {type(forecast_output)}. Cannot plot forecast.")

    except Exception as e:
        print(f"An error occurred during forecast preparation: {e}.")

    return future_forecast_series


def plot_data_with_forecast(historical_df_to_plot: pd.DataFrame, forecast_series: pd.Series, historical_label: str, forecast_steps: int, plot_title: str):
    """
    Plots the specified historical data DataFrame and the future forecast on the same graph.
    """
    # Only plot if there is historical data to show OR forecast data available
    if not historical_df_to_plot.empty or not forecast_series.empty:
        plt.figure(figsize=(15, 7))
        ax = plt.gca() # Get the current axes

        # Plot historical data
        if not historical_df_to_plot.empty:
            ax.plot(historical_df_to_plot.index, historical_df_to_plot['Close'], label=historical_label, color='blue')
            # Add a vertical line at the end of historical data slice
            if len(historical_df_to_plot.index) > 0:
                 last_hist_date_plot = historical_df_to_plot.index.max() # Use max date of the plotted slice
                 ax.axvline(last_hist_date_plot, color='gray', linestyle='--', alpha=0.7, label='End of Historical Data')


        # Plot forecast data - Pandas will align by date index automatically
        if not forecast_series.empty:
             ax.plot(forecast_series.index, forecast_series, label=f'Forecast ({forecast_steps} steps)', color='red', linestyle='--')

        # --- Customize Plot ---
        plt.title(plot_title) # Use the passed title
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        ax.legend() # Show legend for plotted series
        ax.grid(True)

        # --- Adjust Y-axis limits to fit both historical and forecast ---
        all_values_for_ylim = pd.Series(dtype=float) # Initialize an empty Series to combine data for limits
        if not historical_df_to_plot.empty:
            all_values_for_ylim = pd.concat([all_values_for_ylim, historical_df_to_plot['Close']])
        if not forecast_series.empty:
             all_values_for_ylim = pd.concat([all_values_for_ylim, forecast_series])


        if not all_values_for_ylim.empty:
             try:
                 min_price = all_values_for_ylim.min()
                 max_price = all_values_for_ylim.max()
                 price_range = max_price - min_price
                 # Add buffer, handle case where price_range is 0 (e.g., flat data or single point)
                 buffer = price_range * 0.05 if price_range > 0 else (1 if not historical_df_to_plot.empty or not forecast_series.empty else 0)

                 # Check if min/max are finite before setting limits
                 if np.isfinite(min_price) and np.isfinite(max_price):
                      lower_limit = min_price - buffer
                      upper_limit = max_price + buffer
                       # A small safety margin if limits are too close
                      if (upper_limit - lower_limit < 1) and (not historical_df_to_plot.empty or not forecast_series.empty):
                           avg_price = all_values_for_ylim.mean()
                           lower_limit = avg_price - 50
                           upper_limit = avg_price + 50
                           # Ensure limits are still valid if avg_price was NaN/Inf
                           if not np.isfinite(lower_limit) or not np.isfinite(upper_limit):
                               lower_limit = min_price * 0.95
                               upper_limit = max_price * 1.05


                      ax.set_ylim(lower_limit, upper_limit)

                 else:
                      print("Could not determine suitable y-axis limits due to non-finite values in combined data.")

             except Exception as e:
                 print(f"Could not auto-adjust y-axis limits: {e}")


        # --- Show Plot ---
        plt.show()

    else:
        print("No historical data to plot or forecast available.")


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load Model
    loaded_model = load_model(MODEL_FILENAME)

    # 2. Load and Prepare ALL Historical Data
    # This data is used by the model for forecasting and to anchor the forecast index
    full_hist_data = load_and_prepare_historical_data(CSV_FILENAME)

    # 3. Generate and Prepare Forecast (only if model and full historical data loaded)
    future_forecast = pd.Series(dtype=float) # Initialize as empty
    if loaded_model is not None and not full_hist_data.empty:
        # Pass the FULL historical data and the desired steps (7 for a week)
        future_forecast = generate_and_prepare_forecast(loaded_model, STEPS_TO_FORECAST, full_hist_data)
        # future_forecast will be an empty Series if forecast generation/prep failed

    # --- 4. Plot Results ---

    # Plot 1: Full Historical Data + Forecast
    # Only plot if full historical data OR forecast is available
    if not full_hist_data.empty or not future_forecast.empty:
        print("\nPlotting Full Historical Data and Forecast...")
        # We pass the full_hist_data DataFrame directly to the plotting function
        plot_data_with_forecast(
            historical_df_to_plot=full_hist_data,
            forecast_series=future_forecast,
            historical_label=f'Full Historical Price ({len(full_hist_data)} days)', # Label indicates full data
            forecast_steps=STEPS_TO_FORECAST,
            plot_title='Bitcoin Close Price: Full History and 7-Day Forecast' # Title for the full plot
        )
    else:
        print("\nCannot plot Full Historical Data and Forecast: No data available.")


    # Plot 2: Last 30 Days of Historical Data + Forecast
    # Only plot if full historical data OR forecast is available
    if not full_hist_data.empty or not future_forecast.empty:
        print("\nPlotting Last 30 Days of Historical Data and Forecast...")
        # Slice the last N days from the full historical data for this specific plot
        historical_data_slice_for_plot = pd.DataFrame()
        if not full_hist_data.empty:
             days_to_show = HISTORICAL_DAYS_TO_SHOW_IN_PLOT_SLICE
             if days_to_show > len(full_hist_data):
                  print(f"Warning: Only {len(full_hist_data)} historical days available, less than requested {days_to_show}. Plotting all available historical data in the second plot.")
                  days_to_show = len(full_hist_data)

             # Use iloc[-days_to_show:] to get the last N rows
             historical_data_slice_for_plot = full_hist_data.iloc[-days_to_show:]


        # We pass the sliced historical_data_slice_for_plot DataFrame to the plotting function
        plot_data_with_forecast(
            historical_df_to_plot=historical_data_slice_for_plot,
            forecast_series=future_forecast,
            historical_label=f'Historical Price (Last {len(historical_data_slice_for_plot)} days)', # Label indicates slice
            forecast_steps=STEPS_TO_FORECAST,
            plot_title=f'Bitcoin Close Price: Last {len(historical_data_slice_for_plot)} Days History and {STEPS_TO_FORECAST}-Day Forecast' # Title for the sliced plot
        )
    else:
         print("\nCannot plot Last 30 Days and Forecast: No data available.")
         