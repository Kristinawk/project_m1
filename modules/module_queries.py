# 1. Imports & Definitions:

import pandas as pd
import argparse

#  We want to give user two options:
# -get full table --> pipeline 1
# -get one line from the table --> pipeline 2

# a) Pipeline 1

# print("Find here the nearest BiciMad station to monuments of Madrid: https://github.com/Kristinawk/project_m1/blob/main/data/nearest_bicimad.csv")

# b) Pipeline 2

def user_query(file_path):
    """
    Prompts the user to enter a place of interest and queries a CSV file to find matching records.

    This function asks the user to input a place of interest and searches for that place in a specified CSV file.
    If a matching record is found, it displays the relevant rows from the DataFrame. If no matches are found,
    it notifies the user that the inputted place is incorrect and prompts them to try again.

    Parameters:
    file_path (str): The path to the CSV file containing the places of interest.

    Returns:
    None: The function prints the result directly or displays an error message if no match is found.
    """
    user_query = input('Enter a Place of Interest: ')
    df = pd.read_csv(file_path)
    df_query = df.loc[df['Place of Interest'].isin([user_query])]
    if df_query.empty==True:
        return print('Wrong monument name. Please, try again.')
    else:
        return print(df_query)


# c) Define argparse

def argument_parser():
    """
    Parses command-line arguments for an application to find the nearest BiciMad station to monuments in Madrid.

    This function sets up the command-line argument parser for the application, which allows the user to choose 
    between two options: either getting a table of all monuments or querying information about a specific monument. 
    The function returns the parsed arguments.

    Returns:
    argparse.Namespace: An object containing the parsed command-line arguments, with a `function` attribute 
                        specifying the selected option (either 'table' or 'place').
    """
    parser = argparse.ArgumentParser(description= 'Application to find the nearest BiciMad station to monuments of Madrid' )
    help_message ='You have two options. Option 1: "table" provides information on all monuments. Option 2: "place" provides information on a particular monument' 
    parser.add_argument('-f', '--function', help=help_message, type=str)
    args = parser.parse_args()
    return args