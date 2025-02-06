import unittest, json
from unittest.mock import patch
from xmrig.api import XMRigAPI

class TestXMRigProperties(unittest.TestCase):

    @patch('xmrig.api.XMRigAPI.get_all_responses', return_value=True)
    def setUp(self, mock_get_all_responses):
        with open("api/summary.json", "r") as f:
            self.summary = json.loads(f.read())
        with open("api/backends.json", "r") as f:
            self.backends = json.loads(f.read())
        with open("api/config.json", "r") as f:
            self.config = json.loads(f.read())
        self.api = XMRigAPI("test_miner", "127.0.0.1", "8080")
        self.api._update_cache(self.summary, "summary")
        self.api._update_cache(self.backends, "backends")
        self.api._update_cache(self.config, "config")

    def test_summary_property(self):
        self.assertEqual(self.api.summary, self.summary)
    
    def test_backends_property(self):
        self.assertEqual(self.api.backends, self.backends)
    
    def test_config_property(self):
        self.assertEqual(self.api.config, self.config)
    
    def test_sum_id_property(self):
        self.assertEqual(self.api.sum_id, self.summary["id"])
    
    def test_sum_worker_id_property(self):
        self.assertEqual(self.api.sum_worker_id, self.summary["worker_id"])
    
    def test_sum_uptime_property(self):
        self.assertEqual(self.api.sum_uptime, self.summary["uptime"])
    
    def test_sum_uptime_readable_property(self):
        self.assertEqual(self.api.sum_uptime_readable, "3 days, 0:16:35")
    
    def test_sum_restricted_property(self):
        self.assertEqual(self.api.sum_restricted, self.summary["restricted"])
    
    def test_sum_resources_property(self):
        self.assertEqual(self.api.sum_resources, self.summary["resources"])
    
    def test_sum_memory_usage_property(self):
        self.assertEqual(self.api.sum_memory_usage, self.summary["resources"]["memory"])
    
    def test_sum_free_memory_property(self):
        self.assertEqual(self.api.sum_free_memory, self.summary["resources"]["memory"]["free"])
    
    def test_sum_total_memory_property(self):
        self.assertEqual(self.api.sum_total_memory, self.summary["resources"]["memory"]["total"])
    
    def test_sum_resident_set_memory_property(self):
        self.assertEqual(self.api.sum_resident_set_memory, self.summary["resources"]["memory"]["resident_set_memory"])
    
    def test_sum_load_average_property(self):
        self.assertEqual(self.api.sum_load_average, self.summary["resources"]["load_average"])
    
    def test_sum_hardware_concurrency_property(self):
        self.assertEqual(self.api.sum_hardware_concurrency, self.summary["resources"]["hardware_concurrency"])
    
    def test_sum_features_property(self):
        self.assertEqual(self.api.sum_features, self.summary["features"])
    
    def test_sum_results_property(self):
        self.assertEqual(self.api.sum_results, self.summary["results"])
    
    def test_sum_current_difficulty_property(self):
        self.assertEqual(self.api.sum_current_difficulty, self.summary["results"]["diff_current"])
    
    def test_sum_good_shares_property(self):
        self.assertEqual(self.api.sum_good_shares, self.summary["results"]["shares_good"])
    
    def test_sum_total_shares_property(self):
        self.assertEqual(self.api.sum_total_shares, self.summary["results"]["shares_total"])
    
    def test_sum_avg_time_property(self):
        self.assertEqual(self.api.sum_avg_time, self.summary["results"]["avg_time"])
    
    def test_sum_avg_time_ms_property(self):
        self.assertEqual(self.api.sum_avg_time_ms, self.summary["results"]["avg_time_ms"])
    
    def test_sum_total_hashes_property(self):
        self.assertEqual(self.api.sum_total_hashes, self.summary["results"]["hashes_total"])
    
    def test_sum_best_results_property(self):
        self.assertEqual(self.api.sum_best_results, self.summary["results"]["best"])
    
    def test_sum_algorithm_property(self):
        self.assertEqual(self.api.sum_algorithm, self.summary["algo"])
    
    def test_sum_connection_property(self):
        self.assertEqual(self.api.sum_connection, self.summary["connection"])
    
    def test_sum_pool_info_property(self):
        self.assertEqual(self.api.sum_pool_info, self.summary["connection"]["pool"])
    
    def test_sum_pool_ip_address_property(self):
        self.assertEqual(self.api.sum_pool_ip_address, self.summary["connection"]["ip"])
    
    def test_sum_pool_uptime_property(self):
        self.assertEqual(self.api.sum_pool_uptime, self.summary["connection"]["uptime"])
    
    def test_sum_pool_uptime_ms_property(self):
        self.assertEqual(self.api.sum_pool_uptime_ms, self.summary["connection"]["uptime_ms"])
    
    def test_sum_pool_ping_property(self):
        self.assertEqual(self.api.sum_pool_ping, self.summary["connection"]["ping"])
    
    def test_sum_pool_failures_property(self):
        self.assertEqual(self.api.sum_pool_failures, self.summary["connection"]["failures"])
    
    def test_sum_pool_tls_property(self):
        self.assertEqual(self.api.sum_pool_tls, self.summary["connection"]["tls"])
    
    def test_sum_pool_tls_fingerprint_property(self):
        self.assertEqual(self.api.sum_pool_tls_fingerprint, self.summary["connection"]["tls-fingerprint"])
    
    def test_sum_pool_algo_property(self):
        self.assertEqual(self.api.sum_pool_algo, self.summary["connection"]["algo"])
    
    def test_sum_pool_diff_property(self):
        self.assertEqual(self.api.sum_pool_diff, self.summary["connection"]["diff"])
    
    def test_sum_pool_accepted_jobs_property(self):
        self.assertEqual(self.api.sum_pool_accepted_jobs, self.summary["connection"]["accepted"])
    
    def test_sum_pool_rejected_jobs_property(self):
        self.assertEqual(self.api.sum_pool_rejected_jobs, self.summary["connection"]["rejected"])
    
    def test_sum_pool_average_time_property(self):
        self.assertEqual(self.api.sum_pool_average_time, self.summary["connection"]["avg_time"])
    
    def test_sum_pool_average_time_ms_property(self):
        self.assertEqual(self.api.sum_pool_average_time_ms, self.summary["connection"]["avg_time_ms"])
    
    def test_sum_pool_total_hashes_property(self):
        self.assertEqual(self.api.sum_pool_total_hashes, self.summary["connection"]["hashes_total"])
    
    def test_sum_version_property(self):
        self.assertEqual(self.api.sum_version, self.summary["version"])
    
    def test_sum_kind_property(self):
        self.assertEqual(self.api.sum_kind, self.summary["kind"])
    
    def test_sum_ua_property(self):
        self.assertEqual(self.api.sum_ua, self.summary["ua"])
    
    def test_sum_cpu_info_property(self):
        self.assertEqual(self.api.sum_cpu_info, self.summary["cpu"])
    
    def test_sum_cpu_brand_property(self):
        self.assertEqual(self.api.sum_cpu_brand, self.summary["cpu"]["brand"])
    
    def test_sum_cpu_family_property(self):
        self.assertEqual(self.api.sum_cpu_family, self.summary["cpu"]["family"])
    
    def test_sum_cpu_model_property(self):
        self.assertEqual(self.api.sum_cpu_model, self.summary["cpu"]["model"])
    
    def test_sum_cpu_stepping_property(self):
        self.assertEqual(self.api.sum_cpu_stepping, self.summary["cpu"]["stepping"])
    
    def test_sum_cpu_proc_info_property(self):
        self.assertEqual(self.api.sum_cpu_proc_info, self.summary["cpu"]["proc_info"])
    
    def test_sum_cpu_aes_property(self):
        self.assertEqual(self.api.sum_cpu_aes, self.summary["cpu"]["aes"])
    
    def test_sum_cpu_avx2_property(self):
        self.assertEqual(self.api.sum_cpu_avx2, self.summary["cpu"]["avx2"])
    
    def test_sum_cpu_x64_property(self):
        self.assertEqual(self.api.sum_cpu_x64, self.summary["cpu"]["x64"])
    
    def test_sum_cpu_64_bit_property(self):
        self.assertEqual(self.api.sum_cpu_64_bit, self.summary["cpu"]["64_bit"])
    
    def test_sum_cpu_l2_property(self):
        self.assertEqual(self.api.sum_cpu_l2, self.summary["cpu"]["l2"])
    
    def test_sum_cpu_l3_property(self):
        self.assertEqual(self.api.sum_cpu_l3, self.summary["cpu"]["l3"])
    
    def test_sum_cpu_cores_property(self):
        self.assertEqual(self.api.sum_cpu_cores, self.summary["cpu"]["cores"])
    
    def test_sum_cpu_threads_property(self):
        self.assertEqual(self.api.sum_cpu_threads, self.summary["cpu"]["threads"])
    
    def test_sum_cpu_packages_property(self):
        self.assertEqual(self.api.sum_cpu_packages, self.summary["cpu"]["packages"])
    
    def test_sum_cpu_nodes_property(self):
        self.assertEqual(self.api.sum_cpu_nodes, self.summary["cpu"]["nodes"])
    
    def test_sum_cpu_backend_property(self):
        self.assertEqual(self.api.sum_cpu_backend, self.summary["cpu"]["backend"])
    
    def test_sum_cpu_msr_property(self):
        self.assertEqual(self.api.sum_cpu_msr, self.summary["cpu"]["msr"])
    
    def test_sum_cpu_assembly_property(self):
        self.assertEqual(self.api.sum_cpu_assembly, self.summary["cpu"]["assembly"])
    
    def test_sum_cpu_arch_property(self):
        self.assertEqual(self.api.sum_cpu_arch, self.summary["cpu"]["arch"])
    
    def test_sum_cpu_flags_property(self):
        self.assertEqual(self.api.sum_cpu_flags, self.summary["cpu"]["flags"])
    
    def test_sum_donate_level_property(self):
        self.assertEqual(self.api.sum_donate_level, self.summary["donate_level"])
    
    def test_sum_paused_property(self):
        self.assertEqual(self.api.sum_paused, self.summary["paused"])
    
    def test_sum_algorithms_property(self):
        self.assertEqual(self.api.sum_algorithms, self.summary["algorithms"])
    
    def test_sum_hashrate_property(self):
        self.assertEqual(self.api.sum_hashrate, self.summary["hashrate"])
    
    def test_sum_hashrate_total_property(self):
        self.assertEqual(self.api.sum_hashrate_total, self.summary["hashrate"]["total"])
    
    def test_sum_hashrate_10s_property(self):
        self.assertEqual(self.api.sum_hashrate_10s, self.summary["hashrate"]["total"][0])
    
    def test_sum_hashrate_1m_property(self):
        self.assertEqual(self.api.sum_hashrate_1m, self.summary["hashrate"]["total"][1])
    
    def test_sum_hashrate_15m_property(self):
        self.assertEqual(self.api.sum_hashrate_15m, self.summary["hashrate"]["total"][2])
    
    def test_sum_hashrate_highest_property(self):
        self.assertEqual(self.api.sum_hashrate_highest, self.summary["hashrate"]["highest"])
    
    def test_sum_hugepages_property(self):
        self.assertEqual(self.api.sum_hugepages, self.summary["hugepages"])
    
    def test_enabled_backends_property(self):
        self.assertEqual(self.api.enabled_backends, ["cpu", "opencl", "cuda"])
    
    def test_be_cpu_type_property(self):
        self.assertEqual(self.api.be_cpu_type, self.backends[0]["type"])
    
    def test_be_cpu_enabled_property(self):
        self.assertEqual(self.api.be_cpu_enabled, self.backends[0]["enabled"])
    
    def test_be_cpu_algo_property(self):
        self.assertEqual(self.api.be_cpu_algo, self.backends[0]["algo"])
    
    def test_be_cpu_profile_property(self):
        self.assertEqual(self.api.be_cpu_profile, self.backends[0]["profile"])
    
    def test_be_cpu_hw_aes_property(self):
        self.assertEqual(self.api.be_cpu_hw_aes, self.backends[0]["hw-aes"])
    
    def test_be_cpu_priority_property(self):
        self.assertEqual(self.api.be_cpu_priority, self.backends[0]["priority"])
    
    def test_be_cpu_msr_property(self):
        self.assertEqual(self.api.be_cpu_msr, self.backends[0]["msr"])
    
    def test_be_cpu_asm_property(self):
        self.assertEqual(self.api.be_cpu_asm, self.backends[0]["asm"])
    
    def test_be_cpu_argon2_impl_property(self):
        self.assertEqual(self.api.be_cpu_argon2_impl, self.backends[0]["argon2-impl"])
    
    def test_be_cpu_hugepages_property(self):
        self.assertEqual(self.api.be_cpu_hugepages, self.backends[0]["hugepages"])
    
    def test_be_cpu_memory_property(self):
        self.assertEqual(self.api.be_cpu_memory, self.backends[0]["memory"])
    
    def test_be_cpu_hashrates_property(self):
        self.assertEqual(self.api.be_cpu_hashrates, self.backends[0]["hashrate"])
    
    def test_be_cpu_hashrate_10s_property(self):
        self.assertEqual(self.api.be_cpu_hashrate_10s, self.backends[0]["hashrate"][0])
    
    def test_be_cpu_hashrate_1m_property(self):
        self.assertEqual(self.api.be_cpu_hashrate_1m, self.backends[0]["hashrate"][1])
    
    def test_be_cpu_hashrate_15m_property(self):
        self.assertEqual(self.api.be_cpu_hashrate_15m, self.backends[0]["hashrate"][2])
    
    def test_be_cpu_threads_property(self):
        self.assertEqual(self.api.be_cpu_threads, self.backends[0]["threads"])
    
    def test_be_cpu_threads_intensity_property(self):
        self.assertEqual(self.api.be_cpu_threads_intensity, [1,1,1,1,1,1,1,1])
    
    def test_be_cpu_threads_affinity_property(self):
        self.assertEqual(self.api.be_cpu_threads_affinity, [0,2,4,6,8,10,12,14])
    
    def test_be_cpu_threads_av_property(self):
        self.assertEqual(self.api.be_cpu_threads_av, [1,1,1,1,1,1,1,1])
    
    def test_be_cpu_threads_hashrates_property(self):
        self.assertEqual(self.api.be_cpu_threads_hashrates, [[593.57, 593.42, 580.85],[594.51, 597.24, 584.54],[593.88, 607.76, 597.86],[610.62, 608.23, 597.72],[610.3, 611.16, 600.39],[604.28, 604.37, 595.25],[602.72, 602.24, 594.52],[614.98, 612.18, 603.12]])
    
    def test_be_cpu_threads_hashrates_10s_property(self):
        self.assertEqual(self.api.be_cpu_threads_hashrates_10s, [593.57,594.51,593.88,610.62,610.3,604.28,602.72,614.98])
    
    def test_be_cpu_threads_hashrates_1m_property(self):
        self.assertEqual(self.api.be_cpu_threads_hashrates_1m, [593.42,597.24,607.76,608.23,611.16,604.37,602.24,612.18])
    
    def test_be_cpu_threads_hashrates_15m_property(self):
        self.assertEqual(self.api.be_cpu_threads_hashrates_15m, [580.85,584.54,597.86,597.72,600.39,595.25,594.52,603.12])
    
    def test_be_opencl_type_property(self):
        self.assertEqual(self.api.be_opencl_type, self.backends[1]["type"])
    
    def test_be_opencl_enabled_property(self):
        self.assertEqual(self.api.be_opencl_enabled, self.backends[1]["enabled"])
    
    def test_be_opencl_algo_property(self):
        self.assertEqual(self.api.be_opencl_algo, self.backends[1]["algo"])
    
    def test_be_opencl_profile_property(self):
        self.assertEqual(self.api.be_opencl_profile, self.backends[1]["profile"])
    
    def test_be_opencl_platform_property(self):
        self.assertEqual(self.api.be_opencl_platform, self.backends[1]["platform"])
    
    def test_be_opencl_platform_index_property(self):
        self.assertEqual(self.api.be_opencl_platform_index, self.backends[1]["platform"]["index"])
    
    def test_be_opencl_platform_profile_property(self):
        self.assertEqual(self.api.be_opencl_platform_profile, self.backends[1]["platform"]["profile"])
    
    def test_be_opencl_platform_version_property(self):
        self.assertEqual(self.api.be_opencl_platform_version, self.backends[1]["platform"]["version"])
    
    def test_be_opencl_platform_name_property(self):
        self.assertEqual(self.api.be_opencl_platform_name, self.backends[1]["platform"]["name"])
    
    def test_be_opencl_platform_vendor_property(self):
        self.assertEqual(self.api.be_opencl_platform_vendor, self.backends[1]["platform"]["vendor"])
    
    def test_be_opencl_platform_extensions_property(self):
        self.assertEqual(self.api.be_opencl_platform_extensions, self.backends[1]["platform"]["extensions"])
    
    def test_be_opencl_hashrates_property(self):
        self.assertEqual(self.api.be_opencl_hashrates, self.backends[1]["hashrate"])
    
    def test_be_opencl_hashrate_10s_property(self):
        self.assertEqual(self.api.be_opencl_hashrate_10s, self.backends[1]["hashrate"][0])
    
    def test_be_opencl_hashrate_1m_property(self):
        self.assertEqual(self.api.be_opencl_hashrate_1m, self.backends[1]["hashrate"][1])
    
    def test_be_opencl_hashrate_15m_property(self):
        self.assertEqual(self.api.be_opencl_hashrate_15m, self.backends[1]["hashrate"][2])
    
    def test_be_opencl_threads_property(self):
        self.assertEqual(self.api.be_opencl_threads, self.backends[1]["threads"])
    
    def test_be_opencl_threads_index_property(self):
        self.assertEqual(self.api.be_opencl_threads_index, [self.backends[1]["threads"][0]["index"]])
    
    def test_be_opencl_threads_intensity_property(self):
        self.assertEqual(self.api.be_opencl_threads_intensity, [self.backends[1]["threads"][0]["intensity"]])
    
    def test_be_opencl_threads_worksize_property(self):
        self.assertEqual(self.api.be_opencl_threads_worksize, [self.backends[1]["threads"][0]["worksize"]])
    
    def test_be_opencl_threads_unroll_property(self):
        self.assertEqual(self.api.be_opencl_threads_unroll, [self.backends[1]["threads"][0]["unroll"]])
    
    def test_be_opencl_threads_affinity_property(self):
        self.assertEqual(self.api.be_opencl_threads_affinity, [self.backends[1]["threads"][0]["affinity"]])
    
    def test_be_opencl_threads_hashrates_property(self):
        self.assertEqual(self.api.be_opencl_threads_hashrates, [self.backends[1]["threads"][0]["hashrate"]])
    
    def test_be_opencl_threads_hashrate_10s_property(self):
        self.assertEqual(self.api.be_opencl_threads_hashrate_10s, [self.backends[1]["threads"][0]["hashrate"][0]])
    
    def test_be_opencl_threads_hashrate_1m_property(self):
        self.assertEqual(self.api.be_opencl_threads_hashrate_1m, [self.backends[1]["threads"][0]["hashrate"][1]])
    
    def test_be_opencl_threads_hashrate_15m_property(self):
        self.assertEqual(self.api.be_opencl_threads_hashrate_15m, [self.backends[1]["threads"][0]["hashrate"][2]])
    
    def test_be_opencl_threads_board_property(self):
        self.assertEqual(self.api.be_opencl_threads_board, [self.backends[1]["threads"][0]["board"]])
    
    def test_be_opencl_threads_name_property(self):
        self.assertEqual(self.api.be_opencl_threads_name, [self.backends[1]["threads"][0]["name"]])
    
    def test_be_opencl_threads_bus_id_property(self):
        self.assertEqual(self.api.be_opencl_threads_bus_id, [self.backends[1]["threads"][0]["bus_id"]])
    
    def test_be_opencl_threads_cu_property(self):
        self.assertEqual(self.api.be_opencl_threads_cu, [self.backends[1]["threads"][0]["cu"]])
    
    def test_be_opencl_threads_global_mem_property(self):
        self.assertEqual(self.api.be_opencl_threads_global_mem, [self.backends[1]["threads"][0]["global_mem"]])
    
    def test_be_opencl_threads_health_property(self):
        self.assertEqual(self.api.be_opencl_threads_health, [self.backends[1]["threads"][0]["health"]])
    
    def test_be_opencl_threads_health_temp_property(self):
        self.assertEqual(self.api.be_opencl_threads_health_temp, [self.backends[1]["threads"][0]["health"]["temperature"]])
    
    def test_be_opencl_threads_health_power_property(self):
        self.assertEqual(self.api.be_opencl_threads_health_power, [self.backends[1]["threads"][0]["health"]["power"]])
    
    def test_be_opencl_threads_health_clock_property(self):
        self.assertEqual(self.api.be_opencl_threads_health_clock, [self.backends[1]["threads"][0]["health"]["clock"]])
    
    def test_be_opencl_threads_health_mem_clock_property(self):
        self.assertEqual(self.api.be_opencl_threads_health_mem_clock, [self.backends[1]["threads"][0]["health"]["mem_clock"]])
    
    def test_be_opencl_threads_health_rpm_property(self):
        self.assertEqual(self.api.be_opencl_threads_health_rpm, [self.backends[1]["threads"][0]["health"]["rpm"]])
    
    def test_be_cuda_type_property(self):
        self.assertEqual(self.api.be_cuda_type, self.backends[2]["type"])
    
    def test_be_cuda_enabled_property(self):
        self.assertEqual(self.api.be_cuda_enabled, self.backends[2]["enabled"])
    
    def test_be_cuda_algo_property(self):
        self.assertEqual(self.api.be_cuda_algo, self.backends[2]["algo"])
    
    def test_be_cuda_profile_property(self):
        self.assertEqual(self.api.be_cuda_profile, self.backends[2]["profile"])
    
    def test_be_cuda_versions_property(self):
        self.assertEqual(self.api.be_cuda_versions, self.backends[2]["versions"])
    
    def test_be_cuda_runtime_property(self):
        self.assertEqual(self.api.be_cuda_runtime, self.backends[2]["versions"]["cuda-runtime"])
    
    def test_be_cuda_driver_property(self):
        self.assertEqual(self.api.be_cuda_driver, self.backends[2]["versions"]["cuda-driver"])
    
    def test_be_cuda_plugin_property(self):
        self.assertEqual(self.api.be_cuda_plugin, self.backends[2]["versions"]["plugin"])
    
    def test_be_cuda_hashrates_property(self):
        self.assertEqual(self.api.be_cuda_hashrates, self.backends[2]["hashrate"])
    
    def test_be_cuda_hashrate_10s_property(self):
        self.assertEqual(self.api.be_cuda_hashrate_10s, self.backends[2]["hashrate"][0])
    
    def test_be_cuda_hashrate_1m_property(self):
        self.assertEqual(self.api.be_cuda_hashrate_1m, self.backends[2]["hashrate"][1])
    
    def test_be_cuda_hashrate_15m_property(self):
        self.assertEqual(self.api.be_cuda_hashrate_15m, self.backends[2]["hashrate"][2])
    
    def test_be_cuda_threads_property(self):
        self.assertEqual(self.api.be_cuda_threads, self.backends[2]["threads"])
    
    def test_be_cuda_threads_index_property(self):
        self.assertEqual(self.api.be_cuda_threads_index, [self.backends[2]["threads"][0]["index"]])
    
    def test_be_cuda_threads_blocks_property(self):
        self.assertEqual(self.api.be_cuda_threads_blocks, [self.backends[2]["threads"][0]["blocks"]])
    
    def test_be_cuda_threads_bfactor_property(self):
        self.assertEqual(self.api.be_cuda_threads_bfactor, [self.backends[2]["threads"][0]["bfactor"]])
    
    def test_be_cuda_threads_bsleep_property(self):
        self.assertEqual(self.api.be_cuda_threads_bsleep, [self.backends[2]["threads"][0]["bsleep"]])
    
    def test_be_cuda_threads_affinity_property(self):
        self.assertEqual(self.api.be_cuda_threads_affinity, [self.backends[2]["threads"][0]["affinity"]])
    
    def test_be_cuda_threads_dataset_host_property(self):
        self.assertEqual(self.api.be_cuda_threads_dataset_host, [self.backends[2]["threads"][0]["dataset_host"]])
    
    def test_be_cuda_threads_hashrates_property(self):
        self.assertEqual(self.api.be_cuda_threads_hashrates, [self.backends[2]["threads"][0]["hashrate"]])
    
    def test_be_cuda_threads_hashrate_10s_property(self):
        self.assertEqual(self.api.be_cuda_threads_hashrate_10s, [self.backends[2]["threads"][0]["hashrate"][0]])
    
    def test_be_cuda_threads_hashrate_1m_property(self):
        self.assertEqual(self.api.be_cuda_threads_hashrate_1m, [self.backends[2]["threads"][0]["hashrate"][1]])
    
    def test_be_cuda_threads_hashrate_15m_property(self):
        self.assertEqual(self.api.be_cuda_threads_hashrate_15m, [self.backends[2]["threads"][0]["hashrate"][2]])
    
    def test_be_cuda_threads_name_property(self):
        self.assertEqual(self.api.be_cuda_threads_name, [self.backends[2]["threads"][0]["name"]])
    
    def test_be_cuda_threads_bus_id_property(self):
        self.assertEqual(self.api.be_cuda_threads_bus_id, [self.backends[2]["threads"][0]["bus_id"]])
    
    def test_be_cuda_threads_smx_property(self):
        self.assertEqual(self.api.be_cuda_threads_smx, [self.backends[2]["threads"][0]["smx"]])
    
    def test_be_cuda_threads_arch_property(self):
        self.assertEqual(self.api.be_cuda_threads_arch, [self.backends[2]["threads"][0]["arch"]])
    
    def test_be_cuda_threads_global_mem_property(self):
        self.assertEqual(self.api.be_cuda_threads_global_mem, [self.backends[2]["threads"][0]["global_mem"]])
    
    def test_be_cuda_threads_clock_property(self):
        self.assertEqual(self.api.be_cuda_threads_clock, [self.backends[2]["threads"][0]["clock"]])
    
    def test_be_cuda_threads_memory_clock_property(self):
        self.assertEqual(self.api.be_cuda_threads_memory_clock, [self.backends[2]["threads"][0]["memory_clock"]])
    
    def test_conf_api_property(self):
        self.assertEqual(self.api.conf_api_property, self.config["api"])
    
    def test_conf_api_id_property(self):
        self.assertEqual(self.api.conf_api_id_property, self.config["api"]["id"])
    
    def test_conf_api_worker_id_property(self):
        self.assertEqual(self.api.conf_api_worker_id_property, self.config["api"]["worker-id"])
    
    def test_conf_http_property(self):
        self.assertEqual(self.api.conf_http_property, self.config["http"])
    
    def test_conf_http_enabled_property(self):
        self.assertEqual(self.api.conf_http_enabled_property, self.config["http"]["enabled"])
    
    def test_conf_http_host_property(self):
        self.assertEqual(self.api.conf_http_host_property, self.config["http"]["host"])
    
    def test_conf_http_port_property(self):
        self.assertEqual(self.api.conf_http_port_property, self.config["http"]["port"])
    
    def test_conf_http_access_token_property(self):
        self.assertEqual(self.api.conf_http_access_token_property, self.config["http"]["access-token"])
    
    def test_conf_http_restricted_property(self):
        self.assertEqual(self.api.conf_http_restricted_property, self.config["http"]["restricted"])
    
    def test_conf_autosave_property(self):
        self.assertEqual(self.api.conf_autosave_property, self.config["autosave"])
    
    def test_conf_background_property(self):
        self.assertEqual(self.api.conf_background_property, self.config["background"])
    
    def test_conf_colors_property(self):
        self.assertEqual(self.api.conf_colors_property, self.config["colors"])
    
    def test_conf_title_property(self):
        self.assertEqual(self.api.conf_title_property, self.config["title"])
    
    def test_conf_randomx_property(self):
        self.assertEqual(self.api.conf_randomx_property, self.config["randomx"])
    
    def test_conf_randomx_init_property(self):
        self.assertEqual(self.api.conf_randomx_init_property, self.config["randomx"]["init"])
    
    def test_conf_randomx_init_avx2_property(self):
        self.assertEqual(self.api.conf_randomx_init_avx2_property, self.config["randomx"]["init-avx2"])
    
    def test_conf_randomx_mode_property(self):
        self.assertEqual(self.api.conf_randomx_mode_property, self.config["randomx"]["mode"])
    
    def test_conf_randomx_1gb_pages_property(self):
        self.assertEqual(self.api.conf_randomx_1gb_pages_property, self.config["randomx"]["1gb-pages"])
    
    def test_conf_randomx_rdmsr_property(self):
        self.assertEqual(self.api.conf_randomx_rdmsr_property, self.config["randomx"]["rdmsr"])
    
    def test_conf_randomx_wrmsr_property(self):
        self.assertEqual(self.api.conf_randomx_wrmsr_property, self.config["randomx"]["wrmsr"])
    
    def test_conf_randomx_cache_qos_property(self):
        self.assertEqual(self.api.conf_randomx_cache_qos_property, self.config["randomx"]["cache_qos"])
    
    def test_conf_randomx_numa_property(self):
        self.assertEqual(self.api.conf_randomx_numa_property, self.config["randomx"]["numa"])
    
    def test_conf_randomx_scratchpad_prefetch_mode_property(self):
        self.assertEqual(self.api.conf_randomx_scratchpad_prefetch_mode_property, self.config["randomx"]["scratchpad_prefetch_mode"])
    
    def test_conf_cpu_property(self):
        self.assertEqual(self.api.conf_cpu_property, self.config["cpu"])
    
    def test_conf_cpu_enabled_property(self):
        self.assertEqual(self.api.conf_cpu_enabled_property, self.config["cpu"]["enabled"])
    
    def test_conf_cpu_huge_pages_property(self):
        self.assertEqual(self.api.conf_cpu_huge_pages_property, self.config["cpu"]["huge-pages"])
    
    def test_conf_cpu_huge_pages_jit_property(self):
        self.assertEqual(self.api.conf_cpu_huge_pages_jit_property, self.config["cpu"]["huge-pages-jit"])
    
    def test_conf_cpu_hw_aes_property(self):
        self.assertEqual(self.api.conf_cpu_hw_aes_property, self.config["cpu"]["hw-aes"])
    
    def test_conf_cpu_priority_property(self):
        self.assertEqual(self.api.conf_cpu_priority_property, self.config["cpu"]["priority"])
    
    def test_conf_cpu_memory_pool_property(self):
        self.assertEqual(self.api.conf_cpu_memory_pool_property, self.config["cpu"]["memory-pool"])
    
    def test_conf_cpu_yield_property(self):
        self.assertEqual(self.api.conf_cpu_yield_property, self.config["cpu"]["yield"])
    
    def test_conf_cpu_max_threads_hint_property(self):
        self.assertEqual(self.api.conf_cpu_max_threads_hint_property, self.config["cpu"]["max-threads-hint"])
    
    def test_conf_cpu_asm_property(self):
        self.assertEqual(self.api.conf_cpu_asm_property, self.config["cpu"]["asm"])
    
    def test_conf_cpu_argon2_impl_property(self):
        self.assertEqual(self.api.conf_cpu_argon2_impl_property, self.config["cpu"]["argon2-impl"])
    
    def test_conf_opencl_property(self):
        self.assertEqual(self.api.conf_opencl_property, self.config["opencl"])
    
    def test_conf_opencl_enabled_property(self):
        self.assertEqual(self.api.conf_opencl_enabled_property, self.config["opencl"]["enabled"])
    
    def test_conf_opencl_cache_property(self):
        self.assertEqual(self.api.conf_opencl_cache_property, self.config["opencl"]["cache"])
    
    def test_conf_opencl_loader_property(self):
        self.assertEqual(self.api.conf_opencl_loader_property, self.config["opencl"]["loader"])
    
    def test_conf_opencl_platform_property(self):
        self.assertEqual(self.api.conf_opencl_platform_property, self.config["opencl"]["platform"])
    
    def test_conf_opencl_adl_property(self):
        self.assertEqual(self.api.conf_opencl_adl_property, self.config["opencl"]["adl"])
    
    def test_conf_cuda_property(self):
        self.assertEqual(self.api.conf_cuda_property, self.config["cuda"])
    
    def test_conf_cuda_enabled_property(self):
        self.assertEqual(self.api.conf_cuda_enabled_property, self.config["cuda"]["enabled"])
    
    def test_conf_cuda_loader_property(self):
        self.assertEqual(self.api.conf_cuda_loader_property, self.config["cuda"]["loader"])
    
    def test_conf_cuda_nvml_property(self):
        self.assertEqual(self.api.conf_cuda_nvml_property, self.config["cuda"]["nvml"])
    
    def test_conf_log_file_property(self):
        self.assertEqual(self.api.conf_log_file_property, self.config["log-file"])
    
    def test_conf_donate_level_property(self):
        self.assertEqual(self.api.conf_donate_level_property, self.config["donate-level"])
    
    def test_conf_donate_over_proxy_property(self):
        self.assertEqual(self.api.conf_donate_over_proxy_property, self.config["donate-over-proxy"])
    
    def test_conf_pools_property(self):
        self.assertEqual(self.api.conf_pools_property, self.config["pools"])
    
    def test_conf_pools_algo_property(self):
        self.assertEqual(self.api.conf_pools_algo_property, [self.config["pools"][0]["algo"]])
    
    def test_conf_pools_coin_property(self):
        self.assertEqual(self.api.conf_pools_coin_property, [self.config["pools"][0]["coin"]])
    
    def test_conf_pools_url_property(self):
        self.assertEqual(self.api.conf_pools_url_property, [self.config["pools"][0]["url"]])
    
    def test_conf_pools_user_property(self):
        self.assertEqual(self.api.conf_pools_user_property, [self.config["pools"][0]["user"]])
    
    def test_conf_pools_pass_property(self):
        self.assertEqual(self.api.conf_pools_pass_property, [self.config["pools"][0]["pass"]])
    
    def test_conf_pools_rig_id_property(self):
        self.assertEqual(self.api.conf_pools_rig_id_property, [self.config["pools"][0]["rig-id"]])
    
    def test_conf_pools_nicehash_property(self):
        self.assertEqual(self.api.conf_pools_nicehash_property, [self.config["pools"][0]["nicehash"]])
    
    def test_conf_pools_keepalive_property(self):
        self.assertEqual(self.api.conf_pools_keepalive_property, [self.config["pools"][0]["keepalive"]])
    
    def test_conf_pools_enabled_property(self):
        self.assertEqual(self.api.conf_pools_enabled_property, [self.config["pools"][0]["enabled"]])
    
    def test_conf_pools_tls_property(self):
        self.assertEqual(self.api.conf_pools_tls_property, [self.config["pools"][0]["tls"]])
    
    def test_conf_pools_sni_property(self):
        self.assertEqual(self.api.conf_pools_sni_property, [self.config["pools"][0]["sni"]])
    
    def test_conf_pools_spend_secret_key_property(self):
        self.assertEqual(self.api.conf_pools_spend_secret_key_property, [self.config["pools"][0]["spend-secret-key"]])
    
    def test_conf_pools_tls_fingerprint_property(self):
        self.assertEqual(self.api.conf_pools_tls_fingerprint_property, [self.config["pools"][0]["tls-fingerprint"]])
    
    def test_conf_pools_daemon_property(self):
        self.assertEqual(self.api.conf_pools_daemon_property, [self.config["pools"][0]["daemon"]])
    
    def test_conf_pools_daemon_poll_interval_property(self):
        self.assertEqual(self.api.conf_pools_daemon_poll_interval_property, [self.config["pools"][0]["daemon-poll-interval"]])
    
    def test_conf_pools_daemon_job_timeout_property(self):
        self.assertEqual(self.api.conf_pools_daemon_job_timeout_property, [self.config["pools"][0]["daemon-job-timeout"]])
    
    def test_conf_pools_daemon_zmq_port_property(self):
        self.assertEqual(self.api.conf_pools_daemon_zmq_port_property, [self.config["pools"][0]["daemon-zmq-port"]])
    
    def test_conf_pools_socks5_property(self):
        self.assertEqual(self.api.conf_pools_socks5_property, [self.config["pools"][0]["socks5"]])
    
    def test_conf_pools_self_select_property(self):
        self.assertEqual(self.api.conf_pools_self_select_property, [self.config["pools"][0]["self-select"]])
    
    def test_conf_pools_submit_to_origin_property(self):
        self.assertEqual(self.api.conf_pools_submit_to_origin_property, [self.config["pools"][0]["submit-to-origin"]])
    
    def test_conf_retries_property(self):
        self.assertEqual(self.api.conf_retries_property, self.config["retries"])
    
    def test_conf_retry_pause_property(self):
        self.assertEqual(self.api.conf_retry_pause_property, self.config["retry-pause"])
    
    def test_conf_print_time_property(self):
        self.assertEqual(self.api.conf_print_time_property, self.config["print-time"])
    
    def test_conf_health_print_time_property(self):
        self.assertEqual(self.api.conf_health_print_time_property, self.config["health-print-time"])
    
    def test_conf_dmi_property(self):
        self.assertEqual(self.api.conf_dmi_property, self.config["dmi"])
    
    def test_conf_syslog_property(self):
        self.assertEqual(self.api.conf_syslog_property, self.config["syslog"])
    
    def test_conf_tls_property(self):
        self.assertEqual(self.api.conf_tls_property, self.config["tls"])
    
    def test_conf_tls_enabled_property(self):
        self.assertEqual(self.api.conf_tls_enabled_property, self.config["tls"]["enabled"])
    
    def test_conf_tls_protocols_property(self):
        self.assertEqual(self.api.conf_tls_protocols_property, self.config["tls"]["protocols"])
    
    def test_conf_tls_cert_property(self):
        self.assertEqual(self.api.conf_tls_cert_property, self.config["tls"]["cert"])
    
    def test_conf_tls_cert_key_property(self):
        self.assertEqual(self.api.conf_tls_cert_key_property, self.config["tls"]["cert_key"])
    
    def test_conf_tls_ciphers_property(self):
        self.assertEqual(self.api.conf_tls_ciphers_property, self.config["tls"]["ciphers"])
    
    def test_conf_tls_ciphersuites_property(self):
        self.assertEqual(self.api.conf_tls_ciphersuites_property, self.config["tls"]["ciphersuites"])
    
    def test_conf_tls_dhparam_property(self):
        self.assertEqual(self.api.conf_tls_dhparam_property, self.config["tls"]["dhparam"])
    
    def test_conf_dns_property(self):
        self.assertEqual(self.api.conf_dns_property, self.config["dns"])
    
    def test_conf_dns_ipv6_property(self):
        self.assertEqual(self.api.conf_dns_ipv6_property, self.config["dns"]["ipv6"])
    
    def test_conf_dns_ttl_property(self):
        self.assertEqual(self.api.conf_dns_ttl_property, self.config["dns"]["ttl"])
    
    def test_conf_user_agent_property(self):
        self.assertEqual(self.api.conf_user_agent_property, self.config["user-agent"])
    
    def test_conf_verbose_property(self):
        self.assertEqual(self.api.conf_verbose_property, self.config["verbose"])
    
    def test_conf_watch_property(self):
        self.assertEqual(self.api.conf_watch_property, self.config["watch"])
    
    def test_conf_rebench_algo_property(self):
        self.assertEqual(self.api.conf_rebench_algo_property, self.config["rebench-algo"])
    
    def test_conf_bench_algo_time_property(self):
        self.assertEqual(self.api.conf_bench_algo_time_property, self.config["bench-algo-time"])
    
    def test_conf_pause_on_battery_property(self):
        self.assertEqual(self.api.conf_pause_on_battery_property, self.config["pause-on-battery"])
    
    def test_conf_pause_on_active_property(self):
        self.assertEqual(self.api.conf_pause_on_active_property, self.config["pause-on-active"])
    
    def test_conf_benchmark_property(self):
        self.assertEqual(self.api.conf_benchmark_property, self.config["benchmark"])
    
    def test_conf_benchmark_size_property(self):
        self.assertEqual(self.api.conf_benchmark_size_property, self.config["benchmark"]["size"])
    
    def test_conf_benchmark_algo_property(self):
        self.assertEqual(self.api.conf_benchmark_algo_property, self.config["benchmark"]["algo"])
    
    def test_conf_benchmark_submit_property(self):
        self.assertEqual(self.api.conf_benchmark_submit_property, self.config["benchmark"]["submit"])
    
    def test_conf_benchmark_verify_property(self):
        self.assertEqual(self.api.conf_benchmark_verify_property, self.config["benchmark"]["verify"])
    
    def test_conf_benchmark_seed_property(self):
        self.assertEqual(self.api.conf_benchmark_seed_property, self.config["benchmark"]["seed"])
    
    def test_conf_benchmark_hash_property(self):
        self.assertEqual(self.api.conf_benchmark_hash_property, self.config["benchmark"]["hash"])


if __name__ == '__main__':
    unittest.main()
