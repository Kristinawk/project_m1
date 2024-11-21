# 1. Imports & Definitions:

import pandas as pd
import requests
from shapely.geometry import Point
import geopandas as gpd
from modules import module_definitions as md


# 2. Acquisition & Wrangling:
# 2.a) Read & transform csv

def read_csv(file_path):
    """
    Reads a tab-separated values (TSV) file into a pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV (or TSV) file to be read. The file should be tab-separated,
                     and the first column will be used as the index.

    Returns:
    pandas.DataFrame: A DataFrame containing the data from the file, with the first column as the index.
    """
    df_read_csv = pd.read_csv(file_path, sep='\t', index_col=0)
    return df_read_csv


def string_to_coordinates(string):
    """
    Converts a string representation of coordinates into a list of floats.

    This function takes a string containing coordinates in the format of a list, such as
    '[x1, y1]', and converts it into a list of floats, such as [x1, y1].

    Parameters:
    string (str): A string representing a list of coordinates, where elements are separated by commas
                  and surrounded by square brackets, e.g., '[1.0, 2.5]'.

    Returns:
    list: A list of floats representing the coordinates extracted from the string.
    """
    list_coordinates = [float(element) for element in string.replace("[", "").replace("]", "").replace(" ","").split(",")]
    return list_coordinates


def normalize_csv(df, orig_column, new_col1, new_col2):
    """
    Normalizes the values in a specified column of a DataFrame.

    This function applies the `string_to_coordinates` function to a specified column in the DataFrame,
    splitting the resulting coordinate list into two separate columns.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to be normalized.
    orig_column (str): The name of the original column containing string representations of coordinates.
    new_col1 (str): The name of the new column to store the first coordinate extracted from `orig_column`.
    new_col2 (str): The name of the new column to store the second coordinate extracted from `orig_column`.

    Returns:
    pandas.DataFrame: The updated DataFrame with the original column normalized and two new columns added,
                       one for each coordinate.
    """
    df[orig_column] = df[orig_column].apply(string_to_coordinates)
    df[new_col1] = df[orig_column].apply(lambda row: row[0])
    df[new_col2] = df[orig_column].apply(lambda row: row[1])
    return df


# 2.b) Get data from API REST and transform

def get_dataset(api_endpoint, dataset):
    """
    Fetches a dataset from a given API endpoint and returns it as a pandas DataFrame.

    This function sends a GET request to the specified API endpoint, retrieves the JSON response,
    and extracts the data stored in the "@graph" key to load it into a pandas DataFrame.

    Parameters:
    api_endpoint (str): The base URL of the API to which the request will be made.
    dataset (str): The specific dataset name or path to append to the `api_endpoint` to fetch the data.

    Returns:
    pandas.DataFrame: A DataFrame containing the dataset retrieved from the API, 
                       with data extracted from the "@graph" key in the JSON response.
    """
    response = requests.get(api_endpoint+dataset)
    json_data = response.json() 
    df_dataset = pd.DataFrame(json_data["@graph"]) # the data that we need is stored in key "@graph" within json
    return df_dataset


def normalize_dataset(df, columns_list):
    """
    Normalizes specific columns in a DataFrame by expanding dictionary-like entries into separate columns.

    This function performs two main actions:
    1. Drops any rows with missing values (nulls) from the DataFrame.
    2. Expands dictionary-like entries in the specified columns by applying `pd.Series` to each entry and 
       adding the resulting new columns to the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be normalized.
    columns_list (list of str): A list of column names that contain dictionary-like structures which should 
                                be expanded into individual columns.

    Returns:
    pandas.DataFrame: The updated DataFrame with rows containing missing values removed, and dictionary-like
                       columns expanded into separate columns.
    """
    df = df.dropna() # 1 drop nulls
    for column in columns_list: # 2 normalize dictionaries within columns
        df = pd.concat([df.drop(columns = [column]), df[column].apply(pd.Series)], axis = 1)
    return df


# 2.c) Build main df as cross join of bicimad stations and places of interest

