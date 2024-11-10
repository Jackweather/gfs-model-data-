import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Create a new figure
plt.figure(figsize=(12, 8))

# Set up Basemap
m = Basemap(projection='lcc', 
            resolution='i', 
            lat_0=37.5, lon_0=-96, 
            width=5E6, height=3E6)

# Draw coastlines, country borders, and states
m.drawcoastlines()
m.drawcountries()
m.drawstates()

# Draw latitude lines from 10°N to 50°N
m.drawparallels(range(10, 51, 5), labels=[1, 0, 0, 0])  # From 10°N to 50°N
# Draw longitude lines from -130° to -60°
m.drawmeridians(range(-130, -60, 10), labels=[0, 0, 0, 1])  # From -130° to -60°

# Fill the land and ocean
m.fillcontinents(color='lightgray', lake_color='aqua')
m.drawmapboundary(fill_color='aqua')

# Title
plt.title('Map of the USA Showing Latitude Lines Down to 10°N')

# Show the plot
plt.show()
