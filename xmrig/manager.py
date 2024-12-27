"""
XMRig Manager module.

This module provides the XMRigManager class to manage multiple XMRig miners via their APIs.
It includes functionalities for:

- Adding new miners to the manager.
- Removing miners from the manager.
- Retrieving a specific miner's API instance.
- Performing actions (e.g., pause, resume, stop) on all managed miners.
- Updating all miners' cached data.
- Listing all managed miners.
- Deleting all miner-related data from the database.
"""
import requests
from xmrig.api import XMRigAPI
from xmrig.helpers import log, XMRigAPIError
from xmrig.db import XMRigDatabase
from typing import Callable, Optional, List

class XMRigManager:
    """
    A class to manage multiple XMRig miners via their APIs.

    Attributes:
        _miners (Dict[str, XMRigAPI]): A dictionary to store miner API instances.
        _api_factory (Callable[..., XMRigAPI]): Factory for creating XMRigAPI instances.
        _db_url (str): Database URL for storing miner data.
        _db_engine (Optional[Engine]): SQLAlchemy engine instance for database operations.
    """

    def __init__(self, api_factory: Callable[..., XMRigAPI] = XMRigAPI, db_url: str = 'sqlite:///xmrig-api.db'):
        """
        Initializes the manager with an empty collection of miners.

        Args:
            api_factory (Callable): Factory for creating XMRigAPI instances.
            db_url (str): Database URL for storing miner data.
        """
        self._miners = {}
        self._api_factory = api_factory
        self._db_url = db_url
        self._db_engine = None
        if self._db_url is not None:
            self._db_engine = XMRigDatabase.init_db(self._db_url)

    def add_miner(self, miner_name: str, ip: str, port: int, access_token: Optional[str] = None, tls_enabled: bool = False) -> None:
        """
        Adds a new miner to the manager.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (int): Port of the XMRig API.
            access_token (Optional[str], optional): Access token for authorization. Defaults to None.
            tls_enabled (bool, optional): TLS status of the miner/API. Defaults to False.
        """
        try:
            if miner_name in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' already exists.")

            # Use the injected factory to create the API instance
            self._miners[miner_name] = self._api_factory(miner_name, ip, port, access_token, tls_enabled, self._db_url)
            log.info(f"Miner '{miner_name}' added to manager.")
        except Exception as e:
            log.error(f"An error occurred adding miner '{miner_name}': {e}")
            raise XMRigAPIError() from e

    def remove_miner(self, miner_name: str) -> None:
        """
        Removes a miner from the manager.

        Args:
            miner_name (str): The unique name of the miner to remove.
        """
        try:
            if miner_name not in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' does not exist.")
            
            if self._db_engine is not None:
                XMRigDatabase.delete_all_miner_data_from_db(miner_name, self._db_engine)
            del self._miners[miner_name]
            log.info(f"Miner '{miner_name}' removed from manager.")
        except Exception as e:
            log.error(f"An error occurred removing miner '{miner_name}': {e}")
            raise XMRigAPIError() from e

    def get_miner(self, miner_name: str) -> XMRigAPI:
        """
        Retrieves a specific miner's API instance.

        Args:
            miner_name (str): The unique name of the miner.

        Returns:
            XMRigAPI: The API instance for the requested miner.
        """
        try:
            if miner_name not in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' does not exist.")
            
            return self._miners[miner_name]
        except Exception as e:
            log.error(f"An error occurred retrieving miner '{miner_name}': {e}")
            raise XMRigAPIError() from e

    def perform_action_on_all(self, action: str) -> None:
        """
        Performs the specified action on all miners.

        Args:
            action (str): The action to perform ('pause', 'resume', 'stop', etc.).
        """
        try:
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
                    raise XMRigAPIError(f"Action '{action}' is not a valid method for miner API.")
        except Exception as e:
            log.error(f"An error occurred performing action '{action}' on all miners: {e}")
            raise XMRigAPIError() from e

    def get_all_miners_endpoints(self) -> bool:
        """
        Updates all miners' cached data.

        Returns:
            bool: True if successful, or False if an error occurred.
        """
        try:
            for miner_name, miner_api in self._miners.items():
                success = miner_api.get_all_responses()
                if success:
                    log.info(f"Miner '{miner_name}' successfully updated.")
                else:
                    log.warning(f"Failed to update miner '{miner_name}'.")
            return True
        except requests.exceptions.JSONDecodeError as e:
            log.error(f"An error occurred decoding the response: {e}")
            return False
        except Exception as e:
            log.error(f"An error occurred updating all miners' endpoints: {e}")
            raise XMRigAPIError() from e

    def list_miners(self) -> List[str]:
        """
        Lists all managed miners.

        Returns:
            List[str]: A list of miner names.
        """
        try:
            return list(self._miners.keys())
        except Exception as e:
            log.error(f"An error occurred listing miners: {e}")
            raise XMRigAPIError() from e
