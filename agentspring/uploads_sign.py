import datetime
from typing import Optional
import boto3
from google.cloud import storage
from .config import settings

def s3_sign_post(bucket: str, key: str, expires_seconds: int = 3600) -> dict:
    s3 = boto3.client("s3")
    fields = {"acl": "private"}
    conditions = [["content-length-range", 0, 104857600]]  # up to 100MB
    post = s3.generate_presigned_post(Bucket=bucket, Key=key, Fields=fields, Conditions=conditions, ExpiresIn=expires_seconds)
    return {"url": post["url"], "fields": post["fields"]}

def gcs_sign_put(bucket: str, key: str, expires_seconds: int = 3600) -> dict:
    cred_json = settings.GCS_CREDENTIALS_JSON
    if cred_json:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(eval(cred_json))
        client = storage.Client(credentials=creds)
    else:
        client = storage.Client()
    b = client.bucket(bucket)
    blob = b.blob(key)
    url = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(seconds=expires_seconds), method="PUT")
    return {"url": url, "headers": {"Content-Type": "application/octet-stream"}}
