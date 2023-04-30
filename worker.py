import logging
import multiprocessing
from multiprocessing import freeze_support
from messaging.handlers import listen_for_messages

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Run the FastAPI application
if __name__ == "__main__":
    freeze_support()
    
    logger.info("Starting Pub/Sub message listener...")
    
    # Start the Pub/Sub message listener process in a separate process
    listener_process = multiprocessing.Process(target=listen_for_messages)
    listener_process.start()

    while True:
        pass  