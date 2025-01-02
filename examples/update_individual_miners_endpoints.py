from env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a, name_b, ip_b, port_b, access_token_b, tls_enabled_b
from xmrig import XMRigManager

manager = XMRigManager()
log.info("Adding miners to the manager...")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
manager.add_miner(name_b, ip_b, port_b, access_token_b, tls_enabled_b)
log.info("Retrieving individual miners...")
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)
log.info(f"Updating endpoints for {name_a}")
miner_a.get_endpoint("summary")
miner_a.get_endpoint("backends")
miner_a.get_endpoint("config")
log.info(f"Updating endpoints for {name_b}")
miner_b.get_endpoint("summary")
miner_b.get_endpoint("backends")
miner_b.get_endpoint("config")
