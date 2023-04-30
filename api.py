import json
import logging
import uvicorn
from multiprocessing import freeze_support
from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile
from providers.gcp import process_file_topic_name, upload_storage_file, publish_to_topic, get_storage_client, health_check_topic_name
from typing import Union

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@app.get("/health")
def health_check(request: Request, args: Union[str, None] = None, credentials: Union[str, None] = None):
    logger.info("Health check endpoint accessed\nRequest:\n{request}\nArgs:\n{args}\nCredentials:\n{credentials}")
    # validate args and credentials before using them

    if not args and not credentials:
        return "OK"

    if not args:
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": "args is required."})


    if not credentials:
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": "credentials is required."})
    
    if "owner" not in args:
        raise HTTPException(status_code=401, detail={ "status" : "unauthorized" } )

    args = {
        "service_name": "ie-api",
        "sender_ip": request.client.host,
    }


    message = {"requestor": "ie-api", "arguments": json.dumps(args), "credentials": json.dumps(credentials)}
    messageid = publish_to_topic(message, health_check_topic_name)

    return {
        "api": "active",
        "messaging": "active" if messageid else "inactive",
        "worker": "not implemented",
    }


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
async def upload_file(
    subscriber_id: Union[str, None] = None,
    subscription: Union[str, None] = None,
    file: UploadFile = File(...),
    body: str = Body(...),
):
    if subscriber_id is None or subscription is None:
        error_msg = "subscriber_id and subscription are required."
        logger.error(
            "Bad request received for /ingest-file endpoint: %s", error_msg)
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": error_msg})

    body = json.loads(body) if body else None
    
    result = await upload_storage_file(body, file, subscriber_id)
    
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
