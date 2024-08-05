import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_REGION = os.getenv('S3_REGION')
    S3_BUCKET = os.getenv('S3_BUCKET')
    KMS_KEY_ID = os.getenv('KMS_KEY_ID')
    AI71_API_KEY = os.getenv('AI71_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_REGION = os.getenv('PINECONE_REGION')  # Update with your actual region
    PINECONE_HOST = "https://personalized-tests-9zt3ujr.svc.aped-4627-b74a.pinecone.io"  # Add your Pinecone host here

    def __str__(self):
        return (f"SECRET_KEY: {self.SECRET_KEY}\n"
                f"AWS_ACCESS_KEY_ID: {self.AWS_ACCESS_KEY_ID}\n"
                f"AWS_SECRET_ACCESS_KEY: {self.AWS_SECRET_ACCESS_KEY}\n"
                f"S3_REGION: {self.S3_REGION}\n"
                f"S3_BUCKET: {self.S3_BUCKET}\n"
                f"KMS_KEY_ID: {self.KMS_KEY_ID}\n"
                f"AI71_API_KEY: {self.AI71_API_KEY}\n"
                f"PINECONE_API_KEY: {self.PINECONE_API_KEY}\n"
                f"PINECONE_REGION: {self.PINECONE_REGION}\n"
                f"PINECONE_HOST: {self.PINECONE_HOST}\n")
