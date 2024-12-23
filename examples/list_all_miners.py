import logging
from xmrig import XMRigManager

# Remove miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.remove_miner("Miner1")
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)  # Add back for rest of example code

# List all miners
log = logging.getLogger("MyLog")
log.info(manager.list_miners())
