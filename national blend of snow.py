import cfgrib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

# Path to your .grib2 file
file_path = r'C:\Users\jacfo\Downloads\web gfs data model folder\blend.t18z.core.f156.co.grib2'

# Open the .grib2 file using cfgrib
ds = cfgrib.open_dataset(file_path)

# Extract latitude and longitude values
latitudes = ds['latitude'].values
longitudes = ds['longitude'].values

# Adjust longitude if they are in a 0 to 360 degree range
longitudes = np.where(longitudes > 180, longitudes - 360, longitudes)

# Check the adjusted range
print(f"\nAdjusted Longitude range: {longitudes.min()} to {longitudes.max()}")
print(f"Latitude range: {latitudes.min()} to {latitudes.max()}")

# Define the extent for the USA (approximate bounding box)
min_lon, max_lon = -130, -60  # Longitude bounds for the continental US
min_lat, max_lat = 24, 50     # Latitude bounds for the continental US

# Create a map using Cartopy
fig = plt.figure(figsize=(12, 9))  # Set figure size in inches

# Use a PlateCarree projection for the map
ax = plt.axes(projection=ccrs.PlateCarree())

# Add US map features
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAND, facecolor='lightgray')

# Add state boundaries
ax.add_feature(cfeature.STATES, edgecolor='gray')

# Set extent to zoom in on the continental US
ax.set_extent([min_lon, max_lon, min_lat, max_lat])

# Plot the gridded data (for example, using a variable like 'unknown')
if 'unknown' in ds:
    # Assuming 'unknown' contains the data to plot (modify this to your actual variable)
    data = ds['unknown'].values

    # If the data is in non-inch units, multiply by the conversion factor for inches
    # For example, assume the data is in meters, and you want to convert it to inches:
    # Conversion factor from meters to inches (1 meter = 39.37 inches)
    conversion_factor = 39.37
    data_in_inches = data * conversion_factor

    # Plot the data with the correct extent
    im = ax.imshow(data_in_inches, cmap='viridis', origin='lower',
                   extent=[longitudes.min(), longitudes.max(),
                           latitudes.min(), latitudes.max()])

    # Add a colorbar with label in inches
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', label='Data in Inches')

    # Add a title
    ax.set_title('Visualization of Data in Inches')

plt.show()
