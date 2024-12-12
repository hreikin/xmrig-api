from xmrig.api import XMRigAPI
from xmrig.logger import log

class XMRigManager:
    """
    A class to manage multiple XMRig miners via their APIs.
    """

    def __init__(self, api_factory=XMRigAPI):
        """
        Initializes the manager with an empty collection of miners.

        Args:
            api_factory (callable): Factory for creating XMRigAPI instances.
        """
        self._miners = {}
        self._api_factory = api_factory

    def add_miner(self, miner_name: str, ip: str, port: str, access_token: str = None, tls_enabled: bool = False):
        """
        Adds a new miner to the manager.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (int): Port of the XMRig API.
            access_token (str, optional): Access token for authorization. Defaults to None.
            tls_enabled (bool, optional): TLS status of the miner/API. Defaults to False.
        """
        if miner_name in self._miners:
            raise ValueError(f"Miner with name '{miner_name}' already exists.")

        # Use the injected factory to create the API instance
        self._miners[miner_name] = self._api_factory(ip, port, access_token, tls_enabled)
        log.info(f"Miner '{miner_name}' added to manager.")

    def remove_miner(self, miner_name: str):
        """
        Removes a miner from the manager.

        Args:
            miner_name (str): The unique name of the miner to remove.
        """
        if miner_name not in self._miners:
            raise ValueError(f"Miner with name '{miner_name}' does not exist.")
        
        del self._miners[miner_name]
        log.info(f"Miner '{miner_name}' removed from manager.")

    def get_miner(self, miner_name: str) -> XMRigAPI:
        """
        Retrieves a specific miner's API instance.

        Args:
            miner_name (str): The unique name of the miner.

        Returns:
            XMRigAPI: The API instance for the requested miner.
        """
        if miner_name not in self._miners:
            raise ValueError(f"Miner with name '{miner_name}' does not exist.")
        
        return self._miners[miner_name]

    def perform_action_on_all(self, action: str):
        """
        Performs the specified action on all miners.

        Args:
            action (str): The action to perform ('pause', 'resume', 'stop', etc.).
        """
        for miner_name, miner_api in self._miners.items():
            method = getattr(miner_api, f"{action}_miner", None)
            if method and callable(method):
                success = method()
                if success:
                    log.info(f"Action '{action}' successfully performed on '{miner_name}'.")
                else:
                    log.warning(f"Action '{action}' failed on '{miner_name}'.")
            else:
                log.error(f"Action '{action}' is not a valid method for miner API.")

    def update_all_miners(self):
        """
        Updates all miners' cached data.
        """
        for miner_name, miner_api in self._miners.items():
            success = miner_api.update_all_responses()
            if success:
                log.info(f"Miner '{miner_name}' successfully updated.")
            else:
                log.warning(f"Failed to update miner '{miner_name}'.")

    def list_miners(self) -> list:
        """
        Lists all managed miners.

        Returns:
            list: A list of miner names.
        """
        return list(self._miners.keys())
