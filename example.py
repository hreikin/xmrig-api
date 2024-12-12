import logging
from xmrig import XMRigManager

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the log level for the entire application, change to DEBUG to print all responses.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Consistent format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
log = logging.getLogger("MyLog")

# Add miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.add_miner("Miner2", "127.0.0.1", "37842", "SECRET", tls_enabled=False)

# Pause all miners
manager.perform_action_on_all("pause")
manager.perform_action_on_all("resume")

# Resume a specific miner
miner = manager.get_miner("Miner1")
miner.stop_miner()
miner.start_miner()

# Update data for a specific miner
miner = manager.get_miner("Miner2")
miner.update_summary()

# Edit and update the miners `config.json` via the HTTP API.
miner = manager.get_miner("Miner1")
miner.update_config()                                                 # This updates the cached data
config = miner.config                                                 # Use the `config` property to access the data
config["api"]["worker-id"] = "ubuntu-cpu"                          # Change something
miner.post_config(config)                                             # Post new config to change it

# Update data for all miners
manager.update_all_miners()

# List all miners
log.info(manager.list_miners())

# Summary and Backends API data is available as properties in either full or individual format.
miner = manager.get_miner("Miner2")
log.info(miner.summary)                                             # Prints the entire `summary` endpoint response
log.info(miner.sum_hashrates)                                       # Prints out the current hashrates
log.info(miner.sum_pool_accepted_jobs)                              # Prints out the accepted_jobs counter
log.info(miner.sum_pool_rejected_jobs)                              # Prints out the rejected_jobs counter
log.info(miner.sum_current_difficulty)                              # Prints out the current difficulty