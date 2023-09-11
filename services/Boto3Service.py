from boto3 import client
from config.ConfigService import config
from botocore.client import BaseClient


class Boto3Service:
    aws_access_key_id: str = config.aws_access_key_id
    aws_secret_access_key: str = config.aws_secret_access_key
    aws_bucket: str = config.aws_bucket
    region_name: str = config.aws_default_region

    @staticmethod
    def get_s3_client() -> BaseClient:
        return client(
            "s3",
            aws_access_key_id=Boto3Service.aws_access_key_id,
            aws_secret_access_key=Boto3Service.aws_secret_access_key,
            region_name=Boto3Service.region_name
        )
