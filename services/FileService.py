import logging
import boto3
from botocore.exceptions import ClientError
import os
from services.Boto3Service import Boto3Service
from services.ConfigService import config


class FileService:
    uploader: Boto3Service

    def __init__(self):
        self.uploader = Boto3Service()

    @staticmethod
    def upload_file(file_name, object_name=None):
        """Upload a file to an S3 bucket

            :param file_name: File to upload
            :param bucket: Bucket to upload to
            :param object_name: S3 object name. If not specified then file_name is used
            :return: True if file was uploaded, else False
            """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = Boto3Service.get_s3_client()
        try:
            s3_client.upload_file(file_name, config.aws_bucket, object_name)
            file_url = f'https://{config.aws_bucket}.s3.amazonaws.com/{object_name}'
            return {"file_url": file_url, "success": True}
        except ClientError as e:
            logging.error(e)
            print(e)
            return {"file_url": None, "success": False}
