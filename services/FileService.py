import logging
from botocore.exceptions import ClientError
import os
from services.Boto3Service import Boto3Service
from config.ConfigService import config


class FileService:
    uploader: Boto3Service

    EXPORTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), '')

    def __init__(self):
        self.uploader = Boto3Service()

    @classmethod
    def get_export_file_path(cls, file_path_within_exports):
        if file_path_within_exports is None:
            return None
        print(file_path_within_exports)
        full_path = os.path.join(FileService.EXPORTS_FOLDER, file_path_within_exports)
        return full_path

    @staticmethod
    def upload_file(file_path, object_name=None):
        print(file_path)
        """Upload a file to an S3 bucket

            :param file_path:
            :param bucket: Bucket to upload to
            :param object_name: S3 object name. If not specified then file_name is used
            :return: True if file was uploaded, else False
            """
        if file_path is None:
            return {"file_url": None, "success": False}

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_path)

        # Upload the file
        s3_client = Boto3Service.get_s3_client()
        try:
            s3_client.upload_file(file_path, config.aws_bucket, object_name)
            file_url = f'https://{config.aws_bucket}.s3.amazonaws.com/{object_name}'
            return {"file_url": file_url, "success": True}
        except ClientError as e:
            logging.error(e)
            print(e)
            return {"file_url": None, "success": False}
