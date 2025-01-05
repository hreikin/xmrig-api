from env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a, name_b, ip_b, port_b, access_token_b, tls_enabled_b
from xmrig import XMRigManager

manager = XMRigManager()
log.info("Adding miners to the manager...")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
manager.add_miner(name_b, ip_b, port_b, access_token_b, tls_enabled_b)
miner_a = manager.get_miner(name_a)
log.info(f"{miner_a._miner_name} Full JSON Data Examples")
log.info(f"Summary Endpoint: {miner_a.summary}")
log.info(f"Backends Endpoint: {miner_a.backends}")
log.info(f"Config Endpoint: {miner_a.config}")
miner_b = manager.get_miner(name_b)
log.info(f"{miner_b._miner_name} Individual Data Examples")
log.info(f"Hashrates: {miner_b.sum_hashrates}")
log.info(f"Accepted Jobs: {miner_b.sum_pool_accepted_jobs}")
log.info(f"Rejected Jobs: {miner_b.sum_pool_rejected_jobs}")