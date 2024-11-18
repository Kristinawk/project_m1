# FindBiciMAD

# About:
FindBiciMAD is a Python Application that allows potential user to find the nearest BiciMad station to a set of places of interest. The app creates a table with relevant information and provides two use cases to the end user: access to the full table or filter the table by specific place of interest.
FindBiciMAD holds the benefit of **modularity**, allowing to execute the pipeline in two steps, which significantly improves user experience.

# Technical specifications:
The input of this app is a csv file with the list of BiciMAD stations and Madrid City Hall API REST with a set of places of interest. Python script combines the information of both datasources, calculates the distance to each BiciMad station and returns the nearest one to each place of interest. The table is stored as csv file and the user can access this information with argparse method.

# Configuration:
Hereby the list of libraries required to run FindBiciMAD: pandas, requests, geopandas and argparse.

# How to build:
To run the app, follow these steps:

1. Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)

2. Ensure Git is installed  
Visit https://git-scm.com to download and install console Git if not already installed

3. Clone the repository  
git clone https://github.com/Kristinawk/project_m1

4. *Only for developers - Re-create the full table  
`python main.py -f "calc"`

5. Launch the query  
 a) get the full table  
 `python main.py -f "table"`  

 b) get the table for a specific place of interest  
 `python main.py -f "place"`

