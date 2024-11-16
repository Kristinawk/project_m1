# 1. Imports & Definitions:
import pandas as pd
import requests
from shapely.geometry import Point
import geopandas as gpd
import argparse

PATH = './data/bicimad_stations.csv'
GEO = 'geometry.coordinates'
API_ENDPOINT="https://datos.madrid.es/egob"
DATASET="/catalogo/300356-0-monumentos-ciudad-madrid.json"
COLUMNS_2FIX = ["address", "location", "organization"]
TABLE_COLS = ['Place of Interest', 'Type of place', 'Place address', 'BiciMAD station', 'Station locaiton', 'Available bikes']
PLACE = 'Monuments'
FILE_PATH = './data/nearest_bicimad.csv'

# 2. Acquisition & Wrangling:
# 2.a) Read & transform csv

def read_csv(file_path):
    df_read_csv = pd.read_csv(PATH, sep='\t', index_col=0)
    return df_read_csv

def string_to_coordinates(string):
    list_coordinates = [float(element) for element in string.replace("[", "").replace("]", "").replace(" ","").split(",")]
    return list_coordinates

def normalize_csv(df, orig_column, new_col1, new_col2):
    df[orig_column] = df[orig_column].apply(lambda row: string_to_coordinates(row))
    df[new_col1] = df[orig_column].apply(lambda row: row[0])
    df[new_col2] = df[orig_column].apply(lambda row: row[1])
    return df

# 2.b) Get data from API REST and transform

def get_dataset(api_endpoint, dataset):
    response = requests.get(api_endpoint+dataset)
    json_data = response.json() 
    df_dataset = pd.DataFrame(json_data["@graph"]) # the data that we need is stored in key "@graph" within json
    return df_dataset

def normalize_dataset(df):
    df = df.dropna() # 1 drop nulls
    for column in COLUMNS_2FIX: # 2 normalize dictionaries within columns
        df = pd.concat([df.drop(columns = [column]), df[column].apply(lambda x: pd.Series(x))], axis = 1)
    return df

# 2.c) Build main df as cross join of bicimad stations and places of interest

def merge(df1, df2):
    df_merged = pd.merge(df1, df2, how="cross")
    return df_merged

# 3. Analysis:
# 3.a) Calculate the distance to each bicimad station

def to_mercator(lat, long):
    # transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
    c = gpd.GeoSeries([Point(lat, long)], crs=4326)
    c = c.to_crs(3857)
    return c

def distance_meters(lat_start, long_start, lat_finish, long_finish):
    # return the distance in metres between to latitude/longitude pair points in degrees 
    # (e.g.: Start Point -> 40.4400607 / -3.6425358 End Point -> 40.4234825 / -3.6292625)
    start = to_mercator(lat_start, long_start)
    finish = to_mercator(lat_finish, long_finish)
    return start.distance(finish)

def add_distance_col(df, col_name, lat_start, long_start, lat_finish, long_finish):
    df[col_name] = df.apply(lambda row: distance_meters(row[lat_start], row[long_start],
                                                                          row[lat_finish], row[long_finish]), axis = 1)
    return df

# 3.b) Group by place of interest:

def group_by(df, col_group, col_agg):
    df_grouped = df.groupby([col_group]).agg(min_value = (col_agg, 'min'), idxmin = (col_agg, 'idxmin')).reset_index()
    df_grouped['idxmin'] = df_grouped['idxmin'].map(df['id_y'])
    df_grouped = df_grouped.rename(columns = {'idxmin': 'id_y', 'min_value': col_agg})
    return df_grouped

# 3.c) Build final table with all necesary columns and create csv

def build_output_table(df_grouped, df_places, df_bici, place, table_cols):
    
    res1 = df_grouped.merge(df_places[['id', 'title', 'street-address']],
                                how='inner', left_on='id_x', right_on='id').drop(columns = ['id']) # add place columns
    
    res2 = res1.merge(df_bici[['id', 'name', 'address', 'dock_bikes']],
                                how='inner', left_on='id_y', right_on='id').drop(columns = ['id']) # add bicimad columns

    res3 = res2.drop(columns = ['distance', 'id_x', 'id_y']) # drop ids


    res3['Type of place'] = place # add column identifying type of place

    #  move new column to the right position
    cols = list(res3.columns.values)
    cols = cols[:1] + cols[-1:] + cols[1:-1]
    res3 = res3[cols] 

    res3.columns = table_cols # rename columns
        
    return  res3


# 4. We want to give user two possibilities:
# -get full table --> pipeline 1
# -get one line from the table --> pipeline 2

# 4.a) Pipeline 1

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)
    return print("Find here the nearest BiciMad station to monuments of Madrid: https://github.com/Kristinawk/project_m1/blob/main/data/nearest_bicimad.csv")

# 4.b) Pipeline 2

def user_query(df):
    user_query = input('Enter a Place of Interest: ')
    df_query = df.loc[df['Place of Interest'].isin([user_query])]
    return print(df_query)

# 4.c) Define argparse

def argument_parser():
    parser = argparse.ArgumentParser(description= 'Application to find the nearest BiciMad station to a Place of Interest' )
    parser.add_argument('-f', '--function', action='store_true')
    args = parser.parse_args()
    return args