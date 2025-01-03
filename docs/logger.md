# Logging

To enable logging within your project and get detailed information from the XMRig-API library, you can configure the logging module in your Python script. Here is an example of how to set up logging:

```python
import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level for the entire application, change to DEBUG to print all responses.
    format='[%(asctime)s - %(name)s] - %(levelname)s - %(message)s',  # Consistent format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

log = logging.getLogger("MyLogger")

# Import the XMRigManager class
from xmrig.manager import XMRigManager

# Example usage
manager = XMRigManager()
log.info("Adding miner")
manager.add_miner("miner1", "127.0.0.1", 8080)
```

This configuration will output detailed debug information to the console, including timestamps, logger names, log levels, and log messages.

