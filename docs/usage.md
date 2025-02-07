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
name_a = "MinerA"
ip_a = "127.0.0.1"
port_a = "37841"
access_token_a = "SECRET"
tls_enabled_a = False
name_b = "MinerB"
ip_b = "127.0.0.1"
port_b = "37842"
access_token_b = "SECRET"
tls_enabled_b = False

manager = XMRigManager()
log.info("Adding miners to the manager...")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
manager.add_miner(name_b, ip_b, port_b, access_token_b, tls_enabled_b)
log.info("Retrieving individual miners...")
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)
log.info(f"Retrieved miner: {miner_a._miner_name}")
log.info(f"Retrieved miner: {miner_b._miner_name}")

# List all miners
log.info("Listing all miners...")
log.info(manager.list_miners())
# Remove miners
log.info(f"Removing miner: {name_a}")
manager.remove_miner(name_a)
# List all miners
log.info("Listing all miners...")
log.info(manager.list_miners())
# Add back for rest of example code
log.info(f"Adding miner back: {name_a}")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
# Get individual miners
log.info("Retrieving individual miners...")
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)
log.info(f"Retrieved miner: {miner_a._miner_name}")
log.info(f"Retrieved miner: {miner_b._miner_name}")
# Update an individual miner's endpoints
log.info(f"Updating endpoints for miner: {miner_a._miner_name}")
miner_a.get_endpoint("summary")
miner_a.get_endpoint("backends")
miner_a.get_endpoint("config")
log.info(f"Updating endpoints for miner: {miner_b._miner_name}")
miner_b.get_endpoint("summary")
miner_b.get_endpoint("backends")
miner_b.get_endpoint("config")
# Update all endpoints for all miners
log.info("Updating all endpoints for all miners...")
manager.update_miners()
# Pause all miners
log.info("Pausing all miners...")
manager.perform_action_on_all("pause")
log.info("Resuming all miners...")
manager.perform_action_on_all("resume")
# Start/stop a specific miner
log.info(f"Stopping miner: {miner_a._miner_name}")
miner_a.perform_action("stop")
log.info(f"Starting miner: {miner_a._miner_name}")
miner_a.perform_action("start")
# Pause/Resume a specific miner
log.info(f"Pausing miner: {miner_b._miner_name}")
miner_b.perform_action("pause")
log.info(f"Resuming miner: {miner_b._miner_name}")
miner_b.perform_action("resume")
# Edit and update the miners `config.json` via the HTTP API.
log.info(f"Editing config for miner: {miner_a._miner_name}")
miner_a.get_endpoint("config")
config = miner_a.config
config["api"]["worker-id"] = "NEW_WORKER_ID"
miner_a.post_config(config)
# Summary and Backends API data is available as properties in either full or individual format.
log.info(f"Summary data for miner: {miner_b._miner_name}")
log.info(miner_b.summary)
log.info(f"Hashrates for miner: {miner_b._miner_name}")
log.info(miner_b.sum_hashrate)
log.info(f"Accepted jobs for miner: {miner_b._miner_name}")
log.info(miner_b.sum_pool_accepted_jobs)
log.info(f"Rejected jobs for miner: {miner_b._miner_name}")
log.info(miner_b.sum_pool_rejected_jobs)
log.info(f"Current difficulty for miner: {miner_b._miner_name}")
log.info(miner_b.sum_current_difficulty)
```

For more examples, visit the [Examples](examples.md) page.