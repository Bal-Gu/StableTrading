import binance
import pandas as pd

# Set up API credentials
API_KEY = "9BeObihj4KEHN2BcDp3JniESBRqP6bUKYFAqQXy3SOAxGnjkUHt71obMCQKTWW9B"
SECRET_KEY = "mb5AW9oYtJZ2CN7Y2WfUlJOsYe24sPOPslESr1UGq0ZSarYbSfyG1SCDohKsLrRl"

# Connect to Binance API
client = binance.Client(API_KEY, SECRET_KEY)

# Define the duration and interval for the historical data
duration = 90 * 24 * 60  # 3 months in minutes
interval = binance.Client.KLINE_INTERVAL_1MINUTE

# Empty list to store the historical candlestick data
historical_data = []

# Fetch historical data iteratively
start_time = None
while duration > 0:
    # Adjust the limit to fetch a maximum of 500 candles per call

    # Fetch the candlestick data
    klines = client.get_historical_klines("TUSDUSDT", interval, end_str=start_time, limit=500)

    # Extract the relevant data from the API response
    data = [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in klines]

    # Append the data to the historical_data list
    historical_data.extend(data)

    # Update the start_time and duration for the next API call
    start_time = str(data[0][0] - 600000)
    duration -= 500
    print(duration)

# Create a DataFrame from the historical_data list
columns = ["timestamp", "open", "high", "low", "close", "volume"]
df = pd.DataFrame(historical_data, columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to datetime

# Display the DataFrame
print(df.head())
df.to_csv("../Data/tusdusdt.csv")
