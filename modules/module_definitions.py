# Definitions:

path_input = './data/bicimad_stations.csv'
geo = 'geometry.coordinates'
api_endpoint = "https://datos.madrid.es/egob"
dataset = "/catalogo/300356-0-monumentos-ciudad-madrid.json"
columns_2fix = ["address", "location", "organization"]
table_cols = ['Place of Interest', 'Type of place', 'Place address', 'BiciMAD station', 'Station locaiton', 'Available bikes']
place = 'Monuments'
path_output = './data/nearest_bicimad.csv'