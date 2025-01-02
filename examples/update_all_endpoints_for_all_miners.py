from env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a, name_b, ip_b, port_b, access_token_b, tls_enabled_b
from xmrig import XMRigManager

manager = XMRigManager()
log.info("Adding miners to the manager...")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
manager.add_miner(name_b, ip_b, port_b, access_token_b, tls_enabled_b)
miner_a = manager.get_miner(name_a)
miner_b = manager.get_miner(name_b)
log.info("Updating all endpoints for all miners")
manager.get_all_miners_endpoints()
