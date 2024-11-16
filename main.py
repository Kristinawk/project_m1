#imports

from modules import module as md

#input

PATH = './data/bicimad_stations.csv'
GEO = 'geometry.coordinates'
API_ENDPOINT="https://datos.madrid.es/egob"
DATASET="/catalogo/300356-0-monumentos-ciudad-madrid.json"
COLUMNS_2FIX = ["address", "location", "organization"]
TABLE_COLS = ['Place of Interest', 'Type of place', 'Place address', 'BiciMAD station', 'Station locaiton', 'Available bikes']
PLACE = 'Monuments'
FILE_PATH = './data/nearest_bicimad.csv'

#pipeline
if __name__ == '__main__':
    DF_CSV = md.read_csv(PATH)
    DF_DATASET = md.get_dataset(API_ENDPOINT, DATASET)
    DF_BICIMAD = md.normalize_csv(DF_CSV, GEO, 'bm_longitude', 'bm_latitude')
    DF_MONUMENTS = md.normalize_dataset(DF_DATASET)
    DF_FULL_DATASET = md.merge(DF_MONUMENTS, DF_BICIMAD)
    DF_SAMPLE = DF_FULL_DATASET.loc[:791, :].copy() # we create a sample to shorten execution time in the next step
    DF_DISTANCE = md.add_distance_col(DF_SAMPLE, "distance", "latitude", "longitude", "bm_latitude", "bm_longitude")
    DF_GROUPED = md.group_by(DF_DISTANCE, "id_x", "distance")
    DF_OUTPUT = md.build_output_table(DF_GROUPED, DF_MONUMENTS, DF_BICIMAD, PLACE, TABLE_COLS)
    
    if md.argument_parser().function:
        md.user_query(DF_OUTPUT)
    else:
        md.save_csv(DF_OUTPUT, FILE_PATH)