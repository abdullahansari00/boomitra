"""
Download the data from S3 bucket in the empty "s3" folder using the following command:
`aws s3 cp --no-sign-request s3://sentinel-cogs/sentinel-s2-l2a-cogs/36/N/YF/2023/6/S2B_36NYF_20230605_0_L2A/ s3 --recursive`
"""

"""
Referred follwing links for the below code:

https://rasterio.readthedocs.io/en/stable/quickstart.html
https://rasterio.readthedocs.io/en/stable/topics/masking-by-shapefile.html
https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
"""

import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask

# File paths
red_band_path = "s3/B04.tif"
nir_band_path = "s3/B08.tif"
polygon_path = "sample_polygon.geojson"

# Read the polygon
polygon = gpd.read_file(polygon_path)

# Reproject the polygon to match the projection of the given imagery
reprojected_polygon = polygon.to_crs(epsg=32636)
polygon_geometry = reprojected_polygon.geometry[0]

# Open and read the red and NIR bands
with rasterio.open(red_band_path) as red_band_ds, rasterio.open(nir_band_path) as nir_band_ds:
    # Mask the imagery using the reprojected polygon
    red_image, _ = mask(red_band_ds, [polygon_geometry], crop=True)
    nir_image, _ = mask(nir_band_ds, [polygon_geometry], crop=True)

# Calculate NDVI
np.seterr(invalid="ignore")
ndvi = np.divide((nir_image - red_image), (nir_image + red_image))

# Calculate zonal statistics
mean_ndvi = np.nanmean(ndvi)
min_ndvi = np.nanmin(ndvi)
max_ndvi = np.nanmax(ndvi)

# Save zonal statistics to a file
with open("output.txt", "w") as stats_file:
    stats_file.write(f"Max NDVI: {max_ndvi}\n")
    stats_file.write(f"Mean NDVI: {mean_ndvi}\n")
    stats_file.write(f"Min NDVI: {min_ndvi}\n")

# Plot and save NDVI image
plt.imshow(ndvi[0], cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(label="NDVI")
plt.savefig("ndvi.png")
plt.close()
