# 1) NAME= NIKHIL KUMAR SHARMA
# ROLL-NO= 2501730349
# 2) NAME= PIYUSH KHARE
# ROLL-NO= 2501730244
# 3) NAME= MANISH PAL
# ROLL-NO= 2501730384
# 4) NAME= MANAS KUMAR
# ROLL-NO= 2501730275
#------#------#------#
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
import traceback
from PIL import Image

np.random.seed(42)

data_dir = Path("data")
output_dir = Path("output")
data_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)
if not any(data_dir.glob("*.csv")):
    buildings = ["BuildingA", "BuildingB", "BuildingC"]
    start_date = datetime(2025,1,1)
    hours = 28*24
    for b in buildings:
        timestamps = [start_date + timedelta(hours=i) for i in range(hours)]
        base = {"BuildingA":20,"BuildingB":35,"BuildingC":15}[b]
        hour_of_day = np.array([(ts.hour) for ts in timestamps])
        daily_pattern = 5 * np.sin((hour_of_day - 8) / 24 * 2 * np.pi) + 3 * np.where((hour_of_day>=18)&(hour_of_day<=21), 4, 0)
        kwh = base + daily_pattern + np.random.normal(0,2,size=len(timestamps))
        df = pd.DataFrame({"timestamp":timestamps, "kwh":np.round(kwh,3)})
        df.to_csv(data_dir / f"{b}_2025-01.csv", index=False)
    # small corrupt example to test error handling
    with open(data_dir / "BuildingD_bad.csv","w") as f:
        f.write("this,is,not,a,valid,csv\n1,2,3\n4,5\n")

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest")

# --- Task 1: Ingest ---
def ingest_csvs(data_folder: Path):
    csv_files = list(data_folder.glob("*.csv"))
    combined_rows = []
    logs = {"missing": [], "invalid": []}
    for csv in csv_files:
        try:
            try:
                df = pd.read_csv(csv, on_bad_lines='skip', parse_dates=["timestamp"])
            except TypeError:
                df = pd.read_csv(csv, error_bad_lines=False, parse_dates=["timestamp"])
            if "timestamp" not in df.columns or "kwh" not in df.columns:
                if df.shape[1] >= 2:
                    df = df.iloc[:, :2]
                    df.columns = ["timestamp", "kwh"]
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
                else:
                    raise ValueError("Insufficient columns")
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
            df["kwh"] = pd.to_numeric(df["kwh"], errors='coerce')
            df = df.dropna(subset=["timestamp","kwh"])
            building_name = csv.stem.split("_")[0] if "_" in csv.stem else csv.stem
            df["building"] = df.get("building", building_name)
            df["month"] = df["timestamp"].dt.to_period("M").astype(str)
            combined_rows.append(df)
            logger.info(f"Ingested {csv.name} ({len(df)} rows)")
        except FileNotFoundError:
            logs["missing"].append(str(csv))
            logger.error(f"File not found: {csv}")
        except Exception as e:
            logs["invalid"].append({"file": str(csv), "error": str(e)})
            logger.error(f"Failed to read {csv}: {e}\n{traceback.format_exc()}")
    if combined_rows:
        df_combined = pd.concat(combined_rows, ignore_index=True)
        df_combined = df_combined.sort_values(["building","timestamp"])
        return df_combined, logs
    else:
        return pd.DataFrame(), logs

df_combined, ingest_logs = ingest_csvs(data_dir)
cleaned_csv_path = output_dir / "cleaned_energy_data.csv"
df_combined.to_csv(cleaned_csv_path, index=False)

# --- Task 2: Aggregation functions ---
def calculate_daily_totals(df: pd.DataFrame):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    daily = df.groupby("building")["kwh"].resample("D").sum().reset_index()
    return daily

def calculate_weekly_aggregates(df: pd.DataFrame):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    weekly = df.groupby("building")["kwh"].resample("W").sum().reset_index()
    return weekly

def building_wise_summary(df: pd.DataFrame):
    grouped = df.groupby("building")["kwh"].agg(['mean','min','max','sum','std']).reset_index().rename(columns={
        'mean':'mean_kwh','min':'min_kwh','max':'max_kwh','sum':'total_kwh','std':'std_kwh'
    })
    return grouped

daily_totals = calculate_daily_totals(df_combined)
weekly_aggregates = calculate_weekly_aggregates(df_combined)
building_summary = building_wise_summary(df_combined)
building_summary.to_csv(output_dir / "building_summary.csv", index=False)

# --- Task 3: OOP Model ---
class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = pd.to_datetime(timestamp)
        self.kwh = float(kwh)

