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
- helpers: Configures logging and handles custom exceptions.
- properties: Contains the XMRigProperties class for retrieving and caching properties.
- db: Contains the XMRigDatabase class for database operations.

Public Functions:

XMRigAPI:

- set_auth_header
- get_summary
- get_backends
- get_config
- post_config
- get_all_responses
- pause_miner
- resume_miner
- stop_miner
- start_miner

XMRigManager:

- add_miner
- remove_miner
- get_miner
- edit_miner
- perform_action_on_all
- get_all_miners_endpoints
- list_miners

XMRigDatabase:

- init_db
- check_table_exists
- insert_data_to_db
- fallback_to_db
- delete_all_miner_data_from_db

XMRigProperties:

- summary
- backends
- config
- sum_id
- sum_worker_id
- sum_uptime
- sum_uptime_readable
- sum_restricted
- sum_resources
- sum_memory_usage
- sum_free_memory
- sum_total_memory
- sum_resident_set_memory
- sum_load_average
- sum_hardware_concurrency
- sum_features
- sum_results
- sum_current_difficulty
- sum_good_shares
- sum_total_shares
- sum_avg_time
- sum_avg_time_ms
- sum_total_hashes
- sum_best_results
- sum_algorithm
- sum_connection
- sum_pool_info
- sum_pool_ip_address
- sum_pool_uptime
- sum_pool_uptime_ms
- sum_pool_ping
- sum_pool_failures
- sum_pool_tls
- sum_pool_tls_fingerprint
- sum_pool_algo
- sum_pool_diff
- sum_pool_accepted_jobs
- sum_pool_rejected_jobs
- sum_pool_average_time
- sum_pool_average_time_ms
- sum_pool_total_hashes
- sum_version
- sum_kind
- sum_ua
- sum_cpu_info
- sum_cpu_brand
- sum_cpu_family
- sum_cpu_model
- sum_cpu_stepping
- sum_cpu_proc_info
- sum_cpu_aes
- sum_cpu_avx2
- sum_cpu_x64
- sum_cpu_64_bit
- sum_cpu_l2
- sum_cpu_l3
- sum_cpu_cores
- sum_cpu_threads
- sum_cpu_packages
- sum_cpu_nodes
- sum_cpu_backend
- sum_cpu_msr
- sum_cpu_assembly
- sum_cpu_arch
- sum_cpu_flags
- sum_donate_level
- sum_paused
- sum_algorithms
- sum_hashrates
- sum_hashrate_10s
- sum_hashrate_1m
- sum_hashrate_15m
- sum_hashrate_highest
- sum_hugepages
- enabled_backends
- be_cpu_type
- be_cpu_enabled
- be_cpu_algo
- be_cpu_profile
- be_cpu_hw_aes
- be_cpu_priority
- be_cpu_msr
- be_cpu_asm
- be_cpu_argon2_impl
- be_cpu_hugepages
- be_cpu_memory
- be_cpu_hashrates
- be_cpu_hashrate_10s
- be_cpu_hashrate_1m
- be_cpu_hashrate_15m
- be_cpu_threads
- be_cpu_threads_intensity
- be_cpu_threads_affinity
- be_cpu_threads_av
- be_cpu_threads_hashrates_10s
- be_cpu_threads_hashrates_1m
- be_cpu_threads_hashrates_15m
- be_opencl_type
- be_opencl_enabled
- be_opencl_algo
- be_opencl_profile
- be_opencl_platform
- be_opencl_platform_index
- be_opencl_platform_profile
- be_opencl_platform_version
- be_opencl_platform_name
- be_opencl_platform_vendor
- be_opencl_platform_extensions
- be_opencl_hashrates
- be_opencl_hashrate_10s
- be_opencl_hashrate_1m
- be_opencl_hashrate_15m
- be_opencl_threads
- be_opencl_threads_index
- be_opencl_threads_intensity
- be_opencl_threads_worksize
- be_opencl_threads_amount
- be_opencl_threads_unroll
- be_opencl_threads_affinity
- be_opencl_threads_hashrates
- be_opencl_threads_hashrate_10s
- be_opencl_threads_hashrate_1m
- be_opencl_threads_hashrate_15m
- be_opencl_threads_board
- be_opencl_threads_name
- be_opencl_threads_bus_id
- be_opencl_threads_cu
- be_opencl_threads_global_mem
- be_opencl_threads_health
- be_opencl_threads_health_temp
- be_opencl_threads_health_power
- be_opencl_threads_health_clock
- be_opencl_threads_health_mem_clock
- be_opencl_threads_health_rpm
- be_cuda_type
- be_cuda_enabled
- be_cuda_algo
- be_cuda_profile
- be_cuda_versions
- be_cuda_runtime
- be_cuda_driver
- be_cuda_plugin
- be_cuda_hashrates
- be_cuda_hashrate_10s
- be_cuda_hashrate_1m
- be_cuda_hashrate_15m
- be_cuda_threads
- be_cuda_threads_index
- be_cuda_threads_amount
- be_cuda_threads_blocks
- be_cuda_threads_bfactor
- be_cuda_threads_bsleep
- be_cuda_threads_affinity
- be_cuda_threads_dataset_host
- be_cuda_threads_hashrates
- be_cuda_threads_hashrate_10s
- be_cuda_threads_hashrate_1m
- be_cuda_threads_hashrate_15m
- be_cuda_threads_name
- be_cuda_threads_bus_id
- be_cuda_threads_smx
- be_cuda_threads_arch
- be_cuda_threads_global_mem
- be_cuda_threads_clock
- be_cuda_threads_memory_clock

Private Functions:

XMRigAPI:

- _update_properties_cache

XMRigProperties:

- _get_data_from_response

Exceptions:

- XMRigAPIError
- XMRigAuthorizationError
- XMRigConnectionError
- XMRigDatabaseError
- XMRigManagerError
- XMRigPropertiesError
"""

from .api import XMRigAPI
from .manager import XMRigManager
from .db import XMRigDatabase
from .helpers import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError

__name__ = "xmrig"
__version__ = "0.0.12"
__author__ = "hreikin"
__email__ = "hreikin@gmail.com"
__license__ = "MIT"
__description__ = "This module provides objects to interact with the XMRig miner API, manage multiple miners, and store collected data in a database."
__url__ = "https://hreikin.co.uk/xmrig-api"

__all__ = ["XMRigAPI", "XMRigAPIError", "XMRigAuthorizationError", "XMRigConnectionError", "XMRigDatabase", "XMRigDatabaseError", "XMRigManager", "XMRigManagerError", "XMRigProperties", "XMRigPropertiesError"]