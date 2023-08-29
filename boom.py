"""
Referred follwing links for the below code:

https://rasterio.readthedocs.io/en/stable/quickstart.html
https://rasterio.readthedocs.io/en/stable/topics/masking-by-shapefile.html
https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
"""

import os
import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask

class CalculateNDVI:
    def __init__(self, red_band_path, nir_band_path, polygon_path, output_folder):
        self.red_band_path = red_band_path
        self.nir_band_path = nir_band_path
        self.polygon_path = polygon_path
        self.output_folder = output_folder

        os.makedirs(self.output_folder, exist_ok=True)
        np.seterr(invalid="ignore")

    def read_polygon(self):
        polygon = gpd.read_file(self.polygon_path)
        reprojected_polygon = polygon.to_crs(epsg=32636)
        self.polygon_geometry = reprojected_polygon.geometry[0]

    def extract_image(self):
        with rasterio.Env(AWS_NO_SIGN_REQUEST="YES"):
            with rasterio.open(self.red_band_path) as red_band_ds, rasterio.open(self.nir_band_path) as nir_band_ds:
                self.red_image, _ = mask(red_band_ds, [self.polygon_geometry], crop=True)
                self.nir_image, _ = mask(nir_band_ds, [self.polygon_geometry], crop=True)

    def calculate_ndvi(self):
        self.ndvi = np.divide((self.nir_image - self.red_image), (self.nir_image + self.red_image))

    def calculate_zonal_stats(self):
        self.mean_ndvi = np.nanmean(self.ndvi)
        self.min_ndvi = np.nanmin(self.ndvi)
        self.max_ndvi = np.nanmax(self.ndvi)

    def save_stats_to_file(self):
        stats_file_path = self.output_folder + "/stats.txt"
        with open(stats_file_path, "w") as stats_file:
            stats_file.write(f"Max NDVI: {self.max_ndvi}\n")
            stats_file.write(f"Mean NDVI: {self.mean_ndvi}\n")
            stats_file.write(f"Min NDVI: {self.min_ndvi}\n")

    def save_ndvi_image(self):
        ndvi_image_path = self.output_folder + "/ndvi.png"
        plt.imshow(self.ndvi[0], cmap="RdYlGn", vmin=-1, vmax=1)
        plt.colorbar(label="NDVI")
        plt.savefig(ndvi_image_path)
        plt.close()

    def process(self):
        self.read_polygon()
        self.extract_image()
        self.calculate_ndvi()
        self.calculate_zonal_stats()
        self.save_stats_to_file()
        self.save_ndvi_image()

# File paths
s3_path = "s3://sentinel-cogs/sentinel-s2-l2a-cogs/36/N/YF/2023/6/S2B_36NYF_20230605_0_L2A/"
red_band_path = s3_path + "B04.tif"
nir_band_path = s3_path + "B08.tif"
polygon_path = "sample_polygon.geojson"
output_folder = "output"

ndvi_calculator = CalculateNDVI(red_band_path, nir_band_path, polygon_path, output_folder)
ndvi_calculator.process()
