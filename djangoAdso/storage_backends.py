# core/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from djangoAdso.settings import DEBUG

class MediaStorage(S3Boto3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        # 1. Generate the signed URL using the internal connection (http://minio:9000)
        url = super().url(name, parameters, expire, http_method)
        
        # 2. Replace the internal Docker address with your public domain
        #    This keeps the ?Signature=... part intact
        if DEBUG:
            return url.replace('http://minio:9000', 'https://minio.mishu-soft.org')
        else:
            return url.replace('http://minio:9000', 'https://minio.adso-peru.org')