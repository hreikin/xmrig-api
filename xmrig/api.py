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

import requests
from xmrig.helpers import log, XMRigAPIError, XMRigConnectionError, XMRigAuthorizationError
from xmrig.properties import XMRigProperties
from xmrig.db import XMRigDatabase
from typing import Optional, Dict, Any

# TODO: Check database fallback functionality after changes to update_backends, it no longer falls back to the database.
# TODO: Test config properties work on a live miner.
# TODO: Fix examples to run from root of project as well as from the examples folder.
# TODO: Update mock and live tests to reflect the changes in the module.
# TODO: Update docstrings.
# TODO: Update the documentation to include all classses, methods, attributes, exceptions, modules, public functions, private functions, properties, etc.

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
        _summary_response (Optional[Dict[str, Any]]): Response from the summary endpoint.
        _backends_response (Optional[List[Dict[str, Any]]]): Response from the backends endpoint.
        _config_response (Optional[Dict[str, Any]]): Response from the config `GET` endpoint.
        _post_config_response (Optional[Dict[str, Any]]): Response from the config `PUT` endpoint.
        _new_config (Optional[Dict[str, Any]]): Config to update with.
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
        # Do i need these 2 or just use local variables?
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
        """
        try:
            self._headers["Authorization"] = f"Bearer {self._access_token}"
            log.debug(f"Authorization header successfully changed.")
            return True
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(f"An error occurred setting the Authorization Header: {e}") from e

    def get_endpoint(self, endpoint: str) -> bool:
        """
        Updates the cached data from the specified XMRig API endpoint.

        Args:
            endpoint (str): The endpoint to fetch data from. Should be one of 'summary', 'backends', or 'config'.

        Returns:
            bool: True if the cached data is successfully updated or False if an error occurred.
        """
        url_map = {
            "summary": self._summary_url,
            "backends": self._backends_url,
            "config": self._config_url
        }
        try:
            response = requests.get(url_map[endpoint], headers=self._headers)
            if response.status_code == 401:
                raise XMRigAuthorizationError()
            response.raise_for_status()
            try:
                json_response = response.json()
            except requests.exceptions.JSONDecodeError as e:
                json_response = None
                raise e
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
            log.error(f"An error occurred decoding the {endpoint} response: {e}")
            return False
        except requests.exceptions.RequestException as e:
            log.error(f"An error occurred while connecting to {url_map[endpoint]}: {e}")
            return False
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(f"An authorization error occurred updating the {endpoint}, please provide a valid access token: {e}") from e
        except Exception as e:
            log.error(f"An error occurred updating the {endpoint}: {e}")
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
            self._post_config_response = requests.post(self._config_url, json=config, headers=self._headers)
            if self._post_config_response.status_code == 401:
                raise XMRigAuthorizationError()
            # Raise an HTTPError for bad responses (4xx and 5xx)
            self._post_config_response.raise_for_status()
            self._update_properties_cache(self._post_config_response, "config")
            log.debug(f"Config endpoint successfully updated.")
            return True
        except requests.exceptions.JSONDecodeError as e:
            log.error(f"An error occurred decoding the config response: {e}")
            return False
        except requests.exceptions.RequestException as e:
            raise XMRigConnectionError(f"An error occurred while connecting to {self._config_url}: {e}") from e
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(f"An authorization error occurred posting the config, please provide a valid access token: {e}") from e
        except Exception as e:
            raise XMRigAPIError(f"An error occurred posting the config: {e}") from e

    def get_all_responses(self) -> bool:
        """
        Retrieves all responses from the API.

        Returns:
            bool: True if successful, or False if an error occurred.
        """
        try:
            summary_success = self.get_endpoint("summary")
            backends_success = self.get_endpoint("backends")
            config_success = self.get_endpoint("config")
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
            raise XMRigConnectionError(f"A connection error occurred pausing the miner: {e}") from e
        except Exception as e:
            raise XMRigAPIError(f"An error occurred pausing the miner: {e}") from e

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
            raise XMRigConnectionError(f"A connection error occurred resuming the miner: {e}") from e
        except Exception as e:
            raise XMRigAPIError(f"An error occurred resuming the miner: {e}") from e

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
            raise XMRigConnectionError(f"A connection error occurred stopping the miner: {e}") from e
        except Exception as e:
            raise XMRigAPIError(f"An error occurred stopping the miner: {e}") from e

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
            raise XMRigConnectionError(f"A connection error occurred starting the miner: {e}") from e
        except Exception as e:
            raise XMRigAPIError(f"An error occurred starting the miner: {e}") from e