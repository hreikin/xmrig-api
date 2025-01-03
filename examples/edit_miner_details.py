from env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a
from xmrig import XMRigManager

manager = XMRigManager()
log.info("Adding miners to the manager...")
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
miner_a = manager.get_miner(name_a)
log.info(f"Initial miner name: {miner_a._miner_name}")
log.info("Changing miner name...")
new_details = {
    'miner_name': "NewMinerName",
}
manager.edit_miner(name_a, new_details)
miner_a = manager.get_miner("NewMinerName")
log.info(f"New miner name: {miner_a._miner_name}")