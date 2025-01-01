import paho.mqtt.client as mqtt
import os
import logging
import cv2
import numpy as np
from app.services.face_service import recognize_face
import queue
import threading
import time
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = os.getenv("MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "esp32/cam")
IMAGE_SAVE_PATH = os.getenv("IMAGE_SAVE_PATH", "uploads")

if not os.path.exists(IMAGE_SAVE_PATH):
    os.makedirs(IMAGE_SAVE_PATH)

# Queue for images
image_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    logger.info("Connected to MQTT Broker with result code %s", str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    logger.info("Received message on topic %s", msg.topic)
    image_data = msg.payload
    # Generate a unique filename for each image
    unique_filename = f"image_{uuid.uuid4().hex}.jpg"
    image_path = os.path.join(IMAGE_SAVE_PATH, unique_filename)
    with open(image_path, "wb") as f:
        f.write(image_data)
    logger.info("Image saved to %s", image_path)
    image_queue.put(image_path)

def process_image_queue():
    """
    Continuously process incoming images from the queue:
      1) Quickly check for a face with a Haar cascade.
      2) If found, run DeepFace recognition.
      3) Display result / skip if no face.
      4) Delete the image after processing.
    """
    while True:
        image_path = image_queue.get()
        if image_path is None:
            break

        start_time = time.time()
        recognized_student_id, confidence = recognize_face(image_path)
        img = cv2.imread(image_path)
        if img is not None:
            if recognized_student_id:
                label = f"ID: {recognized_student_id} (conf: {confidence:.2f})"
            else:
                label = "No face detected"
            cv2.putText(img, label, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Received Image', img)
            cv2.waitKey(1)
        else:
            logger.error("Failed to load image for display")

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info("Processed image in %.2f seconds", processing_time)

        # Delete the image after processing
        try:
            os.remove(image_path)
            logger.info("Deleted image %s", image_path)
        except Exception as e:
            logger.error("Failed to delete image %s: %s", image_path, e)

        image_queue.task_done()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Start the worker thread to process images
image_processing_thread = threading.Thread(target=process_image_queue, daemon=True)
image_processing_thread.start()