python3 plot_mediterranean_january.pyimport argparse
import os
from datetime import datetime
import matplotlib.pyplot as plt
import xarray as xr


def mediterranean_region_shape():
    """Return an approximate Mediterranean Sea polygon as lon/lat tuples."""
    return [
        (-6.0, 30.0),  # Gibraltar / western entrance
        (36.0, 30.0),  # eastern Mediterranean near Suez
        (36.0, 45.0),  # eastern Mediterranean north edge
        (27.0, 44.0),  # Aegean Sea region
        (18.0, 44.5),  # Adriatic region
        (12.0, 44.0),  # Tyrrhenian Sea region
        (6.0, 42.0),   # western Mediterranean
        (0.0, 40.0),   # near Sardinia/Corsica
        (-6.0, 37.0),  # Gulf of Cadiz / Strait of Gibraltar
        (-6.0, 30.0),  # back to southern boundary
    ]


def first_of_month_time(ds):
    if "time" not in ds.coords:
        return ds
    first_of_month = ds.indexes["time"].to_period("M").to_timestamp()
    return ds.assign_coords(time=first_of_month)


def subset_mediterranean(ds):
    lat_min, lat_max = 30.0, 46.0
    lon_min, lon_max = -6.0, 36.0

    ds = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    return ds


def print_summary(ds):
    print("Dataset loaded successfully")
    print("---------------------------")
    print(ds)
    print("\nMediterranean shape (lon, lat) vertices:")
    for lon, lat in mediterranean_region_shape():
        print(f"- ({lon}, {lat})")

    print("\nSubset dimensions:")
    for dim, size in ds.dims.items():
        print(f"- {dim}: {size}")

    if "time" in ds.coords:
        times = ds["time"].values
        print("\nTime coordinate after first-of-month adjustment:")
        for t in times:
            print(f"- {t}")

    if "analysed_sst" in ds.data_vars:
        print("\nTemperature variable: analysed_sst")
        print(f"Units: {ds.analysed_sst.attrs.get('units', 'unknown')}")
        print(f"Range: {ds.analysed_sst.min().item():.2f} to {ds.analysed_sst.max().item():.2f}")


def save_to_csv(ds, output_file):
    df = ds["analysed_sst"].to_dataframe().reset_index()
    df = df[["time", "lat", "lon", "analysed_sst"]]
    df.to_csv(output_file, index=False)
    print(f"\nSaved Mediterranean CSV subset to: {output_file}")


def save_map(ds, output_image):
    if "analysed_sst" not in ds.data_vars:
        raise ValueError("Dataset does not contain analysed_sst")

    sst = ds["analysed_sst"].isel(time=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = sst.plot.pcolormesh(
        ax=ax,
        x="lon",
        y="lat",
        cmap="viridis",
        add_colorbar=True,
        cbar_kwargs={"label": f"{ds.analysed_sst.attrs.get('units', 'unknown')}"},
    )

    lon_pts, lat_pts = zip(*mediterranean_region_shape())
    ax.plot(lon_pts, lat_pts, color="red", linewidth=1.5, label="Mediterranean region")
    ax.set_title("Mediterranean Sea Surface Temperature")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(output_image, dpi=150)
    plt.close(fig)
    print(f"\nSaved Mediterranean map image to: {output_image}")


def main():
    parser = argparse.ArgumentParser(
        description="Read a NetCDF SST file, subset to the Mediterranean Sea, and align dates to the first of each month."
    )
    parser.add_argument("file", help="Path to the .nc file or glob pattern")
    parser.add_argument("--output", help="Optional output file for the Mediterranean subset (.nc or .csv)")
    args = parser.parse_args()

    if any(ch in args.file for ch in "*?["):
        ds = xr.open_mfdataset(args.file, combine="by_coords")
    else:
        ds = xr.open_dataset(args.file)

    ds = first_of_month_time(ds)
    med_ds = subset_mediterranean(ds)

    print_summary(med_ds)

    if args.output:
        if args.output.lower().endswith(".csv"):
            save_to_csv(med_ds, args.output)
            png_output = os.path.splitext(args.output)[0] + ".png"
            save_map(med_ds, png_output)
        elif args.output.lower().endswith(".png"):
            save_map(med_ds, args.output)
        else:
            med_ds.to_netcdf(args.output)
            print(f"\nSaved Mediterranean subset to: {args.output}")


if __name__ == "__main__":
    main()
