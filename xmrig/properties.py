"""
This module provides the XMRigProperties class, which is used to retrieve and cache various
properties and statistics from the XMRig miner's API responses. It also includes functionality
to fallback to the database if the data is not available in the cached responses.

Features:
- Retrieve and cache summary endpoint data.
- Retrieve and cache backends endpoint data.
- Retrieve and cache config endpoint data.
- Fallback to database retrieval if data is not available in cached responses.
- Provide various properties to access specific data points from the cached responses.
"""

from typing import Any, Dict, List, Union, Optional
from datetime import timedelta
from xmrig.helpers import log
from xmrig.db import XMRigDatabase
from json import JSONDecodeError

class XMRigProperties:
    """
    A class to represent and cache properties and statistics from the XMRig miner's API responses.

    Attributes:
        _summary_response (Dict[str, Any]): Cached summary endpoint data.
        _backends_response (List[Dict[str, Any]]): Cached backends endpoint data.
        _config_response (Dict[str, Any]): Cached config endpoint data.
        _db_url (Optional[str]): Database URL for storing miner data.
        _db_engine (Optional[Engine]): SQLAlchemy engine instance for database operations.
        _summary_table_name (str): Table name for summary data.
        _backends_table_names (List[str]): Table names for backends data.
        _config_table_name (str): Table name for config data.
    """
    def __init__(self, summary_response: Dict[str, Any], backends_response: List[Dict[str, Any]], config_response: Dict[str, Any], miner_name: str, db_url: Optional[str] = None):
        """
        Initializes the XMRigProperties instance with the provided API responses and database URL.

        Args:
            summary_response (Dict[str, Any]): Cached summary endpoint data.
            backends_response (List[Dict[str, Any]]): Cached backends endpoint data.
            config_response (Dict[str, Any]): Cached config endpoint data.
            miner_name (str): Unique name for the miner.
            db_url (Optional[str]): Database URL for storing miner data. Defaults to None.
        """
        self._summary_response = summary_response
        self._backends_response = backends_response
        self._config_response = config_response
        self._db_url = db_url
        self._db_engine = None
        if self._db_url is not None:
            self._db_engine = XMRigDatabase.init_db(self._db_url)
        self._summary_table_name = f"'{miner_name}-summary'"
        self._backends_table_names = [f"'{miner_name}-cpu-backend'", f"'{miner_name}-opencl-backend'", f"'{miner_name}-cuda-backend'"]
        self._config_table_name = f"'{miner_name}-config'"
    
    def _get_data_from_response(self, response: Union[Dict[str, Any], List[Dict[str, Any]]], keys: List[Union[str, int]], fallback_table_name: Union[str, List[str]]) -> Union[Any, str]:
        """
        Retrieves the data from the response using the provided keys. Falls back to the database if the data is not available.

        Args:
            response (Union[Dict[str, Any], List[Dict[str, Any]]]): The response data.
            keys (List[Union[str, int]]): The keys to use to retrieve the data.
            fallback_table_name (Union[str, List[str]]): The table name or list of table names to use for fallback database retrieval.

        Returns:
            Union[Any, str]: The retrieved data, or a default string value of "N/A" if not available.
        """
        try:
            data = response
            if len(keys) > 0:
                for key in keys:
                    data = data[key]
            else:
                data = data
            return data
        except (KeyError, TypeError, JSONDecodeError) as e:
            if self._db_engine is not None:
                log.debug(f"An error occurred fetching the data from the response using the provided keys, trying database: {e}")
                try:
                    return XMRigDatabase.fallback_to_db(fallback_table_name, keys, self._db_engine)
                except Exception as db_e:
                    log.error(f"An error occurred fetching the data from the database: {db_e}")
                    return "N/A"
            else:
                log.error(f"An error occurred fetching the data from the response using the provided keys: {e}")
                return "N/A"

    # TODO: Add config data points to properties.

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
        return self._get_data_from_response(self._summary_response, [], self._summary_table_name)

    @property
    def backends(self) -> Union[List[Dict[str, Any]], str]:
        """
        Retrieves the entire cached backends endpoint data.

        Returns:
            Union[List[Dict[str, Any]], str]: Current backends response, or "N/A" if not available.
        """
        all_backends = []
        for backend_table in self._backends_table_names:
            if XMRigDatabase.check_table_exists(self._db_url, backend_table):
                all_backends.append(self._get_data_from_response(self._backends_response, [], backend_table))
        all_backends = [i for i in all_backends if i != "N/A"]
        return all_backends

    @property
    def config(self) -> Union[Dict[str, Any], str]:
        """
        Retrieves the entire cached config endpoint data.

        Returns:
            Union[Dict[str, Any], str]: Current config response, or "N/A" if not available.
        """
        return self._get_data_from_response(self._config_response, [], self._config_table_name)
    
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
        return self._get_data_from_response(self._summary_response, ["id"], self._summary_table_name)

    @property
    def sum_worker_id(self) -> Union[str, Any]:
        """
        Retrieves the cached worker ID information from the summary data.

        Returns:
            Union[str, Any]: Worker ID information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["worker_id"], self._summary_table_name)

    @property
    def sum_uptime(self) -> Union[int, Any]:
        """
        Retrieves the cached current uptime from the summary data.

        Returns:
            Union[int, Any]: Current uptime in seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["uptime"], self._summary_table_name)

    @property
    def sum_uptime_readable(self) -> str:
        """
        Retrieves the cached uptime in a human-readable format from the summary data.

        Returns:
            str: Uptime in the format "days, hours:minutes:seconds", or "N/A" if not available.
        """
        result = self._get_data_from_response(self._summary_response, ["uptime"], self._summary_table_name)
        return str(timedelta(seconds=result)) if result != "N/A" else result

    @property
    def sum_restricted(self) -> Union[bool, Any]:
        """
        Retrieves the cached current restricted status from the summary data.

        Returns:
            Union[bool, Any]: Current restricted status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["restricted"], self._summary_table_name)

    @property
    def sum_resources(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached resources information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Resources information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources"], self._summary_table_name)

    @property
    def sum_memory_usage(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached memory usage from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Memory usage information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "memory"], self._summary_table_name)

    @property
    def sum_free_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached free memory from the summary data.

        Returns:
            Union[int, Any]: Free memory information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "free"], self._summary_table_name)

    @property
    def sum_total_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached total memory from the summary data.

        Returns:
            Union[int, Any]: Total memory information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "total"], self._summary_table_name)

    @property
    def sum_resident_set_memory(self) -> Union[int, Any]:
        """
        Retrieves the cached resident set memory from the summary data.

        Returns:
            Union[int, Any]: Resident set memory information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "resident_set_memory"], self._summary_table_name)

    @property
    def sum_load_average(self) -> Union[List[float], Any]:
        """
        Retrieves the cached load average from the summary data.

        Returns:
            Union[List[float], Any]: Load average information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "load_average"], self._summary_table_name)

    @property
    def sum_hardware_concurrency(self) -> Union[int, Any]:
        """
        Retrieves the cached hardware concurrency from the summary data.

        Returns:
            Union[int, Any]: Hardware concurrency information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["resources", "hardware_concurrency"], self._summary_table_name)

    @property
    def sum_features(self) -> Union[List[str], Any]:
        """
        Retrieves the cached supported features information from the summary data.

        Returns:
            Union[List[str], Any]: Supported features information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["features"], self._summary_table_name)

    @property
    def sum_results(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached results information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Results information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results"], self._summary_table_name)

    @property
    def sum_current_difficulty(self) -> Union[int, Any]:
        """
        Retrieves the cached current difficulty from the summary data.

        Returns:
            Union[int, Any]: Current difficulty, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "diff_current"], self._summary_table_name)

    @property
    def sum_good_shares(self) -> Union[int, Any]:
        """
        Retrieves the cached good shares from the summary data.

        Returns:
            Union[int, Any]: Good shares, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "shares_good"], self._summary_table_name)

    @property
    def sum_total_shares(self) -> Union[int, Any]:
        """
        Retrieves the cached total shares from the summary data.

        Returns:
            Union[int, Any]: Total shares, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "shares_total"], self._summary_table_name)

    @property
    def sum_avg_time(self) -> Union[int, Any]:
        """
        Retrieves the cached average time information from the summary data.

        Returns:
            Union[int, Any]: Average time information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "avg_time"], self._summary_table_name)

    @property
    def sum_avg_time_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached average time in `ms` information from the summary data.

        Returns:
            Union[int, Any]: Average time in `ms` information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "avg_time_ms"], self._summary_table_name)

    @property
    def sum_total_hashes(self) -> Union[int, Any]:
        """
        Retrieves the cached total number of hashes from the summary data.

        Returns:
            Union[int, Any]: Total number of hashes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "hashes_total"], self._summary_table_name)

    @property
    def sum_best_results(self) -> Union[List[int], Any]:
        """
        Retrieves the cached best results from the summary data.

        Returns:
            Union[List[int], Any]: Best results, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["results", "best"], self._summary_table_name)

    @property
    def sum_algorithm(self) -> Union[str, Any]:
        """
        Retrieves the cached current mining algorithm from the summary data.

        Returns:
            Union[str, Any]: Current mining algorithm, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["algo"], self._summary_table_name)

    @property
    def sum_connection(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached connection information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Connection information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection"], self._summary_table_name)

    @property
    def sum_pool_info(self) -> Union[str, Any]:
        """
        Retrieves the cached pool information from the summary data.

        Returns:
            Union[str, Any]: Pool information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "pool"], self._summary_table_name)

    @property
    def sum_pool_ip_address(self) -> Union[str, Any]:
        """
        Retrieves the cached IP address from the summary data.

        Returns:
            Union[str, Any]: IP address, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "ip"], self._summary_table_name)

    @property
    def sum_pool_uptime(self) -> Union[int, Any]:
        """
        Retrieves the cached pool uptime information from the summary data.

        Returns:
            Union[int, Any]: Pool uptime information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "uptime"], self._summary_table_name)

    @property
    def sum_pool_uptime_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached pool uptime in ms from the summary data.

        Returns:
            Union[int, Any]: Pool uptime in ms, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "uptime_ms"], self._summary_table_name)

    @property
    def sum_pool_ping(self) -> Union[int, Any]:
        """
        Retrieves the cached pool ping information from the summary data.

        Returns:
            Union[int, Any]: Pool ping information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "ping"], self._summary_table_name)

    @property
    def sum_pool_failures(self) -> Union[int, Any]:
        """
        Retrieves the cached pool failures information from the summary data.

        Returns:
            Union[int, Any]: Pool failures information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "failures"], self._summary_table_name)

    @property
    def sum_pool_tls(self) -> Union[bool, Any]:
        """
        Retrieves the cached pool tls status from the summary data.

        Returns:
            Union[bool, Any]: Pool tls status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "tls"], self._summary_table_name)

    @property
    def sum_pool_tls_fingerprint(self) -> Union[str, Any]:
        """
        Retrieves the cached pool tls fingerprint information from the summary data.

        Returns:
            Union[str, Any]: Pool tls fingerprint information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "tls-fingerprint"], self._summary_table_name)

    @property
    def sum_pool_algo(self) -> Union[str, Any]:
        """
        Retrieves the cached pool algorithm information from the summary data.

        Returns:
            Union[str, Any]: Pool algorithm information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "algo"], self._summary_table_name)

    @property
    def sum_pool_diff(self) -> Union[int, Any]:
        """
        Retrieves the cached pool difficulty information from the summary data.

        Returns:
            Union[int, Any]: Pool difficulty information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "diff"], self._summary_table_name)

    @property
    def sum_pool_accepted_jobs(self) -> Union[int, Any]:
        """
        Retrieves the cached number of accepted jobs from the summary data.

        Returns:
            Union[int, Any]: Number of accepted jobs, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "accepted"], self._summary_table_name)

    @property
    def sum_pool_rejected_jobs(self) -> Union[int, Any]:
        """
        Retrieves the cached number of rejected jobs from the summary data.

        Returns:
            Union[int, Any]: Number of rejected jobs, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response,  ["connection", "rejected"], self._summary_table_name)

    @property
    def sum_pool_average_time(self) -> Union[int, Any]:
        """
        Retrieves the cached pool average time information from the summary data.

        Returns:
            Union[int, Any]: Pool average time information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "avg_time"], self._summary_table_name)

    @property
    def sum_pool_average_time_ms(self) -> Union[int, Any]:
        """
        Retrieves the cached pool average time in ms from the summary data.

        Returns:
            Union[int, Any]: Pool average time in ms, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "avg_time_ms"], self._summary_table_name)

    @property
    def sum_pool_total_hashes(self) -> Union[int, Any]:
        """
        Retrieves the cached pool total hashes information from the summary data.

        Returns:
            Union[int, Any]: Pool total hashes information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["connection", "hashes_total"], self._summary_table_name)

    @property
    def sum_version(self) -> Union[str, Any]:
        """
        Retrieves the cached version information from the summary data.

        Returns:
            Union[str, Any]: Version information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["version"], self._summary_table_name)

    @property
    def sum_kind(self) -> Union[str, Any]:
        """
        Retrieves the cached kind information from the summary data.

        Returns:
            Union[str, Any]: Kind information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["kind"], self._summary_table_name)

    @property
    def sum_ua(self) -> Union[str, Any]:
        """
        Retrieves the cached user agent information from the summary data.

        Returns:
            Union[str, Any]: User agent information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["ua"], self._summary_table_name)

    @property
    def sum_cpu_info(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached CPU information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: CPU information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu"], self._summary_table_name)

    @property
    def sum_cpu_brand(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU brand information from the summary data.

        Returns:
            Union[str, Any]: CPU brand information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "brand"], self._summary_table_name)

    @property
    def sum_cpu_family(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU family information from the summary data.

        Returns:
            Union[int, Any]: CPU family information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "family"], self._summary_table_name)

    @property
    def sum_cpu_model(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU model information from the summary data.

        Returns:
            Union[int, Any]: CPU model information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "model"], self._summary_table_name)

    @property
    def sum_cpu_stepping(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU stepping information from the summary data.

        Returns:
            Union[int, Any]: CPU stepping information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response,  ["cpu", "stepping"], self._summary_table_name)

    @property
    def sum_cpu_proc_info(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU frequency information from the summary data.

        Returns:
            Union[int, Any]: CPU frequency information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "proc_info"], self._summary_table_name)

    @property
    def sum_cpu_aes(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU AES support status from the summary data.

        Returns:
            Union[bool, Any]: CPU AES support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "aes"], self._summary_table_name)

    @property
    def sum_cpu_avx2(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU AVX2 support status from the summary data.

        Returns:
            Union[bool, Any]: CPU AVX2 support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "avx2"], self._summary_table_name)

    @property
    def sum_cpu_x64(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU x64 support status from the summary data.

        Returns:
            Union[bool, Any]: CPU x64 support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "x64"], self._summary_table_name)

    @property
    def sum_cpu_64_bit(self) -> Union[bool, Any]:
        """
        Retrieves the cached CPU 64-bit support status from the summary data.

        Returns:
            Union[bool, Any]: CPU 64-bit support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "64_bit"], self._summary_table_name)

    @property
    def sum_cpu_l2(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU L2 cache size from the summary data.

        Returns:
            Union[int, Any]: CPU L2 cache size, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "l2"], self._summary_table_name)

    @property
    def sum_cpu_l3(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU L3 cache size from the summary data.

        Returns:
            Union[int, Any]: CPU L3 cache size, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "l3"], self._summary_table_name)

    @property
    def sum_cpu_cores(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU cores count from the summary data.

        Returns:
            Union[int, Any]: CPU cores count, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "cores"], self._summary_table_name)

    @property
    def sum_cpu_threads(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU threads count from the summary data.

        Returns:
            Union[int, Any]: CPU threads count, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "threads"], self._summary_table_name)

    @property
    def sum_cpu_packages(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU packages count from the summary data.

        Returns:
            Union[int, Any]: CPU packages count, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "packages"], self._summary_table_name)

    @property
    def sum_cpu_nodes(self) -> Union[int, Any]:
        """
        Retrieves the cached CPU nodes count from the summary data.

        Returns:
            Union[int, Any]: CPU nodes count, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "nodes"], self._summary_table_name)

    @property
    def sum_cpu_backend(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU backend information from the summary data.

        Returns:
            Union[str, Any]: CPU backend information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response,  ["cpu", "backend"], self._summary_table_name)

    @property
    def sum_cpu_msr(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU MSR information from the summary data.

        Returns:
            Union[str, Any]: CPU MSR information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "msr"], self._summary_table_name)

    @property
    def sum_cpu_assembly(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU assembly information from the summary data.

        Returns:
            Union[str, Any]: CPU assembly information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response,  ["cpu", "assembly"], self._summary_table_name)

    @property
    def sum_cpu_arch(self) -> Union[str, Any]:
        """
        Retrieves the cached CPU architecture information from the summary data.

        Returns:
            Union[str, Any]: CPU architecture information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "arch"], self._summary_table_name)

    @property
    def sum_cpu_flags(self) -> Union[List[str], Any]:
        """
        Retrieves the cached CPU flags information from the summary data.

        Returns:
            Union[List[str], Any]: CPU flags information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["cpu", "flags"], self._summary_table_name)

    @property
    def sum_donate_level(self) -> Union[int, Any]:
        """
        Retrieves the cached donate level information from the summary data.

        Returns:
            Union[int, Any]: Donate level information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["donate_level"], self._summary_table_name)

    @property
    def sum_paused(self) -> Union[bool, Any]:
        """
        Retrieves the cached paused status from the summary data.

        Returns:
            Union[bool, Any]: Paused status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["paused"], self._summary_table_name)

    @property
    def sum_algorithms(self) -> Union[List[str], Any]:
        """
        Retrieves the cached algorithms information from the summary data.

        Returns:
            Union[List[str], Any]: Algorithms information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["algorithms"], self._summary_table_name)

    @property
    def sum_hashrates(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the cached hashrate information from the summary data.

        Returns:
            Union[Dict[str, Any], Any]: Hashrate information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hashrate"], self._summary_table_name)

    @property
    def sum_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 10 seconds from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 0], self._summary_table_name)

    @property
    def sum_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 1 minute from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 1], self._summary_table_name)

    @property
    def sum_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the cached hashrate for the last 15 minutes from the summary data.

        Returns:
            Union[float, Any]: Hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 2], self._summary_table_name)

    @property
    def sum_hashrate_highest(self) -> Union[float, Any]:
        """
        Retrieves the cached highest hashrate from the summary data.

        Returns:
            Union[float, Any]: Highest hashrate, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hashrate", "highest"], self._summary_table_name)

    @property
    def sum_hugepages(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the cached hugepages information from the summary data.

        Returns:
            Union[List[Dict[str, Any]], Any]: Hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._summary_response, ["hugepages"], self._summary_table_name)

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
        all_backend_types = []
        for backend_table in self._backends_table_names:
            if XMRigDatabase.check_table_exists(self._db_url, backend_table):
                all_backend_types.append(self._get_data_from_response(self._backends_response, ["type"], backend_table))
        # edit all_backend_types to remove any value that is "N/A"
        all_backend_types = [i for i in all_backend_types if i != "N/A"]
        return all_backend_types

    @property
    def be_cpu_type(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend type from the backends data.

        Returns:
            Union[str, Any]: CPU backend type, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "type"], self._backends_table_names[0])

    @property
    def be_cpu_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "enabled"], self._backends_table_names[0])

    @property
    def be_cpu_algo(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend algorithm from the backends data.

        Returns:
            Union[str, Any]: CPU backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "algo"], self._backends_table_names[0])

    @property
    def be_cpu_profile(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend profile from the backends data.

        Returns:
            Union[str, Any]: CPU backend profile, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "profile"], self._backends_table_names[0])

    @property
    def be_cpu_hw_aes(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend hardware AES support status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend hardware AES support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hw-aes"], self._backends_table_names[0])

    @property
    def be_cpu_priority(self) -> Union[int, Any]:
        """
        Retrieves the CPU backend priority from the backends data.

        Returns:
            Union[int, Any]: CPU backend priority, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "priority"], self._backends_table_names[0])

    @property
    def be_cpu_msr(self) -> Union[bool, Any]:
        """
        Retrieves the CPU backend MSR support status from the backends data.

        Returns:
            Union[bool, Any]: CPU backend MSR support status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "msr"], self._backends_table_names[0])

    @property
    def be_cpu_asm(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend assembly information from the backends data.

        Returns:
            Union[str, Any]: CPU backend assembly information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "asm"], self._backends_table_names[0])

    @property
    def be_cpu_argon2_impl(self) -> Union[str, Any]:
        """
        Retrieves the CPU backend Argon2 implementation from the backends data.

        Returns:
            Union[str, Any]: CPU backend Argon2 implementation, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "argon2-impl"], self._backends_table_names[0])

    @property
    def be_cpu_hugepages(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the CPU backend hugepages information from the backends data.

        Returns:
            Union[List[Dict[str, Any]], Any]: CPU backend hugepages information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hugepages"], self._backends_table_names[0])

    @property
    def be_cpu_memory(self) -> Union[int, Any]:
        """
        Retrieves the CPU backend memory information from the backends data.

        Returns:
            Union[int, Any]: CPU backend memory information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "memory"], self._backends_table_names[0])

    @property
    def be_cpu_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hashrate"], self._backends_table_names[0])

    @property
    def be_cpu_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 0], self._backends_table_names[0])

    @property
    def be_cpu_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 1], self._backends_table_names[0])

    @property
    def be_cpu_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CPU backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CPU backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 2], self._backends_table_names[0])
    
    @property
    def be_cpu_threads(self) -> Union[List[Dict[str, Any]], Any]:
        """
        Retrieves the CPU backend threads information from the backends data.

        Returns:
            Union[List[Dict[str, Any]], Any]: CPU backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0])

    @property
    def be_cpu_threads_intensity(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads intensity information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads intensity information, or "N/A" if not available.
        """
        intensities = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                intensities.append(i["intensity"])
        return intensities

    @property
    def be_cpu_threads_affinity(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads affinity information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads affinity information, or "N/A" if not available.
        """
        affinities = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                affinities.append(i["affinity"])
        return affinities

    @property
    def be_cpu_threads_av(self) -> Union[List[int], Any]:
        """
        Retrieves the CPU backend threads AV information from the backends data.

        Returns:
            Union[List[int], Any]: CPU backend threads AV information, or "N/A" if not available.
        """
        avs = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                avs.append(i["av"])
        return avs

    @property
    def be_cpu_threads_hashrates_10s(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 10 seconds from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                hashrates_10s.append(i["hashrate"][0])
        return hashrates_10s

    @property
    def be_cpu_threads_hashrates_1m(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 1 minute from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                hashrates_1m.append(i["hashrate"][1])
        return hashrates_1m

    @property
    def be_cpu_threads_hashrates_15m(self) -> Union[List[float], Any]:
        """
        Retrieves the CPU backend threads hashrates for the last 15 minutes from the backends data.

        Returns:
            Union[List[float], Any]: CPU backend threads hashrates for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        for i in self._get_data_from_response(self._backends_response, [0, "threads"], self._backends_table_names[0]):
                hashrates_15m.append(i["hashrate"][2])
        return hashrates_15m

    @property
    def be_opencl_type(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend type from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend type, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "type"], self._backends_table_names[1])

    @property
    def be_opencl_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the OpenCL backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: OpenCL backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "enabled"], self._backends_table_names[1])

    @property
    def be_opencl_algo(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend algorithm from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "algo"], self._backends_table_names[1])

    @property
    def be_opencl_profile(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend profile from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend profile, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "profile"], self._backends_table_names[1])

    @property
    def be_opencl_platform(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend platform information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend platform information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform"], self._backends_table_names[1])

    @property
    def be_opencl_platform_index(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend platform index from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend platform index, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "index"], self._backends_table_names[1])

    @property
    def be_opencl_platform_profile(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform profile from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform profile, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "profile"], self._backends_table_names[1])

    @property
    def be_opencl_platform_version(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform version from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform version, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "version"], self._backends_table_names[1])

    @property
    def be_opencl_platform_name(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform name from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform name, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "name"], self._backends_table_names[1])

    @property
    def be_opencl_platform_vendor(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform vendor from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform vendor, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "vendor"], self._backends_table_names[1])

    @property
    def be_opencl_platform_extensions(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend platform extensions from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend platform extensions, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "platform", "extensions"], self._backends_table_names[1])

    @property
    def be_opencl_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the OpenCL backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: OpenCL backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "hashrate"], self._backends_table_names[1])

    @property
    def be_opencl_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 0], self._backends_table_names[1])

    @property
    def be_opencl_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 1], self._backends_table_names[1])

    @property
    def be_opencl_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 2], self._backends_table_names[1])

    @property
    def be_opencl_threads(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend threads information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0], self._backends_table_names[1])

    @property
    def be_opencl_threads_index(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads index from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads index, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "index"], self._backends_table_names[1])

    @property
    def be_opencl_threads_intensity(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads intensity from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads intensity, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "intensity"], self._backends_table_names[1])

    @property
    def be_opencl_threads_worksize(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads worksize from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads worksize, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "worksize"], self._backends_table_names[1])

    @property
    def be_opencl_threads_amount(self) -> Union[List[int], Any]:
        """
        Retrieves the OpenCL backend threads amount from the backends data.

        Returns:
            Union[List[int], Any]: OpenCL backend threads amount, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "threads"], self._backends_table_names[1])

    @property
    def be_opencl_threads_unroll(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads unroll from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads unroll, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "unroll"], self._backends_table_names[1])

    @property
    def be_opencl_threads_affinity(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads affinity from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads affinity, or "N/A" if not available.
        """
        
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "affinity"], self._backends_table_names[1])

    @property
    def be_opencl_threads_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the OpenCL backend threads hashrates from the backends data.

        Returns:
            Union[List[float], Any]: OpenCL backend threads hashrates, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate"], self._backends_table_names[1])

    @property
    def be_opencl_threads_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 0], self._backends_table_names[1])

    @property
    def be_opencl_threads_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 1], self._backends_table_names[1])

    @property
    def be_opencl_threads_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: OpenCL backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 2], self._backends_table_names[1])

    @property
    def be_opencl_threads_board(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads board information from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads board information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "board"], self._backends_table_names[1])

    @property
    def be_opencl_threads_name(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads name from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads name, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "name"], self._backends_table_names[1])

    @property
    def be_opencl_threads_bus_id(self) -> Union[str, Any]:
        """
        Retrieves the OpenCL backend threads bus ID from the backends data.

        Returns:
            Union[str, Any]: OpenCL backend threads bus ID, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "bus_id"], self._backends_table_names[1])

    @property
    def be_opencl_threads_cu(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads compute units from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads compute units, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "cu"], self._backends_table_names[1])

    @property
    def be_opencl_threads_global_mem(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads global memory from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads global memory, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "global_mem"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the OpenCL backend threads health information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: OpenCL backend threads health information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health_temp(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health temperature from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health temperature, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "temperature"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health_power(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health power from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health power, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "power"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health_clock(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health clock from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health clock, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "clock"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health_mem_clock(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health memory clock from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health memory clock, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "mem_clock"], self._backends_table_names[1])

    @property
    def be_opencl_threads_health_rpm(self) -> Union[int, Any]:
        """
        Retrieves the OpenCL backend threads health RPM from the backends data.

        Returns:
            Union[int, Any]: OpenCL backend threads health RPM, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "rpm"], self._backends_table_names[1])

    @property
    def be_cuda_type(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend type from the backends data.

        Returns:
            Union[str, Any]: CUDA backend type, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "type"], self._backends_table_names[2])

    @property
    def be_cuda_enabled(self) -> Union[bool, Any]:
        """
        Retrieves the CUDA backend enabled status from the backends data.

        Returns:
            Union[bool, Any]: CUDA backend enabled status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "enabled"], self._backends_table_names[2])

    @property
    def be_cuda_algo(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend algorithm from the backends data.

        Returns:
            Union[str, Any]: CUDA backend algorithm, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "algo"], self._backends_table_names[2])

    @property
    def be_cuda_profile(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend profile from the backends data.

        Returns:
            Union[str, Any]: CUDA backend profile, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "profile"], self._backends_table_names[2])

    @property
    def be_cuda_versions(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the CUDA backend versions information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: CUDA backend versions information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "versions"], self._backends_table_names[2])

    @property
    def be_cuda_runtime(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend runtime version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend runtime version, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "versions", "cuda-runtime"], self._backends_table_names[2])

    @property
    def be_cuda_driver(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend driver version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend driver version, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "versions", "cuda-driver"], self._backends_table_names[2])

    @property
    def be_cuda_plugin(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend plugin version from the backends data.

        Returns:
            Union[str, Any]: CUDA backend plugin version, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "versions", "plugin"], self._backends_table_names[2])

    @property
    def be_cuda_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CUDA backend hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CUDA backend hashrates, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "hashrate"], self._backends_table_names[2])

    @property
    def be_cuda_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 0], self._backends_table_names[2])

    @property
    def be_cuda_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 1], self._backends_table_names[2])

    @property
    def be_cuda_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CUDA backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 2], self._backends_table_names[2])

    @property
    def be_cuda_threads(self) -> Union[Dict[str, Any], Any]:
        """
        Retrieves the CUDA backend threads information from the backends data.

        Returns:
            Union[Dict[str, Any], Any]: CUDA backend threads information, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0], self._backends_table_names[2])

    @property
    def be_cuda_threads_index(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads index from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads index, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "index"], self._backends_table_names[2])

    @property
    def be_cuda_threads_amount(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads amount from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads amount, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "threads"], self._backends_table_names[2])

    @property
    def be_cuda_threads_blocks(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads blocks from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads blocks, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "blocks"], self._backends_table_names[2])

    @property
    def be_cuda_threads_bfactor(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads bfactor from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads bfactor, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bfactor"], self._backends_table_names[2])

    @property
    def be_cuda_threads_bsleep(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads bsleep from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads bsleep, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bsleep"], self._backends_table_names[2])

    @property
    def be_cuda_threads_affinity(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads affinity from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads affinity, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "affinity"], self._backends_table_names[2])

    @property
    def be_cuda_threads_dataset_host(self) -> Union[bool, Any]:
        """
        Retrieves the CUDA backend threads dataset host status from the backends data.

        Returns:
            Union[bool, Any]: CUDA backend threads dataset host status, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "dataset_host"], self._backends_table_names[2])

    @property
    def be_cuda_threads_hashrates(self) -> Union[List[float], Any]:
        """
        Retrieves the CUDA backend threads hashrates from the backends data.

        Returns:
            Union[List[float], Any]: CUDA backend threads hashrates, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate"], self._backends_table_names[2])

    @property
    def be_cuda_threads_hashrate_10s(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 0], self._backends_table_names[2])

    @property
    def be_cuda_threads_hashrate_1m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 1], self._backends_table_names[2])

    @property
    def be_cuda_threads_hashrate_15m(self) -> Union[float, Any]:
        """
        Retrieves the CUDA backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            Union[float, Any]: CUDA backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 2], self._backends_table_names[2])

    @property
    def be_cuda_threads_name(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend threads name from the backends data.

        Returns:
            Union[str, Any]: CUDA backend threads name, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "name"], self._backends_table_names[2])

    @property
    def be_cuda_threads_bus_id(self) -> Union[str, Any]:
        """
        Retrieves the CUDA backend threads bus ID from the backends data.

        Returns:
            Union[str, Any]: CUDA backend threads bus ID, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bus_id"], self._backends_table_names[2])

    @property
    def be_cuda_threads_smx(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads SMX count from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads SMX count, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "smx"], self._backends_table_names[2])

    @property
    def be_cuda_threads_arch(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads architecture from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads architecture, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "arch"], self._backends_table_names[2])

    @property
    def be_cuda_threads_global_mem(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads global memory from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads global memory, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "global_mem"], self._backends_table_names[2])

    @property
    def be_cuda_threads_clock(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads clock from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads clock, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "clock"], self._backends_table_names[2])

    @property
    def be_cuda_threads_memory_clock(self) -> Union[int, Any]:
        """
        Retrieves the CUDA backend threads memory clock from the backends data.

        Returns:
            Union[int, Any]: CUDA backend threads memory clock, or "N/A" if not available.
        """
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "memory_clock"], self._backends_table_names[2])

