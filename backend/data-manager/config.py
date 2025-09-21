import os

PROJECT_ID = os.getenv("GCP_PROJECT", "aianalyst-redflaggers")
BUCKET_NAME = os.getenv("BUCKET_NAME", "pitchdeck-storage-289")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION","europe-west3")
CORPUS_ID = os.getenv("CORPUS_ID","projects/aianalyst-redflaggers/locations/europe-west3/ragCorpora/2305843009213693952")
CORPUS_DISPLAY_NAME = os.getenv("CORPUS_DISPLAY_NAME", "startup-docs")
