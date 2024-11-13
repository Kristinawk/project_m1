# 1. Imports & Definitions:
import pandas as pd
import requests
from shapely.geometry import Point
import geopandas as gpd

PATH = '../data/bicimad_stations.csv'
GEO = 'geometry.coordinates'
API_ENDPOINT="https://datos.madrid.es/egob"
DATASET="/catalogo/300356-0-monumentos-ciudad-madrid.json"
COLUMNS_2FIX = ["address", "location", "organization"]
TABLE_COLS = ['Place of Interest', 'Type of place', 'Place address', 'BiciMAD station', 'Station locaiton', 'Available bikes']
PLACE = 'Monuments'
FILE_PATH = '../data/nearest_bicimad.csv'

# 2. Acquisition & Wrangling:
# 2.a) Read & transform csv