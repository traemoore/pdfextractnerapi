import logging
import multiprocessing
from multiprocessing import freeze_support
from fastapi import FastAPI, File, HTTPException, UploadFile
from providers.gcp import upload_storage_file, publish_to_topic, get_storage_client, get_subscription_client, get_project_id
from messaging.handlers import listen_for_messages
from typing import Union

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Endpoints
@app.get("/health")
def health_check():
    logging.info("Health check endpoint accessed")
    return {"status": "active"}


@app.get("/gcp-auth")
def gcp_auth_status():
    try:
        buckets = get_storage_client().list_buckets()
        logging.info("GCP authentication status endpoint accessed. Authenticated: %s", buckets is not None)
        return {"authenticated": buckets is not None}
    except Exception as e:
        logging.error("Error occurred during GCP authentication status check: %s", e)
        return {"error": str(e)}


@app.post("/ingest-file")
async def upload_file(subscriber_id: Union[str, None] = None, subscription: Union[str, None] = None, file: UploadFile = File(...)):
    if subscriber_id is None or subscription is None:
        error_msg = "subscriber_id and subscription are required."
        logging.error("Bad request received for /ingest-file endpoint: %s", error_msg)
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": error_msg})
    
    result = await upload_storage_file(file)
    
    if result["error"]:
        error_msg = result["error"]
        logging.error("Error occurred during file upload: %s", error_msg)
        raise HTTPException(status_code=500, detail={
                            "status": "Internal Server Error", "error": error_msg})
    else:
        message_id = publish_to_topic(result["file_location"], subscriber_id, subscription)
        logging.info("File upload successful. Message published to Pub/Sub. Message ID: %s", message_id)
        return {"status": "success", "file_location": result["file_location"], "message_id": message_id}


# Run the FastAPI application
if __name__ == "__main__":
    freeze_support()

    # Start the Pub/Sub message listener process in a separate process
    listener_process = multiprocessing.Process(target=listen_for_messages)
    listener_process.start()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
