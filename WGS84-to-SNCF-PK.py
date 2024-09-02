import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import tqdm

# Load railway points data. Download file from:
# https://github.com/nicolaswurtz/extras-opendata-sncf-reseau/blob/master/pks.csv.zip
railway_df = pd.read_csv('pks.csv')
railway_gdf = gpd.GeoDataFrame(
    railway_df,
    geometry=gpd.points_from_xy(railway_df.lon, railway_df.lat),
    crs="EPSG:4326"
).to_crs("EPSG:2154")

# Load your CSV with WGS84 points (in my case camera positions)
camera_df = pd.read_csv('camera.csv', delimiter=',')  # Adjust delimiter if necessary
camera_gdf = gpd.GeoDataFrame(
    camera_df,
    geometry=gpd.points_from_xy(camera_df['Lon (WGS84)'], camera_df['Lat (WGS84)']),
    crs="EPSG:4326"
).to_crs("EPSG:2154")

# Function to find the nearest railway point for each camera
def find_nearest_railway(camera_row):
    # Calculate distances from this camera point to all railway points
    distances = railway_gdf.geometry.distance(camera_row.geometry)
    nearest_idx = distances.idxmin()  # Index of the nearest railway point

    nearest_railway = railway_gdf.loc[nearest_idx]
    
    return {
        'nearest_code_ligne': nearest_railway['code_ligne'], 'nearest_pk': nearest_railway['pk'], 
        'nearest_vitesse': nearest_railway['vitesse'], 'nearest_altitude': nearest_railway['altitude'], 
        'nearest_lat': nearest_railway['lat'], 'nearest_lon': nearest_railway['lon']
    }

# Applying the function and collecting results
results = [find_nearest_railway(row) for index, row in tqdm.tqdm(camera_gdf.iterrows(), total=camera_gdf.shape[0], desc="Finding nearest railway points")]

# Convert results to DataFrame
results_df = pd.DataFrame(results)
# Merge with the original camera DataFrame
updated_camera_df = pd.concat([camera_df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)

# Save to CSV
updated_camera_df.to_csv('updated_camera_with_railway_info.csv', index=False)
