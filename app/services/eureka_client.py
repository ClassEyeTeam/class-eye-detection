import py_eureka_client.eureka_client as eureka_client
import os
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_with_eureka(app_name: str, port: int) -> None:
    eureka_server = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")
    logger.info("Eureka server URL: %s", eureka_server)

    # Get the container's hostname or IP address
    instance_host = socket.gethostname()
    instance_ip = socket.gethostbyname(instance_host)

    logger.info("Instance host: %s", instance_host)
    logger.info("Instance IP: %s", instance_ip)

    eureka_client.init(
        eureka_server=eureka_server,
        app_name=app_name,
        instance_port=port,
        instance_host=instance_ip
    )
    logger.info("Registered with Eureka: %s", eureka_server)