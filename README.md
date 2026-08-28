# Mediterranean Sea Surface Temperature Analysis

This project processes monthly sea surface temperature (SST) data and extracts a consistent Mediterranean Sea region for spatial and time-series analysis. It uses the ESA Climate Change Initiative / GHRSST OSTIA NetCDF files stored in `data/` to produce filtered CSV datasets, temperature maps, animated monthly visualizations, and yearly average-temperature summaries.

## Objective

The project is intended to:

- isolate SST observations for the Mediterranean region;
- normalize monthly timestamps to the first day of each month;
- convert temperatures from Kelvin to Celsius for analysis and presentation;
- visualize the spatial distribution of SST;
- compare annual average temperatures for selected months, including January, July, and August.

The geographic extraction window is approximately 30-46°N and 6°W-36°E. The export workflow also applies the source dataset's `mask` variable so that masked or non-sea grid cells are excluded.

## Data

Input files are monthly NetCDF files in `data/`, named in the form:

```text
YYYYMM-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_ICDR3.0-v02.0-fv01.0.nc
```

The code expects these files to contain:

- `analysed_sst`: the analysed sea surface temperature variable;
- `time`, `lat`, and `lon` coordinates;
- `mask`: a sea/region mask used during Mediterranean export.

The included dataset contains 120 monthly NetCDF files. The analysis is based on the files currently present in this repository; it is not a live connection to an external data service.

## Libraries

The Python workflow uses:

- **xarray** to open and subset NetCDF datasets;
- **pandas** to reshape tabular data, calculate averages, and write CSV files;
- **NumPy** for numeric arrays and colorbar tick values;
- **Matplotlib** to create SST maps and time-series charts;
- **Pillow** to combine rendered map images into animated GIFs;
- **argparse**, **pathlib**, **os**, and **datetime** from the Python standard library for command-line options, paths, and dates.

Install the third-party dependencies with:

```bash
python3 -m pip install xarray pandas numpy matplotlib pillow netCDF4
```

`netCDF4` provides a common backend for reading the source NetCDF files. A compatible xarray backend may be used instead if the local environment is already configured for one.

## Workflow

Run commands from the project root.

### 1. Export Mediterranean monthly data

```bash
python3 export_mediterranean_months.py data --months 01 07 08
```

This creates one CSV per matching year and month in `data_med/`, for example `data_med/1980_01_med.csv`. Each CSV contains `time`, `lat`, `lon`, and `temperature`, with the temperature values retained in the source unit, Kelvin.

The default export months are January and July:

```bash
python3 export_mediterranean_months.py
```

### 2. Inspect or export a NetCDF subset

`read_sst.py` is intended as an exploratory utility for loading one NetCDF file or a file pattern, printing dataset information, subsetting the Mediterranean bounding box, and optionally saving a NetCDF, CSV, or PNG result.

Example intended usage:

```bash
python3 read_sst.py 'data/*.nc' --output mediterranean_subset.csv
```

The CSV option also creates a PNG map beside the CSV. The current checked-in version of this file contains an extra text fragment before its first import and must be cleaned before this command can run.

### 3. Create monthly SST animations

```bash
python3 plot_mediterranean.py data_med --month 01
python3 plot_mediterranean.py data_med --month 08
```

For each selected month, the plotting workflow:

1. reads the corresponding exported CSV files;
2. converts Kelvin to Celsius;
3. renders a fixed-range 0-35°C spatial heatmap for each year;
4. writes frame images to `data_med_images_<month>/`;
5. combines the frames into `data_med_<month>.gif`.

### 4. Calculate annual monthly averages

```bash
python3 plot_january_average.py data_med --months 01 07
```

The script calculates the mean temperature of every valid grid-cell observation for each year and selected month. It writes a summary CSV and a line chart. The default output names are `january_july_average_temperature.csv` and `january_july_average_temperature.png`, even when different months are supplied.

## Outputs

The repository currently includes these result types:

- `data_med/`: Mediterranean CSV exports;
- `data_med_images/`, `data_med_images_01/`, and `data_med_images_08/`: individual map frames;
- `data_med_01.gif` and `data_med_08.gif`: animated monthly spatial visualizations;
- `january_average_temperature.csv` and `.png`: January yearly averages and chart;
- `08_average_temperature.csv` and `.png`: August yearly averages and chart;
- `january_july_average_temperature.csv` and `.png`: combined January and July yearly comparison.

The included summary values show a gradual increase in the calculated annual averages over much of the available record. For example, the January summary rises from 14.59°C in 1980 to 16.05°C in 2025, while the August summary rises from 24.91°C to 26.58°C over the same years. These are descriptive results for this extracted grid and period, not a formal climate-trend estimate.

## Project layout

```text
data/                         Source monthly NetCDF files
data_med/                     Mediterranean CSV exports
data_med_images*/             Rendered map frames
*.gif                         Animated monthly maps
*.csv                         Exported and summarized tabular results
*.png                         Static maps and summary charts
*.py                          Processing, inspection, export, and plotting code
```

## Notes and limitations

- The region is selected using a latitude/longitude bounding box; it is not a detailed coastline polygon in the export workflow.
- The exported temperature column preserves the source values in Kelvin. Celsius conversion is performed when plotting or calculating averages.
- Missing or masked observations can affect the number of grid cells contributing to each average.
- The repository does not currently include automated tests, a pinned dependency file, or a formal trend-analysis model.