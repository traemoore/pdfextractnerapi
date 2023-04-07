import multiprocessing
from multiprocessing import freeze_support
from fastapi import FastAPI, File, HTTPException, UploadFile
from providers.gcp import upload_storage_file, publish_to_topic, get_storage_client, get_subscription_client, get_project_id
from messaging.handlers import listen_for_messages
from typing import Union

app = FastAPI()


# Endpoints
@app.get("/health")
def health_check():
    return {"status": "active"}


@app.get("/gcp-auth")
def gcp_auth_status():
    try:
        buckets = get_storage_client().list_buckets()
        return {"authenticated": buckets is not None}
    except Exception as e:
        return {"error": str(e)}


@app.post("/ingest-file")
async def upload_file(subscriber_id: Union[str, None] = None, subscription: Union[str, None] = None, file: UploadFile = File(...)):
    if subscriber_id is None or subscription is None:
        raise HTTPException(status_code=400, detail={
                            "status": "Bad Request", "error": "subscriber_id and subscription are required."})
    result = await upload_storage_file(file)
    if result["error"]:
        raise HTTPException(status_code=500, detail={
                            "status": "Internal Server Error", "error": result["error"]})
    else:
        message_id = publish_to_topic(result["file_location"], subscriber_id, subscription)
        return {"status": "success", "file_location": result["file_location"], "message_id": message_id}


# Run the FastAPI application
if __name__ == "__main__":
    freeze_support()

    # Start the Pub/Sub message listener process in a separate process
    listener_process = multiprocessing.Process(target=listen_for_messages)
    listener_process.start()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
