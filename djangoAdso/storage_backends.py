from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Create a SECONDARY client dedicated only to generating public links.
        # This client points to the PUBLIC URL (minio.mishu-soft.org).
        self.signing_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_PUBLIC_ENDPOINT, # We will add this to settings
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=boto3.session.Config(signature_version='s3v4'),
            region_name='us-east-1' # Default MinIO region
        )

    def url(self, name, parameters=None, expire=None, http_method=None):
        # Use the SIGNING client (Public) instead of the default connection (Internal)
        # to generate the Presigned URL.
        
        if expire is None:
            expire = self.querystring_expire

        params = parameters.copy() if parameters else {}
        params['Bucket'] = self.bucket_name
        params['Key'] = name

        url = self.signing_client.generate_presigned_url(
            'get_object',
            Params=params,
            ExpiresIn=expire,
            HttpMethod=http_method
        )
        return url