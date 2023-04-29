import json
import logging
from extractlib.document.process import process_document as extract_document
from fastapi import HTTPException
from providers.gcp import processed_file_results_topic_name, process_file_failure_topic_name, download_storage_file, publish_to_topic
import tempfile

logging.basicConfig(level=logging.INFO)

def process_document(url_path: str, subscriber: str):
    
    parts = url_path.split('/')
    target = parts[1:]
    path = '/'.join(target)
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            path = download_document(temp_dir, path)
        except HTTPException as e:
            logging.error("Error while downloading document: %s", e)
            raise e
        except Exception as e:
            logging.error("Unexpected error while downloading document: %s", e)
            raise HTTPException(status_code=500, detail=str(e))
        
        if path is None:
            raise HTTPException(status_code=404, detail="Document not found")

        try:
            result = extract_document(path, use_multithreading=True)
            result_message = {
                "storage_path": url_path,
                "subscriber_id": subscriber,
                "topic": "processed-file-results",
                "results": json.dumps(result)
            }
            
            logging.info("sending message:\n%s", result_message)
            message_id = publish_to_topic(result_message, processed_file_results_topic_name)
            return message_id
        except Exception as e:
            logging.error("Error during document extraction: %s", e)
            message_id = publish_to_topic(
                {'storage_path': url_path, 
                 'subscriber_id': subscriber, 
                 'reason': str(e) }, process_file_failure_topic_name)
            if not message_id:
                logging.error("Error publishing message to topic: %s", e)
                raise HTTPException(status_code=500, detail=str(e))
            # raise HTTPException(status_code=500, detail=str(e))

    return True

def download_document(temp_dir: str, url_path: str):
    file_bites = download_storage_file(url_path)
    file_name = url_path.split('/')[-1]

    # use a tempdir to store the file
    path = f"{temp_dir}/{file_name}"
    with open(path, "wb") as f:
        f.write(file_bites)

    return path
