from .env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a, name_b, ip_b, port_b, access_token_b, tls_enabled_b
from xmrig import XMRigManager

manager = XMRigManager()
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
manager.add_miner(name_b, ip_b, port_b, access_token_b, tls_enabled_b)
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)

# List all miners
log.info(manager.list_miners())
# Remove miners
manager.remove_miner(name_a)
# List all miners
log.info(manager.list_miners())
# Add back for rest of example code
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
# Get individual miners
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)
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
miner_a.get_config()
config = miner_a.data.config
config["api"]["worker-id"] = "NEW_WORKER_ID"
miner_a.post_config(config)
# Summary and Backends API data is available as properties in either full or individual format.
log.info(miner_b.data.summary)
log.info(miner_b.data.sum_hashrates)
log.info(miner_b.data.sum_pool_accepted_jobs)
log.info(miner_b.data.sum_pool_rejected_jobs)
log.info(miner_b.data.sum_current_difficulty)