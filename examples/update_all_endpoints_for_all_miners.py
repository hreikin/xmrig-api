import logging
from xmrig import XMRigManager

# ...existing code...

# Update all endpoints for all miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.add_miner("Miner2", "127.0.0.1", "37842", "SECRET", tls_enabled=False)
manager.get_all_miners_endpoints()
