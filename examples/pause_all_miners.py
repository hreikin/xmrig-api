import logging
from xmrig import XMRigManager

# ...existing code...

# Pause all miners
manager = XMRigManager()
manager.add_miner("Miner1", "127.0.0.1", "37841", "SECRET", tls_enabled=False)
manager.add_miner("Miner2", "127.0.0.1", "37842", "SECRET", tls_enabled=False)
manager.perform_action_on_all("pause")
manager.perform_action_on_all("resume")
