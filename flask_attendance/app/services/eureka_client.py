import py_eureka_client.eureka_client as eureka_client

def register_with_eureka(app_name: str, port: int) -> None:
    eureka_client.init(
        eureka_server="http://localhost:8761/eureka",
        app_name=app_name,
        instance_port=port,
        instance_host="localhost"
    )