import logging
import uvicorn
from multiprocessing import freeze_support
from fastapi import FastAPI, File, HTTPException, UploadFile
from providers.gcp import process_file_topic_name, upload_storage_file, publish_to_topic, get_storage_client
from typing import Union

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "active"}


@app.get("/auth")
def gcp_auth_status():
    try:
        buckets = get_storage_client().list_buckets()
        logger.info(
            "GCP authentication status endpoint accessed. Authenticated: %s", buckets is not None)
        return {"authenticated": buckets is not None}
    except Exception as e:
        logger.error(
            "Error occurred during GCP authentication status check: %s", e)
        return {"error": str(e)}


@app.post("/ingest-file")
async def upload_file(subscriber_id: Union[str, None] = None, subscription: Union[str, None] = None, file: UploadFile = File(...)):
    if subscriber_id is None or subscription is None:
        error_msg = "subscriber_id and subscription are required."
        logger.error(
            "Bad request received for /ingest-file endpoint: %s", error_msg)
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": error_msg})

    result = await upload_storage_file(file, subscriber_id)

    if result["error"]:
        error_msg = result["error"]
        logger.error("Error occurred during file upload: %s", error_msg)
        raise HTTPException(status_code=500, detail={
                            "status": "Internal Server Error", "error": error_msg})
    else:
        file_location = result["file_location"]
        message_id = publish_to_topic(
            {"storage_path": result["file_location"], 
             "subscriber_id": subscriber_id, 
             "subscription": subscription}, process_file_topic_name)
        
        logger.info(
            f"File uploaded to {file_location} successfully. Message published to Pub/Sub. Message ID: {message_id}", )
        return {"status": "success", "file_location": result["file_location"], "message_id": message_id}


# Run the FastAPI application
if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
