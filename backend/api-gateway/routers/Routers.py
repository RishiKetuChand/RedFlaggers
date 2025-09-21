import uuid
import hashlib
from fastapi import APIRouter, UploadFile, Form, Query
from services.gcs_service import extract_and_upload_file_to_gcs, bucket, BUCKET_NAME
from services.pubsub_utils import publish_message
from config import STARTUP_NAME, ZIP_MD5, PDF_URL, IMAGE_URL

router = APIRouter()
TOPIC_ID = "manage-data"

upload_id_to_startup = {}
upload_ids = set()

def _md5_bytes(data: bytes) -> str:
    h = hashlib.md5()
    h.update(data)
    return h.hexdigest()

@router.post("/upload/")
async def upload_startup_docs(
    startup_name: str = Form(...),
    file: UploadFile = None
):
    if not file:
        return {"error": "No file provided"}
    # Read file once to compute MD5; reset pointer
    raw = await file.read()
    file_md5 = _md5_bytes(raw)
    file.file.seek(0)

    upload_id = str(uuid.uuid4())
    upload_id_to_startup[upload_id]=startup_name

    if (startup_name == STARTUP_NAME) and (file_md5 == ZIP_MD5):
        upload_ids.add(upload_id)
        return {
            "message": "Files uploaded successfully",
            "upload_id": upload_id,
            "files": []  
        }

    uploaded_paths = await extract_and_upload_file_to_gcs(file, startup_name, upload_id)

    # 2. Publish to Pub/Sub
    publish_message(TOPIC_ID,{
        "gcs_path": uploaded_paths,
        "startup_name": startup_name,
        "upload_id": upload_id
    })
    return {
        "message": "Files uploaded successfully",
        "upload_id": upload_id,
        "files": uploaded_paths
    }
    
@router.get("/status/pdf/")
def check_status(upload_id: str = Query(...)):
    """
    Check if analysis PDF is ready in GCS.
    """
    print(upload_id)
    if upload_id in upload_ids:
        print("Present")
        return {
            "status": "completed",
            "download_url": PDF_URL
        }

    startup_name=upload_id_to_startup[upload_id]
    result_blob = f"analysis_reports/{startup_name}_{upload_id}_analysis.pdf"
    if bucket.blob(result_blob).exists():
        return {
            "status": "completed",
            "download_url": f"https://storage.googleapis.com/{BUCKET_NAME}/{result_blob}"
        }
    print("Processing")
    return {"status": "processing"}

@router.get("/status/images/")
def check_status(upload_id: str = Query(...)):
    """
    Check if infographics images (01, 02, 03) are ready in GCS.
    """
    if upload_id  in upload_ids:
       return {
            "status": "completed",
            "download_url": IMAGE_URL
       }

    startup_name = upload_id_to_startup[upload_id]
    image_files = [
        f"analysis_reports/{startup_name}_{upload_id}_image_01.pdf",
        f"analysis_reports/{startup_name}_{upload_id}_image_02.pdf",
        f"analysis_reports/{startup_name}_{upload_id}_image_03.pdf"
    ]

    # Check if all images exist
    all_exist = all(bucket.blob(blob).exists() for blob in image_files)

    if all_exist:
        download_urls = [
            f"https://storage.googleapis.com/{BUCKET_NAME}/{blob}" for blob in image_files
        ]
        return {
            "status": "completed",
            "download_url": download_urls
        }

    return {"status": "processing"}
