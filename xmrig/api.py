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

# // TODO: Remove quotes from table names in variables, add them to the query string instead, update check_table_exists, etc to reflect this change
# // TODO: Merge properties.py into this class, remove the properties.py file
# // TODO: Add the json flattened into the db as well as the raw json
# // TODO: Create new method to retrieve data from the db and return a single item or multiple from a timerange, default to the last 1 result
# // TODO: Update _get_data_from_cache method to use new method to retrieve data from the db, add a selection argument to the method to allow for selecting specific columns
# // TODO: Update the property getters
# // TODO: Update delete_all_miner_data_from_db method and related variables to reflect the new changes to table names stored within the db
# TODO: Work through methods to make some private ?
# TODO: PEP compliant docstrings
# TODO: Merge test_properties.py into test_api.py
# TODO: Update tests to reflect the recent changes

import requests, traceback
from xmrig.logger import log
from xmrig.exceptions import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError, XMRigDatabaseError
from xmrig.db import XMRigDatabase
from typing import Optional, Dict, List, Any, Union
from datetime import datetime, timedelta
from json import JSONDecodeError

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
        _summary_cache (Dict[str, Any]): Cached summary endpoint data.
        _backends_cache (List[Dict[str, Any]]): Cached backends endpoint data.
        _config_cache (Dict[str, Any]): Cached config endpoint data.
        _summary_table_name (str): Table name for summary data.
        _backends_table_names (List[str]): Table names for backends data.
        _config_table_name (str): Table name for config data.
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
        self._summary_cache = None
        self._backends_cache = None
        self._config_cache = None
        self._summary_table_name = f"{self._miner_name}-summary"
        self._backends_table_name = f"{self._miner_name}-backends"
        self._config_table_name = f"{self._miner_name}-config"
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
        self.get_all_responses()
        log.info(f"XMRigAPI initialized for {self._base_url}")
    
    def _update_cache(self, response, endpoint) -> None:
        """
        Sets the properties for the XMRigAPI instance.
        """
        if endpoint == "summary":
            self._summary_cache = response
        if endpoint == "backends":
            self._backends_cache = response
        if endpoint == "config":
            self._config_cache = response
    
    def _get_data_from_cache(self, response: Union[Dict[str, Any], List[Dict[str, Any]]], keys: List[Union[str, int]], table_name: Union[str, List[str]], selection: Union[str, List[str]]) -> Union[Any, str]:
        """
        Retrieves the data from the response using the provided keys. Falls back to the database if the data is not available.

        Args:
            response (Union[Dict[str, Any], List[Dict[str, Any]]]): The response data.
            keys (List[Union[str, int]]): The keys to use to retrieve the data.
            table_name (Union[str, List[str]]): The table name or list of table names to use for fallback database retrieval.
            selection (Union[str, List[str]], optional): Column(s) to select from the table.

        Returns:
            Union[Any, str]: The retrieved data, or a default string value of "N/A" if not available.

        Raises:
            JSONDecodeError: If there is an error decoding the JSON response.
            KeyError: If a key is not found in the response data.
            XMRigDatabaseError: If there is an error retrieving data from the database.
        """
        data = "N/A"
        try:
            if response == None:
                # TODO: Use this exception or requests.exceptions.JSONDecodeError ?
                raise JSONDecodeError("No response data available, trying database.", "", 0)
            else:
                data = response
                if len(keys) > 0:
                    for key in keys:
                        data = data[key]
        except JSONDecodeError as e:
            if self._db_url is not None:
                try:
                    return self._fallback_to_db(self._db_url, table_name, selection)
                except XMRigDatabaseError as db_e:
                    # TODO: Could this message be better ?
                    log.error(f"An error occurred fetching the backends data from the database, has the miner just been added AND started/restarted within the last 15 minutes ? {db_e}")
                    data = "N/A"
        except KeyError as e:
            log.error(f"Key not found in the response data: {e}")
            data = "N/A"
        return data
    
    def _fallback_to_db(self, db_url, table_name, selection) -> List[Dict[str, Any]]:
        result = XMRigDatabase.retrieve_data_from_db(db_url, table_name, selection)
        return result[0].get(selection, "N/A")
    
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
            raise XMRigAuthorizationError(e, traceback.format_exc(), f"An error occurred setting the Authorization Header: {e}") from e

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
                self._update_cache(json_response, endpoint)
                log.debug(f"{endpoint.capitalize()} endpoint successfully fetched.")
                if self._db_url is not None:
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
            raise XMRigConnectionError(e, traceback.format_exc(), f"An error occurred while connecting to {url_map[endpoint]}:") from e
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(e, traceback.format_exc(), f"An authorization error occurred updating the {endpoint}, please provide a valid access token:") from e
        except Exception as e:
            raise XMRigAPIError(e, traceback.format_exc(), f"An error occurred updating the {endpoint}:") from e

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
            raise XMRigConnectionError(e, traceback.format_exc(), f"An error occurred while connecting to {self._config_url}:") from e
        except XMRigAuthorizationError as e:
            raise XMRigAuthorizationError(e, traceback.format_exc(), f"An authorization error occurred posting the config, please provide a valid access token:") from e
        except Exception as e:
            raise XMRigAPIError(e, traceback.format_exc(), f"An error occurred posting the config:") from e

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
                self.post_config(self._config_cache)
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
            raise XMRigConnectionError(e, traceback.format_exc(), f"A connection error occurred {action}ing the miner:") from e
        except Exception as e:
            raise XMRigAPIError(e, traceback.format_exc(), f"An error occurred {action}ing the miner:") from e
    
    ############################
    # Full data from endpoints #
    ############################

    @property
    def summary(self) -> Union[Dict[str, Any], str]:
        """
        Retrieves the entire cached summary endpoint data.

        Returns:
            Union[Dict[str, Any], str]: Current summary response, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, [], self._summary_table_name, "full_json")

    @property
    def backends(self) -> Union[List[Dict[str, Any]], str]:
        """
        Retrieves the entire cached backends endpoint data.

        Returns:
            Union[List[Dict[str, Any]], str]: Current backends response, or "N/A" if not available.
        """
        # table name for this property shouldnt matter as long as it is a backend table because it is used 
        # to get the miners name because it has its own special handling when it falls back to the db
        return self._get_data_from_cache(self._backends_cache, [], self._backends_table_name, "full_json")

    @property
    def config(self) -> Union[Dict[str, Any], str]:
        """
        Retrieves the entire cached config endpoint data.

        Returns:
            Union[Dict[str, Any], str]: Current config response, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, [], self._config_table_name, "full_json")
    
    ##############################
    # Data from summary endpoint #
    ##############################

    @property
    def sum_id(self) -> Union[str, Any]:
        """
        Retrieves the cached ID information from the summary data.

        Returns:
            Union[str, Any]: ID information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["id"], self._summary_table_name, "id")

    @property
    def sum_worker_id(self) -> Union[str, Any]:
        """
        Retrieves the cached worker ID information from the summary data.

        Returns:
            Union[str, Any]: Worker ID information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["worker_id"], self._summary_table_name, "worker_id")

    @property
    def sum_uptime(self) -> Union[int, Any]:
        """
        Retrieves the cached current uptime from the summary data.

        Returns:
            Union[int, Any]: Current uptime in seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["uptime"], self._summary_table_name, "uptime")

    @property
    def sum_uptime_readable(self) -> str:
        """
        Retrieves the cached uptime in a human-readable format from the summary data.

        Returns:
            str: Uptime in the format "days, hours:minutes:seconds", or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._summary_cache, ["uptime"], self._summary_table_name, "uptime")
        return str(timedelta(seconds=result)) if result != "N/A" else result

    @property
    def sum_restricted(self) -> Union[bool, Any]:
        """
        Retrieves the cached current restricted status from the summary data.

        Returns:
            Union[bool, Any]: Current restricted status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["restricted"], self._summary_table_name, "restricted")

    @property
    def sum_resources(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached resources information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Resources information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources"], self._summary_table_name, "resources")

    @property
    def sum_memory_usage(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached memory usage from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Memory usage information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory"], self._summary_table_name, "resources.memory")

    @property
    def sum_free_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached free memory from the summary data.

        Returns:
            Union[int, Any]: Free memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "free"], self._summary_table_name, "resources.memory.free")

    @property
    def sum_total_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached total memory from the summary data.

        Returns:
            Union[int, Any]: Total memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "total"], self._summary_table_name, "resources.memory.total")

    @property
    def sum_resident_set_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached resident set memory from the summary data.

        Returns:
            Union[int, Any]: Resident set memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "resident_set_memory"], self._summary_table_name, "resources.memory.resident_set_memory")

    @property
    def sum_load_average(self) -> Union[List[float], Any]:
        """
        Retrieves the cached load average from the summary data.

        Returns:
            Union[List[float], Any]: Load average information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "load_average"], self._summary_table_name, "resources.load_average")

    @property
    def sum_hardware_concurrency(self) -> Union[int, Any]:
        """
        Retrieves the cached hardware concurrency from the summary data.

        Returns:
            Union[int, Any]: Hardware concurrency information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "hardware_concurrency"], self._summary_table_name, "resources.hardware_concurrency")

    @property
    def sum_features(self) -> Union[List[str], Any]:
        """
        Retrieves the cached supported features information from the summary data.

        Returns:
            Union[List[str], Any]: Supported features information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["features"], self._summary_table_name, "features")

    @property
    def sum_results(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached results information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Results information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results"], self._summary_table_name, "results")

    @property
    def sum_current_difficulty(self) -> Union[int, Any]:
        """
        Retrieves the cached current difficulty from the summary data.

        Returns:
            Union[int, Any]: Current difficulty, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "diff_current"], self._summary_table_name, "results.diff_current")

    @property
    def sum_good_shares(self) -> Union[int, Any]:
        """
        Retrieves the cached good shares from the summary data.

        Returns:
            Union[int, Any]: Good shares, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "shares_good"], self._summary_table_name, "results.shares_good")

    @property
    def sum_total_shares(self) -> Union[int, Any]:
        """
        Retrieves the cached total shares from the summary data.

        Returns:
            Union[int, Any]: Total shares, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "shares_total"], self._summary_table_name, "results.shares_total")

    @property
    def sum_avg_time(self) -> Union[int, Any]:
        """
        Retrieves the cached average time information from the summary data.

        Returns:
            Union[int, Any]: Average time information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "avg_time"], self._summary_table_name, "results.avg_time")

    @property
    def sum_avg_time_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached average time in `ms` information from the summary data.

        Returns:
            Union[int, Any]: Average time in `ms` information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "avg_time_ms"], self._summary_table_name, "results.avg_time_ms")

    @property
    def sum_total_hashes(self) -> Union[int, Any]:
        """
        Retrieves the cached total number of hashes from the summary data.

        Returns:
            Union[int, Any]: Total number of hashes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "hashes_total"], self._summary_table_name, "results.hashes_total")

    @property
    def sum_best_results(self) -> Union[List[int], Any]:
        """
        Retrieves the cached best results from the summary data.

        Returns:
            Union[List[int], Any]: Best results, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "best"], self._summary_table_name, "results.best")

    @property
    def sum_algorithm(self) -> Union[str, Any]:
        """
        Retrieves the cached current mining algorithm from the summary data.

        Returns:
            Union[str, Any]: Current mining algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["algo"], self._summary_table_name, "algo")

    @property
    def sum_connection(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached connection information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Connection information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection"], self._summary_table_name, "connection")

    @property
    def sum_pool_info(self) -> Union[str, Any]:
        """
        Retrieves the cached pool information from the summary data.

        Returns:
            Union[str, Any]: Pool information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "pool"], self._summary_table_name, "connection.pool")

    @property
    def sum_pool_ip_address(self) -> Union[str, Any]:
        """
        Retrieves the cached IP address from the summary data.

        Returns:
            Union[str, Any]: IP address, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "ip"], self._summary_table_name, "connection.ip")

    @property
    def sum_pool_uptime(self) -> Union[int, Any]:
        """
        Retrieves the cached pool uptime information from the summary data.

        Returns:
            Union[int, Any]: Pool uptime information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "uptime"], self._summary_table_name, "connection.uptime")

    @property
    def sum_pool_uptime_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached pool uptime in ms from the summary data.

        Returns:
            Union[int, Any]: Pool uptime in ms, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "uptime_ms"], self._summary_table_name, "connection.uptime_ms")

    @property
    def sum_pool_ping(self) -> Union[int, Any]:
        """
        Retrieves the cached pool ping information from the summary data.

        Returns:
            Union[int, Any]: Pool ping information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "ping"], self._summary_table_name, "connection.ping")

    @property
    def sum_pool_failures(self) -> Union[int, Any]:
        """
        Retrieves the cached pool failures information from the summary data.

        Returns:
            Union[int, Any]: Pool failures information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "failures"], self._summary_table_name, "connection.failures")

    @property
    def sum_pool_tls(self) -> Union[bool, Any]:
        """
        Retrieves the cached pool tls status from the summary data.

        Returns:
            Union[bool, Any]: Pool tls status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "tls"], self._summary_table_name, "connection.tls")

    @property
    def sum_pool_tls_fingerprint(self) -> Union[str, Any]:
        """
        Retrieves the cached pool tls fingerprint information from the summary data.

        Returns:
            Union[str, Any]: Pool tls fingerprint information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "tls-fingerprint"], self._summary_table_name, "connection.tls-fingerprint")

    @property
    def sum_pool_algo(self) -> Union[str, Any]:
        """
        Retrieves the cached pool algorithm information from the summary data.

        Returns:
            Union[str, Any]: Pool algorithm information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "algo"], self._summary_table_name, "connection.algo")

    @property
    def sum_pool_diff(self) -> Union[int, Any]:
        """
        Retrieves the cached pool difficulty information from the summary data.

        Returns:
            Union[int, Any]: Pool difficulty information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "diff"], self._summary_table_name, "connection.diff")

    @property
    def sum_pool_accepted_jobs(self) -> Union[int, Any]:
        """
        Retrieves the cached number of accepted jobs from the summary data.

        Returns:
            Union[int, Any]: Number of accepted jobs, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "accepted"], self._summary_table_name, "connection.accepted")

    @property
    def sum_pool_rejected_jobs(self) -> Union[int, Any]:
        """
        Retrieves the cached number of rejected jobs from the summary data.

        Returns:
            Union[int, Any]: Number of rejected jobs, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["connection", "rejected"], self._summary_table_name, "connection.rejected")

    @property
    def sum_pool_average_time(self) -> Union[int, Any]:
        """
        Retrieves the cached pool average time information from the summary data.

        Returns:
            Union[int, Any]: Pool average time information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "avg_time"], self._summary_table_name, "connection.avg_time")

    @property
    def sum_pool_average_time_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached pool average time in ms from the summary data.

        Returns:
            Union[int, Any]: Pool average time in ms, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "avg_time_ms"], self._summary_table_name, "connection.avg_time_ms")

    @property
    def sum_pool_total_hashes(self) -> Union[int, Any]:
        """
        Retrieves the cached pool total hashes information from the summary data.

        Returns:
            Union[int, Any]: Pool total hashes information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "hashes_total"], self._summary_table_name, "connection.hashes_total")

    @property
    def sum_version(self) -> Union[str, Any]:
        """
        Retrieves the cached version information from the summary data.

        Returns:
            Union[str, Any]: Version information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["version"], self._summary_table_name, "version")

    @property
    def sum_kind(self) -> Union[str, Any]:
        """
        Retrieves the cached kind information from the summary data.

        Returns:
            Union[str, Any]: Kind information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["kind"], self._summary_table_name, "kind")

    @property
    def sum_ua(self) -> Union[str, Any]:
        """
        Retrieves the cached user agent information from the summary data.

        Returns:
            Union[str, Any]: User agent information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["ua"], self._summary_table_name, "ua")

    @property
    def sum_cpu_info(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached CPU information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: CPU information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu"], self._summary_table_name, "cpu")

    @property
    def sum_cpu_brand(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU brand information from the summary data.

        Returns:
            Union[str, Any]: CPU brand information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "brand"], self._summary_table_name, "cpu.brand")

    @property
    def sum_cpu_family(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU family information from the summary data.

        Returns:
            Union[int, Any]: CPU family information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "family"], self._summary_table_name, "cpu.family")

    @property
    def sum_cpu_model(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU model information from the summary data.

        Returns:
            Union[int, Any]: CPU model information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "model"], self._summary_table_name, "cpu.model")

    @property
    def sum_cpu_stepping(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU stepping information from the summary data.

        Returns:
            Union[int, Any]: CPU stepping information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "stepping"], self._summary_table_name, "cpu.stepping")

    @property
    def sum_cpu_proc_info(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU frequency information from the summary data.

        Returns:
            Union[int, Any]: CPU frequency information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "proc_info"], self._summary_table_name, "cpu.proc_info")

    @property
    def sum_cpu_aes(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU AES support status from the summary data.

        Returns:
            Union[bool, Any]: CPU AES support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "aes"], self._summary_table_name, "cpu.aes")

    @property
    def sum_cpu_avx2(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU AVX2 support status from the summary data.

        Returns:
            Union[bool, Any]: CPU AVX2 support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "avx2"], self._summary_table_name, "cpu.avx2")

    @property
    def sum_cpu_x64(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU x64 support status from the summary data.

        Returns:
            Union[bool, Any]: CPU x64 support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "x64"], self._summary_table_name, "cpu.x64")

    @property
    def sum_cpu_64_bit(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU 64-bit support status from the summary data.

        Returns:
            Union[bool, Any]: CPU 64-bit support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "64_bit"], self._summary_table_name, "cpu.64_bit")

    @property
    def sum_cpu_l2(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU L2 cache size from the summary data.

        Returns:
            Union[int, Any]: CPU L2 cache size, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "l2"], self._summary_table_name, "cpu.l2")

    @property
    def sum_cpu_l3(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU L3 cache size from the summary data.

        Returns:
            Union[int, Any]: CPU L3 cache size, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "l3"], self._summary_table_name, "cpu.l3")

    @property
    def sum_cpu_cores(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU cores count from the summary data.

        Returns:
            Union[int, Any]: CPU cores count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "cores"], self._summary_table_name, "cpu.cores")

    @property
    def sum_cpu_threads(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU threads count from the summary data.

        Returns:
            Union[int, Any]: CPU threads count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "threads"], self._summary_table_name, "cpu.threads")

    @property
    def sum_cpu_packages(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU packages count from the summary data.

        Returns:
            Union[int, Any]: CPU packages count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "packages"], self._summary_table_name, "cpu.packages")

    @property
    def sum_cpu_nodes(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU nodes count from the summary data.

        Returns:
            Union[int, Any]: CPU nodes count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "nodes"], self._summary_table_name, "cpu.nodes")

    @property
    def sum_cpu_backend(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU backend information from the summary data.

        Returns:
            Union[str, Any]: CPU backend information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "backend"], self._summary_table_name, "cpu.backend")

    @property
    def sum_cpu_msr(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU MSR information from the summary data.

        Returns:
            Union[str, Any]: CPU MSR information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "msr"], self._summary_table_name, "cpu.msr")

    @property
    def sum_cpu_assembly(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU assembly information from the summary data.

        Returns:
            Union[str, Any]: CPU assembly information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "assembly"], self._summary_table_name, "cpu.assembly")

    @property
    def sum_cpu_arch(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU architecture information from the summary data.

        Returns:
            Union[str, Any]: CPU architecture information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "arch"], self._summary_table_name, "cpu.arch")

    @property
    def sum_cpu_flags(self) -> Union[List[str], Any]:
        """
        Retrieves the cached CPU flags information from the summary data.

        Returns:
            Union[List[str], Any]: CPU flags information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "flags"], self._summary_table_name, "cpu.flags")

    @property
    def sum_donate_level(self) -> Union[int, Any]:
        """
        Retrieves the cached donate level information from the summary data.

        Returns:
            Union[int, Any]: Donate level information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["donate_level"], self._summary_table_name, "donate_level")

    @property
    def sum_paused(self) -> Union[bool, Any]:
        """
        Retrieves the cached paused status from the summary data.

        Returns:
            Union[bool, Any]: Paused status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["paused"], self._summary_table_name, "paused")

    @property
    def sum_algorithms(self) -> Union[List[str], Any]:
        """
        Retrieves the cached algorithms information from the summary data.

        Returns:
            Union[List[str], Any]: Algorithms information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["algorithms"], self._summary_table_name, "algorithms")

    @property
    def sum_hashrates(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached hashrate information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Hashrate information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate"], self._summary_table_name, "hashrate")

    @property
    def sum_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 10 seconds from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "total", 0], self._summary_table_name, "hashrate.total.0")

    @property
    def sum_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 1 minute from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "total", 1], self._summary_table_name, "hashrate.total.1")

    @property
    def sum_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 15 minutes from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "total", 2], self._summary_table_name, "hashrate.total.2")

    @property
    def sum_hashrate_highest(self) -> Union[float, Any]:
        """
        Retrieves the cached highest hashrate from the summary data.

        Returns:
            Union[float, Any]: Highest hashrate, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "highest"], self._summary_table_name, "hashrate.highest")

    @property
    def sum_hugepages(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the cached hugepages information from the summary data.

        Returns:
            Union[List[Dict[str, Any]], Any]: Hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hugepages"], self._summary_table_name, "hugepages")

    ###############################
    # Data from backends endpoint #
    ###############################

    @property
    def enabled_backends(self) -> Union[List[str], Any]:
        """
        Retrieves the enabled backends from the backends data.

        Returns:
            Union[List[str], Any]: Enabled backends, or "N/A" if not available.
        """
        enabled_backends = []
        # get the enabled backends from the backends data, the backends data is a list of variable length, use _get_data_from_cache to get the data
        for i in range(3):
            if self._get_data_from_cache(self._backends_cache, [i, "enabled"], self._backends_table_name, f"{i}.enabled"):
                enabled_backends.append(self._get_data_from_cache(self._backends_cache, [i, "type"], self._backends_table_name, f"{i}.type"))
        # remove any entries that match "N/A"
        enabled_backends = [x for x in enabled_backends if x not in ["N/A", "0.type", "1.type", "2.type"]]
        return enabled_backends

    @property
    def be_cpu_type(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend type from the backends data.

        Returns:
            Union[str, Any]: CPU backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "type"], self._backends_table_name, "0.type")

    @property
    def be_cpu_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "enabled"], self._backends_table_name, "0.enabled")

    @property
    def be_cpu_algo(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend algorithm from the backends data.

        Returns:
            Union[str, Any]: CPU backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "algo"], self._backends_table_name, "0.algo")

    @property
    def be_cpu_profile(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend profile from the backends data.

        Returns:
            Union[str, Any]: CPU backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "profile"], self._backends_table_name, "0.profile")

    @property
    def be_cpu_hw_aes(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend hardware AES support status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend hardware AES support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hw-aes"], self._backends_table_name, "0.hw-aes")

    @property
    def be_cpu_priority(self) -> Union[int, Any]:
        """
        Retrieves the CPU backend priority from the backends data.

        Returns:
            Union[int, Any]: CPU backend priority, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "priority"], self._backends_table_name, "0.priority")

    @property
    def be_cpu_msr(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend MSR support status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend MSR support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "msr"], self._backends_table_name, "0.msr")

    @property
    def be_cpu_asm(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend assembly information from the backends data.

        Returns:
            Union[str, Any]: CPU backend assembly information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "asm"], self._backends_table_name, "0.asm")

    @property
    def be_cpu_argon2_impl(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend Argon2 implementation from the backends data.

        Returns:
            Union[str, Any]: CPU backend Argon2 implementation, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "argon2-impl"], self._backends_table_name, "0.argon2-impl")

    @property
    def be_cpu_hugepages(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the CPU backend hugepages information from the backends data.

        Returns:
            Union[List[Dict[str, Any]], Any]: CPU backend hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hugepages"], self._backends_table_name, "0.hugepages")

    @property
    def be_cpu_memory(self) -> Union[int, Any]:
        """
        Retrieves the CPU backend memory information from the backends data.

        Returns:
            Union[int, Any]: CPU backend memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "memory"], self._backends_table_name, "0.memory")

    @property
    def be_cpu_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hashrate"], self._backends_table_name, "0.hashrate")

    @property
    def be_cpu_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hashrate", 0], self._backends_table_name, "0.hashrate.0")

    @property
    def be_cpu_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hashrate", 1], self._backends_table_name, "0.hashrate.1")

    @property
    def be_cpu_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hashrate", 2], self._backends_table_name, "0.hashrate.2")
    
    @property
    def be_cpu_threads(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the CPU backend threads information from the backends data.

        Returns:
            Union[List[Dict[str, Any]], Any]: CPU backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads")

    @property
    def be_cpu_threads_intensity(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads intensity information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads intensity information, or "N/A" if not available.
        """
        intensities = []
        try:
            threads = self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads")
            for i in threads:
                intensities.append(i["intensity"])
        except TypeError as e:
            return "N/A"
        return intensities

    @property
    def be_cpu_threads_affinity(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads affinity information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads affinity information, or "N/A" if not available.
        """
        affinities = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads"):
                    affinities.append(i["affinity"])
        except TypeError as e:
            return "N/A"
        return affinities

    @property
    def be_cpu_threads_av(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads AV information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads AV information, or "N/A" if not available.
        """
        avs = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads"):
                    avs.append(i["av"])
        except TypeError as e:
            return "N/A"
        return avs

    @property
    def be_cpu_threads_hashrates_10s(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 10 seconds from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads"):
                    hashrates_10s.append(i["hashrate"][0])
        except TypeError as e:
            return "N/A"
        return hashrates_10s

    @property
    def be_cpu_threads_hashrates_1m(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 1 minute from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        try:
           for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads"):
                    hashrates_1m.append(i["hashrate"][1])
        except TypeError as e:
            return "N/A"
        return hashrates_1m

    @property
    def be_cpu_threads_hashrates_15m(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 15 minutes from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "0.threads"):
                    hashrates_15m.append(i["hashrate"][2])
        except TypeError as e:
            return "N/A"
        return hashrates_15m

    @property
    def be_opencl_type(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend type from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "type"], self._backends_table_name, "1.type")

    @property
    def be_opencl_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the OpenCL backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: OpenCL backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "enabled"], self._backends_table_name, "1.enabled")

    @property
    def be_opencl_algo(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend algorithm from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "algo"], self._backends_table_name, "1.algo")

    @property
    def be_opencl_profile(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend profile from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "profile"], self._backends_table_name, "1.profile")

    @property
    def be_opencl_platform(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend platform information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend platform information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform"], self._backends_table_name, "1.platform")

    @property
    def be_opencl_platform_index(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend platform index from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend platform index, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "index"], self._backends_table_name, "1.platform.index")

    @property
    def be_opencl_platform_profile(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform profile from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "profile"], self._backends_table_name, "1.platform.profile")

    @property
    def be_opencl_platform_version(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform version from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "version"], self._backends_table_name, "1.platform.version")

    @property
    def be_opencl_platform_name(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform name from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform name, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "name"], self._backends_table_name, "1.platform.name")

    @property
    def be_opencl_platform_vendor(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform vendor from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform vendor, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "vendor"], self._backends_table_name, "1.platform.vendor")

    @property
    def be_opencl_platform_extensions(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform extensions from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform extensions, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "extensions"], self._backends_table_name, "1.platform.extensions")

    @property
    def be_opencl_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the OpenCL backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: OpenCL backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "hashrate"], self._backends_table_name, "1.hashrate")

    @property
    def be_opencl_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "hashrate", 0], self._backends_table_name, "1.hashrate.0")

    @property
    def be_opencl_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "hashrate", 1], self._backends_table_name, "1.hashrate.1")

    @property
    def be_opencl_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "hashrate", 2], self._backends_table_name, "1.hashrate.2")

    @property
    def be_opencl_threads(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend threads information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0], self._backends_table_name, "1.threads.0")

    @property
    def be_opencl_threads_index(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads index from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads index, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "index"], self._backends_table_name, "1.threads.0.index")

    @property
    def be_opencl_threads_intensity(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads intensity from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads intensity, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "intensity"], self._backends_table_name, "1.threads.0.intensity")

    @property
    def be_opencl_threads_worksize(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads worksize from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads worksize, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "worksize"], self._backends_table_name, "1.threads.0.worksize")

    @property
    def be_opencl_threads_amount(self) -> Union[List[int], Any]:
        """
        Retrieves the OpenCL backend threads amount from the backends data.

        Returns:
            Union[List[int], Any]: OpenCL backend threads amount, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "threads"], self._backends_table_name, "1.threads.0.threads")

    @property
    def be_opencl_threads_unroll(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads unroll from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads unroll, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "unroll"], self._backends_table_name, "1.threads.0.unroll")

    @property
    def be_opencl_threads_affinity(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads affinity from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads affinity, or "N/A" if not available.
        """
        
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "affinity"], self._backends_table_name, "1.threads.0.affinity")

    @property
    def be_opencl_threads_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the OpenCL backend threads hashrates from the backends data.

        Returns:
            Union[List[float], Any]: OpenCL backend threads hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "hashrate"], self._backends_table_name, "1.threads.0.hashrate")

    @property
    def be_opencl_threads_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "hashrate", 0], self._backends_table_name, "1.threads.0.hashrate.0")

    @property
    def be_opencl_threads_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "hashrate", 1], self._backends_table_name, "1.threads.0.hashrate.1")

    @property
    def be_opencl_threads_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "hashrate", 2], self._backends_table_name, "1.threads.0.hashrate.2")

    @property
    def be_opencl_threads_board(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads board information from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads board information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "board"], self._backends_table_name, "1.threads.0.board")

    @property
    def be_opencl_threads_name(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads name from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads name, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "name"], self._backends_table_name, "1.threads.0.name")

    @property
    def be_opencl_threads_bus_id(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads bus ID from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads bus ID, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "bus_id"], self._backends_table_name, "1.threads.0.bus_id")

    @property
    def be_opencl_threads_cu(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads compute units from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads compute units, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "cu"], self._backends_table_name, "1.threads.0.cu")

    @property
    def be_opencl_threads_global_mem(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads global memory from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads global memory, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "global_mem"], self._backends_table_name, "1.threads.0.global_mem")

    @property
    def be_opencl_threads_health(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend threads health information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend threads health information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health"], self._backends_table_name, "1.threads.0.health")

    @property
    def be_opencl_threads_health_temp(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health temperature from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health temperature, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health", "temperature"], self._backends_table_name, "1.threads.0.health.temperature")

    @property
    def be_opencl_threads_health_power(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health power from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health power, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health", "power"], self._backends_table_name, "1.threads.0.health.power")

    @property
    def be_opencl_threads_health_clock(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health clock from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health clock, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health", "clock"], self._backends_table_name, "1.threads.0.health.clock")

    @property
    def be_opencl_threads_health_mem_clock(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health memory clock from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health memory clock, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health", "mem_clock"], self._backends_table_name, "1.threads.0.health.mem_clock")

    @property
    def be_opencl_threads_health_rpm(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health RPM from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health RPM, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads", 0, "health", "rpm"], self._backends_table_name, "1.threads.0.health.rpm")

    @property
    def be_cuda_type(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend type from the backends data.

        Returns:
            Union[str, Any]: CUDA backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "type"], self._backends_table_name, "2.type")

    @property
    def be_cuda_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the CUDA backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: CUDA backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "enabled"], self._backends_table_name, "2.enabled")

    @property
    def be_cuda_algo(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend algorithm from the backends data.

        Returns:
            Union[str, Any]: CUDA backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "algo"], self._backends_table_name, "2.algo")

    @property
    def be_cuda_profile(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend profile from the backends data.

        Returns:
            Union[str, Any]: CUDA backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "profile"], self._backends_table_name, "2.profile")

    @property
    def be_cuda_versions(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the CUDA backend versions information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: CUDA backend versions information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions"], self._backends_table_name, "2.versions")

    @property
    def be_cuda_runtime(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend runtime version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend runtime version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "cuda-runtime"], self._backends_table_name, "2.versions.cuda-runtime")

    @property
    def be_cuda_driver(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend driver version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend driver version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "cuda-driver"], self._backends_table_name, "2.versions.cuda-driver")

    @property
    def be_cuda_plugin(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend plugin version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend plugin version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "plugin"], self._backends_table_name, "2.versions.plugin")

    @property
    def be_cuda_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CUDA backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CUDA backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "hashrate"], self._backends_table_name, "2.hashrate")

    @property
    def be_cuda_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "hashrate", 0], self._backends_table_name, "2.hashrate.0")

    @property
    def be_cuda_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "hashrate", 1], self._backends_table_name, "2.hashrate.1")

    @property
    def be_cuda_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "hashrate", 2], self._backends_table_name, "2.hashrate.2")

    @property
    def be_cuda_threads(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the CUDA backend threads information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: CUDA backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0], self._backends_table_name, "2.threads.0")

    @property
    def be_cuda_threads_index(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads index from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads index, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "index"], self._backends_table_name, "2.threads.0.index")

    @property
    def be_cuda_threads_amount(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads amount from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads amount, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "threads"], self._backends_table_name, "2.threads.0.threads")

    @property
    def be_cuda_threads_blocks(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads blocks from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads blocks, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "blocks"], self._backends_table_name, "2.threads.0.blocks")

    @property
    def be_cuda_threads_bfactor(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads bfactor from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads bfactor, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "bfactor"], self._backends_table_name, "2.threads.0.bfactor")

    @property
    def be_cuda_threads_bsleep(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads bsleep from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads bsleep, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "bsleep"], self._backends_table_name, "2.threads.0.bsleep")

    @property
    def be_cuda_threads_affinity(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads affinity from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads affinity, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "affinity"], self._backends_table_name, "2.threads.0.affinity")

    @property
    def be_cuda_threads_dataset_host(self) -> Union[bool, Any]:
        """
        Retrieves the CUDA backend threads dataset host status from the backends data.

        Returns:
            Union[bool, Any]: CUDA backend threads dataset host status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "dataset_host"], self._backends_table_name, "2.threads.0.dataset_host")

    @property
    def be_cuda_threads_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CUDA backend threads hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CUDA backend threads hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "hashrate"], self._backends_table_name, "2.threads.0.hashrate")

    @property
    def be_cuda_threads_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "hashrate", 0], self._backends_table_name, "2.threads.0.hashrate.0")

    @property
    def be_cuda_threads_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "hashrate", 1], self._backends_table_name, "2.threads.0.hashrate.1")

    @property
    def be_cuda_threads_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "hashrate", 2], self._backends_table_name, "2.threads.0.hashrate.2")

    @property
    def be_cuda_threads_name(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend threads name from the backends data.

        Returns:
            Union[str, Any]: CUDA backend threads name, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "name"], self._backends_table_name, "2.threads.0.name")

    @property
    def be_cuda_threads_bus_id(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend threads bus ID from the backends data.

        Returns:
            Union[str, Any]: CUDA backend threads bus ID, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "bus_id"], self._backends_table_name, "2.threads.0.bus_id")

    @property
    def be_cuda_threads_smx(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads SMX count from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads SMX count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "smx"], self._backends_table_name, "2.threads.0.smx")

    @property
    def be_cuda_threads_arch(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads architecture from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads architecture, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "arch"], self._backends_table_name, "2.threads.0.arch")

    @property
    def be_cuda_threads_global_mem(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads global memory from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads global memory, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "global_mem"], self._backends_table_name, "2.threads.0.global_mem")

    @property
    def be_cuda_threads_clock(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads clock from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads clock, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "clock"], self._backends_table_name, "2.threads.0.clock")

    @property
    def be_cuda_threads_memory_clock(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads memory clock from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads memory clock, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads", 0, "memory_clock"], self._backends_table_name, "2.threads.0.memory_clock")

    #############################
    # Data from config endpoint #
    #############################

    @property
    def conf_api_property(self) -> Dict[str, Union[str, None]]:
        """
        Retrieves the API property from the config data.

        Returns:
            Dict[str, Union[str, None]]: API property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api"], self._config_table_name, "api")

    @property
    def conf_api_id_property(self) -> Optional[str]:
        """
        Retrieves the API ID property from the config data.

        Returns:
            Optional[str]: API ID property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api", "id"], self._config_table_name, "api.id")

    @property
    def conf_api_worker_id_property(self) -> str:
        """
        Retrieves the API worker ID property from the config data.

        Returns:
            str: API worker ID property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api", "worker-id"], self._config_table_name, "api.worker-id")

    @property
    def conf_http_property(self) -> Dict[str, Union[str, int, bool]]:
        """
        Retrieves the HTTP property from the config data.

        Returns:
            Dict[str, Union[str, int, bool]]: HTTP property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http"], self._config_table_name, "http")

    @property
    def conf_http_enabled_property(self) -> bool:
        """
        Retrieves the HTTP enabled property from the config data.

        Returns:
            bool: HTTP enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "enabled"], self._config_table_name, "http.enabled")

    @property
    def conf_http_host_property(self) -> str:
        """
        Retrieves the HTTP host property from the config data.

        Returns:
            str: HTTP host property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "host"], self._config_table_name, "http.host")

    @property
    def conf_http_port_property(self) -> int:
        """
        Retrieves the HTTP port property from the config data.

        Returns:
            int: HTTP port property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "port"], self._config_table_name, "http.port")

    @property
    def conf_http_access_token_property(self) -> str:
        """
        Retrieves the HTTP access token property from the config data.

        Returns:
            str: HTTP access token property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "access-token"], self._config_table_name, "http.access-token")

    @property
    def conf_http_restricted_property(self) -> bool:
        """
        Retrieves the HTTP restricted property from the config data.

        Returns:
            bool: HTTP restricted property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "restricted"], self._config_table_name, "http.restricted")

    @property
    def conf_autosave_property(self) -> bool:
        """
        Retrieves the autosave property from the config data.

        Returns:
            bool: Autosave property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["autosave"], self._config_table_name, "autosave")

    @property
    def conf_background_property(self) -> bool:
        """
        Retrieves the background property from the config data.

        Returns:
            bool: Background property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["background"], self._config_table_name, "background")

    @property
    def conf_colors_property(self) -> bool:
        """
        Retrieves the colors property from the config data.

        Returns:
            bool: Colors property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["colors"], self._config_table_name, "colors")

    @property
    def conf_title_property(self) -> bool:
        """
        Retrieves the title property from the config data.

        Returns:
            bool: Title property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["title"], self._config_table_name, "title")

    @property
    def conf_randomx_property(self) -> Dict[str, Union[str, int, bool]]:
        """
        Retrieves the RandomX property from the config data.

        Returns:
            Dict[str, Union[str, int, bool]]: RandomX property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx"], self._config_table_name, "randomx")

    @property
    def conf_randomx_init_property(self) -> int:
        """
        Retrieves the RandomX init property from the config data.

        Returns:
            int: RandomX init property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "init"], self._config_table_name, "randomx.init")

    @property
    def conf_randomx_init_avx2_property(self) -> int:
        """
        Retrieves the RandomX init AVX2 property from the config data.

        Returns:
            int: RandomX init AVX2 property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "init-avx2"], self._config_table_name, "randomx.init-avx2")

    @property
    def conf_randomx_mode_property(self) -> str:
        """
        Retrieves the RandomX mode property from the config data.

        Returns:
            str: RandomX mode property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "mode"], self._config_table_name, "randomx.mode")

    @property
    def conf_randomx_1gb_pages_property(self) -> bool:
        """
        Retrieves the RandomX 1GB pages property from the config data.

        Returns:
            bool: RandomX 1GB pages property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "1gb-pages"], self._config_table_name, "randomx.1gb-pages")

    @property
    def conf_randomx_rdmsr_property(self) -> bool:
        """
        Retrieves the RandomX RDMSR property from the config data.

        Returns:
            bool: RandomX RDMSR property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "rdmsr"], self._config_table_name, "randomx.rdmsr")

    @property
    def conf_randomx_wrmsr_property(self) -> bool:
        """
        Retrieves the RandomX WRMSR property from the config data.

        Returns:
            bool: RandomX WRMSR property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "wrmsr"], self._config_table_name, "randomx.wrmsr")

    @property
    def conf_randomx_cache_qos_property(self) -> bool:
        """
        Retrieves the RandomX cache QoS property from the config data.

        Returns:
            bool: RandomX cache QoS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "cache_qos"], self._config_table_name, "randomx.cache_qos")

    @property
    def conf_randomx_numa_property(self) -> bool:
        """
        Retrieves the RandomX NUMA property from the config data.

        Returns:
            bool: RandomX NUMA property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "numa"], self._config_table_name, "randomx.numa")

    @property
    def conf_randomx_scratchpad_prefetch_mode_property(self) -> int:
        """
        Retrieves the RandomX scratchpad prefetch mode property from the config data.

        Returns:
            int: RandomX scratchpad prefetch mode property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "scratchpad_prefetch_mode"], self._config_table_name, "randomx.scratchpad_prefetch_mode")

    @property
    def conf_cpu_property(self) -> Dict[str, Union[str, int, bool, None]]:
        """
        Retrieves the CPU property from the config data.

        Returns:
            Dict[str, Union[str, int, bool, None]]: CPU property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu"], self._config_table_name, "cpu")

    @property
    def conf_cpu_enabled_property(self) -> bool:
        """
        Retrieves the CPU enabled property from the config data.

        Returns:
            bool: CPU enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "enabled"], self._config_table_name, "cpu.enabled")

    @property
    def conf_cpu_huge_pages_property(self) -> bool:
        """
        Retrieves the CPU huge pages property from the config data.

        Returns:
            bool: CPU huge pages property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "huge-pages"], self._config_table_name, "cpu.huge-pages")

    @property
    def conf_cpu_huge_pages_jit_property(self) -> bool:
        """
        Retrieves the CPU huge pages JIT property from the config data.

        Returns:
            bool: CPU huge pages JIT property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "huge-pages-jit"], self._config_table_name, "cpu.huge-pages-jit")

    @property
    def conf_cpu_hw_aes_property(self) -> Optional[bool]:
        """
        Retrieves the CPU hardware AES property from the config data.

        Returns:
            Optional[bool]: CPU hardware AES property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "hw-aes"], self._config_table_name, "cpu.hw-aes")

    @property
    def conf_cpu_priority_property(self) -> Optional[int]:
        """
        Retrieves the CPU priority property from the config data.

        Returns:
            Optional[int]: CPU priority property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "priority"], self._config_table_name, "cpu.priority")

    @property
    def conf_cpu_memory_pool_property(self) -> bool:
        """
        Retrieves the CPU memory pool property from the config data.

        Returns:
            bool: CPU memory pool property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "memory-pool"], self._config_table_name, "cpu.memory-pool")

    @property
    def conf_cpu_yield_property(self) -> bool:
        """
        Retrieves the CPU yield property from the config data.

        Returns:
            bool: CPU yield property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "yield"], self._config_table_name, "cpu.yield")

    @property
    def conf_cpu_max_threads_hint_property(self) -> int:
        """
        Retrieves the CPU max threads hint property from the config data.

        Returns:
            int: CPU max threads hint property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "max-threads-hint"], self._config_table_name, "cpu.max-threads-hint")

    @property
    def conf_cpu_asm_property(self) -> bool:
        """
        Retrieves the CPU ASM property from the config data.

        Returns:
            bool: CPU ASM property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "asm"], self._config_table_name, "cpu.asm")

    @property
    def conf_cpu_argon2_impl_property(self) -> Optional[str]:
        """
        Retrieves the CPU Argon2 implementation property from the config data.

        Returns:
            Optional[str]: CPU Argon2 implementation property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "argon2-impl"], self._config_table_name, "cpu.argon2-impl")

    @property
    def conf_cpu_cn_lite_0_property(self) -> bool:
        """
        Retrieves the CPU CN Lite 0 property from the config data.

        Returns:
            bool: CPU CN Lite 0 property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "cn-lite/0"], self._config_table_name, "cpu.cn-lite/0")

    @property
    def conf_cpu_cn_0_property(self) -> bool:
        """
        Retrieves the CPU CN 0 property from the config data.

        Returns:
            bool: CPU CN 0 property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "cn/0"], self._config_table_name, "cpu.cn/0")

    @property
    def conf_opencl_property(self) -> Dict[str, Union[str, int, bool, List[Dict[str, Union[int, List[int], bool]]]]]:
        """
        Retrieves the OpenCL property from the config data.

        Returns:
            Dict[str, Union[str, int, bool, List[Dict[str, Union[int, List[int], bool]]]]]: OpenCL property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl"], self._config_table_name, "opencl")

    @property
    def conf_opencl_enabled_property(self) -> bool:
        """
        Retrieves the OpenCL enabled property from the config data.

        Returns:
            bool: OpenCL enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "enabled"], self._config_table_name, "opencl.enabled")

    @property
    def conf_opencl_cache_property(self) -> bool:
        """
        Retrieves the OpenCL cache property from the config data.

        Returns:
            bool: OpenCL cache property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "cache"], self._config_table_name, "opencl.cache")

    @property
    def conf_opencl_loader_property(self) -> Optional[str]:
        """
        Retrieves the OpenCL loader property from the config data.

        Returns:
            Optional[str]: OpenCL loader property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "loader"], self._config_table_name, "opencl.loader")

    @property
    def conf_opencl_platform_property(self) -> str:
        """
        Retrieves the OpenCL platform property from the config data.

        Returns:
            str: OpenCL platform property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "platform"], self._config_table_name, "opencl.platform")

    @property
    def conf_opencl_adl_property(self) -> bool:
        """
        Retrieves the OpenCL ADL property from the config data.

        Returns:
            bool: OpenCL ADL property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "adl"], self._config_table_name, "opencl.adl")

    @property
    def conf_opencl_cn_lite_0_property(self) -> bool:
        """
        Retrieves the OpenCL CN Lite 0 from the config data.

        Returns:
            bool: OpenCL CN Lite 0, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "cn-lite/0"], self._config_table_name, "opencl.cn-lite/0")

    @property
    def conf_opencl_cn_0_property(self) -> bool:
        """
        Retrieves the OpenCL CN 0 from the config data.

        Returns:
            bool: OpenCL CN 0, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "cn/0"], self._config_table_name, "opencl.cn/0")

    @property
    def conf_opencl_panthera_property(self) -> bool:
        """
        Retrieves the OpenCL Panthera from the config data.

        Returns:
            bool: OpenCL Panthera, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "panthera"], self._config_table_name, "opencl.panthera")

    @property
    def conf_cuda_property(self) -> Dict[str, Union[str, bool, None]]:
        """
        Retrieves the CUDA from the config data.

        Returns:
            Dict[str, Union[str, bool, None]]: CUDA, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda"], self._config_table_name, "cuda")

    @property
    def conf_cuda_enabled_property(self) -> bool:
        """
        Retrieves the CUDA enabled status from the config data.

        Returns:
            bool: CUDA enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "enabled"], self._config_table_name, "cuda.enabled")

    @property
    def conf_cuda_loader_property(self) -> Optional[str]:
        """
        Retrieves the CUDA loader from the config data.

        Returns:
            Optional[str]: CUDA loader, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "loader"], self._config_table_name, "cuda.loader")

    @property
    def conf_cuda_nvml_property(self) -> bool:
        """
        Retrieves the CUDA NVML from the config data.

        Returns:
            bool: CUDA NVML, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "nvml"], self._config_table_name, "cuda.nvml")

    @property
    def conf_cuda_cn_lite_0_property(self) -> bool:
        """
        Retrieves the CUDA CN Lite 0 from the config data.

        Returns:
            bool: CUDA CN Lite 0, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "cn-lite/0"], self._config_table_name, "cuda.cn-lite/0")

    @property
    def conf_cuda_cn_0_property(self) -> bool:
        """
        Retrieves the CUDA CN 0 from the config data.

        Returns:
            bool: CUDA CN 0, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "cn/0"], self._config_table_name, "cuda.cn/0")

    @property
    def conf_cuda_panthera_property(self) -> bool:
        """
        Retrieves the CUDA Panthera from the config data.

        Returns:
            bool: CUDA Panthera, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "panthera"], self._config_table_name, "cuda.panthera")
    
    @property
    def conf_cuda_astrobwt_property(self) -> bool:
        """
        Retrieves the CUDA Astrobwt from the config data.

        Returns:
            bool: CUDA Astrobwt, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "astrobwt"], self._config_table_name, "cuda.astrobwt")

    @property
    def conf_log_file_property(self) -> Optional[str]:
        """
        Retrieves the log file from the config data.

        Returns:
            Optional[str]: Log file, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["log-file"], self._config_table_name, "log-file")

    @property
    def conf_donate_level_property(self) -> int:
        """
        Retrieves the donate level from the config data.

        Returns:
            int: Donate level, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["donate-level"], self._config_table_name, "donate-level")

    @property
    def conf_donate_over_proxy_property(self) -> int:
        """
        Retrieves the donate over proxy from the config data.

        Returns:
            int: Donate over proxy, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["donate-over-proxy"], self._config_table_name, "donate-over-proxy")

    @property
    def conf_pools_property(self) -> List[Dict[str, Union[str, int, bool, None]]]:
        """
        Retrieves the pools from the config data.

        Returns:
            List[Dict[str, Union[str, int, bool, None]]]: Pools, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools")

    @property
    def conf_pools_algo_property(self) -> str:
        """
        Retrieves the pools algorithm from the config data.

        Returns:
            str: Pools algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "algo"], self._config_table_name, "pools.0.algo")

    @property
    def conf_pools_coin_property(self) -> str:
        """
        Retrieves the pools coin from the config data.

        Returns:
            str: Pools coin, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "coin"], self._config_table_name, "pools.0.coin")

    @property
    def conf_pools_url_property(self) -> str:
        """
        Retrieves the pools URL from the config data.

        Returns:
            str: Pools URL, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "url"], self._config_table_name, "pools.0.url")

    @property
    def conf_pools_user_property(self) -> str:
        """
        Retrieves the pools user from the config data.

        Returns:
            str: Pools user, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "user"], self._config_table_name, "pools.0.user")

    @property
    def conf_pools_pass_property(self) -> str:
        """
        Retrieves the pools password from the config data.

        Returns:
            str: Pools password, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "pass"], self._config_table_name, "pools.0.pass")

    @property
    def conf_pools_rig_id_property(self) -> str:
        """
        Retrieves the pools rig ID from the config data.

        Returns:
            str: Pools rig ID, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "rig-id"], self._config_table_name, "pools.0.rig-id")

    @property
    def conf_pools_nicehash_property(self) -> bool:
        """
        Retrieves the pools NiceHash status from the config data.

        Returns:
            bool: Pools NiceHash status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "nicehash"], self._config_table_name, "pools.0.nicehash")

    @property
    def conf_pools_keepalive_property(self) -> bool:
        """
        Retrieves the pools keepalive status from the config data.

        Returns:
            bool: Pools keepalive status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "keepalive"], self._config_table_name, "pools.0.keepalive")

    @property
    def conf_pools_enabled_property(self) -> bool:
        """
        Retrieves the pools enabled status from the config data.

        Returns:
            bool: Pools enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "enabled"], self._config_table_name, "pools.0.enabled")

    @property
    def conf_pools_tls_property(self) -> bool:
        """
        Retrieves the pools TLS status from the config data.

        Returns:
            bool: Pools TLS status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "tls"], self._config_table_name, "pools.0.tls")

    @property
    def conf_pools_sni_property(self) -> bool:
        """
        Retrieves the pools SNI status from the config data.

        Returns:
            bool: Pools SNI status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "sni"], self._config_table_name, "pools.0.sni")

    @property
    def conf_pools_spend_secret_key_property(self) -> bool:
        """
        Retrieves the pools spend secret key status from the config data.

        Returns:
            bool: Pools SNI status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "sni"], self._config_table_name, "pools.0.sni")

    @property
    def conf_pools_tls_fingerprint_property(self) -> Optional[str]:
        """
        Retrieves the pools TLS fingerprint from the config data.

        Returns:
            Optional[str]: Pools TLS fingerprint, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "tls-fingerprint"], self._config_table_name, "pools.0.tls-fingerprint")

    @property
    def conf_pools_daemon_property(self) -> bool:
        """
        Retrieves the pools daemon status from the config data.

        Returns:
            bool: Pools daemon status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "daemon"], self._config_table_name, "pools.0.daemon")

    @property
    def conf_pools_daemon_poll_interval_property(self) -> bool:
        """
        Retrieves the pools daemon poll interval from the config data.

        Returns:
            bool: Pools daemon poll interval, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "daemon-poll-interval"], self._config_table_name, "pools.0.daemon-poll-interval")

    @property
    def conf_pools_daemon_job_timeout_property(self) -> bool:
        """
        Retrieves the pools daemon job timeout from the config data.

        Returns:
            bool: Pools daemon job timeout, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "daemon-job-timeout"], self._config_table_name, "pools.0.daemon-job-timeout")
    
    @property
    def conf_pools_daemon_zmq_port_property(self) -> bool:
        """
        Retrieves the pools daemon ZMQ port from the config data.

        Returns:
            bool: Pools daemon ZMQ port, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "daemon-zmq-port"], self._config_table_name, "pools.0.daemon-zmq-port")

    @property
    def conf_pools_socks5_property(self) -> Optional[str]:
        """
        Retrieves the pools SOCKS5 from the config data.

        Returns:
            Optional[str]: Pools SOCKS5, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "socks5"], self._config_table_name, "pools.0.socks5")

    @property
    def conf_pools_self_select_property(self) -> Optional[str]:
        """
        Retrieves the pools self-select from the config data.

        Returns:
            Optional[str]: Pools self-select, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "self-select"], self._config_table_name, "pools.0.self-select")

    @property
    def conf_pools_submit_to_origin_property(self) -> bool:
        """
        Retrieves the pools submit to origin status from the config data.

        Returns:
            bool: Pools submit to origin status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools", 0, "submit-to-origin"], self._config_table_name, "pools.0.submit-to-origin")

    @property
    def conf_retries_property(self) -> int:
        """
        Retrieves the retries from the config data.

        Returns:
            int: Retries, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["retries"], self._config_table_name, "retries")

    @property
    def conf_retry_pause_property(self) -> int:
        """
        Retrieves the retry pause from the config data.

        Returns:
            int: Retry pause, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["retry-pause"], self._config_table_name, "retry-pause")

    @property
    def conf_print_time_property(self) -> int:
        """
        Retrieves the print time from the config data.

        Returns:
            int: Print time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["print-time"], self._config_table_name, "print-time")

    @property
    def conf_health_print_time_property(self) -> int:
        """
        Retrieves the health print time from the config data.

        Returns:
            int: Health print time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["health-print-time"], self._config_table_name, "health-print-time")

    @property
    def conf_dmi_property(self) -> bool:
        """
        Retrieves the DMI status from the config data.

        Returns:
            bool: DMI status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dmi"], self._config_table_name, "dmi")

    @property
    def conf_syslog_property(self) -> bool:
        """
        Retrieves the syslog status from the config data.

        Returns:
            bool: Syslog status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["syslog"], self._config_table_name, "syslog")

    @property
    def conf_tls_property(self) -> Dict[str, Optional[Union[str, bool]]]:
        """
        Retrieves the TLS property from the config data.

        Returns:
            Dict[str, Optional[Union[str, bool]]]: TLS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls"], self._config_table_name, "tls")

    @property
    def conf_tls_enabled_property(self) -> bool:
        """
        Retrieves the TLS enabled status from the config data.

        Returns:
            bool: TLS enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "enabled"], self._config_table_name, "tls.enabled")

    @property
    def conf_tls_protocols_property(self) -> Optional[str]:
        """
        Retrieves the TLS protocols from the config data.

        Returns:
            Optional[str]: TLS protocols, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "protocols"], self._config_table_name, "tls.protocols")

    @property
    def conf_tls_cert_property(self) -> Optional[str]:
        """
        Retrieves the TLS certificate from the config data.

        Returns:
            Optional[str]: TLS certificate, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "cert"], self._config_table_name, "tls.cert")

    @property
    def conf_tls_cert_key_property(self) -> Optional[str]:
        """
        Retrieves the TLS certificate key from the config data.

        Returns:
            Optional[str]: TLS certificate key, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "cert_key"], self._config_table_name, "tls.cert_key")

    @property
    def conf_tls_ciphers_property(self) -> Optional[str]:
        """
        Retrieves the TLS ciphers from the config data.

        Returns:
            Optional[str]: TLS ciphers, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "ciphers"], self._config_table_name, "tls.ciphers")

    @property
    def conf_tls_ciphersuites_property(self) -> Optional[str]:
        """
        Retrieves the TLS ciphersuites from the config data.

        Returns:
            Optional[str]: TLS ciphersuites, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "ciphersuites"], self._config_table_name, "tls.ciphersuites")

    @property
    def conf_tls_dhparam_property(self) -> Optional[str]:
        """
        Retrieves the TLS DH parameter from the config data.

        Returns:
            Optional[str]: TLS DH parameter, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "dhparam"], self._config_table_name, "tls.dhparam")

    @property
    def conf_dns_property(self) -> Dict[str, Union[bool, int]]:
        """
        Retrieves the DNS property from the config data.

        Returns:
            Dict[str, Union[bool, int]]: DNS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns"], self._config_table_name, "dns")

    @property
    def conf_dns_ipv6_property(self) -> bool:
        """
        Retrieves the DNS IPv6 status from the config data.

        Returns:
            bool: DNS IPv6 status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns", "ipv6"], self._config_table_name, "dns.ipv6")

    @property
    def conf_dns_ttl_property(self) -> int:
        """
        Retrieves the DNS TTL from the config data.

        Returns:
            int: DNS TTL, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns", "ttl"], self._config_table_name, "dns.ttl")

    @property
    def conf_user_agent_property(self) -> Optional[str]:
        """
        Retrieves the user agent from the config data.

        Returns:
            Optional[str]: User agent, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["user-agent"], self._config_table_name, "user-agent")

    @property
    def conf_verbose_property(self) -> int:
        """
        Retrieves the verbose level from the config data.

        Returns:
            int: Verbose level, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["verbose"], self._config_table_name, "verbose")

    @property
    def conf_watch_property(self) -> bool:
        """
        Retrieves the watch status from the config data.

        Returns:
            bool: Watch status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["watch"], self._config_table_name, "watch")

    @property
    def conf_rebench_algo_property(self) -> bool:
        """
        Retrieves the rebench algorithm status from the config data.

        Returns:
            bool: Rebench algorithm status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["rebench-algo"], self._config_table_name, "rebench-algo")

    @property
    def conf_bench_algo_time_property(self) -> int:
        """
        Retrieves the bench algorithm time from the config data.

        Returns:
            int: Bench algorithm time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["bench-algo-time"], self._config_table_name, "bench-algo-time")

    @property
    def conf_pause_on_battery_property(self) -> bool:
        """
        Retrieves the pause on battery status from the config data.

        Returns:
            bool: Pause on battery status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pause-on-battery"], self._config_table_name, "pause-on-battery")

    @property
    def conf_pause_on_active_property(self) -> bool:
        """
        Retrieves the pause on active status from the config data.

        Returns:
            bool: Pause on active status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pause-on-active"], self._config_table_name, "pause-on-active")

# Define the public interface of the module
__all__ = ["XMRigAPI"]