import os
import requests
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime
from PIL import Image

# Folder paths for GRIB data and image outputs
base_folder = "./public"
grib_folder = os.path.join(base_folder, "grib")
images_folder = os.path.join(base_folder, "images")

# Ensure the folders exist
os.makedirs(grib_folder, exist_ok=True)
os.makedirs(images_folder, exist_ok=True)

# Get today's date and format it for the URL
today = datetime.now()
date_str = today.strftime("%Y%m%d")

# Determine the most recent GFS run based on the current hour
current_hour = today.hour
hour_str = f"{(current_hour // 6) * 6:02d}"  # Get the latest run in 6-hour intervals

# Forecast steps limited to f000 to f012 and then every 6 hours up to f096
forecast_steps = [f"f{str(i).zfill(3)}" for i in range(13)]  # Generates ['f000', 'f001', ..., 'f012']
forecast_steps += [f"f{str(i).zfill(3)}" for i in range(12, 97, 6)]  # Adds ['f018', 'f024', ..., 'f096']

# Base URL for downloading the latest GFS model data
base_url = f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=/gfs.{date_str}/{hour_str}/atmos"

# Download GRIB files
for step in forecast_steps:
    url = f"{base_url}&file=gfs.t{hour_str}z.pgrb2.0p25.{step}&var_REFC=on&var_REFD=on&lev_entire_atmosphere=on"
    filename = os.path.join(grib_folder, f"gfs.t{hour_str}z.pgrb2.0p25.{step}.grib2")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

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

    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgray', lake_color='lightblue')

    lon_grid, lat_grid = np.meshgrid(longitude, latitude)
    x, y = m(lon_grid, lat_grid)
    reflectivity_plot = m.contourf(x, y, refc, cmap='plasma', levels=np.linspace(refc.min(), refc.max(), 50), alpha=0.75)  # Reduced levels to 50 for quicker rendering
    plt.colorbar(reflectivity_plot, orientation='vertical').set_label('Reflectivity (dBZ)')
    plt.title(f'Reflectivity ({os.path.basename(file_path)})')
    plt.savefig(save_path, dpi=150)  # Lowered DPI for faster saving
    plt.close()
    print(f"Saved plot: {save_path}")
    ds.close()

# Plot and save images for each forecast step
for step in forecast_steps:
    file_path = os.path.join(grib_folder, f"gfs.t{hour_str}z.pgrb2.0p25.{step}.grib2")
    plot_save_path = os.path.join(images_folder, f"plot_{hour_str}_{step}.png")
    plot_reflectivity(file_path, plot_save_path)

# Create an animated GIF
plot_files = [os.path.join(images_folder, f"plot_{hour_str}_{step}.png") for step in forecast_steps]
images = [Image.open(file) for file in plot_files if os.path.exists(file)]
animation_path = os.path.join(images_folder, "gfs_animation.gif")
if images:  # Ensure there are images to create a GIF
    images[0].save(animation_path, save_all=True, append_images=images[1:], duration=500, loop=0)
    print(f"GIF created: {animation_path}")
else:
    print("No images found to create a GIF.")
