from soil_health_main import compute_soil_health
import os 
import configparser 
import ee 
import glob 
from logs import MyLogger
import argparse
from delete_files import Delete_files
from invalid import create_invalidation
from _get_detials import get_info

def get_path(param, fdr_name):
    nnut = glob.glob(f"../data/models/{fdr_name[0]}/{param}*.pkl")[0]
    nslr = glob.glob(f"../data/models/{fdr_name[1]}/{param}*.pkl")[0]
    return nnut, nslr

    
def run(farm_cor, lang=''):
    
    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)
    
    logger = MyLogger(module_name=__name__,
                      filename="../logs/soil_health.log").create_logs()
    

    ee.Initialize()

    config = configparser.ConfigParser()

    config.read('../Config/config.ini')
    
    df, referal_code = get_info(farm_cor)
    
    if referal_code == '19615':
        return
    

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
    
        compute_soil_health(farm_cor, pixel_size, input_bands, soil_nuts, nuts_ranges, lang, 
                            report = True, push_s3 = True)
    except Exception as e:
        logger.info(f"{e}")
        
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--fid", help = " Farm id")
    parser.add_argument("-l", "--lang", help = " language")
    args = parser.parse_args()
    
    if args.fid:
        print("fid is: % s" % args.fid)
        Delete_files(int(args.fid))
        run(int(args.fid), args.lang)
    else:

        farm_list = [63007]
        for i in farm_list:   
            Delete_files(i) 
            run(i)
