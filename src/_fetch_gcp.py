import sqlalchemy
import pandas as pd

def gcp_check():
    
    dbname="sat2farmdb"
    user="remote"
    password="satelite"
    host="34.125.75.120"
    port=3306


    engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}")


    # try:
    #    engine.connect()
    # except sqlalchemy.exc.SQLAlchemyError as e:
    #     print(e)
        
    old = pd.read_csv('/home/satyukt/Projects/1000/aws/soil_health_info/gcp_info.csv')

    # engine.connect()

    results = pd.read_sql_query(
            "select farm_id from paymentGateway ", engine)
    
    
    
    farm_list=[]
    if len(old)<len(results):
        result = results.tail(len(results)-len(old))
        farm_list = result['farm_id'].values.tolist()
        results.to_csv('/home/satyukt/Projects/1000/aws/soil_health_info/gcp_info.csv')
        
        return True,farm_list
    
    return False,farm_list
        
        
    
    
    # results.tail[len(results)-len(old)]
    # print(results)











if __name__ == "__main__": 
    
    
    gcp_check()
    
    