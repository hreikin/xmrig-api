import logging
from xmrig import XMRigManager

# Get individual miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.add_miner("Miner2", "127.0.0.1", "37842", "SECRET", tls_enabled=False)
miner_a = manager.get_miner("Miner1")
miner_b = manager.get_miner("Miner2")

# Update an individual miner's endpoints
miner_a.get_summary()
miner_a.get_backends()
miner_a.get_config()
miner_b.get_summary()
miner_b.get_backends()
miner_b.get_config()
