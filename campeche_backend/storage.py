from storages.backends.s3boto3 import S3Boto3Storage
import os

class PublicMediaStorage(S3Boto3Storage):
    """
    Almacenamiento para archivos públicos como imágenes de productos.
    Usa las variables AWS_* del settings.py para el nombre del bucket.
    """
    location = ''
    default_acl = 'public-read'
    file_overwrite = False