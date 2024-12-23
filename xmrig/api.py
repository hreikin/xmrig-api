"""
XMRig API interaction library.

This module provides the XMRigAPI class and methods to interact with the XMRig miner API.
It includes functionalities for:

- Fetching status and managing configurations.
- Controlling the mining process.
- Storing collected data in a database.

Classes:
    XMRigAPI: A class to interact with the XMRig miner API.
"""

import requests
from datetime import timedelta
from xmrig.helpers import log, _insert_data_to_db, XMRigAPIError, XMRigConnectionError, XMRigAuthorizationError
from xmrig.properties import XMRigProperties
from sqlalchemy.engine import Engine
from typing import Optional, Dict, Any

# TODO: Update examples to reflect the new changes in the API.
# TODO: Update tests to cover all new functionality in helpers.py.
# TODO: Properties should fallback to using the database if the cached data is not available, handle JSONDecodeError and exception from missing table/data within database to continue running and return "N/A" for the property.
# TODO: Add an examples page to the documentation containing all the examples from the examples folder.
# TODO: Add version notification to docs when viewing main branch, look for a plugin/addon.

class XMRigAPI:
    """
    A class to interact with the XMRig miner API.

    Attributes:
        _miner_name (str): Unique name for the miner.
        _ip (str): IP address of the XMRig API.
        _port (str): Port of the XMRig API.
        _access_token (str): Access token for authorization.
        _base_url (str): Base URL for the XMRig API.
        _json_rpc_url (str): URL for the json RPC.
        _summary_url (str): URL for the summary endpoint.
        _backends_url (str): URL for the backends endpoint.
        _config_url (str): URL for the config endpoint.
        _summary_response (dict): Response from the summary endpoint.
        _backends_response (dict): Response from the backends endpoint.
        _config_response (dict): Response from the config `GET` endpoint.
        _post_config_response (dict): Response from the config `PUT` endpoint.
        _new_config (dict): Config to update with.
        _headers (dict): Headers for all API/RPC requests.
        _json_rpc_payload (dict): Default payload to send with RPC request.
        _db_engine (Engine): SQLAlchemy engine instance for database operations.
    """

    def __init__(self, miner_name: str, ip: str, port: int, access_token: Optional[str] = None, tls_enabled: bool = False, db_engine: Optional[Engine] = None):
        """
        Initializes the XMRig instance with the provided IP, port, and access token.

        The `ip` can be either an IP address or domain name with its TLD (e.g. `example.com`). The schema is not 
        required and the appropriate one will be chosen based on the `tls_enabled` value.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (int): Port of the XMRig API.
            access_token (str, optional): Access token for authorization. Defaults to None.
            tls_enabled (bool, optional): TLS status of the miner/API. 
            db_engine (Engine, optional): SQLAlchemy engine instance for database operations. Defaults to None.
        """
        self._miner_name = miner_name
        self._ip = ip
        self._port = port
        self._access_token = access_token
        self._base_url = f"http://{ip}:{port}"
        if tls_enabled == True:
            self._base_url = f"https://{ip}:{port}"
        self._db_engine = db_engine
        self._json_rpc_url = f"{self._base_url}/json_rpc"
        self._summary_url = f"{self._base_url}/2/summary"
        self._backends_url = f"{self._base_url}/2/backends"
        self._config_url = f"{self._base_url}/2/config"
        self._summary_response = None
        self._backends_response = None
        self._config_response = None
        self._post_config_response = None
        self._new_config = None
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Host": f"{self._base_url}",
            "Connection": "keep-alive",
            "Authorization": f"Bearer {self._access_token}"
        }
        self._json_rpc_payload = {
            "method": None,
            "jsonrpc": "2.0",
            "id": 1,
        }
        self.data = XMRigProperties(self._summary_response, self._backends_response, self._config_response)
        self.get_all_responses()
        log.info(f"XMRigAPI initialized for {self._base_url}")
    
    def _update_properties(self) -> None:
        """
        Sets the properties for the XMRigAPI instance.

        Args:
            data (Dict[str, Any]): Data to set as properties.
        """
        self.data = XMRigProperties(self._summary_response, self._backends_response, self._config_response)

    def set_auth_header(self) -> bool:
        """
        Update the Authorization header for the HTTP requests.

        Returns:
            bool: True if the Authorization header was changed, or False if an error occurred.
        """
        try:
            self._headers['Authorization'] = f"Bearer {self._access_token}"
            log.debug(f"Authorization header successfully changed.")
            return True
        except XMRigAuthorizationError as e:
            log.error(f"An error occurred setting the Authorization Header: {e}")
            raise XMRigAuthorizationError() from e

    def get_summary(self) -> bool:
        """
        Updates the cached summary data from the XMRig API.

        Returns:
            bool: True if the cached data is successfully updated or False if an error occurred.
        """
        try:
            summary_response = requests.get(
                self._summary_url, headers=self._headers)
            if summary_response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            summary_response.raise_for_status()
            self._summary_response = summary_response.json()
            self._update_properties()
            log.debug(f"Summary endpoint successfully fetched.")
            if self._db_engine is not None:
                _insert_data_to_db(self._summary_response, f"{self._miner_name}-summary", self._db_engine)
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while connecting to {self._summary_url}: {e}")
            return False
        except requests.exceptions.JSONDecodeError as e:
            log.error(f"An error occurred decoding the response: {e}")
            return False
        except XMRigAuthorizationError as e:
            log.error(f"An error occurred updating the summary: {e}")
            raise XMRigAuthorizationError() from e
        except Exception as e:
            log.error(f"An error occurred updating the summary: {e}")
            return False

    def get_backends(self) -> bool:
        """
        Updates the cached backends data from the XMRig API.

        Returns:
            bool: True if the cached data is successfully updated or False if an error occurred.
        """
        try:
            backends_response = requests.get(
                self._backends_url, headers=self._headers)
            if backends_response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            backends_response.raise_for_status()
            self._backends_response = backends_response.json()
            self._update_properties()
            log.debug(f"Backends endpoint successfully fetched.")
            if self._db_engine is not None:
                _insert_data_to_db(self._backends_response, f"{self._miner_name}-backends", self._db_engine)
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while connecting to {self._backends_url}: {e}")
            return False
        except requests.exceptions.JSONDecodeError as e:
            log.error(f"An error occurred decoding the response: {e}")
            return False
        except XMRigAuthorizationError as e:
            log.error(f"An error occurred updating the backends: {e}")
            raise XMRigAuthorizationError() from e
        except Exception as e:
            log.error(f"An error occurred updating the backends: {e}")
            return False

    def get_config(self) -> bool:
        """
        Updates the cached config data from the XMRig API.

        Returns:
            bool: True if the cached data is successfully updated, or False if an error occurred.
        """
        try:
            config_response = requests.get(
                self._config_url, headers=self._headers)
            if config_response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            config_response.raise_for_status()
            self._config_response = config_response.json()
            self._update_properties()
            log.debug(f"Config endpoint successfully fetched.")
            if self._db_engine is not None:
                _insert_data_to_db(self._config_response, f"{self._miner_name}-config", self._db_engine)
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while connecting to {self._config_url}: {e}")
            return False
        except requests.exceptions.JSONDecodeError as e:
            log.error(f"An error occurred decoding the response: {e}")
            return False
        except XMRigAuthorizationError as e:
            log.error(f"An error occurred updating the config: {e}")
            raise XMRigAuthorizationError() from e
        except Exception as e:
            log.error(f"An error occurred updating the config: {e}")
            return False

    def post_config(self, config: Dict[str, Any]) -> bool:
        """
        Updates the miners config data via the XMRig API.

        Args:
            config (Dict[str, Any]): Configuration data to update.

        Returns:
            bool: True if the config was changed successfully, or False if an error occurred.
        """
        try:
            self._post_config_response = requests.post(
                self._config_url, json=config, headers=self._headers)
            if self._post_config_response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            self._post_config_response.raise_for_status()
            self._update_properties()
            log.debug(f"Config endpoint successfully updated.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while connecting to {self._config_url}: {e}")
            raise XMRigConnectionError() from e
        except XMRigAuthorizationError as e:
            log.error(f"An error occurred updating the summary: {e}")
            raise XMRigAuthorizationError() from e
        except Exception as e:
            log.error(f"An error occurred posting the config: {e}")
            raise XMRigAPIError() from e

    def get_all_responses(self) -> bool:
        """
        Retrieves all responses from the API.

        Returns:
            bool: True if successful, or False if an error occurred.
        """
        try:
            summary_success = self.get_summary()
            backends_success = self.get_backends()
            config_success = self.get_config()
            return summary_success and backends_success and config_success
        except Exception as e:
            log.error(f"An error occurred fetching all responses: {e}")
            return False

    def pause_miner(self) -> bool:
        """
        Pauses the miner.

        Returns:
            bool: True if the miner was successfully paused, or False if an error occurred.
        """
        try:
            url = f"{self._json_rpc_url}"
            payload = self._json_rpc_payload
            payload["method"] = "pause"
            response = requests.post(url, json=payload, headers=self._headers)
            response.raise_for_status()
            log.debug(f"Miner successfully paused.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred pausing the miner: {e}")
            raise XMRigConnectionError() from e
        except Exception as e:
            log.error(f"An error occurred pausing the miner: {e}")
            raise XMRigAPIError() from e

    def resume_miner(self) -> bool:
        """
        Resumes the miner.

        Returns:
            bool: True if the miner was successfully resumed, or False if an error occurred.
        """
        try:
            url = f"{self._json_rpc_url}"
            payload = self._json_rpc_payload
            payload["method"] = "resume"
            response = requests.post(url, json=payload, headers=self._headers)
            response.raise_for_status()
            log.debug(f"Miner successfully resumed.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred resuming the miner: {e}")
            raise XMRigConnectionError() from e
        except Exception as e:
            log.error(f"An error occurred resuming the miner: {e}")
            raise XMRigAPIError() from e

    def stop_miner(self) -> bool:
        """
        Stops the miner.

        Returns:
            bool: True if the miner was successfully stopped, or False if an error occurred.
        """
        try:
            url = f"{self._json_rpc_url}"
            payload = self._json_rpc_payload
            payload["method"] = "stop"
            response = requests.post(url, json=payload, headers=self._headers)
            response.raise_for_status()
            log.debug(f"Miner successfully stopped.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred stopping the miner: {e}")
            raise XMRigConnectionError() from e
        except Exception as e:
            log.error(f"An error occurred stopping the miner: {e}")
            raise XMRigAPIError() from e

    # TODO: The `start` json RPC method is not implemented by XMRig yet, use alternative function below until PR 3030 is 
    # TODO: merged see https://github.com/xmrig/xmrig/issues/2826#issuecomment-1146465641
    # TODO: https://github.com/xmrig/xmrig/issues/3220#issuecomment-1450691309 and
    # TODO: https://github.com/xmrig/xmrig/pull/3030 for more infomation.
    def start_miner(self) -> bool:
        """
        Starts the miner.

        Returns:
            bool: True if the miner was successfully started, or False if an error occurred.
        """
        try:
            self.get_config()
            self.post_config(self._config_response)
            log.debug(f"Miner successfully started.")
            return True
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred starting the miner: {e}")
            raise XMRigConnectionError() from e
        except Exception as e:
            log.error(f"An error occurred starting the miner: {e}")
            raise XMRigAPIError() from e