import paho.mqtt.client as mqtt
import os
import logging
import cv2
import numpy as np
from app.services.face_service import recognize_face
from app.services.attendance_service import record_attendance
import queue
import threading
import time
import uuid
import pytz
from datetime import datetime

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


# AUTH_TOKEN = get_auth_token()

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
      3) Log result / skip if no face.
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
                # Record attendance
                local_tz = pytz.timezone('Europe/Paris') 
                timestamp = datetime.now(local_tz).isoformat()
                attendance_data = {
                    "student_id": recognized_student_id,
                    "confidence": confidence,
                    "timestamp": timestamp
                }
                record_attendance(attendance_data)
                logger.info(f"Recognized student: {recognized_student_id}, Confidence: {confidence:.2f}")
            else:
                logger.info("No face detected")
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