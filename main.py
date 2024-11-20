#imports

from modules import module_definitions as md
from modules import module_calculation as mc
from modules import module_queries as mq


#pipeline
if __name__ == '__main__':
    if mq.argument_parser().function == "calc":
        DF_CSV = mc.read_csv(md.path_input)
        DF_DATASET = mc.get_dataset(md.api_endpoint, md.dataset)
        DF_BICIMAD = mc.normalize_csv(DF_CSV, md.geo, 'bm_longitude', 'bm_latitude')
        DF_MONUMENTS = mc.normalize_dataset(DF_DATASET, md.columns_2fix)
        DF_FULL_DATASET = mc.merge(DF_MONUMENTS, DF_BICIMAD)
        DF_DISTANCE = mc.add_distance_col(DF_FULL_DATASET, "distance", "latitude", "longitude", "bm_latitude", "bm_longitude")
        DF_GROUPED = mc.group_by(DF_DISTANCE, "id_x", "distance")
        DF_OUTPUT = mc.build_output_table(DF_GROUPED, DF_MONUMENTS, DF_BICIMAD, md.place, md.table_cols, md.path_output)
    elif mq.argument_parser().function == "table":
        print("Find here the nearest BiciMad station to monuments of Madrid: https://github.com/Kristinawk/project_m1/blob/main/data/nearest_bicimad.csv")
    elif mq.argument_parser().function == "place":
        mq.user_query(md.path_output)
    else:
        print("FATAL ERROR...you need to select the correct method")