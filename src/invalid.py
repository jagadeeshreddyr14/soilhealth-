import boto3
import time

cf = boto3.client('cloudfront',
                aws_access_key_id= "AKIAXMFIWZ7AO7DFOCVK",
                aws_secret_access_key="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")
 
DISTRIBUTION_ID = "EO2OPL2AVSFSD"
 

def create_invalidation():
    res = cf.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': [
                    '/*'
                ]
            },
            'CallerReference': str(time.time()).replace(".", "")
        }
    )
    invalidation_id = res['Invalidation']['Id']
    print("Invalidation created successfully with Id: " + invalidation_id)
    return invalidation_id
if __name__ == "__main__":
    id = create_invalidation()
    print("Invalidation created successfully with Id: " + id)