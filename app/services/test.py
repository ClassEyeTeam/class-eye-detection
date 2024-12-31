import paho.mqtt.client as mqtt
import cv2
import numpy as np

# MQTT settings
broker = 'test.mosquitto.org'
port = 1883
topic = 'esp32/cam'

# Callback when a message is received
def on_message(client, userdata, message):
    print(f"Received message on topic {message.topic}, size: {len(message.payload)} bytes")
    try:
        # Convert binary data to numpy array
        np_arr = np.frombuffer(message.payload, np.uint8)
        # Decode image
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is not None:
            # Display image
            cv2.imshow('Received Image', img)
            cv2.waitKey(1)  # Display the image for 1 ms
        else:
            print("Failed to decode image")
    except Exception as e:
        print(f"Error processing message: {e}")

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