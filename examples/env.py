import logging
# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the log level for the entire application, change to DEBUG to print all responses.
    format='[%(asctime)s - %(name)s] - %(levelname)s - %(message)s',  # Consistent format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
log = logging.getLogger("ExampleLog")
name_a = "MinerA"
ip_a = "127.0.0.1"
port_a = "37841"
access_token_a = "SECRET"
tls_enabled_a = False
name_b = "MinerB"
ip_b = "127.0.0.1"
port_b = "37482"
access_token_b = "SECRET"
tls_enabled_b = False

log.info("###################################################################################################################################")
log.info("## Please ensure you have a running XMRig instance to connect to and have updated the connection details within the env.py file. ##")
log.info("###################################################################################################################################")