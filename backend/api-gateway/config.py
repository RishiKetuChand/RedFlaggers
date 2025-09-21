import os

PROJECT_ID = os.getenv("GCP_PROJECT", "aianalyst-redflaggers")
BUCKET_NAME = os.getenv("BUCKET_NAME", "pitchdeck-storage-289")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION","europe-west3")
CORPUS_ID = os.getenv("CORPUS_ID","projects/aianalyst-redflaggers/locations/europe-west3/ragCorpora/2305843009213693952")
CORPUS_DISPLAY_NAME = os.getenv("CORPUS_DISPLAY_NAME", "startup-docs")

STARTUP_NAME = "Inlustro_Demo"
ZIP_MD5 = "0464abac7076e5079531c36883d0c81f"
PDF_URL = "https://storage.googleapis.com/pitchdeck-storage-289/analysis_reports/InLustro_85c2f6af-e2bd-4836-8068-70e9211849a7_analysis.pdf"
IMAGE_URL = ["https://storage.googleapis.com/pitchdeck-storage-289/analysis_reports/InLustro_2345234562349834_image_1.png","https://storage.googleapis.com/pitchdeck-storage-289/analysis_reports/InLustro_2345234562349834_image_2.png","https://storage.googleapis.com/pitchdeck-storage-289/analysis_reports/InLustro_2345234562349834_image_3.png"]
