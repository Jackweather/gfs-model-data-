import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from PIL import Image
import matplotlib.colors as mcolors  # Import for color handling

# Folder paths for GRIB data and image outputs
base_folder = "./public"  # Use the "public" folder directly
grib_folder = os.path.join(base_folder, "grib")
images_folder = os.path.join(base_folder, "rainpng")  # Subfolder for images (Netlify will read this)
os.makedirs(grib_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)  # Ensure the "rainpng" folder exists

# Define the forecast steps to process
forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]  # f000 to f012
forecast_steps += [f"f{str(i).zfill(3)}" for i in range(18, 97, 6)]  # f018, f024, ..., f096

# Define potential GFS run hours
run_hours = ["00", "06", "12", "18"]

# Function to find the latest available run based on files in the folder
def find_latest_run(grib_folder):
    for run_hour in reversed(run_hours):  # Check from latest to earliest
        for step in forecast_steps:
            file_path = os.path.join(grib_folder, f"gfs.t{run_hour}z.pgrb2.0p25.{step}.grib2")
            if os.path.exists(file_path):
                print(f"Detected latest available run: {run_hour}z")
                return run_hour
    print("No valid GFS run found.")
    return None

# Function to create reflectivity plots
def plot_reflectivity(file_path, save_path):
    ds = xr.open_dataset(file_path, engine='cfgrib')
    refc = ds['refc']
    latitude = ds['latitude'].values
    longitude = ds['longitude'].values

    plt.figure(figsize=(12, 8))
    lon_min, lon_max = -125, -66
    lat_min, lat_max = 20, 50  # Adjusted to go down to 20° latitude
    m = Basemap(projection='lcc', resolution='i',
                lat_0=(lat_min + lat_max) / 2, lon_0=(lon_min + lon_max) / 2,
                llcrnrlon=lon_min, urcrnrlon=lon_max,
                llcrnrlat=lat_min, urcrnrlat=lat_max)

    # Map drawing with specified colors
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgray', lake_color='lightblue')

    lon_grid, lat_grid = np.meshgrid(longitude, latitude)
    x, y = m(lon_grid, lat_grid)

    # Define color levels and colormap based on real-life rain intensity (dBZ)
    levels = [10, 20, 30, 40, 50, 60, 75]  # Custom levels for rain intensity
    colors = ['#b2ff59', '#66bb6a', '#ffff00', '#ff8c00', '#ff0000', '#8b0000']  # Light green to dark red
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(levels, cmap.N)

    # Plot rain reflectivity with custom color levels
    rain_plot = m.contourf(x, y, refc, levels=levels, cmap=cmap, norm=norm, extend='max')
    cbar = plt.colorbar(rain_plot, orientation='vertical', pad=0.04)
    cbar.set_label('Rain Reflectivity (dBZ)')
    cbar.set_ticks(levels[:-1])  # Only place ticks at the boundaries between color levels
    cbar.set_ticklabels([
        '10-20 (Light Rain)', '20-30 (Moderate Rain)', 
        '30-40 (Heavy Rain)', '40-50 (Very Heavy Rain)', 
        '50-60 (Intense Rain)', '60+ (Extreme Rain)'
    ])
    
    plt.title(f'Reflectivity ({os.path.basename(file_path)})')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved plot: {save_path}")
    ds.close()

# Find the latest run available in the GRIB folder
latest_run_hour = find_latest_run(grib_folder)

# Only proceed if a valid run hour was found
if latest_run_hour:
    plot_files = []
    for step in forecast_steps:
        file_path = os.path.join(grib_folder, f"gfs.t{latest_run_hour}z.pgrb2.0p25.{step}.grib2")
        if os.path.exists(file_path):  # Only process if file exists
            plot_save_path = os.path.join(images_folder, f"plot_{latest_run_hour}_{step}.png")  # Save directly in "rainpng"
            plot_reflectivity(file_path, plot_save_path)
            plot_files.append(plot_save_path)
        else:
            print(f"File not found: {file_path}. Skipping this step.")

    # Create an animated GIF if plot files were generated
    if plot_files:
        images = [Image.open(file) for file in plot_files]
        animation_path = os.path.join(images_folder, "gfs_animation.gif")
        images[0].save(animation_path, save_all=True, append_images=images[1:], duration=500, loop=0)
        print(f"GIF created: {animation_path}")
    else:
        print("No images found to create a GIF.")
else:
    print("No valid GFS run available to process.")
