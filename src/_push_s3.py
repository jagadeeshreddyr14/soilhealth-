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

    local_path = '/home/satyukt/Desktop/myfiles/soil/report/30257.pdf'

    s3path = 'sat2farm/17309/30257/soilReportPDF/30257.pdf'

    uploadfile(local_path, s3path)
