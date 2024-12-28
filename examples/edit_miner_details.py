from env import log, name_a, ip_a, port_a, access_token_a, tls_enabled_a
from xmrig import XMRigManager

manager = XMRigManager()
manager.add_miner(name_a, ip_a, port_a, access_token_a, tls_enabled_a)
miner_a = manager.get_miner(name_a)
log.info(f"Initial miner name: {miner_a._miner_name}")
log.info("Changing miner name . . .")
new_details = {
    'miner_name': "NewMinerName",
}
miner_a = manager.edit_miner(miner_a, new_details)
log.info(f"New miner name: {miner_a._miner_name}")