## Installation

The module can be installed from PyPi or Github with pip:

```
pip install xmrig-api

# Or to install from the Github repository
pip install xmrig-api@git+https://github.com/hreikin/xmrig-api.git@main     # Can use a tag, commit hash, branch, etc
```

## Usage

Here is a basic implementation of the API Wrapper now dubbed XMRigAPI.

```python
import logging
from xmrig import XMRigManager

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

log.info("###############################################################################################################################")
log.info("## Please ensure you have a running XMRig instance to connect to and have updated the connection details within the example. ##")
log.info("###############################################################################################################################")

# Add miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.add_miner("Miner2", "127.0.0.1", "37842", "SECRET", tls_enabled=False)
# Remove miners
manager.remove_miner("Miner1")
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)      # Add back for rest of example code

# List all miners
log.info(manager.list_miners())

# Get individual miners
miner_a = manager.get_miner("Miner1")
miner_b = manager.get_miner("Miner2")

# Update an individual miner's endpoints
miner_a.get_summary()
miner_a.get_backends()
miner_a.get_config()
miner_b.get_summary()
miner_b.get_backends()
miner_b.get_config()

# Update all endpoints for all miners
manager.get_all_miners_endpoints()

# Pause all miners
manager.perform_action_on_all("pause")
manager.perform_action_on_all("resume")

# Start/stop a specific miner
miner_a.stop_miner()
miner_a.start_miner()

# Pause/Resume a specific miner
miner_b.pause_miner()
miner_b.resume_miner()

# Edit and update the miners `config.json` via the HTTP API.
miner_a.get_config()                                                       # This updates the cached data
config = miner_a.data.config                                               # Use the `config` property to access the data
config["api"]["worker-id"] = "NEW_WORKER_ID"                               # Change something
miner_a.post_config(config)                                                # Post new config to change it

# Summary and Backends API data is available as properties in either full or individual format.
log.info(miner_b.data.summary)                                             # Prints the entire `summary` endpoint response
log.info(miner_b.data.sum_hashrates)                                       # Prints out the current hashrates
log.info(miner_b.data.sum_pool_accepted_jobs)                              # Prints out the accepted_jobs counter
log.info(miner_b.data.sum_pool_rejected_jobs)                              # Prints out the rejected_jobs counter
log.info(miner_b.data.sum_current_difficulty)                              # Prints out the current difficulty
```

For more examples, visit the [Examples](examples.md) page.