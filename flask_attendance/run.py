from app import create_app
from app.services.eureka_client import register_with_eureka
import os
import logging
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()
# Create and run the app
app = create_app()

if __name__ == "__main__":
    logger.info("the eurikaservice url is {} ",os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka") )
    register_with_eureka("face-detection-service", 5000)
    app.run(host="0.0.0.0", port=5000)