import pandas as pd

# Read the CSV file with semicolon as separator
df = pd.read_csv("measurements_coding_challenge.csv", sep=';')

# Convert columns to appropriate data types
def convert_to_numeric(column):
    return pd.to_numeric(column, errors='coerce')

df['grid_purchase'] = convert_to_numeric(df['grid_purchase'])
df['grid_feedin'] = convert_to_numeric(df['grid_feedin'])
df['direct_consumption'] = convert_to_numeric(df['direct_consumption'])

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Convert 'date' column to datetime.date
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

# drop duplicates in data
df = df.drop_duplicates()

# drop rows with completely missing energy data
df.dropna(subset=['grid_purchase', 'grid_feedin', 'direct_consumption'], how='all', inplace=True)

# Extract hour from timestamp
df["hour"] = df["timestamp"].dt.hour

# Group by date and hour to calculate total grid_purchase and grid_feedin
hourly_totals = df.groupby(["date", "hour"], as_index=False)[["grid_purchase", "grid_feedin"]].sum()

# Identify the hour with the highest grid_feedin for each day
hourly_totals["is_peak_feed_in_hour"] = hourly_totals.groupby("date")["grid_feedin"].transform(lambda x: x == x.max())

# Total grid purchase and feed-in per serial number
summary = df.groupby('serial')[['grid_purchase', 'grid_feedin']].sum().sort_values(by='grid_purchase', ascending=False)

# Save cleaned data and summary
df.to_csv("cleaned_measurements.csv", index=False)
hourly_totals.to_csv("hourly_grid_totals_with_peak_flag.csv", index=False)
summary.to_csv("summary_by_serial.csv")
