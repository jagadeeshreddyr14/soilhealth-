import pymysql


    
def get_info(farm_id):
    
    
    db = pymysql.connect(host ="3.14.103.172", user = "satyukt",password = "Welcome@123", database = "dummy_api")
    cursor = db.cursor()
    
    referal_query = f"select referal_code from user_details where mobile_no in (select user_name from  user_credentials \
    where user_id in (select clientID from polygonStore where id={farm_id}));"
    cursor.execute(referal_query)
    referal_code = cursor.fetchone()
    result_query = f"select clientID, polyinfo, croptype from polygonStore where id = {farm_id}"
    cursor.execute(result_query)
    results = cursor.fetchone()
    
    if referal_code == None:
        return results, referal_code
    else:
        return results, referal_code[0]


if __name__ == "__main__":
    
    fid = [60789]
    # 58925
    for fi in fid:
        df, referal_code = get_info(fi)
    
        id_client, polyinfo, crop = df
    

        print(fi, crop)