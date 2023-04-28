import io
import logging
import json
from typing import Union
from avro.schema import parse
from avro.io import BinaryEncoder, DatumWriter
from fastapi import File, UploadFile
from google.api_core.exceptions import NotFound
from google.cloud import pubsub_v1, storage
from google.cloud.pubsub import SchemaServiceClient
from google.pubsub_v1.types import Encoding
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file('./providers/secrets/gcp_client_secret.json')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# set global variables
project_id = creds.project_id
topic_name = f'process-file'
bucket_name = 'extractner-ingestion'
schema_folder = 'message-schemas'
request_schema_id = 'extraction-request'
response_schema_id = 'extraction-response'

# Initialize a publisher_client client object and a storage client object
subscriber_client = pubsub_v1.SubscriberClient(credentials=creds)
publisher_client = pubsub_v1.PublisherClient(credentials=creds)
storage_client = storage.Client(credentials=creds)
schema_client = SchemaServiceClient(credentials=creds)
schema_cache = {}

def get_project_id():
    return creds.project_id

async def upload_storage_file(file: UploadFile, folder: str = 'default') -> dict:
    try:
        bucket = storage_client.get_bucket(bucket_name)
        upload_path = f'{folder}/{file.filename}'
        blob = bucket.blob(upload_path)
        blob.upload_from_file(file.file, content_type=file.content_type)
        logging.info(f"Uploaded file: {upload_path}")
        return {
            "file_location": f'{bucket_name}/{upload_path}',
            "content_type": file.content_type,
            "error": False
        }
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return {
            "file_location": None,
            "content_type": None,
            "error": str(e)
        }


def get_storage_client():
    return storage_client

def get_subscription_client():
    return subscriber_client

def get_schema(schema_id):
    try:
        # check if schema exists in schema cache
        if schema_id in schema_cache:
            return schema_cache[schema_id]

        # Get the schema object from GCP
        schema_path = schema_client.schema_path(project_id, schema_id)
        schema = schema_client.get_schema(request={"name": schema_path})        
        schema_cache[schema_id] = parse(schema.definition)

        return schema_cache[schema_id]
    except Exception as e:
        logging.error(f"Error getting schema: {e}")
        return None

def publish_to_topic(storage_path, subscriber_id, subscription):
   
    # Fetch the Topic schema from GCP
    avro_schema = get_schema(request_schema_id)
    
    if avro_schema is None:
        raise Exception("Topic schema not found.")
    
    record = {
            "storage_path": storage_path,
            "subscriber_id": subscriber_id,
            "subscription": subscription
        }

    topic_path  = publisher_client.topic_path(project_id, topic_name)
    message_schema_validation = avro_schema.validate(record)

    if message_schema_validation is None:
        raise Exception("Message schema validation failed.")
    
    message_id = send_message(avro_schema, record, topic_path)

    logging.info(f"Published message ID: {message_id}")
    return message_id

def send_message(avro_schema, record, topic_path):
    writer = DatumWriter(avro_schema)
    bout = io.BytesIO()
    try:
        # Get the topic encoding type.
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding

        # Encode the data according to the message serialization type.
        if encoding == Encoding.BINARY:
            encoder = BinaryEncoder(bout)
            writer.write(record, encoder)
            data = bout.getvalue()
            print(f"Preparing a binary-encoded message:\n{data.decode()}")
        elif encoding == Encoding.JSON:
            data_str = json.dumps(record)
            print(f"Preparing a JSON-encoded message:\n{data_str}")
            data = data_str.encode("utf-8")
        else:
            print(f"No encoding specified in {topic_path}. Abort.")
            exit(0)

        future = publisher_client.publish(topic_path, data)
        return future.result()
    except NotFound:
        print(f"{topic_name} not found.")