from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "hour.csv"
OUTPUT_DIR = ROOT / "output"
IMAGE_DIR = ROOT / "images"

SEASONS = {1: "Winter", 2: "Spring", 3: "Summer", 4: "Fall"}
WEATHER = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Weather"}
WEEKDAYS = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGE_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH, parse_dates=["dteday"])
    required = {"instant", "dteday", "season", "hr", "workingday", "weathersit", "casual", "registered", "cnt"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["instant"].duplicated().any():
        raise ValueError("Duplicate instant values detected")
    if not (df["casual"] + df["registered"]).eq(df["cnt"]).all():
        raise ValueError("Rental total does not match casual + registered")

    clean = df.copy()
    clean["season_name"] = clean["season"].map(SEASONS)
    clean["weather_name"] = clean["weathersit"].map(WEATHER)
    clean["weekday_name"] = clean["weekday"].map(WEEKDAYS)
    clean["day_type"] = clean["workingday"].map({1: "Working Day", 0: "Weekend/Holiday"})
    clean["datetime"] = clean["dteday"] + pd.to_timedelta(clean["hr"], unit="h")
    clean.to_csv(OUTPUT_DIR / "bike_hourly_clean.csv", index=False)

    hourly = (
        clean.groupby("hr", as_index=False)
        .agg(avg_rentals=("cnt", "mean"), avg_casual=("casual", "mean"), avg_registered=("registered", "mean"))
    )
    hourly.to_csv(OUTPUT_DIR / "hourly_demand.csv", index=False)

    seasonal = (
        clean.groupby("season_name", as_index=False)
        .agg(total_rentals=("cnt", "sum"), avg_hourly_rentals=("cnt", "mean"))
        .sort_values("avg_hourly_rentals", ascending=False)
    )
    seasonal.to_csv(OUTPUT_DIR / "seasonal_demand.csv", index=False)

    weather = (
        clean.groupby("weather_name", as_index=False)
        .agg(total_rentals=("cnt", "sum"), avg_hourly_rentals=("cnt", "mean"), observations=("cnt", "size"))
        .sort_values("avg_hourly_rentals", ascending=False)
    )
    weather.to_csv(OUTPUT_DIR / "weather_demand.csv", index=False)

    day_type = (
        clean.groupby("day_type", as_index=False)
        .agg(total_rentals=("cnt", "sum"), avg_hourly_rentals=("cnt", "mean"), registered_share=("registered", "sum"))
    )
    day_type["registered_share"] = day_type["registered_share"] / day_type["total_rentals"]
    day_type.to_csv(OUTPUT_DIR / "day_type_summary.csv", index=False)

    peak_hour = int(hourly.loc[hourly["avg_rentals"].idxmax(), "hr"])
    peak_season = str(seasonal.iloc[0]["season_name"])
    clear_avg = float(weather.loc[weather["weather_name"] == "Clear", "avg_hourly_rentals"].iloc[0])
    bad_weather_avg = float(weather.iloc[-1]["avg_hourly_rentals"])
    summary_lines = [
        f"Rows analyzed: {len(clean):,}",
        f"Total rentals: {clean['cnt'].sum():,}",
        f"Peak average demand hour: {peak_hour:02d}:00",
        f"Highest average demand season: {peak_season}",
        f"Average hourly rentals in clear weather: {clear_avg:.1f}",
        f"Average hourly rentals in the lowest-demand weather group: {bad_weather_avg:.1f}",
    ]
    (OUTPUT_DIR / "analysis_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle("Bike Sharing Demand Analysis", fontsize=16, fontweight="bold")

    axes[0, 0].plot(hourly["hr"], hourly["avg_rentals"], color="#1565C0", linewidth=2)
    axes[0, 0].set_title("Average Rentals by Hour")
    axes[0, 0].set_xlabel("Hour")
    axes[0, 0].set_ylabel("Average rentals")
    axes[0, 0].set_xticks(range(0, 24, 3))

    axes[0, 1].bar(seasonal["season_name"], seasonal["avg_hourly_rentals"], color="#00897B")
    axes[0, 1].set_title("Average Demand by Season")
    axes[0, 1].set_ylabel("Average rentals")

    weather_plot = weather.sort_values("avg_hourly_rentals")
    axes[1, 0].barh(weather_plot["weather_name"], weather_plot["avg_hourly_rentals"], color="#EF6C00")
    axes[1, 0].set_title("Average Demand by Weather")
    axes[1, 0].set_xlabel("Average rentals")

    axes[1, 1].bar(day_type["day_type"], day_type["avg_hourly_rentals"], color=["#6A1B9A", "#5E35B1"])
    axes[1, 1].set_title("Average Demand by Day Type")
    axes[1, 1].set_ylabel("Average rentals")

    for ax in axes.flat:
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(IMAGE_DIR / "dashboard_preview.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print("Bike sharing analysis completed.")


if __name__ == "__main__":
    main()
