from soil_health_main import compute_soil_health
import os 
import configparser 
import ee 
import glob 
from logs import MyLogger
import argparse
from delete_files import Delete_files
from invalid import create_invalidation
import pandas as pd

def get_path(param, fdr_name):
    nnut = glob.glob(f"../data/models/{fdr_name[0]}/{param}*.pkl")[0]
    nslr = glob.glob(f"../data/models/{fdr_name[1]}/{param}*.pkl")[0]
    return nnut, nslr

    
def run(farm):
    
    logger = MyLogger(module_name=__name__,
                      filename="../logs/soil_health.log").create_logs()
    
    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    ee.Initialize()

    config = configparser.ConfigParser()

    config.read('../Config/config.ini')

    path_tiff = config['Output_path']['path_tiff']
    path_csv = config['Output_path']['path_csv']
    path_png = config['Output_path']['path_png']
    
    nuts_ranges = {
        'N': (100, 300), #100 - 300
        'P': (5, 50),  #22.4 - 56.0
        'K': (100, 400), #100 - 400
        'pH': (4.5, 8.5), #6.5 - 7.5
        'OC': (0, 0.75) #0.3 - 0.75
    } 

    pixel_size = 0.000277777778/3 # 30 meter by 3 -> 10 meter
    input_bands = ['B8', 'B4', 'B5', 'B11', 'B9', 'B1',
                'SR_n2', 'SR_N', 'TBVI1', 'NDWI', 'NDVI_G']

    soil_nuts = [get_path(param, ["ml", "slr"])
                for param in ['pH', 'P', 'K', 'OC', 'N']]
    
    try:
    
        compute_soil_health(farm, pixel_size, input_bands, soil_nuts, nuts_ranges, 
                                    path_tiff, path_png, path_csv, report = True, push_s3 = True)
        
    except Exception as e:
        logger.info(f"{e}")
        
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--fid", help = " Farm id")
    args = parser.parse_args()
    
    if args.fid:
        print("farmid as: % s" % args.fid)
        Delete_files(int(args.fid))
        run(int(args.fid))
    else:
        
        farm_list  = [60947]
        for i in farm_list:   
            Delete_files(i) 
            run(i)
