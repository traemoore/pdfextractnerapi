from providers.gcp import get_project_id, get_subscription_client


subscription_name = 'process-file-sub'

# Define the message handler function to process incoming messages
def message_handler(message):
    # Process the message here
    print(f'Received message: {message}')

    # Acknowledge the message to remove it from the subscription
    message.ack()

# Define the Pub/Sub message listener process
def listen_for_messages():
    # Initialize a subscriber client object
    subscriber = get_subscription_client()

    # Subscribe to the specified subscription and start listening for messages
    subscription_path = subscriber.subscription_path(
        get_project_id(), subscription_name)
    subscriber.subscribe(subscription_path, callback=message_handler)

    # Block the main thread to keep the process running
    print(f'Listening for messages on subscription {subscription_name}...')
    while True:
        pass