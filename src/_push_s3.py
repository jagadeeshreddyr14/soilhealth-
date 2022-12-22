import boto3
import pandas as pd 
from invalid import create_invalidation
from _get_detials import get_info
from datetime import datetime 

s3 = boto3.resource(
    's3',
    region_name='us-east-1',
    aws_access_key_id="AKIAXMFIWZ7AO7DFOCVK",
    aws_secret_access_key="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"
)


def uploadfile(localpath, s3path):
    s3.meta.client.upload_file(localpath, "data.satyukt.com", s3path, ExtraArgs={
                               "ContentType": "application/pdf", "ACL": "public-read"})


if __name__ == "__main__":
    
    
    farm_list = [62325, 62318]
    # create_invalidation()
    for fid in farm_list:
        
        df, referal_code = get_info(fid)
    
        cid, polyinfo, crop = df
    


        try:
            fid_ti = f"{fid}_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}"
            local_path = f'/home/satyukt/Projects/1000/soil_health/output/Report/{fid}.pdf'
            s3path = f'sat2farm/{cid}/{fid}/soilReportPDF/{fid_ti}.pdf'
            print(cid, fid)
            uploadfile(local_path, s3path)
        except:
            pass

