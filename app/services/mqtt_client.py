import paho.mqtt.client as mqtt
import os
import logging
import cv2
import numpy as np
from app.services.face_service import process_images, recognize_face
import queue
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "esp32/cam")
IMAGE_SAVE_PATH = os.getenv("IMAGE_SAVE_PATH", "uploads")

# Ensure the upload directory exists
if not os.path.exists(IMAGE_SAVE_PATH):
    os.makedirs(IMAGE_SAVE_PATH)

# Create a queue to manage incoming images
image_queue = queue.Queue()

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    logger.info("Connected to MQTT Broker with result code %s", str(rc))
    client.subscribe(MQTT_TOPIC)

# Callback when a PUBLISH message is received from the server
# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    logger.info("Received message on topic %s", msg.topic)
    image_data = msg.payload
    image_path = os.path.join(IMAGE_SAVE_PATH, "received_image.jpg")
    with open(image_path, "wb") as f:
        f.write(image_data)
    logger.info("Image saved to %s", image_path)
    image_queue.put(image_path)


# Function to process images from the queue
def process_image_queue():
    while True:
        image_path = image_queue.get()
        if image_path is None:
            break
        # Process the image for face detection and recognition
        recognized_student_id, confidence = recognize_face(image_path)

        # Load the image using OpenCV
        img = cv2.imread(image_path)
        if img is not None:
            # Annotate the image with the user ID or "unknown"
            if recognized_student_id:
                print(f"Recognized student: {recognized_student_id}, Confidence: {confidence:.2f}")
                label = f"ID: {recognized_student_id}, Confidence: {confidence:.2f}"
            else:
                label = "No face detected"
                print("No face detected")
            cv2.putText(img, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Received Image', img)
            cv2.waitKey(1)  # Display the image for 1 ms
        else:
            logger.error("Failed to load image for display")
        image_queue.task_done()

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT client loop
client.loop_start()

# Start the image processing thread
image_processing_thread = threading.Thread(target=process_image_queue)
image_processing_thread.start()