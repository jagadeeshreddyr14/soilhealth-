import pandas as pd
import sqlalchemy
import pymysql
import requests


# def reverse_geocode(farm_path):
    
#     x = eval(farn)
    
#     pjson = x['geo_json']['geometry']['coordinates']
#     value = pjson[0].centroid
#     req = requests.get(
#         f"https://nominatim.openstreetmap.org/reverse?lon={value.x}&lat={value.y}&format=jsonv2"
#     )
#     data = req.json()
#     try:
#         state = data["address"]['state']
#     except:
#         pass
#     try:
#         district = data['address']['state_district'].replace('Urban','').replace(' ','')
#     except:
#         district= data['address']['city_district'].replace('Urban','').replace(' ','')
        
#     return district, state


    
def get_info(farm_id):
    
    dbname="dummy_api"
    user="satyukt"
    password="Welcome@123"
    host="3.14.103.172"
     
    # # engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}")
    
    # results = pd.read_sql_query(f"select clientID, polyinfo, croptype from polygonStore where id = {farm_id}", engine)
    # referal_code = pd.read_sql_query(f"select referal_code from user_details where mobile_no in (select user_name from \
    #                                  user_credentials where user_id in (select clientID from polygonStore \
    #                                  where id={farm_id}))",engine)
    
    db = pymysql.connect(host ="3.14.103.172", user = "satyukt",password = "Welcome@123", database = "dummy_api")
    cursor = db.cursor()
    
    referal_query = f"select referal_code from user_details where mobile_no in (select user_name from  user_credentials \
    where user_id in (select clientID from polygonStore where id={farm_id}));"
    cursor.execute(referal_query)
    referal_code = cursor.fetchone()
    result_query = f"select clientID, polyinfo, croptype from polygonStore where id = {farm_id}"
    cursor.execute(result_query)
    results = cursor.fetchone()
    #                                  where id={farm_id})
    if referal_code == None:
        return results, referal_code
    else:
        return results, referal_code[0]


if __name__ == "__main__":
    
    fid = [60918]
    # 58925
    for fi in fid:
        df, referal_code = get_info(fi)
    
        id_client, polyinfo, crop = df
    

        print(fi, polyinfo)