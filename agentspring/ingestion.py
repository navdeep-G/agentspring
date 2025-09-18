import io
from typing import List, Tuple
from pypdf import PdfReader
from .config import settings
def _hash(data: bytes) -> str:
    import hashlib as _h; return _h.sha256(data).hexdigest()[:16]
def extract_text(name: str, content: bytes) -> str:
    n = (name or "").lower()
    if n.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        out = []
        for p in reader.pages: out.append(p.extract_text() or "")
        return "\n".join(out)
    try: return content.decode("utf-8")
    except Exception: return content.decode("latin-1", errors="ignore")
def chunk_text(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    chunks=[]; i=0; n=len(text)
    while i<n:
        end=min(n,i+size); chunks.append(text[i:end]); i=end-overlap; i=0 if i<0 else i
    return chunks
def s3_iter_objects(bucket: str, prefix: str = "") -> List[Tuple[str, bytes]]:
    import boto3; s3=boto3.client("s3"); items=[]; kwargs={"Bucket":bucket,"Prefix":prefix}
    while True:
        resp=s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            key=obj["Key"]; 
            if key.endswith("/"): continue
            body=s3.get_object(Bucket=bucket, Key=key)["Body"].read(); items.append((key, body))
        if resp.get("IsTruncated"): kwargs["ContinuationToken"]=resp.get("NextContinuationToken")
        else: break
    return items
def gcs_iter_objects(bucket: str, prefix: str = "") -> List[Tuple[str, bytes]]:
    from google.cloud import storage
    cred_json = settings.GCS_CREDENTIALS_JSON
    if cred_json:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(eval(cred_json))
        client = storage.Client(credentials=creds)
    else:
        client = storage.Client()
    b = client.bucket(bucket); items=[]
    for blob in client.list_blobs(b, prefix=prefix):
        if blob.name.endswith("/"): continue
        items.append((blob.name, blob.download_as_bytes()))
    return items