def merge(df1, df2):
    """
    Merges two DataFrames using a cross join, meaning every row of the first DataFrame 
    is combined with every row of the second DataFrame.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to be merged.
    df2 (pandas.DataFrame): The second DataFrame to be merged.

    Returns:
    pandas.DataFrame: A new DataFrame that results from the cross join of `df1` and `df2`.
    """
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
    """
    Adds a new column to the DataFrame calculating the distance between two geographical points.

    This function computes the distance (in meters) between two sets of latitude and longitude 
    coordinates for each row in the DataFrame and adds the results as a new column.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the latitude and longitude values.
    col_name (str): The name of the new column to store the calculated distance.
    lat_start (str): The name of the column containing the starting latitude value.
    long_start (str): The name of the column containing the starting longitude value.
    lat_finish (str): The name of the column containing the finishing latitude value.
    long_finish (str): The name of the column containing the finishing longitude value.

    Returns:
    pandas.DataFrame: The updated DataFrame with the new column containing the calculated distances.
    """
    df[col_name] = df.apply(lambda row: distance_meters(row[lat_start], row[long_start],
                                                                          row[lat_finish], row[long_finish]), axis = 1)
    return df


# 3.b) Group by place of interest:

def group_by(df, col_group, col_agg):
    """
    Groups the DataFrame by a specified column and aggregates another column with the minimum value 
    and the index of the minimum value.

    This function groups the DataFrame by the column specified in `col_group`, then for each group, 
    it calculates the minimum value of the column specified in `col_agg` and the index of that minimum value. 
    The resulting DataFrame includes the minimum value and the corresponding index, which is mapped to another column.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be grouped and aggregated.
    col_group (str): The column to group by.
    col_agg (str): The column to aggregate, calculating the minimum value and the index of that minimum.

    Returns:
    pandas.DataFrame: The grouped and aggregated DataFrame, with the minimum value and the corresponding index 
                       from the specified column.
    """
    df_grouped = df.groupby([col_group]).agg(min_value = (col_agg, 'min'), idxmin = (col_agg, 'idxmin')).reset_index()
    df_grouped['idxmin'] = df_grouped['idxmin'].map(df['id_y'])
    df_grouped = df_grouped.rename(columns = {'idxmin': 'id_y', 'min_value': col_agg})
    return df_grouped


# 3.c) Build final table with all necesary columns and create csv

def build_output_table(df_grouped, df_places, df_bici, place, table_cols, file_path):
    """
    Builds an output table by merging and processing data from multiple DataFrames and saves it as a CSV.

    This function takes three DataFrames (`df_grouped`, `df_places`, `df_bici`), merges them based on common IDs, 
    drops unnecessary columns, adds a column identifying the type of place, reorders columns, and renames them. 
    The result is saved as a CSV file at the specified `file_path`.

    Parameters:
    df_grouped (pandas.DataFrame): The DataFrame containing grouped and aggregated data that will be merged with other data.
    df_places (pandas.DataFrame): A DataFrame containing place-related information (e.g., title, address).
    df_bici (pandas.DataFrame): A DataFrame containing information about bike stations (e.g., name, address, number of docked bikes).
    place (str): A string to identify the type of place, which will be added as a new column in the output table.
    table_cols (list of str): A list of column names to rename the resulting DataFrame columns.
    file_path (str): The path where the resulting table will be saved as a CSV file.

    Returns:
    pandas.DataFrame: The processed and merged DataFrame with the final output table.
    """
    
    res1 = df_grouped.merge(df_places[['id', 'title', 'street-address']],
                                how='inner', left_on='id_x', right_on='id').drop(columns = ['id']) # add place columns
    
    res2 = res1.merge(df_bici[['id', 'name', 'address', 'dock_bikes']],
                                how='inner', left_on='id_y', right_on='id').drop(columns = ['id']) # add bicimad columns

    res3 = res2.drop(columns = ['distance', 'id_x', 'id_y']) # drop ids


    res3['Type of place'] = place # add column identifying type of place

    # move new column to the right position
    cols = list(res3.columns.values)
    cols = cols[:1] + cols[-1:] + cols[1:-1]
    res3 = res3[cols] 

    res3.columns = table_cols # rename columns

    res3.to_csv(file_path, index=False) # create and save csv
        
    return  res3