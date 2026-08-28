import argparse
from pathlib import Path
import xarray as xr
import pandas as pd

# Mediterranean region boundaries
LAT_MIN = 30.0
LAT_MAX = 46.0
LON_MIN = -6.0
LON_MAX = 36.0
OUTPUT_DIR = Path("data_med")
DEFAULT_MONTHS = {"01", "07"}


def subset_mediterranean(ds: xr.Dataset) -> xr.Dataset:
    subset = ds.sel(lat=slice(LAT_MIN, LAT_MAX), lon=slice(LON_MIN, LON_MAX))
    subset = subset.where(subset["mask"] == 1, drop=True)
    return subset


def first_of_month_time(ds: xr.Dataset) -> xr.Dataset:
    if "time" not in ds.coords:
        return ds
    first_ts = ds.indexes["time"].to_period("M").to_timestamp()
    return ds.assign_coords(time=first_ts)


def export_monthly_file(input_path: Path, months_to_export: set[str]) -> None:
    filename = input_path.stem
    year = filename[:4]
    month = filename[4:6]

    if month not in months_to_export:
        return

    ds = xr.open_dataset(input_path)
    ds = first_of_month_time(ds)
    med = subset_mediterranean(ds)

    if "analysed_sst" not in med.data_vars:
        raise ValueError(f"No analysed_sst variable found in {input_path}")

    df = med["analysed_sst"].to_dataframe().reset_index()
    df = df[["time", "lat", "lon", "analysed_sst"]].rename(columns={"analysed_sst": "temperature"})

    output_file = OUTPUT_DIR / f"{year}_{month}_med.csv"
    df.to_csv(output_file, index=False)
    print(f"Exported {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Export Mediterranean SST monthly subsets for a selected set of months to CSV files."
    )
    parser.add_argument(
        "data_dir",
        nargs="?",
        default="data",
        help="Directory containing the monthly NetCDF files.",
    )
    parser.add_argument(
        "--months",
        nargs="*",
        default=["01", "07"],
        help="Month numbers to export, e.g. 01 07 08.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir)
    months_to_export = set(args.months)

    for nc_file in sorted(data_dir.glob("*.nc")):
        export_monthly_file(nc_file, months_to_export)


if __name__ == "__main__":
    main()
