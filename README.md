

# Energy Measurements Data Pipeline

This project implements a Python-based data pipeline for cleansing and transforming raw energy measurement data from CSV files. The pipeline is containerized with Docker and integrated with **Apache NiFi**, which monitors a directory for incoming files, processes them using the defined Python logic, and outputs transformed data into CSV format.

---

## 📦 Project Structure



.
├── Dockerfile
├── pipeline.py
├── requirements.txt
├── input/                             # Directory monitored by NiFi for raw CSV files
│   └── measurements\_coding\_challenge.csv
├── output/                            # Directory where transformed CSV files are stored
│   ├── cleaned\_measurements.csv
│   ├── hourly\_grid\_totals\_with\_peak\_flag.csv
│   └── summary\_by\_serial.csv
├── nifi/                              # NiFi flow configuration and bootstrap files
└── README.md



---

## 🧰 Features

1. **Load CSV Data**
   - Automatically read raw data from CSV files (semicolon `;` delimited).
   
2. **Clean and Transform**
   - Converts energy-related columns to numeric types, handling errors.
   - Converts date and timestamp columns to proper datetime types.
   - Removes duplicates and fully empty energy rows.

3. **Analysis**
   - Aggregates total `grid_purchase` and `grid_feedin` per hour of each day.
   - Flags the hour of the day with the highest `grid_feedin` as `True`.
   - Aggregates energy data per serial number.

4. **Containerized Environment**
   - Python application and Apache NiFi run within a single Docker container.
   - NiFi listens to a mounted input directory and triggers processing.

---

## 🐍 Python Data Pipeline Logic (`pipeline.py`)

```python
import pandas as pd

# Load CSV
df = pd.read_csv("input/measurements_coding_challenge.csv", sep=';')

# Convert to numeric
def convert_to_numeric(column):
    return pd.to_numeric(column, errors='coerce')

df['grid_purchase'] = convert_to_numeric(df['grid_purchase'])
df['grid_feedin'] = convert_to_numeric(df['grid_feedin'])
df['direct_consumption'] = convert_to_numeric(df['direct_consumption'])

# Convert datetime fields
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

# Drop duplicates and empty rows
df = df.drop_duplicates()
df.dropna(subset=['grid_purchase', 'grid_feedin', 'direct_consumption'], how='all', inplace=True)

# Hourly calculations
df["hour"] = df["timestamp"].dt.hour
hourly_totals = df.groupby(["date", "hour"], as_index=False)[["grid_purchase", "grid_feedin"]].sum()
hourly_totals["is_peak_feed_in_hour"] = hourly_totals.groupby("date")["grid_feedin"].transform(lambda x: x == x.max())

# Serial summary
summary = df.groupby('serial')[['grid_purchase', 'grid_feedin']].sum().sort_values(by='grid_purchase', ascending=False)

# Save outputs
df.to_csv("output/cleaned_measurements.csv", index=False)
hourly_totals.to_csv("output/hourly_grid_totals_with_peak_flag.csv", index=False)
summary.to_csv("output/summary_by_serial.csv")
````

---

## 🐳 Docker Setup

### Dockerfile

```Dockerfile
FROM python:3.10-slim

# Install Java (required for NiFi)
RUN apt-get update && apt-get install -y openjdk-11-jdk wget unzip && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install Apache NiFi
RUN wget https://archive.apache.org/dist/nifi/1.23.2/nifi-1.23.2-bin.zip && \
    unzip nifi-1.23.2-bin.zip && mv nifi-1.23.2 /opt/nifi && rm nifi-1.23.2-bin.zip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app
WORKDIR /app

# Entry point (Python pipeline + start NiFi)
CMD ["bash", "-c", "/opt/nifi/bin/nifi.sh start && sleep 10 && python3 pipeline.py && tail -f /dev/null"]
```

---

## 🏗️ Build and Run

### Step 1: Build Docker Image

```bash
docker build -t energy-pipeline:latest .
```

### Step 2: Run Docker Container

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output energy-pipeline:latest
```

---

## ✅ Output Files

* `output/cleaned_measurements.csv`: Cleaned and type-corrected dataset.
* `output/hourly_grid_totals_with_peak_flag.csv`: Hour-by-hour aggregation with peak indicators.
* `output/summary_by_serial.csv`: Energy summary by battery serial number.

---

## 🔁 NiFi Flow (High-level Overview)

* **Input Directory Monitoring**: NiFi watches `/app/input/` for new CSV files.
* **Trigger Python Pipeline**: When files arrive, a shell command is executed to run the `pipeline.py`.
* **Store Outputs**: Transformed files are saved into `/app/output/`.

> A minimal NiFi flow can be implemented using:
>
> * `GetFile` processor → `ExecuteStreamCommand` (runs `python pipeline.py`) → `PutFile`

---

## 🗂️ Requirements

* Docker Engine
* Git (to clone this repository)

---

## 🌐 Deployment

To deploy to production or share with others, push your code to a GitHub repository and share the public URL.

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/energy-pipeline.git
git push -u origin main
```

---

## 📬 Contact

For questions, feel free to open an issue or contact the repository maintainer.

```

Let me know if you want the `nifi` processor templates or flow configuration files added to this documentation too!
```
