"""
This module provides the XMRigProperties class, which is used to retrieve and cache various
properties and statistics from the XMRig miner's API responses.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import timedelta
from xmrig.helpers import log
from sqlalchemy.engine import Engine

# TODO: Integrate database functionality to fallback and retrieve data from the database if the API or response is not available.
# TODO: If the data from the cached response or data from the database is not available, return a string like "N/A" or "Not Available" instead of False.

class XMRigProperties:
    """
    A class to represent and cache properties and statistics from the XMRig miner's API responses.

    Attributes:
        summary_response (Dict[str, Any]): Cached summary endpoint data.
        backends_response (Dict[str, Any]): Cached backends endpoint data.
        config_response (Dict[str, Any]): Cached config endpoint data.
    """
    def __init__(self, summary_response: Dict[str, Any], backends_response: Dict[str, Any], config_response: Dict[str, Any], db_engine: Engine):
        self._summary_response = summary_response
        self._backends_response = backends_response
        self._config_response = config_response
        self._db_engine = db_engine
    
    # TODO: Add fallback to database if data is not available in the cached response
    # TODO: Handle JSONDecodeError and exception from missing table/data within database

    def _get_data_from_response(self, response: Dict[str, Any], keys: List[str]) -> Union[Any, str]:
        """
        Retrieves the data from the response using the provided keys.

        Args:
            response (Dict[str, Any]): The response data.
            keys (List[str]): The keys to use to retrieve the data.

        Returns:
            Union[Any, str]: The retrieved data, or a default string value of "N/A" if not available.
        """
        try:
            data = response
            if len(keys) > 0:
                for key in keys:
                    data = data[key]
            return data
        except Exception as e:
            log.error(f"An error occurred fetching the data from the response using the provided keys: {e}")
            return "N/A"

    @property
    def summary(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the entire cached summary endpoint data.

        Returns:
            dict: Current summary response, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response)
        return self._get_data_from_response(self._summary_response, [])

    @property
    def backends(self) -> Union[List[Dict[str, Any]], bool]:
        """
        Retrieves the entire cached backends endpoint data.

        Returns:
            list: Current backends response, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response)
        return self._get_data_from_response(self._backends_response, [])

    @property
    def config(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the entire cached config endpoint data.

        Returns:
            dict: Current config response, or "N/A" if not available.
        """
        if self._config_response is not None:
            log.debug(self._config_response)
        return self._get_data_from_response(self._config_response, [])

    @property
    def sum_id(self) -> Union[str, bool]:
        """
        Retrieves the cached ID information from the summary data.

        Returns:
            str: ID information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["id"])
        return self._get_data_from_response(self._summary_response, ["id"])

    @property
    def sum_worker_id(self) -> Union[str, bool]:
        """
        Retrieves the cached worker ID information from the summary data.

        Returns:
            str: Worker ID information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["worker_id"])
        return self._get_data_from_response(self._summary_response, ["worker_id"])

    @property
    def sum_uptime(self) -> Union[int, bool]:
        """
        Retrieves the cached current uptime from the summary data.

        Returns:
            int: Current uptime in seconds, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["uptime"])
        return self._get_data_from_response(self._summary_response, ["uptime"])

    @property
    def sum_uptime_readable(self) -> Union[str, bool]:
        """
        Retrieves the cached uptime in a human-readable format from the summary data.

        Returns:
            str: Uptime in the format "days, hours:minutes:seconds", or "N/A" if not available.
        """
        log.debug(str(timedelta(seconds=self._summary_response["uptime"])))
        return str(timedelta(seconds=self._get_data_from_response(self._summary_response, ["uptime"])))

    @property
    def sum_restricted(self) -> Optional[bool]:
        """
        Retrieves the cached current restricted status from the summary data.

        Returns:
            bool: Current restricted status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["restricted"])
        return self._get_data_from_response(self._summary_response, ["restricted"])

    @property
    def sum_resources(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached resources information from the summary data.

        Returns:
            dict: Resources information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"])
        return self._get_data_from_response(self._summary_response, ["resources"])

    @property
    def sum_memory_usage(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached memory usage from the summary data.

        Returns:
            dict: Memory usage information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["memory"])
        return self._get_data_from_response(self._summary_response, ["resources", "memory"])

    @property
    def sum_free_memory(self) -> Union[int, bool]:
        """
        Retrieves the cached free memory from the summary data.

        Returns:
            int: Free memory information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["memory"]["free"])
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "free"])

    @property
    def sum_total_memory(self) -> Union[int, bool]:
        """
        Retrieves the cached total memory from the summary data.

        Returns:
            int: Total memory information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["memory"]["total"])
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "total"])

    @property
    def sum_resident_set_memory(self) -> Union[int, bool]:
        """
        Retrieves the cached resident set memory from the summary data.

        Returns:
            int: Resident set memory information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["memory"]["resident_set_memory"])
        return self._get_data_from_response(self._summary_response, ["resources", "memory", "resident_set_memory"])

    @property
    def sum_load_average(self) -> Union[List[float], bool]:
        """
        Retrieves the cached load average from the summary data.

        Returns:
            list: Load average information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["load_average"])
        return self._get_data_from_response(self._summary_response, ["resources", "load_average"])

    @property
    def sum_hardware_concurrency(self) -> Union[int, bool]:
        """
        Retrieves the cached hardware concurrency from the summary data.

        Returns:
            int: Hardware concurrency information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["resources"]["hardware_concurrency"])
        return self._get_data_from_response(self._summary_response, ["resources", "hardware_concurrency"])

    @property
    def sum_features(self) -> Union[List[str], bool]:
        """
        Retrieves the cached supported features information from the summary data.

        Returns:
            list: Supported features information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["features"])
        return self._get_data_from_response(self._summary_response, ["features"])

    @property
    def sum_results(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached results information from the summary data.

        Returns:
            dict: Results information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"])
        return self._get_data_from_response(self._summary_response, ["results"])

    @property
    def sum_current_difficulty(self) -> Union[int, bool]:
        """
        Retrieves the cached current difficulty from the summary data.

        Returns:
            int: Current difficulty, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["diff_current"])
        return self._get_data_from_response(self._summary_response, ["results", "diff_current"])

    @property
    def sum_good_shares(self) -> Union[int, bool]:
        """
        Retrieves the cached good shares from the summary data.

        Returns:
            int: Good shares, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["shares_good"])
        return self._get_data_from_response(self._summary_response, ["results", "shares_good"])

    @property
    def sum_total_shares(self) -> Union[int, bool]:
        """
        Retrieves the cached total shares from the summary data.

        Returns:
            int: Total shares, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["shares_total"])
        return self._get_data_from_response(self._summary_response, ["results", "shares_total"])

    @property
    def sum_avg_time(self) -> Union[int, bool]:
        """
        Retrieves the cached average time information from the summary data.

        Returns:
            int: Average time information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["avg_time"])
        return self._get_data_from_response(self._summary_response, ["results", "avg_time"])

    @property
    def sum_avg_time_ms(self) -> Union[int, bool]:
        """
        Retrieves the cached average time in `ms` information from the summary data.

        Returns:
            int: Average time in `ms` information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["avg_time_ms"])
        return self._get_data_from_response(self._summary_response, ["results", "avg_time_ms"])

    @property
    def sum_total_hashes(self) -> Union[int, bool]:
        """
        Retrieves the cached total number of hashes from the summary data.

        Returns:
            int: Total number of hashes, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["hashes_total"])
        return self._get_data_from_response(self._summary_response, ["results", "hashes_total"])

    @property
    def sum_best_results(self) -> Union[List[int], bool]:
        """
        Retrieves the cached best results from the summary data.

        Returns:
            list: Best results, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["results"]["best"])
        return self._get_data_from_response(self._summary_response, ["results", "best"])

    @property
    def sum_algorithm(self) -> Union[str, bool]:
        """
        Retrieves the cached current mining algorithm from the summary data.

        Returns:
            str: Current mining algorithm, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["algo"])
        return self._get_data_from_response(self._summary_response, ["algo"])

    @property
    def sum_connection(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached connection information from the summary data.

        Returns:
            dict: Connection information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"])
        return self._get_data_from_response(self._summary_response, ["connection"])

    @property
    def sum_pool_info(self) -> Union[str, bool]:
        """
        Retrieves the cached pool information from the summary data.

        Returns:
            str: Pool information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["pool"])
        return self._get_data_from_response(self._summary_response, ["connection", "pool"])

    @property
    def sum_pool_ip_address(self) -> Union[str, bool]:
        """
        Retrieves the cached IP address from the summary data.

        Returns:
            str: IP address, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["ip"])
        return self._get_data_from_response(self._summary_response, ["connection", "ip"])

    @property
    def sum_pool_uptime(self) -> Union[int, bool]:
        """
        Retrieves the cached pool uptime information from the summary data.

        Returns:
            int: Pool uptime information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["uptime"])
        return self._get_data_from_response(self._summary_response, ["connection", "uptime"])

    @property
    def sum_pool_uptime_ms(self) -> Union[int, bool]:
        """
        Retrieves the cached pool uptime in ms from the summary data.

        Returns:
            int: Pool uptime in ms, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["uptime_ms"])
        return self._get_data_from_response(self._summary_response, ["connection", "uptime_ms"])

    @property
    def sum_pool_ping(self) -> Union[int, bool]:
        """
        Retrieves the cached pool ping information from the summary data.

        Returns:
            int: Pool ping information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["ping"])
        return self._get_data_from_response(self._summary_response, ["connection", "ping"])

    @property
    def sum_pool_failures(self) -> Union[int, bool]:
        """
        Retrieves the cached pool failures information from the summary data.

        Returns:
            int: Pool failures information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["failures"])
        return self._get_data_from_response(self._summary_response, ["connection", "failures"])

    @property
    def sum_pool_tls(self) -> Optional[bool]:
        """
        Retrieves the cached pool tls status from the summary data.

        Returns:
            bool: Pool tls status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["tls"])
        return self._get_data_from_response(self._summary_response, ["connection", "tls"])

    @property
    def sum_pool_tls_fingerprint(self) -> Union[str, bool]:
        """
        Retrieves the cached pool tls fingerprint information from the summary data.

        Returns:
            str: Pool tls fingerprint information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["tls-fingerprint"])
        return self._get_data_from_response(self._summary_response, ["connection", "tls-fingerprint"])

    @property
    def sum_pool_algo(self) -> Union[str, bool]:
        """
        Retrieves the cached pool algorithm information from the summary data.

        Returns:
            str: Pool algorithm information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["algo"])
        return self._get_data_from_response(self._summary_response, ["connection", "algo"])

    @property
    def sum_pool_diff(self) -> Union[int, bool]:
        """
        Retrieves the cached pool difficulty information from the summary data.

        Returns:
            int: Pool difficulty information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["diff"])
        return self._get_data_from_response(self._summary_response, ["connection", "diff"])

    @property
    def sum_pool_accepted_jobs(self) -> Union[int, bool]:
        """
        Retrieves the cached number of accepted jobs from the summary data.

        Returns:
            int: Number of accepted jobs, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["accepted"])
        return self._get_data_from_response(self._summary_response, ["connection", "accepted"])

    @property
    def sum_pool_rejected_jobs(self) -> Union[int, bool]:
        """
        Retrieves the cached number of rejected jobs from the summary data.

        Returns:
            int: Number of rejected jobs, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["rejected"])
        return self._get_data_from_response(self._summary_response,  ["connection", "rejected"])

    @property
    def sum_pool_average_time(self) -> Union[int, bool]:
        """
        Retrieves the cached pool average time information from the summary data.

        Returns:
            int: Pool average time information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["avg_time"])
        return self._get_data_from_response(self._summary_response, ["connection", "avg_time"])

    @property
    def sum_pool_average_time_ms(self) -> Union[int, bool]:
        """
        Retrieves the cached pool average time in ms from the summary data.

        Returns:
            int: Pool average time in ms, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["avg_time_ms"])
        return self._get_data_from_response(self._summary_response, ["connection", "avg_time_ms"])

    @property
    def sum_pool_total_hashes(self) -> Union[int, bool]:
        """
        Retrieves the cached pool total hashes information from the summary data.

        Returns:
            int: Pool total hashes information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["connection"]["hashes_total"])
        return self._get_data_from_response(self._summary_response, ["connection", "hashes_total"])

    @property
    def sum_version(self) -> Union[str, bool]:
        """
        Retrieves the cached version information from the summary data.

        Returns:
            str: Version information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["version"])
        return self._get_data_from_response(self._summary_response, ["version"])

    @property
    def sum_kind(self) -> Union[str, bool]:
        """
        Retrieves the cached kind information from the summary data.

        Returns:
            str: Kind information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["kind"])
        return self._get_data_from_response(self._summary_response, ["kind"])

    @property
    def sum_ua(self) -> Union[str, bool]:
        """
        Retrieves the cached user agent information from the summary data.

        Returns:
            str: User agent information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["ua"])
        return self._get_data_from_response(self._summary_response, ["ua"])

    @property
    def sum_cpu_info(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached CPU information from the summary data.

        Returns:
            dict: CPU information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"])
        return self._get_data_from_response(self._summary_response, ["cpu"])

    @property
    def sum_cpu_brand(self) -> Union[str, bool]:
        """
        Retrieves the cached CPU brand information from the summary data.

        Returns:
            str: CPU brand information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["brand"])
        return self._get_data_from_response(self._summary_response, ["cpu", "brand"])

    @property
    def sum_cpu_family(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU family information from the summary data.

        Returns:
            int: CPU family information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["family"])
        return self._get_data_from_response(self._summary_response, ["cpu", "family"])

    @property
    def sum_cpu_model(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU model information from the summary data.

        Returns:
            int: CPU model information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["model"])
        return self._get_data_from_response(self._summary_response, ["cpu", "model"])

    @property
    def sum_cpu_stepping(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU stepping information from the summary data.

        Returns:
            int: CPU stepping information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["stepping"])
        return self._get_data_from_response(self._summary_response,  ["cpu", "stepping"])

    @property
    def sum_cpu_proc_info(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU frequency information from the summary data.

        Returns:
            int: CPU frequency information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["proc_info"])
        return self._get_data_from_response(self._summary_response, ["cpu", "proc_info"])

    @property
    def sum_cpu_aes(self) -> Optional[bool]:
        """
        Retrieves the cached CPU AES support status from the summary data.

        Returns:
            bool: CPU AES support status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["aes"])
        return self._get_data_from_response(self._summary_response, ["cpu", "aes"])

    @property
    def sum_cpu_avx2(self) -> Optional[bool]:
        """
        Retrieves the cached CPU AVX2 support status from the summary data.

        Returns:
            bool: CPU AVX2 support status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["avx2"])
        return self._get_data_from_response(self._summary_response, ["cpu", "avx2"])

    @property
    def sum_cpu_x64(self) -> Optional[bool]:
        """
        Retrieves the cached CPU x64 support status from the summary data.

        Returns:
            bool: CPU x64 support status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["x64"])
        return self._get_data_from_response(self._summary_response, ["cpu", "x64"])

    @property
    def sum_cpu_64_bit(self) -> Optional[bool]:
        """
        Retrieves the cached CPU 64-bit support status from the summary data.

        Returns:
            bool: CPU 64-bit support status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["64_bit"])
        return self._get_data_from_response(self._summary_response, ["cpu", "64_bit"])

    @property
    def sum_cpu_l2(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU L2 cache size from the summary data.

        Returns:
            int: CPU L2 cache size, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["l2"])
        return self._get_data_from_response(self._summary_response, ["cpu", "l2"])

    @property
    def sum_cpu_l3(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU L3 cache size from the summary data.

        Returns:
            int: CPU L3 cache size, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["l3"])
        return self._get_data_from_response(self._summary_response, ["cpu", "l3"])

    @property
    def sum_cpu_cores(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU cores count from the summary data.

        Returns:
            int: CPU cores count, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["cores"])
        return self._get_data_from_response(self._summary_response, ["cpu", "cores"])

    @property
    def sum_cpu_threads(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU threads count from the summary data.

        Returns:
            int: CPU threads count, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["threads"])
        return self._get_data_from_response(self._summary_response, ["cpu", "threads"])

    @property
    def sum_cpu_packages(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU packages count from the summary data.

        Returns:
            int: CPU packages count, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["packages"])
        return self._get_data_from_response(self._summary_response, ["cpu", "packages"])

    @property
    def sum_cpu_nodes(self) -> Union[int, bool]:
        """
        Retrieves the cached CPU nodes count from the summary data.

        Returns:
            int: CPU nodes count, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["nodes"])
        return self._get_data_from_response(self._summary_response, ["cpu", "nodes"])

    @property
    def sum_cpu_backend(self) -> Union[str, bool]:
        """
        Retrieves the cached CPU backend information from the summary data.

        Returns:
            str: CPU backend information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["backend"])
        return self._get_data_from_response(self._summary_response,  ["cpu", "backend"])

    @property
    def sum_cpu_msr(self) -> Union[str, bool]:
        """
        Retrieves the cached CPU MSR information from the summary data.

        Returns:
            str: CPU MSR information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["msr"])
        return self._get_data_from_response(self._summary_response, ["cpu", "msr"])

    @property
    def sum_cpu_assembly(self) -> Union[str, bool]:
        """
        Retrieves the cached CPU assembly information from the summary data.

        Returns:
            str: CPU assembly information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["assembly"])
        return self._get_data_from_response(self._summary_response,  ["cpu", "assembly"])

    @property
    def sum_cpu_arch(self) -> Union[str, bool]:
        """
        Retrieves the cached CPU architecture information from the summary data.

        Returns:
            str: CPU architecture information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["arch"])
        return self._get_data_from_response(self._summary_response, ["cpu", "arch"])

    @property
    def sum_cpu_flags(self) -> Union[List[str], bool]:
        """
        Retrieves the cached CPU flags information from the summary data.

        Returns:
            list: CPU flags information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["cpu"]["flags"])
        return self._get_data_from_response(self._summary_response, ["cpu", "flags"])

    @property
    def sum_donate_level(self) -> Union[int, bool]:
        """
        Retrieves the cached donate level information from the summary data.

        Returns:
            int: Donate level information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["donate_level"])
        return self._get_data_from_response(self._summary_response, ["donate_level"])

    @property
    def sum_paused(self) -> Optional[bool]:
        """
        Retrieves the cached paused status from the summary data.

        Returns:
            bool: Paused status, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["paused"])
        return self._get_data_from_response(self._summary_response, ["paused"])

    @property
    def sum_algorithms(self) -> Union[List[str], bool]:
        """
        Retrieves the cached algorithms information from the summary data.

        Returns:
            list: Algorithms information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["algorithms"])
        return self._get_data_from_response(self._summary_response, ["algorithms"])

    @property
    def sum_hashrates(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the cached hashrate information from the summary data.

        Returns:
            dict: Hashrate information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hashrate"])
        return self._get_data_from_response(self._summary_response, ["hashrate"])

    @property
    def sum_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the cached hashrate for the last 10 seconds from the summary data.

        Returns:
            float: Hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hashrate"]["total"][0])
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 0])

    @property
    def sum_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the cached hashrate for the last 1 minute from the summary data.

        Returns:
            float: Hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hashrate"]["total"][1])
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 1])

    @property
    def sum_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the cached hashrate for the last 15 minutes from the summary data.

        Returns:
            float: Hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hashrate"]["total"][2])
        return self._get_data_from_response(self._summary_response, ["hashrate", "total", 2])

    @property
    def sum_hashrate_highest(self) -> Union[float, bool]:
        """
        Retrieves the cached highest hashrate from the summary data.

        Returns:
            float: Highest hashrate, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hashrate"]["highest"])
        return self._get_data_from_response(self._summary_response, ["hashrate", "highest"])

    @property
    def sum_hugepages(self) -> Union[List[Dict[str, Any]], bool]:
        """
        Retrieves the cached hugepages information from the summary data.

        Returns:
            list: Hugepages information, or "N/A" if not available.
        """
        if self._summary_response is not None:
            log.debug(self._summary_response["hugepages"])
        return self._get_data_from_response(self._summary_response, ["hugepages"])

    @property
    def enabled_backends(self) -> Union[List[str], bool]:
        """
        Retrieves the enabled backends from the backends data.

        Returns:
            list: Enabled backends, or "N/A" if not available.
        """
        backend_types = []
        for i in self._get_data_from_response(self._backends_response, []):
            if "type" in i and i["enabled"] == True:
                backend_types.append(i["type"])
        if self._backends_response is not None:
            log.debug(backend_types)
        return backend_types

    @property
    def be_cpu_type(self) -> Union[str, bool]:
        """
        Retrieves the CPU backend type from the backends data.

        Returns:
            str: CPU backend type, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["type"])
        return self._get_data_from_response(self._backends_response, [0, "type"])

    @property
    def be_cpu_enabled(self) -> Optional[bool]:
        """
        Retrieves the CPU backend enabled status from the backends data.

        Returns:
            bool: CPU backend enabled status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["enabled"])
        return self._get_data_from_response(self._backends_response, [0, "enabled"])

    @property
    def be_cpu_algo(self) -> Union[str, bool]:
        """
        Retrieves the CPU backend algorithm from the backends data.

        Returns:
            str: CPU backend algorithm, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["algo"])
        return self._get_data_from_response(self._backends_response, [0, "algo"])

    @property
    def be_cpu_profile(self) -> Union[str, bool]:
        """
        Retrieves the CPU backend profile from the backends data.

        Returns:
            str: CPU backend profile, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["profile"])
        return self._get_data_from_response(self._backends_response, [0, "profile"])

    @property
    def be_cpu_hw_aes(self) -> Optional[bool]:
        """
        Retrieves the CPU backend hardware AES support status from the backends data.

        Returns:
            bool: CPU backend hardware AES support status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hw-aes"])
        return self._get_data_from_response(self._backends_response, [0, "hw-aes"])

    @property
    def be_cpu_priority(self) -> Union[int, bool]:
        """
        Retrieves the CPU backend priority from the backends data.

        Returns:
            int: CPU backend priority, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["priority"])
        return self._get_data_from_response(self._backends_response, [0, "priority"])

    @property
    def be_cpu_msr(self) -> Optional[bool]:
        """
        Retrieves the CPU backend MSR support status from the backends data.

        Returns:
            bool: CPU backend MSR support status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["msr"])
        return self._get_data_from_response(self._backends_response, [0, "msr"])

    @property
    def be_cpu_asm(self) -> Union[str, bool]:
        """
        Retrieves the CPU backend assembly information from the backends data.

        Returns:
            str: CPU backend assembly information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["asm"])
        return self._get_data_from_response(self._backends_response, [0, "asm"])

    @property
    def be_cpu_argon2_impl(self) -> Union[str, bool]:
        """
        Retrieves the CPU backend Argon2 implementation from the backends data.

        Returns:
            str: CPU backend Argon2 implementation, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["argon2-impl"])
        return self._get_data_from_response(self._backends_response, [0, "argon2-impl"])

    @property
    def be_cpu_hugepages(self) -> Union[List[Dict[str, Any]], bool]:
        """
        Retrieves the CPU backend hugepages information from the backends data.

        Returns:
            list: CPU backend hugepages information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hugepages"])
        return self._get_data_from_response(self._backends_response, [0, "hugepages"])

    @property
    def be_cpu_memory(self) -> Union[int, bool]:
        """
        Retrieves the CPU backend memory information from the backends data.

        Returns:
            int: CPU backend memory information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["memory"])
        return self._get_data_from_response(self._backends_response, [0, "memory"])

    @property
    def be_cpu_hashrates(self) -> Union[List[float], bool]:
        """
        Retrieves the CPU backend hashrates from the backends data.

        Returns:
            list: CPU backend hashrates, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hashrate"])
        return self._get_data_from_response(self._backends_response, [0, "hashrate"])

    @property
    def be_cpu_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the CPU backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: CPU backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hashrate"][0])
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 0])

    @property
    def be_cpu_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the CPU backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: CPU backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hashrate"][1])
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 1])

    @property
    def be_cpu_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the CPU backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: CPU backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["hashrate"][2])
        return self._get_data_from_response(self._backends_response, [0, "hashrate", 2])

    @property
    def be_cpu_threads(self) -> Union[List[Dict[str, Any]], bool]:
        """
        Retrieves the CPU backend threads information from the backends data.

        Returns:
            list: CPU backend threads information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[0]["threads"])
        return self._get_data_from_response(self._backends_response, [0, "threads"])

    @property
    def be_cpu_threads_intensity(self) -> Union[List[int], bool]:
        """
        Retrieves the CPU backend threads intensity information from the backends data.

        Returns:
            list: CPU backend threads intensity information, or "N/A" if not available.
        """
        intensities = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                intensities.append(i["intensity"])
        log.debug(intensities)
        return intensities

    @property
    def be_cpu_threads_affinity(self) -> Union[List[int], bool]:
        """
        Retrieves the CPU backend threads affinity information from the backends data.

        Returns:
            list: CPU backend threads affinity information, or "N/A" if not available.
        """
        affinities = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                affinities.append(i["affinity"])
        log.debug(affinities)
        return affinities

    @property
    def be_cpu_threads_av(self) -> Union[List[int], bool]:
        """
        Retrieves the CPU backend threads AV information from the backends data.

        Returns:
            list: CPU backend threads AV information, or "N/A" if not available.
        """
        avs = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                avs.append(i["av"])
        log.debug(avs)
        return avs

    @property
    def be_cpu_threads_hashrates_10s(self) -> Union[List[float], bool]:
        """
        Retrieves the CPU backend threads hashrates for the last 10 seconds from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 10 seconds, or "N/A" if not available.
        """
        hashrates_10s = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                hashrates_10s.append(i["hashrate"][0])
        log.debug(hashrates_10s)
        return hashrates_10s

    @property
    def be_cpu_threads_hashrates_1m(self) -> Union[List[float], bool]:
        """
        Retrieves the CPU backend threads hashrates for the last 1 minute from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 1 minute, or "N/A" if not available.
        """
        hashrates_1m = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                hashrates_1m.append(i["hashrate"][1])
        log.debug(hashrates_1m)
        return hashrates_1m

    @property
    def be_cpu_threads_hashrates_15m(self) -> Union[List[float], bool]:
        """
        Retrieves the CPU backend threads hashrates for the last 15 minutes from the backends data.

        Returns:
            list: CPU backend threads hashrates for the last 15 minutes, or "N/A" if not available.
        """
        hashrates_15m = []
        if self._backends_response is not None:
            for i in self._get_data_from_response(self._backends_response, [0, "threads"]):
                hashrates_15m.append(i["hashrate"][2])
        log.debug(hashrates_15m)
        return hashrates_15m

    @property
    def be_opencl_type(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend type from the backends data.

        Returns:
            str: OpenCL backend type, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["type"])
        return self._get_data_from_response(self._backends_response, [1, "type"])

    @property
    def be_opencl_enabled(self) -> Optional[bool]:
        """
        Retrieves the OpenCL backend enabled status from the backends data.

        Returns:
            bool: OpenCL backend enabled status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["enabled"])
        return self._get_data_from_response(self._backends_response, [1, "enabled"])

    @property
    def be_opencl_algo(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend algorithm from the backends data.

        Returns:
            str: OpenCL backend algorithm, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["algo"])
        return self._get_data_from_response(self._backends_response, [1, "algo"])

    @property
    def be_opencl_profile(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend profile from the backends data.

        Returns:
            str: OpenCL backend profile, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["profile"])
        return self._get_data_from_response(self._backends_response, [1, "profile"])

    @property
    def be_opencl_platform(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the OpenCL backend platform information from the backends data.

        Returns:
            dict: OpenCL backend platform information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"])
        return self._get_data_from_response(self._backends_response, [1, "platform"])

    @property
    def be_opencl_platform_index(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend platform index from the backends data.

        Returns:
            int: OpenCL backend platform index, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["index"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "index"])

    @property
    def be_opencl_platform_profile(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend platform profile from the backends data.

        Returns:
            str: OpenCL backend platform profile, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["profile"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "profile"])

    @property
    def be_opencl_platform_version(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend platform version from the backends data.

        Returns:
            str: OpenCL backend platform version, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["version"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "version"])

    @property
    def be_opencl_platform_name(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend platform name from the backends data.

        Returns:
            str: OpenCL backend platform name, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["name"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "name"])

    @property
    def be_opencl_platform_vendor(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend platform vendor from the backends data.

        Returns:
            str: OpenCL backend platform vendor, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["vendor"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "vendor"])

    @property
    def be_opencl_platform_extensions(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend platform extensions from the backends data.

        Returns:
            str: OpenCL backend platform extensions, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["platform"]["extensions"])
        return self._get_data_from_response(self._backends_response, [1, "platform", "extensions"])

    @property
    def be_opencl_hashrates(self) -> Union[List[float], bool]:
        """
        Retrieves the OpenCL backend hashrates from the backends data.

        Returns:
            list: OpenCL backend hashrates, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["hashrate"])
        return self._get_data_from_response(self._backends_response, [1, "hashrate"])

    @property
    def be_opencl_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["hashrate"][0])
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 0])

    @property
    def be_opencl_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["hashrate"][1])
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 1])

    @property
    def be_opencl_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: OpenCL backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["hashrate"][2])
        return self._get_data_from_response(self._backends_response, [1, "hashrate", 2])

    @property
    def be_opencl_threads(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the OpenCL backend threads information from the backends data.

        Returns:
            dict: OpenCL backend threads information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0])

    @property
    def be_opencl_threads_index(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads index from the backends data.

        Returns:
            int: OpenCL backend threads index, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["index"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "index"])

    @property
    def be_opencl_threads_intensity(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads intensity from the backends data.

        Returns:
            int: OpenCL backend threads intensity, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["intensity"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "intensity"])

    @property
    def be_opencl_threads_worksize(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads worksize from the backends data.

        Returns:
            int: OpenCL backend threads worksize, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["worksize"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "worksize"])

    @property
    def be_opencl_threads_amount(self) -> Union[List[int], bool]:
        """
        Retrieves the OpenCL backend threads amount from the backends data.

        Returns:
            list: OpenCL backend threads amount, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["threads"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "threads"])

    @property
    def be_opencl_threads_unroll(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads unroll from the backends data.

        Returns:
            int: OpenCL backend threads unroll, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["unroll"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "unroll"])

    @property
    def be_opencl_threads_affinity(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads affinity from the backends data.

        Returns:
            int: OpenCL backend threads affinity, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["affinity"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "affinity"])

    @property
    def be_opencl_threads_hashrates(self) -> Union[List[float], bool]:
        """
        Retrieves the OpenCL backend threads hashrates from the backends data.

        Returns:
            list: OpenCL backend threads hashrates, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["hashrate"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate"])

    @property
    def be_opencl_threads_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            float: OpenCL backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["hashrate"][0])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 0])

    @property
    def be_opencl_threads_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            float: OpenCL backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["hashrate"][1])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 1])

    @property
    def be_opencl_threads_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the OpenCL backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            float: OpenCL backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["hashrate"][2])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "hashrate", 2])

    @property
    def be_opencl_threads_board(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend threads board information from the backends data.

        Returns:
            str: OpenCL backend threads board information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["board"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "board"])

    @property
    def be_opencl_threads_name(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend threads name from the backends data.

        Returns:
            str: OpenCL backend threads name, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["name"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "name"])

    @property
    def be_opencl_threads_bus_id(self) -> Union[str, bool]:
        """
        Retrieves the OpenCL backend threads bus ID from the backends data.

        Returns:
            str: OpenCL backend threads bus ID, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["bus_id"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "bus_id"])

    @property
    def be_opencl_threads_cu(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads compute units from the backends data.

        Returns:
            int: OpenCL backend threads compute units, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["cu"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "cu"])

    @property
    def be_opencl_threads_global_mem(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads global memory from the backends data.

        Returns:
            int: OpenCL backend threads global memory, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["global_mem"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "global_mem"])

    @property
    def be_opencl_threads_health(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the OpenCL backend threads health information from the backends data.

        Returns:
            dict: OpenCL backend threads health information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health"])

    @property
    def be_opencl_threads_health_temp(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads health temperature from the backends data.

        Returns:
            int: OpenCL backend threads health temperature, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"]["temperature"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "temperature"])

    @property
    def be_opencl_threads_health_power(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads health power from the backends data.

        Returns:
            int: OpenCL backend threads health power, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"]["power"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "power"])

    @property
    def be_opencl_threads_health_clock(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads health clock from the backends data.

        Returns:
            int: OpenCL backend threads health clock, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"]["clock"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "clock"])

    @property
    def be_opencl_threads_health_mem_clock(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads health memory clock from the backends data.

        Returns:
            int: OpenCL backend threads health memory clock, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"]["mem_clock"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "mem_clock"])

    @property
    def be_opencl_threads_health_rpm(self) -> Union[int, bool]:
        """
        Retrieves the OpenCL backend threads health RPM from the backends data.

        Returns:
            int: OpenCL backend threads health RPM, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[1]["threads"][0]["health"]["rpm"])
        return self._get_data_from_response(self._backends_response, [1, "threads", 0, "health", "rpm"])

    @property
    def be_cuda_type(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend type from the backends data.

        Returns:
            str: CUDA backend type, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["type"])
        return self._get_data_from_response(self._backends_response, [2, "type"])

    @property
    def be_cuda_enabled(self) -> Optional[bool]:
        """
        Retrieves the CUDA backend enabled status from the backends data.

        Returns:
            bool: CUDA backend enabled status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["enabled"])
        return self._get_data_from_response(self._backends_response, [2, "enabled"])

    @property
    def be_cuda_algo(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend algorithm from the backends data.

        Returns:
            str: CUDA backend algorithm, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["algo"])
        return self._get_data_from_response(self._backends_response, [2, "algo"])

    @property
    def be_cuda_profile(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend profile from the backends data.

        Returns:
            str: CUDA backend profile, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["profile"])
        return self._get_data_from_response(self._backends_response, [2, "profile"])

    @property
    def be_cuda_versions(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the CUDA backend versions information from the backends data.

        Returns:
            dict: CUDA backend versions information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["versions"])
        return self._get_data_from_response(self._backends_response, [2, "versions"])

    @property
    def be_cuda_runtime(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend runtime version from the backends data.

        Returns:
            str: CUDA backend runtime version, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["versions"]["cuda-runtime"])
        return self._get_data_from_response(self._backends_response, [2, "versions", "cuda-runtime"])

    @property
    def be_cuda_driver(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend driver version from the backends data.

        Returns:
            str: CUDA backend driver version, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["versions"]["cuda-driver"])
        return self._get_data_from_response(self._backends_response, [2, "versions", "cuda-driver"])

    @property
    def be_cuda_plugin(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend plugin version from the backends data.

        Returns:
            str: CUDA backend plugin version, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["versions"]["plugin"])
        return self._get_data_from_response(self._backends_response, [2, "versions", "plugin"])

    @property
    def be_cuda_hashrates(self) -> Union[List[float], bool]:
        """
        Retrieves the CUDA backend hashrates from the backends data.

        Returns:
            list: CUDA backend hashrates, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["hashrate"])
        return self._get_data_from_response(self._backends_response, [2, "hashrate"])

    @property
    def be_cuda_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend hashrate for the last 10 seconds from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["hashrate"][0])
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 0])

    @property
    def be_cuda_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend hashrate for the last 1 minute from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["hashrate"][1])
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 1])

    @property
    def be_cuda_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend hashrate for the last 15 minutes from the backends data.

        Returns:
            float: CUDA backend hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["hashrate"][2])
        return self._get_data_from_response(self._backends_response, [2, "hashrate", 2])

    @property
    def be_cuda_threads(self) -> Union[Dict[str, Any], bool]:
        """
        Retrieves the CUDA backend threads information from the backends data.

        Returns:
            dict: CUDA backend threads information, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0])

    @property
    def be_cuda_threads_index(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads index from the backends data.

        Returns:
            int: CUDA backend threads index, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["index"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "index"])

    @property
    def be_cuda_threads_amount(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads amount from the backends data.

        Returns:
            int: CUDA backend threads amount, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["threads"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "threads"])

    @property
    def be_cuda_threads_blocks(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads blocks from the backends data.

        Returns:
            int: CUDA backend threads blocks, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["blocks"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "blocks"])

    @property
    def be_cuda_threads_bfactor(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads bfactor from the backends data.

        Returns:
            int: CUDA backend threads bfactor, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["bfactor"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bfactor"])

    @property
    def be_cuda_threads_bsleep(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads bsleep from the backends data.

        Returns:
            int: CUDA backend threads bsleep, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["bsleep"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bsleep"])

    @property
    def be_cuda_threads_affinity(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads affinity from the backends data.

        Returns:
            int: CUDA backend threads affinity, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["affinity"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "affinity"])

    @property
    def be_cuda_threads_dataset_host(self) -> Optional[bool]:
        """
        Retrieves the CUDA backend threads dataset host status from the backends data.

        Returns:
            bool: CUDA backend threads dataset host status, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["dataset_host"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "dataset_host"])

    @property
    def be_cuda_threads_hashrates(self) -> Union[List[float], bool]:
        """
        Retrieves the CUDA backend threads hashrates from the backends data.

        Returns:
            list: CUDA backend threads hashrates, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["hashrate"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate"])

    @property
    def be_cuda_threads_hashrate_10s(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend threads hashrate for the last 10 seconds from the backends data.

        Returns:
            float: CUDA backend threads hashrate for the last 10 seconds, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["hashrate"][0])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 0])

    @property
    def be_cuda_threads_hashrate_1m(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend threads hashrate for the last 1 minute from the backends data.

        Returns:
            float: CUDA backend threads hashrate for the last 1 minute, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["hashrate"][1])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 1])

    @property
    def be_cuda_threads_hashrate_15m(self) -> Union[float, bool]:
        """
        Retrieves the CUDA backend threads hashrate for the last 15 minutes from the backends data.

        Returns:
            float: CUDA backend threads hashrate for the last 15 minutes, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["hashrate"][2])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "hashrate", 2])

    @property
    def be_cuda_threads_name(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend threads name from the backends data.

        Returns:
            str: CUDA backend threads name, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["name"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "name"])

    @property
    def be_cuda_threads_bus_id(self) -> Union[str, bool]:
        """
        Retrieves the CUDA backend threads bus ID from the backends data.

        Returns:
            str: CUDA backend threads bus ID, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["bus_id"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "bus_id"])

    @property
    def be_cuda_threads_smx(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads SMX count from the backends data.

        Returns:
            int: CUDA backend threads SMX count, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["smx"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "smx"])

    @property
    def be_cuda_threads_arch(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads architecture from the backends data.

        Returns:
            int: CUDA backend threads architecture, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["arch"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "arch"])

    @property
    def be_cuda_threads_global_mem(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads global memory from the backends data.

        Returns:
            int: CUDA backend threads global memory, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["global_mem"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "global_mem"])

    @property
    def be_cuda_threads_clock(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads clock from the backends data.

        Returns:
            int: CUDA backend threads clock, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["clock"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "clock"])

    @property
    def be_cuda_threads_memory_clock(self) -> Union[int, bool]:
        """
        Retrieves the CUDA backend threads memory clock from the backends data.

        Returns:
            int: CUDA backend threads memory clock, or "N/A" if not available.
        """
        if self._backends_response is not None:
            log.debug(self._backends_response[2]["threads"][0]["memory_clock"])
        return self._get_data_from_response(self._backends_response, [2, "threads", 0, "memory_clock"])

