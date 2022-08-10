import boto3

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
    
    
    id_client = '17684'
    farm_id = '55633'
    
    local_path = f'/home/satyukt/Projects/1000/soil_health/output/Report/{farm_id}.pdf'

    s3path = f'sat2farm/{id_client}/{farm_id}/soilReportPDF/{farm_id}.pdf'

    uploadfile(local_path, s3path)
