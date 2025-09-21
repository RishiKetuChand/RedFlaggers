import json
from google.cloud import pubsub_v1
from config import PROJECT_ID, GOOGLE_CLOUD_LOCATION
from services.pubsub_utils import publish_message
from services.corpus_manager import upload_gcs_pdf_to_corpus, create_or_get_corpus
import vertexai
import os

SUBSCRIPTION_ID = "manage-data-sub"
TOPIC_ID = "retrieve-data"


def callback(message: pubsub_v1.subscriber.message.Message):
    print(f"\n📩 Received message: {message.data.decode('utf-8')}")
    try:
        payload = json.loads(message.data.decode("utf-8"))
        gcs_path = payload.get("gcs_path", [])
        startup_name = payload.get("startup_name", "unknown")
        upload_id = payload.get("upload_id")

        if not gcs_path:
            print("⚠️ No google cloud path found in message")
            message.ack()
            return

        #for gcs_uri in gcs_path:

        CORPUS_ID = create_or_get_corpus(startup_name)
        print(f"📤 Uploading {gcs_path} to Vertex AI corpus {CORPUS_ID} [startup={startup_name}]")
        
        upload_gcs_pdf_to_corpus(corpus_id = CORPUS_ID,
                                    gcs_path = gcs_path,
                                    startup_name = startup_name
                                    )

        print(f"✅ Upload complete for upload_id={upload_id}, startup={startup_name}")
        
        # 2. Publish message to "analyse-data"
        publish_message(TOPIC_ID, {
            "startup_name": startup_name,
            "upload_id": upload_id,
            "rag_corpus": CORPUS_ID
        })
        print(f"🚀 Published analyse request for {startup_name}/{upload_id}")
        message.ack()

    except Exception as e:
        print(f"❌ Error processing message: {e}")
        message.nack()

def main():
    print("Starting data-manager...")
    print("GOOGLE_APPLICATION_CREDENTIALS =", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    vertexai.init(project=PROJECT_ID, location=GOOGLE_CLOUD_LOCATION)
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    print(f"Listening for messages on {subscription_path} ...")

    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()

if __name__ == "__main__":
    main()
