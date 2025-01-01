from app import create_app
from app.services.eureka_client import register_with_eureka
import os
import app.services.mqtt_client as mqtt_client

import logging
from dotenv import load_dotenv

# Configure logging to output to the console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create and run the app
app = create_app()

# Register with Eureka
eureka_server = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")
logger.info("Eureka server URL: %s", eureka_server)
register_with_eureka("face-detection-service", 5000)


mqtt_client.client.loop_start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)