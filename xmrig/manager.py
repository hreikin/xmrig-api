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
import traceback
from xmrig.api import XMRigAPI
from xmrig.logger import log
from xmrig.exceptions import XMRigManagerError
from xmrig.db import XMRigDatabase

class XMRigManager:
    """
    A class to manage multiple XMRig miners via their APIs.

    Attributes:
        _miners (dict): A dictionary to store miner API instances.
        _api_factory (XMRigAPI): Factory for creating XMRigAPI instances.
        _db_url (str): Database URL for storing miner data.
    """

    def __init__(self, api_factory=XMRigAPI, db_url = "sqlite:///xmrig-api.db"):
        """
        Initializes the manager with an empty collection of miners.

        Args:
            api_factory (XMRigAPI): Factory for creating XMRigAPI instances.
            db_url (str): Database URL for storing miner data.
        """
        self._miners = {}
        self._api_factory = api_factory
        self._db_url = db_url
        if self._db_url is not None:
            XMRigDatabase.init_db(self._db_url)

    def add_miner(self, miner_name, ip, port, access_token = None, tls_enabled = False):
        """
        Adds a new miner to the manager.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (int): Port of the XMRig API.
            access_token (str, optional): Access token for authorization. Defaults to None.
            tls_enabled (bool, optional): TLS status of the miner/API. Defaults to False.

        Raises:
            XMRigManagerError: If an error occurs while adding the miner.
        """
        try:
            if miner_name in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' already exists.")
            # Use the injected factory to create the API instance
            self._miners[miner_name] = self._api_factory(miner_name, ip, port, access_token, tls_enabled, self._db_url)
            log.info(f"Miner called '{miner_name}' added to manager.")
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred adding miner '{miner_name}':") from e

    def remove_miner(self, miner_name):
        """
        Removes a miner from the manager.

        Args:
            miner_name (str): The unique name of the miner to remove.

        Raises:
            XMRigManagerError: If an error occurs while removing the miner.
        """
        try:
            if miner_name not in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' does not exist.")
            if self._db_url is not None:
                XMRigDatabase.delete_all_miner_data_from_db(miner_name, self._db_url)
            del self._miners[miner_name]
            log.info(f"Miner '{miner_name}' removed from manager.")
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred removing miner '{miner_name}':") from e

    def get_miner(self, miner_name):
        """
        Retrieves a specific miner's API instance.

        Args:
            miner_name (str): The unique name of the miner.

        Returns:
            XMRigAPI: The API instance for the requested miner.

        Raises:
            XMRigManagerError: If an error occurs while retrieving the miner.
        """
        try:
            if miner_name not in self._miners:
                raise ValueError(f"Miner with name '{miner_name}' does not exist.")
            return self._miners[miner_name]
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred retrieving miner '{miner_name}':") from e
    
    def edit_miner(self, miner_name, new_details):
        """
        Edits the details of a miner. The following details can be edited:

        - miner_name (str): A unique name for the miner.
        - ip (str): IP address or domain of the XMRig API.
        - port (int): Port of the XMRig API.
        - access_token (str): Access token for authorization.
        - tls_enabled (bool): TLS status of the miner/API.

        The dictionary can be in any order and can contain any number of the above keys. For example:
        
        full_details = {
            'miner_name': 'new_name',
            'ip': 'new_ip_or_domain_with_tld',
            'port': '1234',
            'access_token': 'new-token',
            'tls_enabled': True
        }

        partial_details = {
            'miner_name': 'new_name',
            'port': '1234'
        }

        Args:
            miner_name (str): The unique name of the miner.
            new_details (dict): The new details for the miner.

        Raises:
            XMRigManagerError: If an error occurs while editing the miner.
        """
        try:
            new_name = ""
            miner_api = self.get_miner(miner_name)
            for key, value in new_details.items():
                if key == "miner_name":
                    if value in self._miners:
                        raise ValueError(f"Miner with name '{value}' already exists.")
                    new_name = value
                    miner_api._miner_name = new_name
                    # Remove old entry and replace with new entry
                    del self._miners[miner_name]
                    self._miners[value] = miner_api
                elif key == "ip":
                    miner_api._ip = value
                elif key == "port":
                    miner_api._port = value
                elif key == "access_token":
                    miner_api.set_auth_header(value)
                elif key == "tls_enabled":
                    miner_api._tls_enabled = value
            # Get the miner API instance with the new name to edit further and then return
            miner_api = self.get_miner(new_name)
            # Check if keys "ip", "port" or "tls_enabled" are in the new_details dictionary to construct the new base URL
            if "ip" in new_details or "port" in new_details or "tls_enabled" in new_details:
                miner_api._base_url = f"http://{miner_api._ip}:{miner_api._port}"
                if miner_api._tls_enabled:
                    self._base_url = f"https://{miner_api._ip}:{miner_api._port}"
            log.info(f"Miner called '{miner_name}' successfully edited." if new_name == "" else f"Miner called '{miner_name}' successfully edited to '{new_name}'.")
            return miner_api
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred editing miner '{miner_name}':") from e

    def perform_action_on_all(self, action):
        """
        Performs the specified action on all miners.

        Args:
            action (str): The action to perform ('pause', 'resume', 'stop', 'start').

        Raises:
            XMRigManagerError: If an error occurs while performing the action on all miners.
        """
        try:
            for miner_name, miner_api in self._miners.items():
                success = miner_api.perform_action(action)
                if success:
                    log.info(f"Action '{action}' successfully performed on '{miner_name}'.")
                else:
                    log.warning(f"Action '{action}' failed on '{miner_name}'.")
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred performing action '{action}' on all miners:") from e

    def update_miners(self, endpoint=None):
        """
        Updates all miners' cached data or calls a specific endpoint on all miners.

        Args:
            endpoint (str, optional): The endpoint to call on each miner. If None, updates all cached data. Defaults to None.

        Returns:
            bool: True if successful, or False if an error occurred.

        Raises:
            XMRigManagerError: If an error occurs while updating the miners or calling the endpoint.
        """
        try:
            for miner_name, miner_api in self._miners.items():
                if endpoint:
                    response = miner_api.get_endpoint(endpoint)
                    if response:
                        log.info(f"{endpoint.capitalize()} endpoint successfully called on '{miner_name}'.")
                    else:
                        log.warning(f"Failed to call '{endpoint}' endpoint on '{miner_name}'.")
                else:
                    success = miner_api.get_all_responses()
                    if success:
                        log.info(f"Miner called '{miner_name}' successfully updated.")
                    else:
                        log.warning(f"Failed to update miner '{miner_name}'.")
            return True
        except Exception as e:
            raise XMRigManagerError(e, traceback.format_exc(), f"An error occurred updating miners or calling endpoint '{endpoint}' on all miners:") from e

    def list_miners(self):
        """
        Lists all managed miners.

        Returns:
            list: A list of miner names.
        """
        return list(self._miners.keys())

# Define the public interface of the module
__all__ = ["XMRigManager"]