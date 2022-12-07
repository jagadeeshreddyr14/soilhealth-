import sqlalchemy
import pandas as pd

def gcp_check(path):
    
    dbname="sat2farmdb"
    user="remote"
    password="satelite"
    host="34.125.75.120"
    port=3306


    engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}")


    old = pd.read_csv(path)


    results = pd.read_sql_query(
            "select farm_id from paymentGateway ", engine)
    
    
    
    farm_list=[]
    if len(old)<len(results):
        result = results.tail(len(results)-len(old))
        farm_list = result['farm_id'].values.tolist()
        # results.to_csv('/home/satyukt/Projects/1000/aws/soil_health_info/gcp_info.csv')
        
        return True, farm_list, results
    
    return False, farm_list, results
        
        
if __name__=="__main__":
    
    path = '/home/satyukt/Projects/1000/aws/soil_health_info/gcp_info.csv'
    gcp_check(path)
    # results.tail[len(results)-len(old)]
    # print(results)












    
    