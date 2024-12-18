import py_eureka_client.eureka_client as eureka_client
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_with_eureka(app_name: str, port: int) -> None:
    eureka_server = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")
    logger.info("Eureka server URL: %s", eureka_server)
    eureka_client.init(
        eureka_server=eureka_server,
        app_name=app_name,
        instance_port=port,
        instance_host="localhost"
    )
    logger.info("Registered with Eureka: %s", eureka_server)