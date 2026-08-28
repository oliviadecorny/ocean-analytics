import argparse
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


SOURCE_DIR = Path("data_med")
C_TEMP_MIN = 0.0
C_TEMP_MAX = 35.0
K_TEMP_MIN = C_TEMP_MIN + 273.15
K_TEMP_MAX = C_TEMP_MAX + 273.15


def celsius_from_kelvin(kelvin: float) -> float:
    return kelvin - 273.15


def format_temperature_tick(value, _pos):
    return f"{value:.0f} °C\n{value + 273.15:.0f} K"


def plot_one_frame(df: pd.DataFrame, output_path: Path):
    if df.empty:
        raise ValueError("Input dataframe is empty")

    df = df.copy()
    df["temperature"] = df["temperature"].apply(celsius_from_kelvin)
    pivot = df.pivot(index="lat", columns="lon", values="temperature").sort_index(ascending=False)

    lon = pivot.columns.to_numpy(dtype=float)
    lat = pivot.index.to_numpy(dtype=float)
    temp = pivot.to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(10, 7))
    mesh = ax.pcolormesh(
        lon,
        lat,
        temp,
        shading="auto",
        cmap="viridis",
        vmin=C_TEMP_MIN,
        vmax=C_TEMP_MAX,
    )

    timestamp = pd.to_datetime(df["time"].iloc[0])
    date_label = timestamp.strftime("%Y-%m-%d")
    ax.set_title(f"Mediterranean Sea Surface Temperature\n{date_label}")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_xlim(lon.min(), lon.max())
    ax.set_ylim(lat.min(), lat.max())

    cbar = fig.colorbar(mesh, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Temperature (°C / K)")
    cbar.set_ticks(np.linspace(C_TEMP_MIN, C_TEMP_MAX, 5))
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(format_temperature_tick))

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def create_gif(image_paths, gif_path: Path):
    frames = [Image.open(path).convert("RGB") for path in image_paths]
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=700,
        loop=0,
    )
    print(f"Created GIF: {gif_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Create individual SST plots for a selected Mediterranean month and combine them into a GIF."
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=str(SOURCE_DIR),
        help="Directory containing monthly Mediterranean CSV exports.",
    )
    parser.add_argument(
        "--month",
        default="01",
        help="Month number to plot, e.g. 01 for January or 08 for August.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    image_dir = Path(f"data_med_images_{args.month}")
    gif_path = Path(f"data_med_{args.month}.gif")
    image_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(source_dir.glob(f"*_{args.month}_med.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No {args.month} Mediterranean CSV files found in {source_dir}")

    frames = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        output_image = image_dir / f"{csv_file.stem}.png"
        plot_one_frame(df, output_image)
        frames.append(output_image)
        print(f"Created image: {output_image}")

    create_gif(frames, gif_path)


if __name__ == "__main__":
    main()
