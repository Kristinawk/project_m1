# 1. Imports & Definitions:
import pandas as pd
import argparse

#  We want to give user two possibilities:
# -get full table --> pipeline 1
# -get one line from the table --> pipeline 2

# a) Pipeline 1

# print("Find here the nearest BiciMad station to monuments of Madrid: https://github.com/Kristinawk/project_m1/blob/main/data/nearest_bicimad.csv")

# b) Pipeline 2

def user_query(file_path):
    user_query = input('Enter a Place of Interest: ')
    df = pd.read_csv(file_path)
    df_query = df.loc[df['Place of Interest'].isin([user_query])]
    if df_query.empty==True:
        return print("Wrong monument name. Please, try again.")
    else:
        return print(df_query)


# c) Define argparse

def argument_parser():
    parser = argparse.ArgumentParser(description= 'Application to find the nearest BiciMad station to monuments of Madrid' )
    help_message ='You have two options. Option 1: "table" provides information on all monuments. Option 2: "place" provides information on a particular monument' 
    parser.add_argument('-f', '--function', help=help_message, type=str)
    args = parser.parse_args()
    return args