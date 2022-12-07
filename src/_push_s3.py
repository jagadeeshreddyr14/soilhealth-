import boto3
import pandas as pd 
from invalid import create_invalidation

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
    farm_list = [60862]
    # create_invalidation()
    for farm_id in farm_list:
        
        client_data = pd.read_csv('/home/satyukt/Projects/1000/aws/soil_health_info/info.csv')


        try:
            id_client,crop,sow = client_data.loc[(client_data['polygon_id'] == int(farm_id)),['client_id','croptype','sowingdate']].values[0]
            local_path = f'/home/satyukt/Projects/1000/soil_health/output/Report/{farm_id}.pdf'
            s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{farm_id}.pdf'
            print(id_client, farm_id)
            uploadfile(local_path, s3path)
        except:
            pass

