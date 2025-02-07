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

# TODO: PEP compliant docstrings
# TODO: [External] Implement similar functionality in companion library p2pool-api

import requests, traceback, logging
from xmrig.exceptions import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError, XMRigDatabaseError
from xmrig.db import XMRigDatabase
from datetime import timedelta
from json import JSONDecodeError

log = logging.getLogger("xmrig.api")

class XMRigAPI:
    """
    A class to interact with the XMRig miner API.

    Attributes:
        _miner_name (str): Unique name for the miner.
        _ip (str): IP address of the XMRig API.
        _port (int): Port of the XMRig API.
        _access_token (str): Access token for authorization.
        _base_url (str): Base URL for the XMRig API.
        _json_rpc_url (str): URL for the JSON RPC.
        _summary_url (str): URL for the summary endpoint.
        _backends_url (str): URL for the backends endpoint.
        _config_url (str): URL for the config endpoint.
        _headers (dict): Headers for all API/RPC requests.
        _json_rpc_payload (dict): Default payload to send with RPC request.
        _summary_cache (dict): Cached summary endpoint data.
        _backends_cache (list): Cached backends endpoint data.
        _config_cache (dict): Cached config endpoint data.
        _summary_table_name (str): Table name for summary data.
        _backends_table_name (str): Table name for backends data.
        _config_table_name (str): Table name for config data.
    """

    def __init__(self, miner_name, ip, port, access_token = None, tls_enabled = False, db_url = None):
        """
        Initializes the XMRig instance with the provided IP, port, and access token.

        The `ip` can be either an IP address or domain name with its TLD (e.g. `example.com`). The schema is not 
        required and the appropriate one will be chosen based on the `tls_enabled` value.

        Args:
            miner_name (str): A unique name for the miner.
            ip (str): IP address or domain of the XMRig API.
            port (int): Port of the XMRig API.
            access_token (str, optional): Access token for authorization. Defaults to None.
            tls_enabled (bool, optional): TLS status of the miner/API. Defaults to False.
            db_url (str, optional): Database URL for storing miner data. Defaults to None.
        """
        self._miner_name = miner_name
        self._ip = ip
        self._port = port
        self._access_token = access_token
        self._tls_enabled = tls_enabled
        self._base_url = f"https://{ip}:{port}" if self._tls_enabled else f"http://{ip}:{port}"
        self._db_url = db_url
        self._json_rpc_url = f"{self._base_url}/json_rpc"
        self._summary_url = f"{self._base_url}/2/summary"
        self._backends_url = f"{self._base_url}/2/backends"
        self._config_url = f"{self._base_url}/2/config"
        self._summary_cache = None
        self._backends_cache = None
        self._config_cache = None
        self._summary_table_name = "summary"
        self._backends_table_name = "backends"
        self._config_table_name = "config"
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
    
    def _update_cache(self, response, endpoint):
        """
        Updates the cached data for an endpoint with the supplied response data.

        Args:
            response (dict | list): The response data.
            endpoint (str): The endpoint from which the data is retrieved.
        """
        if endpoint == "summary":
            self._summary_cache = response
        if endpoint == "backends":
            self._backends_cache = response
        if endpoint == "config":
            self._config_cache = response
    
    def _get_data_from_cache(self, response, keys, table_name, selection):
        """
        Retrieves the data from the response using the provided keys. Falls back to the database if the data is not available.

        Args:
            response (dict | list): The response data.
            keys (list): The keys to use to retrieve the data.
            table_name (str | list): The table name or list of table names to use for fallback database retrieval.
            selection (str): Column to select from the table.

        Returns:
            Any: The retrieved data, or a default string value of "N/A" if not available.

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
                    log.error(f"An error occurred fetching the backends data from the database: {db_e}")
                    data = "N/A"
        except KeyError as e:
            log.error(f"Key not found in the response data: {e}")
            data = "N/A"
        return data
    
    def _fallback_to_db(self, db_url, table_name, selection):
        """
        Fallback to the database if the data is not available in the cache.

        Args:
            db_url (str): Database URL for creating the engine.
            table_name (str): Name of the table to retrieve data from.
            selection (str): Column to select from the table.

        Returns:
            list: List of dictionaries containing the retrieved data.
        """
        result = XMRigDatabase.retrieve_data_from_db(db_url, table_name, self._miner_name, selection)
        return result[0].get(selection, "N/A")
    
    def set_auth_header(self):
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

    def get_endpoint(self, endpoint):
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
                    XMRigDatabase._insert_data_to_db(json_response, self._miner_name, endpoint, self._db_url)
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

    def post_config(self, config):
        """
        Updates the miners config data via the XMRig API.

        Args:
            config (dict): Configuration data to update.

        Returns:
            bool: True if the config was changed successfully, or False if an error occurred.

        Raises:
            XMRigAuthorizationError: If an authorization error occurs.
            XMRigConnectionError: If a connection error occurs.
            XMRigAPIError: If a general API error occurs.
        """
        try:
            response = requests.post(self._config_url, json = config, headers = self._headers)
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

    def get_all_responses(self):
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

    def perform_action(self, action):
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
    def summary(self):
        """
        Retrieves the entire cached summary endpoint data.

        Returns:
            dict: Current summary response, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, [], self._summary_table_name, "full_json")

    @property
    def backends(self):
        """
        Retrieves the entire cached backends endpoint data.

        Returns:
            list: Current backends response, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [], self._backends_table_name, "full_json")

    @property
    def config(self):
        """
        Retrieves the entire cached config endpoint data.

        Returns:
            dict: Current config response, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, [], self._config_table_name, "full_json")
    
    ##############################
    # Data from summary endpoint #
    ##############################

    @property
    def sum_id(self):
        """
        Retrieves the cached ID information from the summary data.

        Returns:
            str: ID information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["id"], self._summary_table_name, "id")

    @property
    def sum_worker_id(self):
        """
        Retrieves the cached worker ID information from the summary data.

        Returns:
            str: Worker ID information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["worker_id"], self._summary_table_name, "worker_id")

    @property
    def sum_uptime(self):
        """
        Retrieves the cached current uptime from the summary data.

        Returns:
            int: Current uptime in seconds, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["uptime"], self._summary_table_name, "uptime")

    @property
    def sum_uptime_readable(self):
        """
        Retrieves the cached uptime in a human-readable format from the summary data.

        Returns:
            str: Uptime in the format "days, hours:minutes:seconds", or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._summary_cache, ["uptime"], self._summary_table_name, "uptime")
        return str(timedelta(seconds=result)) if result != "N/A" else result

    @property
    def sum_restricted(self):
        """
        Retrieves the cached current restricted status from the summary data.

        Returns:
            bool: Current restricted status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["restricted"], self._summary_table_name, "restricted")

    @property
    def sum_resources(self):
        """
        Retrieves the cached resources information from the summary data.

        Returns:
            dict: Resources information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources"], self._summary_table_name, "full_json")

    @property
    def sum_memory_usage(self):
        """
        Retrieves the cached memory usage from the summary data.

        Returns:
            dict: Memory usage information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory"], self._summary_table_name, "resources_memory")

    @property
    def sum_free_memory(self):
        """
        Retrieves the cached free memory from the summary data.

        Returns:
            int: Free memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "free"], self._summary_table_name, "resources_memory_free")

    @property
    def sum_total_memory(self):
        """
        Retrieves the cached total memory from the summary data.

        Returns:
            int: Total memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "total"], self._summary_table_name, "resources_memory_total")

    @property
    def sum_resident_set_memory(self):
        """
        Retrieves the cached resident set memory from the summary data.

        Returns:
            int: Resident set memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "memory", "resident_set_memory"], self._summary_table_name, "resources_memory_rsm")

    @property
    def sum_load_average(self):
        """
        Retrieves the cached load average from the summary data.

        Returns:
            list: Load average information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "load_average"], self._summary_table_name, "resources_load_average")

    @property
    def sum_hardware_concurrency(self):
        """
        Retrieves the cached hardware concurrency from the summary data.

        Returns:
            int: Hardware concurrency information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["resources", "hardware_concurrency"], self._summary_table_name, "resources_hardware_concurrency")

    @property
    def sum_features(self):
        """
        Retrieves the cached supported features information from the summary data.

        Returns:
            list: Supported features information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["features"], self._summary_table_name, "features")

    @property
    def sum_results(self):
        """
        Retrieves the cached results information from the summary data.

        Returns:
            dict: Results information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results"], self._summary_table_name, "results")

    @property
    def sum_current_difficulty(self):
        """
        Retrieves the cached current difficulty from the summary data.

        Returns:
            int: Current difficulty, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "diff_current"], self._summary_table_name, "results_diff_current")

    @property
    def sum_good_shares(self):
        """
        Retrieves the cached good shares from the summary data.

        Returns:
            int: Good shares, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "shares_good"], self._summary_table_name, "results_shares_good")

    @property
    def sum_total_shares(self):
        """
        Retrieves the cached total shares from the summary data.

        Returns:
            int: Total shares, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "shares_total"], self._summary_table_name, "results_shares_total")

    @property
    def sum_avg_time(self):
        """
        Retrieves the cached average time information from the summary data.

        Returns:
            int: Average time information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "avg_time"], self._summary_table_name, "results_avg_time")

    @property
    def sum_avg_time_ms(self):
        """
        Retrieves the cached average time in `ms` information from the summary data.

        Returns:
            int: Average time in `ms` information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "avg_time_ms"], self._summary_table_name, "results_avg_time_ms")

    @property
    def sum_total_hashes(self):
        """
        Retrieves the cached total number of hashes from the summary data.

        Returns:
            int: Total number of hashes, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "hashes_total"], self._summary_table_name, "results_hashes_total")

    @property
    def sum_best_results(self):
        """
        Retrieves the cached best results from the summary data.

        Returns:
            list: Best results, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["results", "best"], self._summary_table_name, "results_best")

    @property
    def sum_algorithm(self):
        """
        Retrieves the cached current mining algorithm from the summary data.

        Returns:
            str: Current mining algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["algo"], self._summary_table_name, "algo")

    @property
    def sum_connection(self):
        """
        Retrieves the cached connection information from the summary data.

        Returns:
            dict: Connection information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection"], self._summary_table_name, "connection")

    @property
    def sum_pool_info(self):
        """
        Retrieves the cached pool information from the summary data.

        Returns:
            str: Pool information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "pool"], self._summary_table_name, "connection_pool")

    @property
    def sum_pool_ip_address(self):
        """
        Retrieves the cached IP address from the summary data.

        Returns:
            str: IP address, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "ip"], self._summary_table_name, "connection_ip")

    @property
    def sum_pool_uptime(self):
        """
        Retrieves the cached pool uptime information from the summary data.

        Returns:
            int: Pool uptime information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "uptime"], self._summary_table_name, "connection_uptime")

    @property
    def sum_pool_uptime_ms(self):
        """
        Retrieves the cached pool uptime in ms from the summary data.

        Returns:
            int: Pool uptime in ms, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "uptime_ms"], self._summary_table_name, "connection_uptime_ms")

    @property
    def sum_pool_ping(self):
        """
        Retrieves the cached pool ping information from the summary data.

        Returns:
            int: Pool ping information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "ping"], self._summary_table_name, "connection_ping")

    @property
    def sum_pool_failures(self):
        """
        Retrieves the cached pool failures information from the summary data.

        Returns:
            int: Pool failures information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "failures"], self._summary_table_name, "connection_failures")

    @property
    def sum_pool_tls(self):
        """
        Retrieves the cached pool tls status from the summary data.

        Returns:
            bool: Pool tls status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "tls"], self._summary_table_name, "connection_tls")

    @property
    def sum_pool_tls_fingerprint(self):
        """
        Retrieves the cached pool tls fingerprint information from the summary data.

        Returns:
            str: Pool tls fingerprint information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "tls-fingerprint"], self._summary_table_name, "connection_tls_fingerprint")

    @property
    def sum_pool_algo(self):
        """
        Retrieves the cached pool algorithm information from the summary data.

        Returns:
            str: Pool algorithm information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "algo"], self._summary_table_name, "connection_algo")

    @property
    def sum_pool_diff(self):
        """
        Retrieves the cached pool difficulty information from the summary data.

        Returns:
            int: Pool difficulty information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "diff"], self._summary_table_name, "connection_diff")

    @property
    def sum_pool_accepted_jobs(self):
        """
        Retrieves the cached number of accepted jobs from the summary data.

        Returns:
            int: Number of accepted jobs, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "accepted"], self._summary_table_name, "connection_accepted")

    @property
    def sum_pool_rejected_jobs(self):
        """
        Retrieves the cached number of rejected jobs from the summary data.

        Returns:
            int: Number of rejected jobs, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["connection", "rejected"], self._summary_table_name, "connection_rejected")

    @property
    def sum_pool_average_time(self):
        """
        Retrieves the cached pool average time information from the summary data.

        Returns:
            int: Pool average time information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "avg_time"], self._summary_table_name, "connection_avg_time")

    @property
    def sum_pool_average_time_ms(self):
        """
        Retrieves the cached pool average time in ms from the summary data.

        Returns:
            int: Pool average time in ms, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "avg_time_ms"], self._summary_table_name, "connection_avg_time_ms")

    @property
    def sum_pool_total_hashes(self):
        """
        Retrieves the cached pool total hashes information from the summary data.

        Returns:
            int: Pool total hashes information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["connection", "hashes_total"], self._summary_table_name, "connection_hashes_total")

    @property
    def sum_version(self):
        """
        Retrieves the cached version information from the summary data.

        Returns:
            str: Version information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["version"], self._summary_table_name, "version")

    @property
    def sum_kind(self):
        """
        Retrieves the cached kind information from the summary data.

        Returns:
            str: Kind information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["kind"], self._summary_table_name, "kind")

    @property
    def sum_ua(self):
        """
        Retrieves the cached user agent information from the summary data.

        Returns:
            str: User agent information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["ua"], self._summary_table_name, "ua")

    @property
    def sum_cpu_info(self):
        """
        Retrieves the cached CPU information from the summary data.

        Returns:
            dict: CPU information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu"], self._summary_table_name, "cpu")

    @property
    def sum_cpu_brand(self):
        """
        Retrieves the cached CPU brand information from the summary data.

        Returns:
            str: CPU brand information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "brand"], self._summary_table_name, "cpu_brand")

    @property
    def sum_cpu_family(self):
        """
        Retrieves the cached CPU family information from the summary data.

        Returns:
            int: CPU family information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "family"], self._summary_table_name, "cpu_family")

    @property
    def sum_cpu_model(self):
        """
        Retrieves the cached CPU model information from the summary data.

        Returns:
            int: CPU model information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "model"], self._summary_table_name, "cpu_model")

    @property
    def sum_cpu_stepping(self):
        """
        Retrieves the cached CPU stepping information from the summary data.

        Returns:
            int: CPU stepping information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "stepping"], self._summary_table_name, "cpu_stepping")

    @property
    def sum_cpu_proc_info(self):
        """
        Retrieves the cached CPU frequency information from the summary data.

        Returns:
            int: CPU frequency information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "proc_info"], self._summary_table_name, "cpu_proc_info")

    @property
    def sum_cpu_aes(self):
        """
        Retrieves the cached CPU AES support status from the summary data.

        Returns:
            bool: CPU AES support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "aes"], self._summary_table_name, "cpu_aes")

    @property
    def sum_cpu_avx2(self):
        """
        Retrieves the cached CPU AVX2 support status from the summary data.

        Returns:
            bool: CPU AVX2 support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "avx2"], self._summary_table_name, "cpu_avx2")

    @property
    def sum_cpu_x64(self):
        """
        Retrieves the cached CPU x64 support status from the summary data.

        Returns:
            bool: CPU x64 support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "x64"], self._summary_table_name, "cpu_x64")

    @property
    def sum_cpu_64_bit(self):
        """
        Retrieves the cached CPU 64-bit support status from the summary data.

        Returns:
            bool: CPU 64-bit support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "64_bit"], self._summary_table_name, "cpu_64_bit")

    @property
    def sum_cpu_l2(self):
        """
        Retrieves the cached CPU L2 cache size from the summary data.

        Returns:
            int: CPU L2 cache size, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "l2"], self._summary_table_name, "cpu_l2")

    @property
    def sum_cpu_l3(self):
        """
        Retrieves the cached CPU L3 cache size from the summary data.

        Returns:
            int: CPU L3 cache size, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "l3"], self._summary_table_name, "cpu_l3")

    @property
    def sum_cpu_cores(self):
        """
        Retrieves the cached CPU cores count from the summary data.

        Returns:
            int: CPU cores count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "cores"], self._summary_table_name, "cpu_cores")

    @property
    def sum_cpu_threads(self):
        """
        Retrieves the cached CPU threads count from the summary data.

        Returns:
            int: CPU threads count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "threads"], self._summary_table_name, "cpu_threads")

    @property
    def sum_cpu_packages(self):
        """
        Retrieves the cached CPU packages count from the summary data.

        Returns:
            int: CPU packages count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "packages"], self._summary_table_name, "cpu_packages")

    @property
    def sum_cpu_nodes(self):
        """
        Retrieves the cached CPU nodes count from the summary data.

        Returns:
            int: CPU nodes count, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "nodes"], self._summary_table_name, "cpu_nodes")

    @property
    def sum_cpu_backend(self):
        """
        Retrieves the cached CPU backend information from the summary data.

        Returns:
            str: CPU backend information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "backend"], self._summary_table_name, "cpu_backend")

    @property
    def sum_cpu_msr(self):
        """
        Retrieves the cached CPU MSR information from the summary data.

        Returns:
            str: CPU MSR information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "msr"], self._summary_table_name, "cpu_msr")

    @property
    def sum_cpu_assembly(self):
        """
        Retrieves the cached CPU assembly information from the summary data.

        Returns:
            str: CPU assembly information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache,  ["cpu", "assembly"], self._summary_table_name, "cpu_assembly")

    @property
    def sum_cpu_arch(self):
        """
        Retrieves the cached CPU architecture information from the summary data.

        Returns:
            str: CPU architecture information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "arch"], self._summary_table_name, "cpu_arch")

    @property
    def sum_cpu_flags(self):
        """
        Retrieves the cached CPU flags information from the summary data.

        Returns:
            list: CPU flags information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["cpu", "flags"], self._summary_table_name, "cpu_flags")

    @property
    def sum_donate_level(self):
        """
        Retrieves the cached donate level information from the summary data.

        Returns:
            int: Donate level information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["donate_level"], self._summary_table_name, "donate_level")

    @property
    def sum_paused(self):
        """
        Retrieves the cached paused status from the summary data.

        Returns:
            bool: Paused status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["paused"], self._summary_table_name, "paused")

    @property
    def sum_algorithms(self):
        """
        Retrieves the cached algorithms information from the summary data.

        Returns:
            list: Algorithms information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["algorithms"], self._summary_table_name, "algorithms")

    @property
    def sum_hashrate(self):
        """
        Retrieves the cached hashrate information from the summary data.

        Returns:
            dict: Hashrate information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate"], self._summary_table_name, "hashrate")
    
    @property
    def sum_hashrate_total(self):
        """
        Retrieves the cached hashrate toal information from the summary data.

        Returns:
            list: Hashrate total information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "total"], self._summary_table_name, "hashrate_total")

    @property
    def sum_hashrate_10s(self):
        """
        Retrieves the cached hashrate for the last 10 seconds from the summary data.

        Returns:
            float: Hashrate for the last 10 seconds, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._summary_cache, ["hashrate", "total"], self._summary_table_name, "hashrate_total")
        return result[0] if result != "N/A" else result

    @property
    def sum_hashrate_1m(self):
        """
        Retrieves the cached hashrate for the last 1 minute from the summary data.

        Returns:
            float: Hashrate for the last 1 minute, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._summary_cache, ["hashrate", "total"], self._summary_table_name, "hashrate_total")
        return result[1] if result != "N/A" else result

    @property
    def sum_hashrate_15m(self):
        """
        Retrieves the cached hashrate for the last 15 minutes from the summary data.

        Returns:
            float: Hashrate for the last 15 minutes, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._summary_cache, ["hashrate", "total"], self._summary_table_name, "hashrate_total")
        return result[2] if result != "N/A" else result

    @property
    def sum_hashrate_highest(self):
        """
        Retrieves the cached highest hashrate from the summary data.

        Returns:
            float: Highest hashrate, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hashrate", "highest"], self._summary_table_name, "hashrate_highest")

    @property
    def sum_hugepages(self):
        """
        Retrieves the cached hugepages information from the summary data.

        Returns:
            list: Hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._summary_cache, ["hugepages"], self._summary_table_name, "hugepages")

    ###############################
    # Data from backends endpoint #
    ###############################

    @property
    def enabled_backends(self):
        """
        Retrieves the enabled backends from the backends data.

        Returns:
            list: Enabled backends, or "N/A" if not available.
        """
        enabled_backends = []
        if self._backends_cache and len(self._backends_cache) >= 1:
            if self._get_data_from_cache(self._backends_cache, [0, "enabled"], self._backends_table_name, "cpu_enabled"):
                enabled_backends.append(self._get_data_from_cache(self._backends_cache, [0, "type"], self._backends_table_name, "cpu_type"))
        if self._backends_cache and len(self._backends_cache) >= 2:
            if self._get_data_from_cache(self._backends_cache, [1, "enabled"], self._backends_table_name, "opencl_enabled"):
                enabled_backends.append(self._get_data_from_cache(self._backends_cache, [1, "type"], self._backends_table_name, "opencl_type"))
            if self._get_data_from_cache(self._backends_cache, [2, "enabled"], self._backends_table_name, "cuda_enabled"):
                enabled_backends.append(self._get_data_from_cache(self._backends_cache, [2, "type"], self._backends_table_name, "cuda_type"))
        return enabled_backends

    @property
    def be_cpu_type(self):
        """
        Retrieves the CPU backend type from the backends data.

        Returns:
            str: CPU backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "type"], self._backends_table_name, "cpu_type")

    @property
    def be_cpu_enabled(self):
        """
        Retrieves the CPU backend enabled status from the backends data.

        Returns:
            bool: CPU backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "enabled"], self._backends_table_name, "cpu_enabled")

    @property
    def be_cpu_algo(self):
        """
        Retrieves the CPU backend algorithm from the backends data.

        Returns:
            str: CPU backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "algo"], self._backends_table_name, "cpu_algo")

    @property
    def be_cpu_profile(self):
        """
        Retrieves the CPU backend profile from the backends data.

        Returns:
            str: CPU backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "profile"], self._backends_table_name, "cpu_profile")

    @property
    def be_cpu_hw_aes(self):
        """
        Retrieves the CPU backend hardware AES support status from the backends data.

        Returns:
            bool: CPU backend hardware AES support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hw-aes"], self._backends_table_name, "cpu_hw_aes")

    @property
    def be_cpu_priority(self):
        """
        Retrieves the CPU backend priority from the backends data.

        Returns:
            int: CPU backend priority, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "priority"], self._backends_table_name, "cpu_priority")

    @property
    def be_cpu_msr(self):
        """
        Retrieves the CPU backend MSR support status from the backends data.

        Returns:
            bool: CPU backend MSR support status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "msr"], self._backends_table_name, "cpu_msr")

    @property
    def be_cpu_asm(self):
        """
        Retrieves the CPU backend assembly information from the backends data.

        Returns:
            str: CPU backend assembly information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "asm"], self._backends_table_name, "cpu_asm")

    @property
    def be_cpu_argon2_impl(self):
        """
        Retrieves the CPU backend Argon2 implementation from the backends data.

        Returns:
            str: CPU backend Argon2 implementation, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "argon2-impl"], self._backends_table_name, "cpu_argon2_impl")

    @property
    def be_cpu_hugepages(self):
        """
        Retrieves the CPU backend hugepages information from the backends data.

        Returns:
            list: CPU backend hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hugepages"], self._backends_table_name, "cpu_hugepages")

    @property
    def be_cpu_memory(self):
        """
        Retrieves the CPU backend memory information from the backends data.

        Returns:
            int: CPU backend memory information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "memory"], self._backends_table_name, "cpu_memory")

    @property
    def be_cpu_hashrates(self):
        """
        Retrieves the CPU backend hashrates from the backends data.

        Returns:
            list: CPU backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "hashrate"], self._backends_table_name, "cpu_hashrate")

    @property
    def be_cpu_hashrate_10s(self):
        """
        Retrieves the CPU backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: CPU backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [0, "hashrate"], self._backends_table_name, "cpu_hashrate")
        return result[0] if result != "N/A" else result

    @property
    def be_cpu_hashrate_1m(self):
        """
        Retrieves the CPU backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: CPU backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [0, "hashrate"], self._backends_table_name, "cpu_hashrate")
        return result[1] if result != "N/A" else result

    @property
    def be_cpu_hashrate_15m(self):
        """
        Retrieves the CPU backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: CPU backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [0, "hashrate"], self._backends_table_name, "cpu_hashrate")
        return result[2] if result != "N/A" else result
    
    @property
    def be_cpu_threads(self):
        """
        Retrieves the CPU backend threads information from the backends data.

        Returns:
            list: CPU backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads")

    @property
    def be_cpu_threads_intensity(self):
        """
        Retrieves the CPU backend threads intensity information from the backends data.

        Returns:
            list: CPU backend threads intensity information, or "N/A" if not available.
        """
        intensities = []
        try:
            threads = self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads")
            for i in threads:
                intensities.append(i["intensity"])
        except TypeError as e:
            return "N/A"
        return intensities

    @property
    def be_cpu_threads_affinity(self):
        """
        Retrieves the CPU backend threads affinity information from the backends data.

        Returns:
            list: CPU backend threads affinity information, or "N/A" if not available.
        """
        affinities = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    affinities.append(i["affinity"])
        except TypeError as e:
            return "N/A"
        return affinities

    @property
    def be_cpu_threads_av(self):
        """
        Retrieves the CPU backend threads AV information from the backends data.

        Returns:
            list: CPU backend threads AV information, or "N/A" if not available.
        """
        avs = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    avs.append(i["av"])
        except TypeError as e:
            return "N/A"
        return avs

    @property
    def be_cpu_threads_hashrates(self):
        """
        Retrieves the CPU backend threads hashrates information from the backends data.

        Returns:
            list: CPU backend threads hashrates information, or "N/A" if not available.
        """
        hashrates = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    hashrates.append(i["hashrate"])
        except TypeError as e:
            return "N/A"
        return hashrates

    @property
    def be_cpu_threads_hashrates_10s(self):
        """
        Retrieves the CPU backend threads hashrates for the last 10 seconds from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    hashrates_10s.append(i["hashrate"][0])
        except TypeError as e:
            return "N/A"
        return hashrates_10s

    @property
    def be_cpu_threads_hashrates_1m(self):
        """
        Retrieves the CPU backend threads hashrates for the last 1 minute from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        try:
           for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    hashrates_1m.append(i["hashrate"][1])
        except TypeError as e:
            return "N/A"
        return hashrates_1m

    @property
    def be_cpu_threads_hashrates_15m(self):
        """
        Retrieves the CPU backend threads hashrates for the last 15 minutes from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [0, "threads"], self._backends_table_name, "cpu_threads"):
                    hashrates_15m.append(i["hashrate"][2])
        except TypeError as e:
            return "N/A"
        return hashrates_15m

    @property
    def be_opencl_type(self):
        """
        Retrieves the OpenCL backend type from the backends data.

        Returns:
            str: OpenCL backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "type"], self._backends_table_name, "opencl_type")

    @property
    def be_opencl_enabled(self):
        """
        Retrieves the OpenCL backend enabled status from the backends data.

        Returns:
            bool: OpenCL backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "enabled"], self._backends_table_name, "opencl_enabled")

    @property
    def be_opencl_algo(self):
        """
        Retrieves the OpenCL backend algorithm from the backends data.

        Returns:
            str: OpenCL backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "algo"], self._backends_table_name, "opencl_algo")

    @property
    def be_opencl_profile(self):
        """
        Retrieves the OpenCL backend profile from the backends data.

        Returns:
            str: OpenCL backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "profile"], self._backends_table_name, "opencl_profile")

    @property
    def be_opencl_platform(self):
        """
        Retrieves the OpenCL backend platform information from the backends data.

        Returns:
            dict: OpenCL backend platform information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform"], self._backends_table_name, "opencl_platform")

    @property
    def be_opencl_platform_index(self):
        """
        Retrieves the OpenCL backend platform index from the backends data.

        Returns:
            int: OpenCL backend platform index, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "index"], self._backends_table_name, "opencl_platform_index")

    @property
    def be_opencl_platform_profile(self):
        """
        Retrieves the OpenCL backend platform profile from the backends data.

        Returns:
            str: OpenCL backend platform profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "profile"], self._backends_table_name, "opencl_platform_profile")

    @property
    def be_opencl_platform_version(self):
        """
        Retrieves the OpenCL backend platform version from the backends data.

        Returns:
            str: OpenCL backend platform version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "version"], self._backends_table_name, "opencl_platform_version")

    @property
    def be_opencl_platform_name(self):
        """
        Retrieves the OpenCL backend platform name from the backends data.

        Returns:
            str: OpenCL backend platform name, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "name"], self._backends_table_name, "opencl_platform_name")

    @property
    def be_opencl_platform_vendor(self):
        """
        Retrieves the OpenCL backend platform vendor from the backends data.

        Returns:
            str: OpenCL backend platform vendor, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "vendor"], self._backends_table_name, "opencl_platform_vendor")

    @property
    def be_opencl_platform_extensions(self):
        """
        Retrieves the OpenCL backend platform extensions from the backends data.

        Returns:
            str: OpenCL backend platform extensions, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "platform", "extensions"], self._backends_table_name, "opencl_platform_extensions")

    @property
    def be_opencl_hashrates(self):
        """
        Retrieves the OpenCL backend hashrates from the backends data.

        Returns:
            list: OpenCL backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "hashrate"], self._backends_table_name, "opencl_hashrate")

    @property
    def be_opencl_hashrate_10s(self):
        """
        Retrieves the OpenCL backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [1, "hashrate"], self._backends_table_name, "opencl_hashrate")
        return result[0] if result != "N/A" else result

    @property
    def be_opencl_hashrate_1m(self):
        """
        Retrieves the OpenCL backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [1, "hashrate"], self._backends_table_name, "opencl_hashrate")
        return result[1] if result != "N/A" else result

    @property
    def be_opencl_hashrate_15m(self):
        """
        Retrieves the OpenCL backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [1, "hashrate"], self._backends_table_name, "opencl_hashrate")
        return result[2] if result != "N/A" else result

    @property
    def be_opencl_threads(self):
        """
        Retrieves the OpenCL backend threads information from the backends data.

        Returns:
            list: OpenCL backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads")

    @property
    def be_opencl_threads_index(self):
        """
        Retrieves the OpenCL backend threads index from the backends data.

        Returns:
            list: OpenCL backend threads index, or "N/A" if not available.
        """
        indexes = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                    indexes.append(i["index"])
        except TypeError as e:
            return "N/A"
        return indexes

    @property
    def be_opencl_threads_intensity(self):
        """
        Retrieves the OpenCL backend threads intensity from the backends data.

        Returns:
            list: OpenCL backend threads intensity, or "N/A" if not available.
        """
        intensities = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                intensities.append(i["intensity"])
        except TypeError as e:
            return "N/A"
        return intensities

    @property
    def be_opencl_threads_worksize(self):
        """
        Retrieves the OpenCL backend threads worksize from the backends data.

        Returns:
            list: OpenCL backend threads worksize, or "N/A" if not available.
        """
        worksizes = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                worksizes.append(i["worksize"])
        except TypeError as e:
            return "N/A"
        return worksizes

    @property
    def be_opencl_threads_unroll(self):
        """
        Retrieves the OpenCL backend threads unroll from the backends data.

        Returns:
            list: OpenCL backend threads unroll, or "N/A" if not available.
        """
        unrolls = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                unrolls.append(i["unroll"])
        except TypeError as e:
            return "N/A"
        return unrolls

    @property
    def be_opencl_threads_affinity(self):
        """
        Retrieves the OpenCL backend threads affinity from the backends data.

        Returns:
            list: OpenCL backend threads affinity, or "N/A" if not available.
        """
        affinities = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                affinities.append(i["affinity"])
        except TypeError as e:
            return "N/A"
        return affinities

    @property
    def be_opencl_threads_hashrates(self):
        """
        Retrieves the OpenCL backend threads hashrates from the backends data.

        Returns:
            list: OpenCL backend threads hashrates, or "N/A" if not available.
        """
        hashrates = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                hashrates.append(i["hashrate"])
        except TypeError as e:
            return "N/A"
        return hashrates

    @property
    def be_opencl_threads_hashrate_10s(self):
        """
        Retrieves the OpenCL backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            list: OpenCL backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                hashrates_10s.append(i["hashrate"][0])
        except KeyError:
            return "N/A"
        return hashrates_10s

    @property
    def be_opencl_threads_hashrate_1m(self):
        """
        Retrieves the OpenCL backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            list: OpenCL backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                hashrates_1m.append(i["hashrate"][1])
        except KeyError:
            return "N/A"
        return hashrates_1m

    @property
    def be_opencl_threads_hashrate_15m(self):
        """
        Retrieves the OpenCL backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            list: OpenCL backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                hashrates_15m.append(i["hashrate"][2])
        except KeyError:
            return "N/A"
        return hashrates_15m

    @property
    def be_opencl_threads_board(self):
        """
        Retrieves the OpenCL backend threads board information from the backends data.

        Returns:
            list: OpenCL backend threads board information, or "N/A" if not available.
        """
        boards = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                boards.append(i["board"])
        except KeyError:
            return "N/A"
        return boards

    @property
    def be_opencl_threads_name(self):
        """
        Retrieves the OpenCL backend threads name from the backends data.

        Returns:
            list: OpenCL backend threads name, or "N/A" if not available.
        """
        names = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                names.append(i["name"])
        except KeyError:
            return "N/A"
        return names

    @property
    def be_opencl_threads_bus_id(self):
        """
        Retrieves the OpenCL backend threads bus ID from the backends data.

        Returns:
            list: OpenCL backend threads bus ID, or "N/A" if not available.
        """
        bus_ids = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                bus_ids.append(i["bus_id"])
        except KeyError:
            return "N/A"
        return bus_ids

    @property
    def be_opencl_threads_cu(self):
        """
        Retrieves the OpenCL backend threads compute units from the backends data.

        Returns:
            list: OpenCL backend threads compute units, or "N/A" if not available.
        """
        cus = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                cus.append(i["cu"])
        except KeyError:
            return "N/A"
        return cus

    @property
    def be_opencl_threads_global_mem(self):
        """
        Retrieves the OpenCL backend threads global memory from the backends data.

        Returns:
            list: OpenCL backend threads global memory, or "N/A" if not available.
        """
        global_mems = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                global_mems.append(i["global_mem"])
        except KeyError:
            return "N/A"
        return global_mems

    @property
    def be_opencl_threads_health(self):
        """
        Retrieves the OpenCL backend threads health information from the backends data.

        Returns:
            list: OpenCL backend threads health information, or "N/A" if not available.
        """
        healths = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                healths.append(i["health"])
        except KeyError:
            return "N/A"
        return healths

    @property
    def be_opencl_threads_health_temp(self):
        """
        Retrieves the OpenCL backend threads health temperature from the backends data.

        Returns:
            list: OpenCL backend threads health temperature, or "N/A" if not available.
        """
        temps = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                temps.append(i["health"]["temperature"])
        except KeyError:
            return "N/A"
        return temps

    @property
    def be_opencl_threads_health_power(self):
        """
        Retrieves the OpenCL backend threads health power from the backends data.

        Returns:
            list: OpenCL backend threads health power, or "N/A" if not available.
        """
        powers = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                powers.append(i["health"]["power"])
        except KeyError:
            return "N/A"
        return powers

    @property
    def be_opencl_threads_health_clock(self):
        """
        Retrieves the OpenCL backend threads health clock from the backends data.

        Returns:
            list: OpenCL backend threads health clock, or "N/A" if not available.
        """
        clocks = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                clocks.append(i["health"]["clock"])
        except KeyError:
            return "N/A"
        return clocks

    @property
    def be_opencl_threads_health_mem_clock(self):
        """
        Retrieves the OpenCL backend threads health memory clock from the backends data.

        Returns:
            list: OpenCL backend threads health memory clock, or "N/A" if not available.
        """
        mem_clocks = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                mem_clocks.append(i["health"]["mem_clock"])
        except KeyError:
            return "N/A"
        return mem_clocks

    @property
    def be_opencl_threads_health_rpm(self):
        """
        Retrieves the OpenCL backend threads health RPM from the backends data.

        Returns:
            list: OpenCL backend threads health RPM, or "N/A" if not available.
        """
        rpms = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [1, "threads"], self._backends_table_name, "opencl_threads"):
                rpms.append(i["health"]["rpm"])
        except KeyError:
            return "N/A"
        return rpms

    @property
    def be_cuda_type(self):
        """
        Retrieves the CUDA backend type from the backends data.

        Returns:
            str: CUDA backend type, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "type"], self._backends_table_name, "cuda_type")

    @property
    def be_cuda_enabled(self):
        """
        Retrieves the CUDA backend enabled status from the backends data.

        Returns:
            bool: CUDA backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "enabled"], self._backends_table_name, "cuda_enabled")

    @property
    def be_cuda_algo(self):
        """
        Retrieves the CUDA backend algorithm from the backends data.

        Returns:
            str: CUDA backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "algo"], self._backends_table_name, "cuda_algo")

    @property
    def be_cuda_profile(self):
        """
        Retrieves the CUDA backend profile from the backends data.

        Returns:
            str: CUDA backend profile, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "profile"], self._backends_table_name, "cuda_profile")

    @property
    def be_cuda_versions(self):
        """
        Retrieves the CUDA backend versions information from the backends data.

        Returns:
            dict: CUDA backend versions information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions"], self._backends_table_name, "cuda_versions")

    @property
    def be_cuda_runtime(self):
        """
        Retrieves the CUDA backend runtime version from the backends data.

        Returns:
            str: CUDA backend runtime version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "cuda-runtime"], self._backends_table_name, "cuda_versions_cuda_runtime")

    @property
    def be_cuda_driver(self):
        """
        Retrieves the CUDA backend driver version from the backends data.

        Returns:
            str: CUDA backend driver version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "cuda-driver"], self._backends_table_name, "cuda_versions_cuda_driver")

    @property
    def be_cuda_plugin(self):
        """
        Retrieves the CUDA backend plugin version from the backends data.

        Returns:
            str: CUDA backend plugin version, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "versions", "plugin"], self._backends_table_name, "cuda_versions_plugin")

    @property
    def be_cuda_hashrates(self):
        """
        Retrieves the CUDA backend hashrates from the backends data.

        Returns:
            list: CUDA backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "hashrate"], self._backends_table_name, "cuda_hashrate")

    @property
    def be_cuda_hashrate_10s(self):
        """
        Retrieves the CUDA backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [2, "hashrate"], self._backends_table_name, "cuda_hashrate")
        return result[0] if result != "N/A" else result

    @property
    def be_cuda_hashrate_1m(self):
        """
        Retrieves the CUDA backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [2, "hashrate"], self._backends_table_name, "cuda_hashrate")
        return result[1] if result != "N/A" else result

    @property
    def be_cuda_hashrate_15m(self):
        """
        Retrieves the CUDA backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        result = self._get_data_from_cache(self._backends_cache, [2, "hashrate"], self._backends_table_name, "cuda_hashrate")
        return result[2] if result != "N/A" else result

    @property
    def be_cuda_threads(self):
        """
        Retrieves the CUDA backend threads information from the backends data.

        Returns:
            list: CUDA backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads")

    @property
    def be_cuda_threads_index(self):
        """
        Retrieves the CUDA backend threads index from the backends data.

        Returns:
            list: CUDA backend threads index, or "N/A" if not available.
        """
        indexes = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                indexes.append(i["index"])
        except KeyError:
            return "N/A"
        return indexes

    @property
    def be_cuda_threads_blocks(self):
        """
        Retrieves the CUDA backend threads blocks from the backends data.

        Returns:
            list: CUDA backend threads blocks, or "N/A" if not available.
        """
        blocks = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                blocks.append(i["blocks"])
        except KeyError:
            return "N/A"
        return blocks

    @property
    def be_cuda_threads_bfactor(self):
        """
        Retrieves the CUDA backend threads bfactor from the backends data.

        Returns:
            list: CUDA backend threads bfactor, or "N/A" if not available.
        """
        bfactors = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                bfactors.append(i["bfactor"])
        except KeyError:
            return "N/A"
        return bfactors

    @property
    def be_cuda_threads_bsleep(self):
        """
        Retrieves the CUDA backend threads bsleep from the backends data.

        Returns:
            list: CUDA backend threads bsleep, or "N/A" if not available.
        """
        bsleeps = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                bsleeps.append(i["bsleep"])
        except KeyError:
            return "N/A"
        return bsleeps

    @property
    def be_cuda_threads_affinity(self):
        """
        Retrieves the CUDA backend threads affinity from the backends data.

        Returns:
            list: CUDA backend threads affinity, or "N/A" if not available.
        """
        affinities = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                affinities.append(i["affinity"])
        except KeyError:
            return "N/A"
        return affinities

    @property
    def be_cuda_threads_dataset_host(self):
        """
        Retrieves the CUDA backend threads dataset host status from the backends data.

        Returns:
            list: CUDA backend threads dataset host status, or "N/A" if not available.
        """
        dataset_hosts = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                dataset_hosts.append(i["dataset_host"])
        except KeyError:
            return "N/A"
        return dataset_hosts

    @property
    def be_cuda_threads_hashrates(self):
        """
        Retrieves the CUDA backend threads hashrates from the backends data.

        Returns:
            list: CUDA backend threads hashrates, or "N/A" if not available.
        """
        hashrates = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                hashrates.append(i["hashrate"])
        except KeyError:
            return "N/A"
        return hashrates

    @property
    def be_cuda_threads_hashrate_10s(self):
        """
        Retrieves the CUDA backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            list: CUDA backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                hashrates_10s.append(i["hashrate"][0])
        except KeyError:
            return "N/A"
        return hashrates_10s

    @property
    def be_cuda_threads_hashrate_1m(self):
        """
        Retrieves the CUDA backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            list: CUDA backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                hashrates_1m.append(i["hashrate"][1])
        except KeyError:
            return "N/A"
        return hashrates_1m

    @property
    def be_cuda_threads_hashrate_15m(self):
        """
        Retrieves the CUDA backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            list: CUDA backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                hashrates_15m.append(i["hashrate"][2])
        except KeyError:
            return "N/A"
        return hashrates_15m

    @property
    def be_cuda_threads_name(self):
        """
        Retrieves the CUDA backend threads name from the backends data.

        Returns:
            list: CUDA backend threads name, or "N/A" if not available.
        """
        names = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                names.append(i["name"])
        except KeyError:
            return "N/A"
        return names

    @property
    def be_cuda_threads_bus_id(self):
        """
        Retrieves the CUDA backend threads bus ID from the backends data.

        Returns:
            list: CUDA backend threads bus ID, or "N/A" if not available.
        """
        bus_ids = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                bus_ids.append(i["bus_id"])
        except KeyError:
            return "N/A"
        return bus_ids

    @property
    def be_cuda_threads_smx(self):
        """
        Retrieves the CUDA backend threads SMX count from the backends data.

        Returns:
            list: CUDA backend threads SMX count, or "N/A" if not available.
        """
        smxs = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                smxs.append(i["smx"])
        except KeyError:
            return "N/A"
        return smxs

    @property
    def be_cuda_threads_arch(self):
        """
        Retrieves the CUDA backend threads architecture from the backends data.

        Returns:
            list: CUDA backend threads architecture, or "N/A" if not available.
        """
        archs = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                archs.append(i["arch"])
        except KeyError:
            return "N/A"
        return archs

    @property
    def be_cuda_threads_global_mem(self):
        """
        Retrieves the CUDA backend threads global memory from the backends data.

        Returns:
            list: CUDA backend threads global memory, or "N/A" if not available.
        """
        global_mems = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                global_mems.append(i["global_mem"])
        except KeyError:
            return "N/A"
        return global_mems

    @property
    def be_cuda_threads_clock(self):
        """
        Retrieves the CUDA backend threads clock from the backends data.

        Returns:
            list: CUDA backend threads clock, or "N/A" if not available.
        """
        clocks = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                clocks.append(i["clock"])
        except KeyError:
            return "N/A"
        return clocks

    @property
    def be_cuda_threads_memory_clock(self):
        """
        Retrieves the CUDA backend threads memory clock from the backends data.

        Returns:
            list: CUDA backend threads memory clock, or "N/A" if not available.
        """
        memory_clocks = []
        try:
            for i in self._get_data_from_cache(self._backends_cache, [2, "threads"], self._backends_table_name, "cuda_threads"):
                memory_clocks.append(i["memory_clock"])
        except KeyError:
            return "N/A"
        return memory_clocks

    #############################
    # Data from config endpoint #
    #############################

    @property
    def conf_api_property(self):
        """
        Retrieves the API property from the config data.

        Returns:
            dict: API property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api"], self._config_table_name, "api")

    @property
    def conf_api_id_property(self):
        """
        Retrieves the API ID property from the config data.

        Returns:
            str: API ID property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api", "id"], self._config_table_name, "api_id")

    @property
    def conf_api_worker_id_property(self):
        """
        Retrieves the API worker ID property from the config data.

        Returns:
            str: API worker ID property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["api", "worker-id"], self._config_table_name, "api_worker_id")

    @property
    def conf_http_property(self):
        """
        Retrieves the HTTP property from the config data.

        Returns:
            dict: HTTP property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http"], self._config_table_name, "http")

    @property
    def conf_http_enabled_property(self):
        """
        Retrieves the HTTP enabled property from the config data.

        Returns:
            bool: HTTP enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "enabled"], self._config_table_name, "http_enabled")

    @property
    def conf_http_host_property(self):
        """
        Retrieves the HTTP host property from the config data.

        Returns:
            str: HTTP host property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "host"], self._config_table_name, "http_host")

    @property
    def conf_http_port_property(self):
        """
        Retrieves the HTTP port property from the config data.

        Returns:
            int: HTTP port property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "port"], self._config_table_name, "http_port")

    @property
    def conf_http_access_token_property(self):
        """
        Retrieves the HTTP access token property from the config data.

        Returns:
            str: HTTP access token property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "access-token"], self._config_table_name, "http_access_token")

    @property
    def conf_http_restricted_property(self):
        """
        Retrieves the HTTP restricted property from the config data.

        Returns:
            bool: HTTP restricted property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["http", "restricted"], self._config_table_name, "http_restricted")

    @property
    def conf_autosave_property(self):
        """
        Retrieves the autosave property from the config data.

        Returns:
            bool: Autosave property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["autosave"], self._config_table_name, "autosave")

    @property
    def conf_background_property(self):
        """
        Retrieves the background property from the config data.

        Returns:
            bool: Background property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["background"], self._config_table_name, "background")

    @property
    def conf_colors_property(self):
        """
        Retrieves the colors property from the config data.

        Returns:
            bool: Colors property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["colors"], self._config_table_name, "colors")

    @property
    def conf_title_property(self):
        """
        Retrieves the title property from the config data.

        Returns:
            bool: Title property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["title"], self._config_table_name, "title")

    @property
    def conf_randomx_property(self):
        """
        Retrieves the RandomX property from the config data.

        Returns:
            dict: RandomX property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx"], self._config_table_name, "randomx")

    @property
    def conf_randomx_init_property(self):
        """
        Retrieves the RandomX init property from the config data.

        Returns:
            int: RandomX init property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "init"], self._config_table_name, "randomx_init")

    @property
    def conf_randomx_init_avx2_property(self):
        """
        Retrieves the RandomX init AVX2 property from the config data.

        Returns:
            int: RandomX init AVX2 property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "init-avx2"], self._config_table_name, "randomx_init_avx2")

    @property
    def conf_randomx_mode_property(self):
        """
        Retrieves the RandomX mode property from the config data.

        Returns:
            str: RandomX mode property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "mode"], self._config_table_name, "randomx_mode")

    @property
    def conf_randomx_1gb_pages_property(self):
        """
        Retrieves the RandomX 1GB pages property from the config data.

        Returns:
            bool: RandomX 1GB pages property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "1gb-pages"], self._config_table_name, "randomx_1gb_pages")

    @property
    def conf_randomx_rdmsr_property(self):
        """
        Retrieves the RandomX RDMSR property from the config data.

        Returns:
            bool: RandomX RDMSR property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "rdmsr"], self._config_table_name, "randomx_rdmsr")

    @property
    def conf_randomx_wrmsr_property(self):
        """
        Retrieves the RandomX WRMSR property from the config data.

        Returns:
            bool: RandomX WRMSR property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "wrmsr"], self._config_table_name, "randomx_wrmsr")

    @property
    def conf_randomx_cache_qos_property(self):
        """
        Retrieves the RandomX cache QoS property from the config data.

        Returns:
            bool: RandomX cache QoS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "cache_qos"], self._config_table_name, "randomx_cache_qos")

    @property
    def conf_randomx_numa_property(self):
        """
        Retrieves the RandomX NUMA property from the config data.

        Returns:
            bool: RandomX NUMA property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "numa"], self._config_table_name, "randomx_numa")

    @property
    def conf_randomx_scratchpad_prefetch_mode_property(self):
        """
        Retrieves the RandomX scratchpad prefetch mode property from the config data.

        Returns:
            int: RandomX scratchpad prefetch mode property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["randomx", "scratchpad_prefetch_mode"], self._config_table_name, "randomx_scratchpad_prefetch_mode")

    @property
    def conf_cpu_property(self):
        """
        Retrieves the CPU property from the config data.

        Returns:
            dict: CPU property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu"], self._config_table_name, "cpu")

    @property
    def conf_cpu_enabled_property(self):
        """
        Retrieves the CPU enabled property from the config data.

        Returns:
            bool: CPU enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "enabled"], self._config_table_name, "cpu_enabled")

    @property
    def conf_cpu_huge_pages_property(self):
        """
        Retrieves the CPU huge pages property from the config data.

        Returns:
            bool: CPU huge pages property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "huge-pages"], self._config_table_name, "cpu_huge_pages")

    @property
    def conf_cpu_huge_pages_jit_property(self):
        """
        Retrieves the CPU huge pages JIT property from the config data.

        Returns:
            bool: CPU huge pages JIT property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "huge-pages-jit"], self._config_table_name, "cpu_huge_pages_jit")

    @property
    def conf_cpu_hw_aes_property(self):
        """
        Retrieves the CPU hardware AES property from the config data.

        Returns:
            bool: CPU hardware AES property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "hw-aes"], self._config_table_name, "cpu_hw_aes")

    @property
    def conf_cpu_priority_property(self):
        """
        Retrieves the CPU priority property from the config data.

        Returns:
            int: CPU priority property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "priority"], self._config_table_name, "cpu_priority")

    @property
    def conf_cpu_memory_pool_property(self):
        """
        Retrieves the CPU memory pool property from the config data.

        Returns:
            bool: CPU memory pool property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "memory-pool"], self._config_table_name, "cpu_memory_pool")

    @property
    def conf_cpu_yield_property(self):
        """
        Retrieves the CPU yield property from the config data.

        Returns:
            bool: CPU yield property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "yield"], self._config_table_name, "cpu_yield")

    @property
    def conf_cpu_max_threads_hint_property(self):
        """
        Retrieves the CPU max threads hint property from the config data.

        Returns:
            int: CPU max threads hint property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "max-threads-hint"], self._config_table_name, "cpu_max_threads_hint")

    @property
    def conf_cpu_asm_property(self):
        """
        Retrieves the CPU ASM property from the config data.

        Returns:
            bool: CPU ASM property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "asm"], self._config_table_name, "cpu_asm")

    @property
    def conf_cpu_argon2_impl_property(self):
        """
        Retrieves the CPU Argon2 implementation property from the config data.

        Returns:
            str: CPU Argon2 implementation property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cpu", "argon2-impl"], self._config_table_name, "cpu_argon2_impl")

    @property
    def conf_opencl_property(self):
        """
        Retrieves the OpenCL property from the config data.

        Returns:
            dict: OpenCL property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl"], self._config_table_name, "opencl")

    @property
    def conf_opencl_enabled_property(self):
        """
        Retrieves the OpenCL enabled property from the config data.

        Returns:
            bool: OpenCL enabled property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "enabled"], self._config_table_name, "opencl_enabled")

    @property
    def conf_opencl_cache_property(self):
        """
        Retrieves the OpenCL cache property from the config data.

        Returns:
            bool: OpenCL cache property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "cache"], self._config_table_name, "opencl_cache")

    @property
    def conf_opencl_loader_property(self):
        """
        Retrieves the OpenCL loader property from the config data.

        Returns:
            str: OpenCL loader property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "loader"], self._config_table_name, "opencl_loader")

    @property
    def conf_opencl_platform_property(self):
        """
        Retrieves the OpenCL platform property from the config data.

        Returns:
            str: OpenCL platform property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "platform"], self._config_table_name, "opencl_platform")

    @property
    def conf_opencl_adl_property(self):
        """
        Retrieves the OpenCL ADL property from the config data.

        Returns:
            bool: OpenCL ADL property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["opencl", "adl"], self._config_table_name, "opencl_adl")

    @property
    def conf_cuda_property(self):
        """
        Retrieves the CUDA from the config data.

        Returns:
            dict: CUDA, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda"], self._config_table_name, "cuda")

    @property
    def conf_cuda_enabled_property(self):
        """
        Retrieves the CUDA enabled status from the config data.

        Returns:
            bool: CUDA enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "enabled"], self._config_table_name, "cuda_enabled")

    @property
    def conf_cuda_loader_property(self):
        """
        Retrieves the CUDA loader from the config data.

        Returns:
            str: CUDA loader, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "loader"], self._config_table_name, "cuda_loader")

    @property
    def conf_cuda_nvml_property(self):
        """
        Retrieves the CUDA NVML from the config data.

        Returns:
            bool: CUDA NVML, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["cuda", "nvml"], self._config_table_name, "cuda_nvml")

    @property
    def conf_log_file_property(self):
        """
        Retrieves the log file from the config data.

        Returns:
            str: Log file, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["log-file"], self._config_table_name, "log_file")

    @property
    def conf_donate_level_property(self):
        """
        Retrieves the donate level from the config data.

        Returns:
            int: Donate level, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["donate-level"], self._config_table_name, "donate_level")

    @property
    def conf_donate_over_proxy_property(self):
        """
        Retrieves the donate over proxy from the config data.

        Returns:
            int: Donate over proxy, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["donate-over-proxy"], self._config_table_name, "donate_over_proxy")

    @property
    def conf_pools_property(self):
        """
        Retrieves the pools from the config data.

        Returns:
            list: Pools, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools")

    @property
    def conf_pools_algo_property(self):
        """
        Retrieves the pools algorithm from the config data.

        Returns:
            list: Pools algorithm, or "N/A" if not available.
        """
        algos = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                algos.append(i["algo"])
        except KeyError:
            return "N/A"
        return algos

    @property
    def conf_pools_coin_property(self):
        """
        Retrieves the pools coin from the config data.

        Returns:
            list: Pools coin, or "N/A" if not available.
        """
        coins = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                coins.append(i["coin"])
        except KeyError:
            return "N/A"
        return coins

    @property
    def conf_pools_url_property(self):
        """
        Retrieves the pools URL from the config data.

        Returns:
            list: Pools URL, or "N/A" if not available.
        """
        urls = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                urls.append(i["url"])
        except KeyError:
            return "N/A"
        return urls

    @property
    def conf_pools_user_property(self):
        """
        Retrieves the pools user from the config data.

        Returns:
            list: Pools user, or "N/A" if not available.
        """
        users = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                users.append(i["user"])
        except KeyError:
            return "N/A"
        return users

    @property
    def conf_pools_pass_property(self):
        """
        Retrieves the pools password from the config data.

        Returns:
            list: Pools password, or "N/A" if not available.
        """
        passwords = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                passwords.append(i["pass"])
        except KeyError:
            return "N/A"
        return passwords

    @property
    def conf_pools_rig_id_property(self):
        """
        Retrieves the pools rig ID from the config data.

        Returns:
            list: Pools rig ID, or "N/A" if not available.
        """
        rig_ids = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                rig_ids.append(i["rig-id"])
        except KeyError:
            return "N/A"
        return rig_ids

    @property
    def conf_pools_nicehash_property(self):
        """
        Retrieves the pools NiceHash status from the config data.

        Returns:
            list: Pools NiceHash status, or "N/A" if not available.
        """
        nicehash_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                nicehash_statuses.append(i["nicehash"])
        except KeyError:
            return "N/A"
        return nicehash_statuses

    @property
    def conf_pools_keepalive_property(self):
        """
        Retrieves the pools keepalive status from the config data.

        Returns:
            list: Pools keepalive status, or "N/A" if not available.
        """
        keepalive_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                keepalive_statuses.append(i["keepalive"])
        except KeyError:
            return "N/A"
        return keepalive_statuses

    @property
    def conf_pools_enabled_property(self):
        """
        Retrieves the pools enabled status from the config data.

        Returns:
            list: Pools enabled status, or "N/A" if not available.
        """
        enabled_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                enabled_statuses.append(i["enabled"])
        except KeyError:
            return "N/A"
        return enabled_statuses

    @property
    def conf_pools_tls_property(self):
        """
        Retrieves the pools TLS status from the config data.

        Returns:
            list: Pools TLS status, or "N/A" if not available.
        """
        tls_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                tls_statuses.append(i["tls"])
        except KeyError:
            return "N/A"
        return tls_statuses

    @property
    def conf_pools_sni_property(self):
        """
        Retrieves the pools SNI status from the config data.

        Returns:
            list: Pools SNI status, or "N/A" if not available.
        """
        sni_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                sni_statuses.append(i["sni"])
        except KeyError:
            return "N/A"
        return sni_statuses

    @property
    def conf_pools_spend_secret_key_property(self):
        """
        Retrieves the pools spend secret key status from the config data.

        Returns:
            list: Pools spend secret key status, or "N/A" if not available.
        """
        spend_secret_key_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                spend_secret_key_statuses.append(i["spend-secret-key"])
        except KeyError:
            return "N/A"
        return spend_secret_key_statuses

    @property
    def conf_pools_tls_fingerprint_property(self):
        """
        Retrieves the pools TLS fingerprint from the config data.

        Returns:
            list: Pools TLS fingerprint, or "N/A" if not available.
        """
        tls_fingerprints = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                tls_fingerprints.append(i["tls-fingerprint"])
        except KeyError:
            return "N/A"
        return tls_fingerprints

    @property
    def conf_pools_daemon_property(self):
        """
        Retrieves the pools daemon status from the config data.

        Returns:
            list: Pools daemon status, or "N/A" if not available.
        """
        daemon_statuses = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                daemon_statuses.append(i["daemon"])
        except KeyError:
            return "N/A"
        return daemon_statuses

    @property
    def conf_pools_daemon_poll_interval_property(self):
        """
        Retrieves the pools daemon poll interval from the config data.

        Returns:
            list: Pools daemon poll interval, or "N/A" if not available.
        """
        daemon_poll_intervals = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                daemon_poll_intervals.append(i["daemon-poll-interval"])
        except KeyError:
            return "N/A"
        return daemon_poll_intervals

    @property
    def conf_pools_daemon_job_timeout_property(self):
        """
        Retrieves the pools daemon job timeout from the config data.

        Returns:
            list: Pools daemon job timeout, or "N/A" if not available.
        """
        daemon_job_timeouts = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                daemon_job_timeouts.append(i["daemon-job-timeout"])
        except KeyError:
            return "N/A"
        return daemon_job_timeouts

    @property
    def conf_pools_daemon_zmq_port_property(self):
        """
        Retrieves the pools daemon ZMQ port from the config data.

        Returns:
            list: Pools daemon ZMQ port, or "N/A" if not available.
        """
        daemon_zmq_ports = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                daemon_zmq_ports.append(i["daemon-zmq-port"])
        except KeyError:
            return "N/A"
        return daemon_zmq_ports

    @property
    def conf_pools_socks5_property(self):
        """
        Retrieves the pools SOCKS5 from the config data.

        Returns:
            list: Pools SOCKS5, or "N/A" if not available.
        """
        socks5_values = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                socks5_values.append(i["socks5"])
        except KeyError:
            return "N/A"
        return socks5_values

    @property
    def conf_pools_self_select_property(self):
        """
        Retrieves the pools self-select from the config data.

        Returns:
            list: Pools self-select, or "N/A" if not available.
        """
        self_selects = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                self_selects.append(i["self-select"])
        except KeyError:
            return "N/A"
        return self_selects

    @property
    def conf_pools_submit_to_origin_property(self):
        """
        Retrieves the pools submit to origin status from the config data.

        Returns:
            list: Pools submit to origin status, or "N/A" if not available.
        """
        submit_to_origins = []
        try:
            for i in self._get_data_from_cache(self._config_cache, ["pools"], self._config_table_name, "pools"):
                submit_to_origins.append(i["submit-to-origin"])
        except KeyError:
            return "N/A"
        return submit_to_origins

    @property
    def conf_retries_property(self):
        """
        Retrieves the retries from the config data.

        Returns:
            int: Retries, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["retries"], self._config_table_name, "retries")

    @property
    def conf_retry_pause_property(self):
        """
        Retrieves the retry pause from the config data.

        Returns:
            int: Retry pause, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["retry-pause"], self._config_table_name, "retry_pause")

    @property
    def conf_print_time_property(self):
        """
        Retrieves the print time from the config data.

        Returns:
            int: Print time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["print-time"], self._config_table_name, "print_time")

    @property
    def conf_health_print_time_property(self):
        """
        Retrieves the health print time from the config data.

        Returns:
            int: Health print time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["health-print-time"], self._config_table_name, "health_print_time")

    @property
    def conf_dmi_property(self):
        """
        Retrieves the DMI status from the config data.

        Returns:
            bool: DMI status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dmi"], self._config_table_name, "dmi")

    @property
    def conf_syslog_property(self):
        """
        Retrieves the syslog status from the config data.

        Returns:
            bool: Syslog status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["syslog"], self._config_table_name, "syslog")

    @property
    def conf_tls_property(self):
        """
        Retrieves the TLS property from the config data.

        Returns:
            dict: TLS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls"], self._config_table_name, "tls")

    @property
    def conf_tls_enabled_property(self):
        """
        Retrieves the TLS enabled status from the config data.

        Returns:
            bool: TLS enabled status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "enabled"], self._config_table_name, "tls_enabled")

    @property
    def conf_tls_protocols_property(self):
        """
        Retrieves the TLS protocols from the config data.

        Returns:
            str: TLS protocols, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "protocols"], self._config_table_name, "tls_protocols")

    @property
    def conf_tls_cert_property(self):
        """
        Retrieves the TLS certificate from the config data.

        Returns:
            str: TLS certificate, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "cert"], self._config_table_name, "tls_cert")

    @property
    def conf_tls_cert_key_property(self):
        """
        Retrieves the TLS certificate key from the config data.

        Returns:
            str: TLS certificate key, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "cert_key"], self._config_table_name, "tls_cert_key")

    @property
    def conf_tls_ciphers_property(self):
        """
        Retrieves the TLS ciphers from the config data.

        Returns:
            str: TLS ciphers, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "ciphers"], self._config_table_name, "tls_ciphers")

    @property
    def conf_tls_ciphersuites_property(self):
        """
        Retrieves the TLS ciphersuites from the config data.

        Returns:
            str: TLS ciphersuites, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "ciphersuites"], self._config_table_name, "tls_ciphersuites")

    @property
    def conf_tls_dhparam_property(self):
        """
        Retrieves the TLS DH parameter from the config data.

        Returns:
            str: TLS DH parameter, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["tls", "dhparam"], self._config_table_name, "tls_dhparam")

    @property
    def conf_dns_property(self):
        """
        Retrieves the DNS property from the config data.

        Returns:
            dict: DNS property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns"], self._config_table_name, "dns")

    @property
    def conf_dns_ipv6_property(self):
        """
        Retrieves the DNS IPv6 status from the config data.

        Returns:
            bool: DNS IPv6 status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns", "ipv6"], self._config_table_name, "dns_ipv6")

    @property
    def conf_dns_ttl_property(self):
        """
        Retrieves the DNS TTL from the config data.

        Returns:
            int: DNS TTL, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["dns", "ttl"], self._config_table_name, "dns_ttl")

    @property
    def conf_user_agent_property(self):
        """
        Retrieves the user agent from the config data.

        Returns:
            str: User agent, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["user-agent"], self._config_table_name, "user_agent")

    @property
    def conf_verbose_property(self):
        """
        Retrieves the verbose level from the config data.

        Returns:
            int: Verbose level, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["verbose"], self._config_table_name, "verbose")

    @property
    def conf_watch_property(self):
        """
        Retrieves the watch status from the config data.

        Returns:
            bool: Watch status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["watch"], self._config_table_name, "watch")

    @property
    def conf_rebench_algo_property(self):
        """
        Retrieves the rebench algorithm status from the config data.

        Returns:
            bool: Rebench algorithm status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["rebench-algo"], self._config_table_name, "rebench_algo")

    @property
    def conf_bench_algo_time_property(self):
        """
        Retrieves the bench algorithm time from the config data.

        Returns:
            int: Bench algorithm time, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["bench-algo-time"], self._config_table_name, "bench_algo_time")

    @property
    def conf_pause_on_battery_property(self):
        """
        Retrieves the pause on battery status from the config data.

        Returns:
            bool: Pause on battery status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pause-on-battery"], self._config_table_name, "pause_on_battery")

    @property
    def conf_pause_on_active_property(self):
        """
        Retrieves the pause on active status from the config data.

        Returns:
            bool: Pause on active status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["pause-on-active"], self._config_table_name, "pause_on_active")
    
    @property
    def conf_benchmark_property(self):
        """
        Retrieves the benchmark property from the config data.

        Returns:
            dict: Benchmark property, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark"], self._config_table_name, "benchmark")
    
    @property
    def conf_benchmark_size_property(self):
        """
        Retrieves the benchmark size from the config data.

        Returns:
            str: Benchmark size, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "size"], self._config_table_name, "benchmark_size")
    
    @property
    def conf_benchmark_algo_property(self):
        """
        Retrieves the benchmark algorithm from the config data.

        Returns:
            str: Benchmark algorithm, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "algo"], self._config_table_name, "benchmark_algo")
    
    @property
    def conf_benchmark_submit_property(self):
        """
        Retrieves the benchmark submit status from the config data.

        Returns:
            bool: Benchmark submit status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "submit"], self._config_table_name, "benchmark_submit")
    
    @property
    def conf_benchmark_verify_property(self):
        """
        Retrieves the benchmark verify status from the config data.

        Returns:
            str: Benchmark verify status, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "verify"], self._config_table_name, "benchmark_verify")
    
    @property
    def conf_benchmark_seed_property(self):
        """
        Retrieves the benchmark seed from the config data.

        Returns:
            str: Benchmark seed, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "seed"], self._config_table_name, "benchmark_seed")
    
    @property
    def conf_benchmark_hash_property(self):
        """
        Retrieves the benchmark hash from the config data.

        Returns:
            str: Benchmark hash, or "N/A" if not available.
        """
        return self._get_data_from_cache(self._config_cache, ["benchmark", "hash"], self._config_table_name, "benchmark_hash")

# Define the public interface of the module
__all__ = ["XMRigAPI"]