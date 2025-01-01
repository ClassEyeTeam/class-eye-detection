import paho.mqtt.client as mqtt
import cv2
import numpy as np
import queue
import threading
# MQTT settings
broker = 'test.mosquitto.org'
port = 1883
topic = 'esp32/cam'
image_queue = queue.Queue()
# Callback when a message is received
def on_message(client, userdata, msg):
    # Convert bytes directly to numpy array
    nparr = np.frombuffer(msg.payload, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return
    
    # Quick face detection before full recognition
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        return
        
    # Only proceed with DeepFace if face detected
    image_queue.put(img)

# Initialize MQTT client
client = mqtt.Client()
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(broker, port)

# Subscribe to topic
client.subscribe(topic)

# Start MQTT loop
client.loop_start()

print(f"Subscribed to topic: {topic}. Waiting for messages...")

# Keep the script running and allow OpenCV to update the display
try:
    while True:
        cv2.waitKey(100)  # Wait for 100 ms to allow OpenCV to process events
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()