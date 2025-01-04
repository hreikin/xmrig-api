"""
XMRig API interaction library.

This module provides the XMRigAPI class and methods to interact with the XMRig miner API.
It includes functionalities for:

- Fetching status and managing configurations.
- Controlling the mining process.
- Storing collected data in a database.
- Retrieving and caching properties and statistics from the API responses.
- Fallback to the database if the data is not available in the cached responses.
"""

import requests, traceback
from xmrig.logger import log
from xmrig.exceptions import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError
from xmrig.properties import XMRigProperties
from xmrig.db import XMRigDatabase
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, timedelta

class XMRigAPI:
    """
    A class to interact with the XMRig miner API.

    Attributes:
        _miner_name (str): Unique name for the miner.
        _ip (str): IP address of the XMRig API.
        _port (str): Port of the XMRig API.
        _access_token (Optional[str]): Access token for authorization.
        _base_url (str): Base URL for the XMRig API.
        _json_rpc_url (str): URL for the JSON RPC.
        _summary_url (str): URL for the summary endpoint.
        _backends_url (str): URL for the backends endpoint.
        _config_url (str): URL for the config endpoint.
        _headers (Dict[str, str]): Headers for all API/RPC requests.
        _json_rpc_payload (Dict[str, Union[str, int]]): Default payload to send with RPC request.
        data (XMRigProperties): Instance of XMRigProperties for accessing cached data.
    """

    def __init__(self, miner_name: str, ip: str, port: str, access_token: Optional[str] = None, tls_enabled: bool = False, db_url: Optional[str] = None) -> None:
        """
        Initializes the XMRig instance with the provided IP, port, and access token.

        The `ip` can be either an IP address or domain name with its TLD (e.g. `example.com`). The schema is not 
        required and the appropriate one will be chosen based on the `tls_enabled` value.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (str): Port of the XMRig API.
            access_token (Optional[str]): Access token for authorization. Defaults to None.
            tls_enabled (bool): TLS status of the miner/API. Defaults to False.
            db_url (Optional[str]): Database URL for storing miner data. Defaults to None.
        """
        self._miner_name = miner_name
        self._ip = ip
        self._port = port
        self._access_token = access_token
        self._tls_enabled = tls_enabled
        self._base_url = f"http://{ip}:{port}"
        if self._tls_enabled:
            self._base_url = f"https://{ip}:{port}"
        self._db_url = db_url
        self._json_rpc_url = f"{self._base_url}/json_rpc"
        self._summary_url = f"{self._base_url}/2/summary"
        self._backends_url = f"{self._base_url}/2/backends"
        self._config_url = f"{self._base_url}/2/config"
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
        self.data = XMRigProperties(None, None, None, self._miner_name, self._db_url)
        self.get_all_responses()
        log.info(f"XMRigAPI initialized for {self._base_url}")
    
    def _update_properties_cache(self, response, endpoint) -> None:
        """
        Sets the properties for the XMRigAPI instance.
        """
        if endpoint == "summary":
            setattr(self.data, "_summary_response", response)
        if endpoint == "backends":
            setattr(self.data, "_backends_response", response)
        if endpoint == "config":
            setattr(self.data, "_config_response", response)

    def set_auth_header(self) -> bool:
        """
        Update the Authorization header for the HTTP requests.

        Returns:
            bool: True if the Authorization header was changed, or False if an error occurred.
        
        Raises:
            XMRigAuthorizationError: An error occurred setting the Authorization Header.
        """
        try:
            self._headers["Authorization"] = f"Bearer {self._access_token}"
            log.debug(f"Authorization header successfully changed.")
            return True
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(e, traceback.print_exc(), f"An error occurred setting the Authorization Header: {e}") from e

    def get_endpoint(self, endpoint: str) -> bool:
        """
        Updates the cached data from the specified XMRig API endpoint.

        Args:
            endpoint (str): The endpoint to fetch data from. Should be one of 'summary', 'backends', or 'config'.

        Returns:
            bool: True if the cached data is successfully updated or False if an error occurred.

        Raises:
            XMRigAuthorizationError: If an authorization error occurs.
            XMRigConnectionError: If a connection error occurs.
            XMRigAPIError: If a general API error occurs.
        """
        url_map = {
            "summary": self._summary_url,
            "backends": self._backends_url,
            "config": self._config_url
        }
        try:
            response = requests.get(url_map[endpoint], headers=self._headers)
            if response.status_code == 401:
                raise XMRigAuthorizationError(message = "401 UNAUTHORIZED")
            response.raise_for_status()
            try:
                json_response = response.json()
            except requests.exceptions.JSONDecodeError as e:
                json_response = None
                raise requests.exceptions.JSONDecodeError("JSON decode error", response.text, response.status_code)
            else:
                self._update_properties_cache(json_response, endpoint)
                log.debug(f"{endpoint.capitalize()} endpoint successfully fetched.")
                if self._db_url is not None:
                    if endpoint == "backends":
                        for backend in json_response:
                            prefix = ["cpu", "opencl", "cuda"][json_response.index(backend)]
                            XMRigDatabase.insert_data_to_db(backend, f"{self._miner_name}-{prefix}-backend", self._db_url)
                    else:
                        XMRigDatabase.insert_data_to_db(json_response, f"{self._miner_name}-{endpoint}", self._db_url)
                return True
        except requests.exceptions.JSONDecodeError as e:
            # INFO: Due to a bug in XMRig, the first 15 minutes a miner is running/restarted its backends 
            # INFO: endpoint will return a malformed JSON response, allow the program to continue running 
            # INFO: to bypass this bug for now until a fix is provided by the XMRig developers.
            log.error("Due to a bug in XMRig, the first 15 minutes a miner is running/restarted its backends endpoint will return a malformed JSON response. If that is the case then this error/warning can be safely ignored.")
            log.error(f"An error occurred decoding the {endpoint} response: {e}")
            return False
        except requests.exceptions.RequestException as e:
            raise XMRigConnectionError(e, traceback.print_exc(), f"An error occurred while connecting to {url_map[endpoint]}:") from e
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(e, traceback.print_exc(), f"An authorization error occurred updating the {endpoint}, please provide a valid access token:") from e
        except Exception as e:
            raise XMRigAPIError(e, traceback.print_exc(), f"An error occurred updating the {endpoint}:") from e

    def post_config(self, config: Dict[str, Any]) -> bool:
        """
        Updates the miners config data via the XMRig API.

        Args:
            config (Dict[str, Any]): Configuration data to update.

        Returns:
            bool: True if the config was changed successfully, or False if an error occurred.

        Raises:
            XMRigAuthorizationError: If an authorization error occurs.
            XMRigConnectionError: If a connection error occurs.
            XMRigAPIError: If a general API error occurs.
        """
        try:
            response = requests.post(self._config_url, json=config, headers=self._headers)
            if response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            # Get the updated config data from the endpoint and update the cached data
            self.get_endpoint("config")
            log.debug(f"Config endpoint successfully updated.")
            return True
        except requests.exceptions.JSONDecodeError as e:
            raise requests.exceptions.JSONDecodeError("JSON decode error", response.text, response.status_code)
        except requests.exceptions.RequestException as e:
            raise XMRigConnectionError(e, traceback.print_exc(), f"An error occurred while connecting to {self._config_url}:") from e
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(e, traceback.print_exc(), f"An authorization error occurred posting the config, please provide a valid access token:") from e
        except Exception as e:
            raise XMRigAPIError(e, traceback.print_exc(), f"An error occurred posting the config:") from e

    def get_all_responses(self) -> bool:
        """
        Retrieves all responses from the API.

        Returns:
            bool: True if successful, or False if an error occurred.

        Raises:
            XMRigAuthorizationError: If an authorization error occurs.
            XMRigConnectionError: If a connection error occurs.
            XMRigAPIError: If a general API error occurs.
        """
        summary_success = self.get_endpoint("summary")
        backends_success = self.get_endpoint("backends")
        config_success = self.get_endpoint("config")
        return summary_success and backends_success and config_success

    def perform_action(self, action: str) -> bool:
        """
        Controls the miner by performing the specified action.

        Args:
            action (str): The action to perform. Valid actions are 'pause', 'resume', 'stop', 'start'.

        Returns:
            bool: True if the action was successfully performed, or False if an error occurred.

        Raises:
            XMRigConnectionError: If a connection error occurs.
            XMRigAPIError: If a general API error occurs.
        """
        try:
            # TODO: The `start` json RPC method is not implemented by XMRig yet, use alternative implementation 
            # TODO: until PR 3030 is merged, see the following issues and PRs for more information: 
            # TODO: https://github.com/xmrig/xmrig/issues/2826#issuecomment-1146465641
            # TODO: https://github.com/xmrig/xmrig/issues/3220#issuecomment-1450691309
            # TODO: https://github.com/xmrig/xmrig/pull/3030
            if action == "start":
                self.get_endpoint("config")
                self.post_config(self.data._config_response)
                log.debug(f"Miner successfully started.")
            else:
                url = f"{self._json_rpc_url}"
                payload = self._json_rpc_payload
                payload["method"] = action
                response = requests.post(url, json=payload, headers=self._headers)
                response.raise_for_status()
                log.debug(f"Miner successfully {action}ed.")
            return True
        except requests.exceptions.RequestException as e:
            raise XMRigConnectionError(e, traceback.print_exc(), f"A connection error occurred {action}ing the miner:") from e
        except Exception as e:

    def retrieve_data(self, table_name: str, selection: Union[str, List[str]] = "*", start_time: datetime = datetime.now() - timedelta(days=1), end_time: datetime = datetime.now(), limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves data from the specified database table within the given timeframe.

        Args:
            table_name (str): Name of the table to retrieve data from.
            selection (Union[str, List[str]], optional): Column(s) to select from the table. Defaults to "*".
            start_time (datetime, optional): Start time for the data retrieval. Defaults to one day ago.
            end_time (datetime, optional): End time for the data retrieval. Defaults to now.
            limit (int, optional): Limit the number of rows retrieved. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing the retrieved data.
        """
        return XMRigDatabase.retrieve_data_from_db(self._db_url, table_name, selection, start_time, end_time, limit)

# Define the public interface of the module
__all__ = ["XMRigAPI"]