class Building:
    def __init__(self, name):
        self.name = name
        self.readings = []
    def add_reading(self, reading: MeterReading):
        self.readings.append(reading)
    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.readings)
    def generate_report(self):
        if not self.readings:
            return {"name":self.name,"count":0,"total":0}
        kwhs = [r.kwh for r in self.readings]
        times = [r.timestamp for r in self.readings]
        return {
            "name": self.name,
            "count": len(self.readings),
            "total": sum(kwhs),
            "mean": np.mean(kwhs),
            "min": np.min(kwhs),
            "max": np.max(kwhs),
            "first": min(times),
            "last": max(times)
        }

class BuildingManager:
    def __init__(self):
        self.buildings = {}
    def add_from_dataframe(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            bname = row["building"]
            if bname not in self.buildings:
                self.buildings[bname] = Building(bname)
            self.buildings[bname].add_reading(MeterReading(row["timestamp"], row["kwh"]))
    def get_reports(self):
        return {name: b.generate_report() for name,b in self.buildings.items()}

manager = BuildingManager()
manager.add_from_dataframe(df_combined)
reports = manager.get_reports()

# --- Task 4: Visuals (three separate plots, stitched to one image)
trend_path = output_dir / "trend_daily.png"
bar_path = output_dir / "bar_avg_weekly.png"
scatter_path = output_dir / "scatter_peak_hour.png"

# 1) Trend (daily)
fig1, ax1 = plt.subplots(figsize=(8,4))
for b in df_combined["building"].unique():
    sub = daily_totals[daily_totals["building"]==b]
    ax1.plot(sub["timestamp"], sub["kwh"], label=b)
ax1.set_title("Daily Consumption Trend (kWh)")
ax1.set_xlabel("Date")
ax1.set_ylabel("kWh")
ax1.legend()
fig1.tight_layout()
fig1.savefig(trend_path)
plt.close(fig1)

# 2) Bar chart (avg weekly)
fig2, ax2 = plt.subplots(figsize=(8,4))
avg_weekly = weekly_aggregates.groupby("building")["kwh"].mean().reset_index().sort_values("kwh",ascending=False)
ax2.bar(avg_weekly["building"], avg_weekly["kwh"])
ax2.set_title("Average Weekly Usage by Building")
ax2.set_xlabel("Building")
ax2.set_ylabel("Avg Weekly kWh")
fig2.tight_layout()
fig2.savefig(bar_path)
plt.close(fig2)

# 3) Scatter (hour-of-day totals)
df_combined["hour"] = pd.to_datetime(df_combined["timestamp"]).dt.hour
peaks = df_combined.groupby(["building","hour"])["kwh"].sum().reset_index()
fig3, ax3 = plt.subplots(figsize=(8,4))
for b in df_combined["building"].unique():
    sub = peaks[peaks["building"]==b]
    ax3.scatter(sub["hour"], sub["kwh"], s=20)
    peak_row = sub.loc[sub["kwh"].idxmax()]
    ax3.scatter([peak_row["hour"]], [peak_row["kwh"]], s=60)
ax3.set_title("Hourly Consumption by Building (sum over month)")
ax3.set_xlabel("Hour of day")
ax3.set_ylabel("Total kWh in month at that hour")
fig3.tight_layout()
fig3.savefig(scatter_path)
plt.close(fig3)

# Stitch images
imgs = [Image.open(p) for p in [trend_path, bar_path, scatter_path]]
w,h = imgs[0].size
canvas = Image.new('RGB', (w*2, h*2), (255,255,255))
canvas.paste(imgs[0], (0,0))
canvas.paste(imgs[1], (w,0))
canvas.paste(imgs[2], (0,h))
canvas.save(output_dir / "dashboard.png")

# --- Task 5: Export & summary
total_consumption = df_combined["kwh"].sum()
highest_building = building_summary.sort_values("total_kwh", ascending=False).iloc[0]["building"]
peak_row = df_combined.loc[df_combined["kwh"].idxmax()]
peak_time = pd.to_datetime(peak_row["timestamp"])
summary_lines = [
    f"Total campus consumption (kWh): {total_consumption:.2f}",
    f"Highest-consuming building: {highest_building}",
    f"Peak single reading: {peak_row['kwh']:.2f} kWh at {peak_time} in {peak_row['building']}",
    "",
    "Avg weekly kWh per building:"
]
for _, r in avg_weekly.iterrows():
    summary_lines.append(f" - {r['building']}: {r['kwh']:.2f}")

with open(output_dir / "summary.txt","w") as f:
    f.write("\n".join(summary_lines))

print("\n".join(summary_lines))
