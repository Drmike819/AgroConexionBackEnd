# campeche_backend/storages.py
from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    location = '' 
    file_overwrite = False
    default_acl = 'public-read' 