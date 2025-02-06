"""
XMRig module initializer

This module provides objects to interact with the XMRig miner API, manage multiple miners, 
and store collected data in a database. It includes functionalities for:

- Fetching status and managing configurations.
- Controlling the mining process.
- Performing actions on all miners.
- Retrieving and caching properties and statistics from the API responses.
- Fallback to the database if the data is not available in the cached responses.
- Deleting all miner-related data from the database.

Classes:

- XMRigAPI: Interacts with the XMRig miner API.
- XMRigAPIError: Custom exception for general API errors.
- XMRigAuthorizationError: Custom exception for authorization errors.
- XMRigConnectionError: Custom exception for connection errors.
- XMRigManager: Manages multiple XMRig miners via their APIs.
- XMRigProperties: Retrieves and caches properties and statistics from the XMRig miner's API responses.
- XMRigDatabase: Handles database operations for storing and managing miner data.

Modules:

- api: Contains the XMRigAPI class and related functionalities.
- manager: Contains the XMRigManager class for managing multiple miners.
- exceptions: Handles custom exceptions.
- properties: Contains the XMRigProperties class for retrieving and caching properties.
- db: Contains the XMRigDatabase class for database operations.

Public Functions:

XMRigAPI:

- set_auth_header: Sets the authorization header for API requests.
- get_endpoint: Fetches data from a specified API endpoint.
- post_config: Posts configuration data to the API.
- get_all_responses: Retrieves all responses from the API.
- perform_action: Executes a specified action on the miner.

XMRigManager:

- add_miner: Adds a new miner to the manager.
- remove_miner: Removes a miner from the manager.
- get_miner: Retrieves a miner by its identifier.
- edit_miner: Edits the configuration of an existing miner.
- perform_action_on_all: Executes a specified action on all managed miners.
- update_miners: Updates the status of all managed miners.
- list_miners: Lists all managed miners.

XMRigDatabase:

- init_db: Initializes the database.
- get_db: Retrieves the database connection.
- check_table_exists: Checks if a specified table exists in the database.
- insert_data_to_db: Inserts data into the database.
- fallback_to_db: Retrieves data from the database if not available in the cache.
- delete_all_miner_data_from_db: Deletes all miner-related data from the database.

XMRigProperties:

- summary: Retrieves a summary of the miner's status.
- backends: Retrieves information about the miner's backends.
- config: Retrieves the miner's configuration.
- sum_id: Retrieves the miner's ID.
- sum_worker_id: Retrieves the worker ID.
- sum_uptime: Retrieves the miner's uptime.
- sum_uptime_readable: Retrieves the miner's uptime in a human-readable format.
- sum_restricted: Retrieves the miner's restricted status.
- sum_resources: Retrieves the miner's resource usage.
- sum_memory_usage: Retrieves the miner's memory usage.
- sum_free_memory: Retrieves the miner's free memory.
- sum_total_memory: Retrieves the miner's total memory.
- sum_resident_set_memory: Retrieves the miner's resident set memory.
- sum_load_average: Retrieves the miner's load average.
- sum_hardware_concurrency: Retrieves the miner's hardware concurrency.
- sum_features: Retrieves the miner's features.
- sum_results: Retrieves the miner's results.
- sum_current_difficulty: Retrieves the miner's current difficulty.
- sum_good_shares: Retrieves the number of good shares.
- sum_total_shares: Retrieves the total number of shares.
- sum_avg_time: Retrieves the average time per share.
- sum_avg_time_ms: Retrieves the average time per share in milliseconds.
- sum_total_hashes: Retrieves the total number of hashes.
- sum_best_results: Retrieves the best results.
- sum_algorithm: Retrieves the algorithm used by the miner.
- sum_connection: Retrieves the miner's connection status.
- sum_pool_info: Retrieves information about the pool.
- sum_pool_ip_address: Retrieves the pool's IP address.
- sum_pool_uptime: Retrieves the pool's uptime.
- sum_pool_uptime_ms: Retrieves the pool's uptime in milliseconds.
- sum_pool_ping: Retrieves the pool's ping.
- sum_pool_failures: Retrieves the number of pool failures.
- sum_pool_tls: Retrieves the pool's TLS status.
- sum_pool_tls_fingerprint: Retrieves the pool's TLS fingerprint.
- sum_pool_algo: Retrieves the pool's algorithm.
- sum_pool_diff: Retrieves the pool's difficulty.
- sum_pool_accepted_jobs: Retrieves the number of accepted jobs by the pool.
- sum_pool_rejected_jobs: Retrieves the number of rejected jobs by the pool.
- sum_pool_average_time: Retrieves the pool's average time per job.
- sum_pool_average_time_ms: Retrieves the pool's average time per job in milliseconds.
- sum_pool_total_hashes: Retrieves the total number of hashes by the pool.
- sum_version: Retrieves the miner's version.
- sum_kind: Retrieves the miner's kind.
- sum_ua: Retrieves the miner's user agent.
- sum_cpu_info: Retrieves information about the CPU.
- sum_cpu_brand: Retrieves the CPU brand.
- sum_cpu_family: Retrieves the CPU family.
- sum_cpu_model: Retrieves the CPU model.
- sum_cpu_stepping: Retrieves the CPU stepping.
- sum_cpu_proc_info: Retrieves the CPU processor information.
- sum_cpu_aes: Retrieves the CPU AES status.
- sum_cpu_avx2: Retrieves the CPU AVX2 status.
- sum_cpu_x64: Retrieves the CPU x64 status.
- sum_cpu_64_bit: Retrieves the CPU 64-bit status.
- sum_cpu_l2: Retrieves the CPU L2 cache size.
- sum_cpu_l3: Retrieves the CPU L3 cache size.
- sum_cpu_cores: Retrieves the number of CPU cores.
- sum_cpu_threads: Retrieves the number of CPU threads.
- sum_cpu_packages: Retrieves the number of CPU packages.
- sum_cpu_nodes: Retrieves the number of CPU nodes.
- sum_cpu_backend: Retrieves the CPU backend.
- sum_cpu_msr: Retrieves the CPU MSR status.
- sum_cpu_assembly: Retrieves the CPU assembly status.
- sum_cpu_arch: Retrieves the CPU architecture.
- sum_cpu_flags: Retrieves the CPU flags.
- sum_donate_level: Retrieves the miner's donation level.
- sum_paused: Retrieves the miner's paused status.
- sum_algorithms: Retrieves the algorithms used by the miner.
- sum_hashrate: Retrieves the miner's hashrates.
- sum_hashrate_10s: Retrieves the miner's hashrate over the last 10 seconds.
- sum_hashrate_1m: Retrieves the miner's hashrate over the last 1 minute.
- sum_hashrate_15m: Retrieves the miner's hashrate over the last 15 minutes.
- sum_hashrate_highest: Retrieves the miner's highest hashrate.
- sum_hugepages: Retrieves the miner's hugepages status.
- enabled_backends: Retrieves the enabled backends.
- be_cpu_type: Retrieves the CPU backend type.
- be_cpu_enabled: Retrieves the CPU backend enabled status.
- be_cpu_algo: Retrieves the CPU backend algorithm.
- be_cpu_profile: Retrieves the CPU backend profile.
- be_cpu_hw_aes: Retrieves the CPU backend hardware AES status.
- be_cpu_priority: Retrieves the CPU backend priority.
- be_cpu_msr: Retrieves the CPU backend MSR status.
- be_cpu_asm: Retrieves the CPU backend assembly status.
- be_cpu_argon2_impl: Retrieves the CPU backend Argon2 implementation.
- be_cpu_hugepages: Retrieves the CPU backend hugepages status.
- be_cpu_memory: Retrieves the CPU backend memory usage.
- be_cpu_hashrates: Retrieves the CPU backend hashrates.
- be_cpu_hashrate_10s: Retrieves the CPU backend hashrate over the last 10 seconds.
- be_cpu_hashrate_1m: Retrieves the CPU backend hashrate over the last 1 minute.
- be_cpu_hashrate_15m: Retrieves the CPU backend hashrate over the last 15 minutes.
- be_cpu_threads: Retrieves the CPU backend threads.
- be_cpu_threads_intensity: Retrieves the CPU backend threads intensity.
- be_cpu_threads_affinity: Retrieves the CPU backend threads affinity.
- be_cpu_threads_av: Retrieves the CPU backend threads AV status.
- be_cpu_threads_hashrates_10s: Retrieves the CPU backend threads hashrate over the last 10 seconds.
- be_cpu_threads_hashrates_1m: Retrieves the CPU backend threads hashrate over the last 1 minute.
- be_cpu_threads_hashrates_15m: Retrieves the CPU backend threads hashrate over the last 15 minutes.
- be_opencl_type: Retrieves the OpenCL backend type.
- be_opencl_enabled: Retrieves the OpenCL backend enabled status.
- be_opencl_algo: Retrieves the OpenCL backend algorithm.
- be_opencl_profile: Retrieves the OpenCL backend profile.
- be_opencl_platform: Retrieves the OpenCL backend platform.
- be_opencl_platform_index: Retrieves the OpenCL backend platform index.
- be_opencl_platform_profile: Retrieves the OpenCL backend platform profile.
- be_opencl_platform_version: Retrieves the OpenCL backend platform version.
- be_opencl_platform_name: Retrieves the OpenCL backend platform name.
- be_opencl_platform_vendor: Retrieves the OpenCL backend platform vendor.
- be_opencl_platform_extensions: Retrieves the OpenCL backend platform extensions.
- be_opencl_hashrates: Retrieves the OpenCL backend hashrates.
- be_opencl_hashrate_10s: Retrieves the OpenCL backend hashrate over the last 10 seconds.
- be_opencl_hashrate_1m: Retrieves the OpenCL backend hashrate over the last 1 minute.
- be_opencl_hashrate_15m: Retrieves the OpenCL backend hashrate over the last 15 minutes.
- be_opencl_threads: Retrieves the OpenCL backend threads.
- be_opencl_threads_index: Retrieves the OpenCL backend threads index.
- be_opencl_threads_intensity: Retrieves the OpenCL backend threads intensity.
- be_opencl_threads_worksize: Retrieves the OpenCL backend threads worksize.
- be_opencl_threads_amount: Retrieves the OpenCL backend threads amount.
- be_opencl_threads_unroll: Retrieves the OpenCL backend threads unroll status.
- be_opencl_threads_affinity: Retrieves the OpenCL backend threads affinity.
- be_opencl_threads_hashrates: Retrieves the OpenCL backend threads hashrates.
- be_opencl_threads_hashrate_10s: Retrieves the OpenCL backend threads hashrate over the last 10 seconds.
- be_opencl_threads_hashrate_1m: Retrieves the OpenCL backend threads hashrate over the last 1 minute.
- be_opencl_threads_hashrate_15m: Retrieves the OpenCL backend threads hashrate over the last 15 minutes.
- be_opencl_threads_board: Retrieves the OpenCL backend threads board.
- be_opencl_threads_name: Retrieves the OpenCL backend threads name.
- be_opencl_threads_bus_id: Retrieves the OpenCL backend threads bus ID.
- be_opencl_threads_cu: Retrieves the OpenCL backend threads compute units.
- be_opencl_threads_global_mem: Retrieves the OpenCL backend threads global memory.
- be_opencl_threads_health: Retrieves the OpenCL backend threads health status.
- be_opencl_threads_health_temp: Retrieves the OpenCL backend threads health temperature.
- be_opencl_threads_health_power: Retrieves the OpenCL backend threads health power usage.
- be_opencl_threads_health_clock: Retrieves the OpenCL backend threads health clock speed.
- be_opencl_threads_health_mem_clock: Retrieves the OpenCL backend threads health memory clock speed.
- be_opencl_threads_health_rpm: Retrieves the OpenCL backend threads health RPM.
- be_cuda_type: Retrieves the CUDA backend type.
- be_cuda_enabled: Retrieves the CUDA backend enabled status.
- be_cuda_algo: Retrieves the CUDA backend algorithm.
- be_cuda_profile: Retrieves the CUDA backend profile.
- be_cuda_versions: Retrieves the CUDA backend versions.
- be_cuda_runtime: Retrieves the CUDA backend runtime version.
- be_cuda_driver: Retrieves the CUDA backend driver version.
- be_cuda_plugin: Retrieves the CUDA backend plugin status.
- be_cuda_hashrates: Retrieves the CUDA backend hashrates.
- be_cuda_hashrate_10s: Retrieves the CUDA backend hashrate over the last 10 seconds.
- be_cuda_hashrate_1m: Retrieves the CUDA backend hashrate over the last 1 minute.
- be_cuda_hashrate_15m: Retrieves the CUDA backend hashrate over the last 15 minutes.
- be_cuda_threads: Retrieves the CUDA backend threads.
- be_cuda_threads_index: Retrieves the CUDA backend threads index.
- be_cuda_threads_amount: Retrieves the CUDA backend threads amount.
- be_cuda_threads_blocks: Retrieves the CUDA backend threads blocks.
- be_cuda_threads_bfactor: Retrieves the CUDA backend threads bfactor.
- be_cuda_threads_bsleep: Retrieves the CUDA backend threads bsleep.
- be_cuda_threads_affinity: Retrieves the CUDA backend threads affinity.
- be_cuda_threads_dataset_host: Retrieves the CUDA backend threads dataset host.
- be_cuda_threads_hashrates: Retrieves the CUDA backend threads hashrates.
- be_cuda_threads_hashrate_10s: Retrieves the CUDA backend threads hashrate over the last 10 seconds.
- be_cuda_threads_hashrate_1m: Retrieves the CUDA backend threads hashrate over the last 1 minute.
- be_cuda_threads_hashrate_15m: Retrieves the CUDA backend threads hashrate over the last 15 minutes.
- be_cuda_threads_name: Retrieves the CUDA backend threads name.
- be_cuda_threads_bus_id: Retrieves the CUDA backend threads bus ID.
- be_cuda_threads_smx: Retrieves the CUDA backend threads SMX.
- be_cuda_threads_arch: Retrieves the CUDA backend threads architecture.
- be_cuda_threads_global_mem: Retrieves the CUDA backend threads global memory.
- be_cuda_threads_clock: Retrieves the CUDA backend threads clock speed.
- be_cuda_threads_memory_clock: Retrieves the CUDA backend threads memory clock speed.
- conf_api_property: Retrieves the API configuration.
- conf_api_id_property: Retrieves the API ID.
- conf_api_worker_id_property: Retrieves the API worker ID.
- conf_http_property: Retrieves the HTTP configuration.
- conf_http_enabled_property: Retrieves the HTTP enabled status.
- conf_http_host_property: Retrieves the HTTP host.
- conf_http_port_property: Retrieves the HTTP port.
- conf_http_access_token_property: Retrieves the HTTP access token.
- conf_http_restricted_property: Retrieves the HTTP restricted status.
- conf_autosave_property: Retrieves the autosave property.
- conf_background_property: Retrieves the background property.
- conf_colors_property: Retrieves the colors property.
- conf_title_property: Retrieves the title property.
- conf_randomx_property: Retrieves the RandomX configuration.
- conf_randomx_init_property: Retrieves the RandomX init property.
- conf_randomx_init_avx2_property: Retrieves the RandomX AVX2 property.
- conf_randomx_mode_property: Retrieves the RandomX mode property.
- conf_randomx_1gb_pages_property: Retrieves the RandomX 1GB pages property.
- conf_randomx_rdmsr_property: Retrieves the RandomX RDMSR property.
- conf_randomx_wrmsr_property: Retrieves the RandomX WRMSR property.
- conf_randomx_cache_qos_property: Retrieves the RandomX cache QoS property.
- conf_randomx_numa_property: Retrieves the RandomX NUMA property.
- conf_randomx_scratchpad_prefetch_mode_property: Retrieves the RandomX scratchpad prefetch mode property.
- conf_cpu_property: Retrieves the CPU configuration.
- conf_cpu_enabled_property: Retrieves the CPU enabled status.
- conf_cpu_huge_pages_property: Retrieves the CPU huge pages property.
- conf_cpu_huge_pages_jit_property: Retrieves the CPU huge pages JIT property.
- conf_cpu_hw_aes_property: Retrieves the CPU HW AES property.
- conf_cpu_priority_property: Retrieves the CPU priority property.
- conf_cpu_memory_pool_property: Retrieves the CPU memory pool property.
- conf_cpu_yield_property: Retrieves the CPU yield property.
- conf_cpu_max_threads_hint_property: Retrieves the CPU max threads hint property.
- conf_cpu_asm_property: Retrieves the CPU ASM property.
- conf_cpu_argon2_impl_property: Retrieves the CPU Argon2 implementation property.
- conf_opencl_property: Retrieves the OpenCL configuration.
- conf_opencl_enabled_property: Retrieves the OpenCL enabled status.
- conf_opencl_cache_property: Retrieves the OpenCL cache property.
- conf_opencl_loader_property: Retrieves the OpenCL loader property.
- conf_opencl_platform_property: Retrieves the OpenCL platform property.
- conf_opencl_adl_property: Retrieves the OpenCL ADL property.
- conf_cuda_property: Retrieves the CUDA configuration.
- conf_cuda_enabled_property: Retrieves the CUDA enabled status.
- conf_cuda_loader_property: Retrieves the CUDA loader property.
- conf_cuda_nvml_property: Retrieves the CUDA NVML property.
- conf_log_file_property: Retrieves the log file property.
- conf_donate_level_property: Retrieves the donation level property.
- conf_donate_over_proxy_property: Retrieves the donation over proxy property.
- conf_pools_property: Retrieves the pools configuration.
- conf_pools_algo_property: Retrieves the pools algorithm.
- conf_pools_coin_property: Retrieves the pools coin.
- conf_pools_url_property: Retrieves the pools URL.
- conf_pools_user_property: Retrieves the pools user.
- conf_pools_pass_property: Retrieves the pools pass.
- conf_pools_rig_id_property: Retrieves the pools rig ID.
- conf_pools_nicehash_property: Retrieves the pools NiceHash property.
- conf_pools_keepalive_property: Retrieves the pools keepalive property.
- conf_pools_enabled_property: Retrieves the pools enabled status.
- conf_pools_tls_property: Retrieves the pools TLS property.
- conf_pools_sni_property: Retrieves the pools SNI property.
- conf_pools_spend_secret_key_property: Retrieves the pools spend secret key property.
- conf_pools_tls_fingerprint_property: Retrieves the pools TLS fingerprint property.
- conf_pools_daemon_property: Retrieves the pools daemon configuration.
- conf_pools_daemon_poll_interval_property: Retrieves the pools daemon poll interval property.
- conf_pools_daemon_job_timeout_property: Retrieves the pools daemon job timeout property.
- conf_pools_daemon_zmq_port_property: Retrieves the pools daemon ZMQ port property.
- conf_pools_socks5_property: Retrieves the pools SOCKS5 property.
- conf_pools_self_select_property: Retrieves the pools self-select property.
- conf_pools_submit_to_origin_property: Retrieves the pools submit to origin property.
- conf_retries_property: Retrieves the retries property.
- conf_retry_pause_property: Retrieves the retry pause property.
- conf_print_time_property: Retrieves the print time property.
- conf_health_print_time_property: Retrieves the health print time property.
- conf_dmi_property: Retrieves the DMI property.
- conf_syslog_property: Retrieves the syslog property.
- conf_tls_property: Retrieves the TLS configuration.
- conf_tls_enabled_property: Retrieves the TLS enabled status.
- conf_tls_protocols_property: Retrieves the TLS protocols property.
- conf_tls_cert_property: Retrieves the TLS cert property.
- conf_tls_cert_key_property: Retrieves the TLS cert key property.
- conf_tls_ciphers_property: Retrieves the TLS ciphers property.
- conf_tls_ciphersuites_property: Retrieves the TLS ciphersuites property.
- conf_tls_dhparam_property: Retrieves the TLS DH param property.
- conf_dns_property: Retrieves the DNS configuration.
- conf_dns_ipv6_property: Retrieves the DNS IPv6 property.
- conf_dns_ttl_property: Retrieves the DNS TTL property.
- conf_user_agent_property: Retrieves the user agent property.
- conf_verbose_property: Retrieves the verbose property.
- conf_watch_property: Retrieves the watch property.
- conf_rebench_algo_property: Retrieves the Rebench Algo property.
- conf_bench_algo_time_property: Retrieves the Benchmark Algorithm Time property.
- conf_pause_on_battery_property: Retrieves the Pause On Battery property.
- conf_pause_on_active_property: Retrieves the Pause On Active property.
- conf_benchmark_property: Retrieves the Benchmark configuration.
- conf_benchmark_size_property: Retrieves the Benchmark Size property.
- conf_benchmark_algo_property: Retrieves the Benchmark Algorithm property.
- conf_benchmark_submit_property: Retrieves the Benchmark Submit property.
- conf_benchmark_verify_property: Retrieves the Benchmark Verify property.
- conf_benchmark_seed_property: Retrieves the Benchmark Seed property.
- conf_benchmark_hash_property: Retrieves the Benchmark Hash property.

Private Functions:

XMRigAPI:

- _update_cache: Updates the cache with new data.
- _get_data_from_cache: Retrieves data from the cache.

Exceptions:

- XMRigAPIError: Raised for general API errors.
- XMRigAuthorizationError: Raised for authorization errors.
- XMRigConnectionError: Raised for connection errors.
- XMRigDatabaseError: Raised for database errors.
- XMRigManagerError: Raised for manager errors.
"""

from .api import XMRigAPI
from .manager import XMRigManager
from .db import XMRigDatabase
from .exceptions import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError, XMRigDatabaseError, XMRigManagerError

__name__ = "xmrig"
__version__ = "0.2.1"
__author__ = "hreikin"
__email__ = "hreikin@gmail.com"
__license__ = "MIT"
__description__ = "This module provides objects to interact with the XMRig miner API, manage multiple miners, and store collected data in a database."
__url__ = "https://hreikin.co.uk/xmrig-api"

__all__ = ["XMRigAPI", "XMRigAPIError", "XMRigAuthorizationError", "XMRigConnectionError", "XMRigDatabase", "XMRigDatabaseError", "XMRigManager", "XMRigManagerError", "XMRigProperties"]