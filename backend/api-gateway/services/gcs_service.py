from google.cloud import storage
from config import BUCKET_NAME
import os
import tempfile
import zipfile
import tarfile
from fastapi import UploadFile

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)   # ✅ Define bucket here

async def extract_and_upload_file_to_gcs(file: UploadFile, startup_name, upload_id):
    """
    Save uploaded zip/tar/pdf to a temp folder and upload to GCS immediately.
    Returns [(gcs_path, filename), ...]
    """
    uploaded_paths = []

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        files_to_process = []
        if file.filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)
                for fname in zip_ref.namelist():
                    path = os.path.join(tmpdir, fname)
                    if os.path.isfile(path):
                        files_to_process.append((path, fname))

        elif file.filename.endswith((".tar", ".tar.gz", ".tgz")):
            with tarfile.open(file_path, "r:*") as tar_ref:
                tar_ref.extractall(tmpdir)
                for fname in tar_ref.getnames():
                    path = os.path.join(tmpdir, fname)
                    if os.path.isfile(path):
                        files_to_process.append((path, fname))

        elif file.filename.endswith(".pdf"):
            files_to_process.append((file_path, file.filename))
        else:
            raise ValueError("File must be .pdf, .zip or .tar(.gz)")

        # ✅ Upload inside the tempdir context
        for path, fname in files_to_process:
            blob_name = f"{startup_name}/{upload_id}_{fname}"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(path)
            uploaded_paths.append(f"gs://{BUCKET_NAME}/{blob_name}")

    return uploaded_paths
