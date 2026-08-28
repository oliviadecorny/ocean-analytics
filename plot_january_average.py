import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


SOURCE_DIR = Path("data_med")
MONTH_COLORS = {
    "01": "tab:blue",
    "07": "tab:orange",
}


def main():
    parser = argparse.ArgumentParser(
        description="Plot the average Mediterranean temperature per year for one or more selected months with annotated date and temperature values."
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=str(SOURCE_DIR),
        help="Directory containing Mediterranean monthly CSV files.",
    )
    parser.add_argument(
        "--months",
        nargs="+",
        default=["01", "07"],
        help="Month numbers to plot together, e.g. 01 07.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    all_records = []

    for month in args.months:
        month_files = sorted(source_dir.glob(f"*_{month}_med.csv"))
        if not month_files:
            raise FileNotFoundError(f"No {month} Mediterranean CSV files found in {source_dir}")

        records = []
        for csv_file in month_files:
            df = pd.read_csv(csv_file)
            if df.empty:
                continue

            df["temperature_c"] = df["temperature"] - 273.15
            avg_temp = df["temperature_c"].mean()
            year = pd.to_datetime(df["time"].iloc[0]).year

            records.append({"month": month, "year": year, "temperature_c": round(avg_temp, 2)})

        all_records.extend(records)

    summary_df = pd.DataFrame(all_records).sort_values(["month", "year"])
    output_image = Path("january_july_average_temperature.png")
    output_csv = Path("january_july_average_temperature.csv")
    summary_df.to_csv(output_csv, index=False)

    fig, ax = plt.subplots(figsize=(12, 7))

    for month in args.months:
        month_df = summary_df[summary_df["month"] == month].copy()
        color = MONTH_COLORS.get(month, "tab:gray")
        ax.plot(
            month_df["year"],
            month_df["temperature_c"],
            marker="o",
            linewidth=2,
            color=color,
            label=f"{month}",
        )

        for _, row in month_df.iterrows():
            ax.annotate(
                f"{row['year']}\n{row['temperature_c']:.1f} °C",
                (row["year"], row["temperature_c"]),
                textcoords="offset points",
                xytext=(6, 6),
                fontsize=8,
                color=color,
            )

    ax.set_title("Average Mediterranean January and July Temperature by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Temperature (°C)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(title="Month")
    ax.set_ylim(min(summary_df["temperature_c"]) - 1, max(summary_df["temperature_c"]) + 1)
    fig.tight_layout()
    fig.savefig(output_image, dpi=150)
    plt.close(fig)

    print(f"Created summary CSV: {output_csv}")
    print(f"Created chart: {output_image}")


if __name__ == "__main__":
    main()
