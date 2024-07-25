import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_REGION = os.getenv('S3_REGION')
    S3_BUCKET = os.getenv('S3_BUCKET')
    KMS_KEY_ID = os.getenv('KMS_KEY_ID')

    def __str__(self):
        return (f"SECRET_KEY: {self.SECRET_KEY}\n"
                f"AWS_ACCESS_KEY_ID: {self.AWS_ACCESS_KEY_ID}\n"
                f"AWS_SECRET_ACCESS_KEY: {self.AWS_SECRET_ACCESS_KEY}\n"
                f"S3_REGION: {self.S3_REGION}\n"
                f"S3_BUCKET: {self.S3_BUCKET}\n"
                f"KMS_KEY_ID: {self.KMS_KEY_ID}\n")
