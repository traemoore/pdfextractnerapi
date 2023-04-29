import json
import logging
from providers.gcp import get_project_id, get_subscription_client
from extraction import process_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

process_file_sub = "process-file-sub"
processed_file_results_sub = "processed-file-results-sub"

# Define the message handler function to process incoming messages
def process_file_message_handler(message):
    # Process the message here
    logger.info(f"Received process request: {message}")
    # b'{"storage_path": "extractner-ingestion/testCompany/test.txt", "subscriber_id": "testCompany", "subscription": "extractionresponse"}'
    message.ack()
    data = json.loads(message.data.decode('utf-8'))
    storage_path = data["storage_path"]
    subscriber_id = data["subscriber_id"]
    
    try:
        message_id = process_document(storage_path, subscriber_id)
    except Exception as e:
        logger.error(f"Error processing file: {storage_path}\n for subscriber_id: {subscriber_id} error:\n{e}")
        
    
    

def test_process_file_results_message_handler(message):
    # Process the message here
    logger.info(f"Received process results: {message}")

    # Acknowledge the message to remove it from the subscription

# Define the Pub/Sub message listener process
def listen_for_messages():
    # Initialize a subscriber client object
    subscriber = get_subscription_client()

    # Subscribe to the specified subscription and start listening for messages
    process_file_sub_path = subscriber.subscription_path(
        get_project_id(), process_file_sub)
    subscriber.subscribe(process_file_sub_path, callback=process_file_message_handler)
    logger.info(f"Listening for messages on subscription {process_file_sub}...")
    
    process_file_results_sub_path = subscriber.subscription_path(
        get_project_id(), processed_file_results_sub)
    subscriber.subscribe(process_file_results_sub_path, callback=test_process_file_results_message_handler)
    logger.info(f"Listening for messages on subscription {processed_file_results_sub}...")
   
    while True:
        pass