import unittest, json
from unittest.mock import patch, MagicMock
from xmrig.api import XMRigAPI, XMRigAuthorizationError


class TestXMRigAPI(unittest.TestCase):

    def setUp(self):
        with patch.object(XMRigAPI, 'update_all_responses', return_value=True):
            self.api = XMRigAPI(ip="127.0.0.1", port="8080", access_token="fake-token", tls_enabled=False)
        
        with open("example-api/example-summary.json", "r") as f:
            self.api._summary_response = json.load(f)
        with open("example-api/example-backends.json", "r") as f:
            self.api._backends_response = json.load(f)
        with open("example-api/example-config.json", "r") as f:
            self.api._config_response = json.load(f)
                                                                                                                                                                                                                                                                                                             
    @patch("requests.get")
    def test_update_summary_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = self.api.update_summary()

        self.assertTrue(result)
        self.assertEqual(self.api._summary_response, {"key": "value"})

    @patch("requests.get")
    def test_update_summary_auth_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.update_summary()

    @patch("requests.get")
    def test_update_backends_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"backend_key": "backend_value"}
        mock_get.return_value = mock_response

        result = self.api.update_backends()

        self.assertTrue(result)
        self.assertEqual(self.api._backends_response, {"backend_key": "backend_value"})

    @patch("requests.get")
    def test_update_config_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"config_key": "config_value"}
        mock_get.return_value = mock_response

        result = self.api.update_config()

        self.assertTrue(result)
        self.assertEqual(self.api._config_response, {"config_key": "config_value"})

    @patch("requests.post")
    def test_post_config_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.post_config({"new_config_key": "new_config_value"})

        self.assertTrue(result)

    @patch("requests.post")
    def test_pause_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.pause_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_resume_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.resume_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_stop_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.stop_miner()

        self.assertTrue(result)

    def test_summary_property(self):
        """Test that the 'summary' property returns a dictionary containing 'worker_id'."""
        result = self.api.summary
        self.assertIsInstance(result, dict)
        self.assertIn("worker_id", result)

    def test_sum_id_property(self):
        """Test that the 'sum_id' property returns a string."""
        result = self.api.sum_id
        self.assertIsInstance(result, str)

    def test_sum_worker_id_property(self):
        """Test that the 'sum_worker_id' property returns a string."""
        result = self.api.sum_worker_id
        self.assertIsInstance(result, str)

    def test_sum_uptime_property(self):
        """Test that the 'sum_uptime' property returns an integer."""
        result = self.api.sum_uptime
        self.assertIsInstance(result, int)

    def test_sum_uptime_readable_property(self):
        """Test that the 'sum_uptime_readable' property returns a string."""
        result = self.api.sum_uptime_readable
        self.assertIsInstance(result, str)

    def test_sum_restricted_property(self):
        """Test that the 'sum_restricted' property returns a boolean."""
        result = self.api.sum_restricted
        self.assertIsInstance(result, bool)

    def test_sum_resources_property(self):
        """Test that the 'sum_resources' property returns a dictionary."""
        result = self.api.sum_resources
        self.assertIsInstance(result, dict)

    def test_sum_memory_usage_property(self):
        """Test that the 'sum_memory_usage' property returns a dictionary."""
        result = self.api.sum_memory_usage
        self.assertIsInstance(result, dict)

    def test_sum_free_memory_property(self):
        """Test that the 'sum_free_memory' property returns an integer."""
        result = self.api.sum_free_memory
        self.assertIsInstance(result, int)

    def test_sum_total_memory_property(self):
        """Test that the 'sum_total_memory' property returns an integer."""
        result = self.api.sum_total_memory
        self.assertIsInstance(result, int)

    def test_sum_resident_set_memory_property(self):
        """Test that the 'sum_resident_set_memory' property returns an integer."""
        result = self.api.sum_resident_set_memory
        self.assertIsInstance(result, int)

    def test_sum_load_average_property(self):
        """Test that the 'sum_load_average' property returns a list."""
        result = self.api.sum_load_average
        self.assertIsInstance(result, list)

    def test_sum_hardware_concurrency_property(self):
        """Test that the 'sum_hardware_concurrency' property returns an integer."""
        result = self.api.sum_hardware_concurrency
        self.assertIsInstance(result, int)

    def test_sum_features_property(self):
        """Test that the 'sum_features' property returns a list."""
        result = self.api.sum_features
        self.assertIsInstance(result, list)

    def test_sum_results_property(self):
        """Test that the 'sum_results' property returns a dictionary."""
        result = self.api.sum_results
        self.assertIsInstance(result, dict)

    def test_sum_current_difficulty_property(self):
        """Test that the 'sum_current_difficulty' property returns an integer."""
        result = self.api.sum_current_difficulty
        self.assertIsInstance(result, int)

    def test_sum_good_shares_property(self):
        """Test that the 'sum_good_shares' property returns an integer."""
        result = self.api.sum_good_shares
        self.assertIsInstance(result, int)

    def test_sum_total_shares_property(self):
        """Test that the 'sum_total_shares' property returns an integer."""
        result = self.api.sum_total_shares
        self.assertIsInstance(result, int)

    def test_sum_avg_time_property(self):
        """Test that the 'sum_avg_time' property returns an integer."""
        result = self.api.sum_avg_time
        self.assertIsInstance(result, int)

    def test_sum_avg_time_ms_property(self):
        """Test that the 'sum_avg_time_ms' property returns an integer."""
        result = self.api.sum_avg_time_ms
        self.assertIsInstance(result, int)

    def test_sum_total_hashes_property(self):
        """Test that the 'sum_total_hashes' property returns an integer."""
        result = self.api.sum_total_hashes
        self.assertIsInstance(result, int)

    def test_sum_best_results_property(self):
        """Test that the 'sum_best_results' property returns a list."""
        result = self.api.sum_best_results
        self.assertIsInstance(result, list)

    def test_sum_algorithm_property(self):
        """Test that the 'sum_algorithm' property returns a string."""
        result = self.api.sum_algorithm
        self.assertIsInstance(result, str)

    def test_sum_connection_property(self):
        """Test that the 'sum_connection' property returns a dictionary."""
        result = self.api.sum_connection
        self.assertIsInstance(result, dict)

    def test_sum_pool_info_property(self):
        """Test that the 'sum_pool_info' property returns a string."""
        result = self.api.sum_pool_info
        self.assertIsInstance(result, str)

    def test_sum_pool_ip_address_property(self):
        """Test that the 'sum_pool_ip_address' property returns a string."""
        result = self.api.sum_pool_ip_address
        self.assertIsInstance(result, str)

    def test_sum_pool_uptime_property(self):
        """Test that the 'sum_pool_uptime' property returns an integer."""
        result = self.api.sum_pool_uptime
        self.assertIsInstance(result, int)

    def test_sum_pool_uptime_ms_property(self):
        """Test that the 'sum_pool_uptime_ms' property returns an integer."""
        result = self.api.sum_pool_uptime_ms
        self.assertIsInstance(result, int)

    def test_sum_pool_ping_property(self):
        """Test that the 'sum_pool_ping' property returns an integer."""
        result = self.api.sum_pool_ping
        self.assertIsInstance(result, int)

    def test_sum_pool_failures_property(self):
        """Test that the 'sum_pool_failures' property returns an integer."""
        result = self.api.sum_pool_failures
        self.assertIsInstance(result, int)

    def test_sum_pool_tls_property(self):
        """Test that the 'sum_pool_tls' property returns a boolean or None."""
        result = self.api.sum_pool_tls
        self.assertIsInstance(result, (bool, type(None)))

    def test_sum_pool_tls_fingerprint_property(self):
        """Test that the 'sum_pool_tls_fingerprint' property returns a string or None."""
        result = self.api.sum_pool_tls_fingerprint
        self.assertIsInstance(result, (str, type(None)))

    def test_sum_pool_algo_property(self):
        """Test that the 'sum_pool_algo' property returns a string."""
        result = self.api.sum_pool_algo
        self.assertIsInstance(result, str)

    def test_sum_pool_diff_property(self):
        """Test that the 'sum_pool_diff' property returns an integer."""
        result = self.api.sum_pool_diff
        self.assertIsInstance(result, int)

    def test_sum_pool_accepted_jobs_property(self):
        """Test that the 'sum_pool_accepted_jobs' property returns an integer."""
        result = self.api.sum_pool_accepted_jobs
        self.assertIsInstance(result, int)

    def test_sum_pool_rejected_jobs_property(self):
        """Test that the 'sum_pool_rejected_jobs' property returns an integer."""
        result = self.api.sum_pool_rejected_jobs
        self.assertIsInstance(result, int)

    def test_sum_pool_average_time_property(self):
        """Test that the 'sum_pool_average_time' property returns an integer."""
        result = self.api.sum_pool_average_time
        self.assertIsInstance(result, int)

    def test_sum_pool_average_time_ms_property(self):
        """Test that the 'sum_pool_average_time_ms' property returns an integer."""
        result = self.api.sum_pool_average_time_ms
        self.assertIsInstance(result, int)

    def test_sum_pool_total_hashes_property(self):
        """Test that the 'sum_pool_total_hashes' property returns an integer."""
        result = self.api.sum_pool_total_hashes
        self.assertIsInstance(result, int)

    def test_sum_version_property(self):
        """Test that the 'sum_version' property returns a string."""
        result = self.api.sum_version
        self.assertIsInstance(result, str)

    def test_sum_kind_property(self):
        """Test that the 'sum_kind' property returns a string."""
        result = self.api.sum_kind
        self.assertIsInstance(result, str)

    def test_sum_ua_property(self):
        """Test that the 'sum_ua' property returns a string."""
        result = self.api.sum_ua
        self.assertIsInstance(result, str)

    def test_sum_cpu_info_property(self):
        """Test that the 'sum_cpu_info' property returns a dictionary."""
        result = self.api.sum_cpu_info
        self.assertIsInstance(result, dict)

    def test_sum_cpu_brand_property(self):
        """Test that the 'sum_cpu_brand' property returns a string."""
        result = self.api.sum_cpu_brand
        self.assertIsInstance(result, str)

    def test_sum_cpu_family_property(self):
        """Test that the 'sum_cpu_family' property returns an integer."""
        result = self.api.sum_cpu_family
        self.assertIsInstance(result, int)

    def test_sum_cpu_model_property(self):
        """Test that the 'sum_cpu_model' property returns an integer."""
        result = self.api.sum_cpu_model
        self.assertIsInstance(result, int)

    def test_sum_cpu_stepping_property(self):
        """Test that the 'sum_cpu_stepping' property returns an integer."""
        result = self.api.sum_cpu_stepping
        self.assertIsInstance(result, int)

    def test_sum_cpu_proc_info_property(self):
        """Test that the 'sum_cpu_proc_info' property returns an integer."""
        result = self.api.sum_cpu_proc_info
        self.assertIsInstance(result, int)

    def test_sum_cpu_aes_property(self):
        """Test that the 'sum_cpu_aes' property returns a boolean."""
        result = self.api.sum_cpu_aes
        self.assertIsInstance(result, bool)

    def test_sum_cpu_avx2_property(self):
        """Test that the 'sum_cpu_avx2' property returns a boolean."""
        result = self.api.sum_cpu_avx2
        self.assertIsInstance(result, bool)

    def test_sum_cpu_x64_property(self):
        """Test that the 'sum_cpu_x64' property returns a boolean."""
        result = self.api.sum_cpu_x64
        self.assertIsInstance(result, bool)

    def test_sum_cpu_64_bit_property(self):
        """Test that the 'sum_cpu_64_bit' property returns a boolean."""
        result = self.api.sum_cpu_64_bit
        self.assertIsInstance(result, bool)

    def test_sum_cpu_l2_property(self):
        """Test that the 'sum_cpu_l2' property returns an integer."""
        result = self.api.sum_cpu_l2
        self.assertIsInstance(result, int)

    def test_sum_cpu_l3_property(self):
        """Test that the 'sum_cpu_l3' property returns an integer."""
        result = self.api.sum_cpu_l3
        self.assertIsInstance(result, int)

    def test_sum_cpu_cores_property(self):
        """Test that the 'sum_cpu_cores' property returns an integer."""
        result = self.api.sum_cpu_cores
        self.assertIsInstance(result, int)

    def test_sum_cpu_threads_property(self):
        """Test that the 'sum_cpu_threads' property returns an integer."""
        result = self.api.sum_cpu_threads
        self.assertIsInstance(result, int)

    def test_sum_cpu_packages_property(self):
        """Test that the 'sum_cpu_packages' property returns an integer."""
        result = self.api.sum_cpu_packages
        self.assertIsInstance(result, int)

    def test_sum_cpu_nodes_property(self):
        """Test that the 'sum_cpu_nodes' property returns an integer."""
        result = self.api.sum_cpu_nodes
        self.assertIsInstance(result, int)

    def test_sum_cpu_backend_property(self):
        """Test that the 'sum_cpu_backend' property returns a string."""
        result = self.api.sum_cpu_backend
        self.assertIsInstance(result, str)

    def test_sum_cpu_msr_property(self):
        """Test that the 'sum_cpu_msr' property returns a string."""
        result = self.api.sum_cpu_msr
        self.assertIsInstance(result, str)

    def test_sum_cpu_assembly_property(self):
        """Test that the 'sum_cpu_assembly' property returns a string."""
        result = self.api.sum_cpu_assembly
        self.assertIsInstance(result, str)

    def test_sum_cpu_arch_property(self):
        """Test that the 'sum_cpu_arch' property returns a string."""
        result = self.api.sum_cpu_arch
        self.assertIsInstance(result, str)

    def test_sum_cpu_flags_property(self):
        """Test that the 'sum_cpu_flags' property returns a list."""
        result = self.api.sum_cpu_flags
        self.assertIsInstance(result, list)

    def test_sum_donate_level_property(self):
        """Test that the 'sum_donate_level' property returns an integer."""
        result = self.api.sum_donate_level
        self.assertIsInstance(result, int)

    def test_sum_paused_property(self):
        """Test that the 'sum_paused' property returns a boolean."""
        result = self.api.sum_paused
        self.assertIsInstance(result, bool)

    def test_sum_algorithms_property(self):
        """Test that the 'sum_algorithms' property returns a list."""
        result = self.api.sum_algorithms
        self.assertIsInstance(result, list)

    def test_sum_hashrates_property(self):
        """Test that the 'sum_hashrates' property returns a dictionary."""
        result = self.api.sum_hashrates
        self.assertIsInstance(result, dict)

    def test_sum_hashrate_10s_property(self):
        """Test that the 'sum_hashrate_10s' property returns a float or None."""
        result = self.api.sum_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_sum_hashrate_1m_property(self):
        """Test that the 'sum_hashrate_1m' property returns a float or None."""
        result = self.api.sum_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_sum_hashrate_15m_property(self):
        """Test that the 'sum_hashrate_15m' property returns a float or None."""
        result = self.api.sum_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_sum_hashrate_highest_property(self):
        """Test that the 'sum_hashrate_highest' property returns a float."""
        result = self.api.sum_hashrate_highest
        self.assertIsInstance(result, float)

    def test_sum_hugepages_property(self):
        """Test that the 'sum_hugepages' property returns a list."""
        result = self.api.sum_hugepages
        self.assertIsInstance(result, list)
    
    def test_backends_property(self):
        """Test that the 'backends' property returns a list containing dictionaries with a 'type' key."""
        result = self.api.backends
        self.assertIsInstance(result, list)
        self.assertIn("type", result[0])

    def test_enabled_backends_property(self):
        """Test that the 'enabled_backends' property returns a list."""
        result = self.api.enabled_backends
        self.assertIsInstance(result, list)

    def test_be_cpu_type_property(self):
        """Test that the 'be_cpu_type' property returns a string."""
        result = self.api.be_cpu_type
        self.assertIsInstance(result, str)

    def test_be_cpu_enabled_property(self):
        """Test that the 'be_cpu_enabled' property returns a boolean."""
        result = self.api.be_cpu_enabled
        self.assertIsInstance(result, bool)

    def test_be_cpu_algo_property(self):
        """Test that the 'be_cpu_algo' property returns a string."""
        result = self.api.be_cpu_algo
        self.assertIsInstance(result, str)

    def test_be_cpu_profile_property(self):
        """Test that the 'be_cpu_profile' property returns a string."""
        result = self.api.be_cpu_profile
        self.assertIsInstance(result, str)

    def test_be_cpu_hw_aes_property(self):
        """Test that the 'be_cpu_hw_aes' property returns a boolean."""
        result = self.api.be_cpu_hw_aes
        self.assertIsInstance(result, bool)

    def test_be_cpu_priority_property(self):
        """Test that the 'be_cpu_priority' property returns an integer."""
        result = self.api.be_cpu_priority
        self.assertIsInstance(result, int)

    def test_be_cpu_msr_property(self):
        """Test that the 'be_cpu_msr' property returns a boolean."""
        result = self.api.be_cpu_msr
        self.assertIsInstance(result, bool)

    def test_be_cpu_asm_property(self):
        """Test that the 'be_cpu_asm' property returns a string."""
        result = self.api.be_cpu_asm
        self.assertIsInstance(result, str)

    def test_be_cpu_argon2_impl_property(self):
        """Test that the 'be_cpu_argon2_impl' property returns a string."""
        result = self.api.be_cpu_argon2_impl
        self.assertIsInstance(result, str)

    def test_be_cpu_hugepages_property(self):
        """Test that the 'be_cpu_hugepages' property returns a list."""
        result = self.api.be_cpu_hugepages
        self.assertIsInstance(result, list)

    def test_be_cpu_memory_property(self):
        """Test that the 'be_cpu_memory' property returns an integer."""
        result = self.api.be_cpu_memory
        self.assertIsInstance(result, int)

    def test_be_cpu_hashrates_property(self):
        """Test that the 'be_cpu_hashrates' property returns a list."""
        result = self.api.be_cpu_hashrates
        self.assertIsInstance(result, list)

    def test_be_cpu_hashrate_10s_property(self):
        """Test that the 'be_cpu_hashrate_10s' property returns a float or None."""
        result = self.api.be_cpu_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_hashrate_1m_property(self):
        """Test that the 'be_cpu_hashrate_1m' property returns a float or None."""
        result = self.api.be_cpu_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_hashrate_15m_property(self):
        """Test that the 'be_cpu_hashrate_15m' property returns a float or None."""
        result = self.api.be_cpu_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_threads_property(self):
        """Test that the 'be_cpu_threads' property returns a list."""
        result = self.api.be_cpu_threads
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_intensity_property(self):
        """Test that the 'be_cpu_threads_intensity' property returns a list."""
        result = self.api.be_cpu_threads_intensity
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_affinity_property(self):
        """Test that the 'be_cpu_threads_affinity' property returns a list."""
        result = self.api.be_cpu_threads_affinity
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_av_property(self):
        """Test that the 'be_cpu_threads_av' property returns a list."""
        result = self.api.be_cpu_threads_av
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_10s_property(self):
        """Test that the 'be_cpu_threads_hashrates_10s' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_10s
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_1m_property(self):
        """Test that the 'be_cpu_threads_hashrates_1m' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_1m
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_15m_property(self):
        """Test that the 'be_cpu_threads_hashrates_15m' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_15m
        self.assertIsInstance(result, list)
    
    #######################################################################

    def test_be_opencl_type_property(self):
        """Test that the 'be_opencl_type' property returns a string."""
        result = self.api.be_opencl_type
        self.assertIsInstance(result, str)

    def test_be_opencl_enabled_property(self):
        """Test that the 'be_opencl_enabled' property returns a boolean."""
        result = self.api.be_opencl_enabled
        self.assertIsInstance(result, bool)

    def test_be_opencl_algo_property(self):
        """Test that the 'be_opencl_algo' property returns a string."""
        result = self.api.be_opencl_algo
        self.assertIsInstance(result, str)

    def test_be_opencl_profile_property(self):
        """Test that the 'be_opencl_profile' property returns a string."""
        result = self.api.be_opencl_profile
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_property(self):
        """Test that the 'be_opencl_platform' property returns a dictionary."""
        result = self.api.be_opencl_platform
        self.assertIsInstance(result, dict)

    def test_be_opencl_platform_index_property(self):
        """Test that the 'be_opencl_platform_index' property returns an integer."""
        result = self.api.be_opencl_platform_index
        self.assertIsInstance(result, int)

    def test_be_opencl_platform_profile_property(self):
        """Test that the 'be_opencl_platform_profile' property returns a string."""
        result = self.api.be_opencl_platform_profile
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_version_property(self):
        """Test that the 'be_opencl_platform_version' property returns a string."""
        result = self.api.be_opencl_platform_version
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_name_property(self):
        """Test that the 'be_opencl_platform_name' property returns a string."""
        result = self.api.be_opencl_platform_name
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_vendor_property(self):
        """Test that the 'be_opencl_platform_vendor' property returns a string."""
        result = self.api.be_opencl_platform_vendor
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_extensions_property(self):
        """Test that the 'be_opencl_platform_extensions' property returns a string."""
        result = self.api.be_opencl_platform_extensions
        self.assertIsInstance(result, str)

    def test_be_opencl_hashrates_property(self):
        """Test that the 'be_opencl_hashrates' property returns a list."""
        result = self.api.be_opencl_hashrates
        self.assertIsInstance(result, list)

    def test_be_opencl_hashrate_10s_property(self):
        """Test that the 'be_opencl_hashrate_10s' property returns a float or None."""
        result = self.api.be_opencl_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_hashrate_1m_property(self):
        """Test that the 'be_opencl_hashrate_1m' property returns a float or None."""
        result = self.api.be_opencl_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_hashrate_15m_property(self):
        """Test that the 'be_opencl_hashrate_15m' property returns a float or None."""
        result = self.api.be_opencl_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_property(self):
        """Test that the 'be_opencl_threads' property returns a dictionary."""
        result = self.api.be_opencl_threads
        self.assertIsInstance(result, dict)

    def test_be_opencl_threads_index_property(self):
        """Test that the 'be_opencl_threads_index' property returns an integer."""
        result = self.api.be_opencl_threads_index
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_intensity_property(self):
        """Test that the 'be_opencl_threads_intensity' property returns an integer."""
        result = self.api.be_opencl_threads_intensity
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_worksize_property(self):
        """Test that the 'be_opencl_threads_worksize' property returns an integer."""
        result = self.api.be_opencl_threads_worksize
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_amount_property(self):
        """Test that the 'be_opencl_threads_amount' property returns a list."""
        result = self.api.be_opencl_threads_amount
        self.assertIsInstance(result, list)

    def test_be_opencl_threads_unroll_property(self):
        """Test that the 'be_opencl_threads_unroll' property returns an integer."""
        result = self.api.be_opencl_threads_unroll
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_affinity_property(self):
        """Test that the 'be_opencl_threads_affinity' property returns an integer."""
        result = self.api.be_opencl_threads_affinity
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_hashrates_property(self):
        """Test that the 'be_opencl_threads_hashrates' property returns a list."""
        result = self.api.be_opencl_threads_hashrates
        self.assertIsInstance(result, list)

    def test_be_opencl_threads_hashrates_10s_property(self):
        """Test that the 'be_opencl_threads_hashrates_10s' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_hashrates_1m_property(self):
        """Test that the 'be_opencl_threads_hashrates_1m' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_hashrates_15m_property(self):
        """Test that the 'be_opencl_threads_hashrates_15m' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_board_property(self):
        """Test that the 'be_opencl_threads_board' property returns a string."""
        result = self.api.be_opencl_threads_board
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_name_property(self):
        """Test that the 'be_opencl_threads_name' property returns a string."""
        result = self.api.be_opencl_threads_name
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_bus_id_property(self):
        """Test that the 'be_opencl_threads_bus_id' property returns a string."""
        result = self.api.be_opencl_threads_bus_id
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_cu_property(self):
        """Test that the 'be_opencl_threads_cu' property returns an integer."""
        result = self.api.be_opencl_threads_cu
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_global_mem_property(self):
        """Test that the 'be_opencl_threads_global_mem' property returns an integer."""
        result = self.api.be_opencl_threads_global_mem
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_property(self):
        """Test that the 'be_opencl_threads_health' property returns a dictionary."""
        result = self.api.be_opencl_threads_health
        self.assertIsInstance(result, dict)

    def test_be_opencl_threads_health_temp_property(self):
        """Test that the 'be_opencl_threads_health_temp' property returns an integer."""
        result = self.api.be_opencl_threads_health_temp
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_power_property(self):
        """Test that the 'be_opencl_threads_health_power' property returns an integer."""
        result = self.api.be_opencl_threads_health_power
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_clock_property(self):
        """Test that the 'be_opencl_threads_health_clock' property returns an integer."""
        result = self.api.be_opencl_threads_health_clock
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_mem_clock_property(self):
        """Test that the 'be_opencl_threads_health_mem_clock' property returns an integer."""
        result = self.api.be_opencl_threads_health_mem_clock
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_rpm_property(self):
        """Test that the 'be_opencl_threads_health_rpm' property returns an integer."""
        result = self.api.be_opencl_threads_health_rpm
        self.assertIsInstance(result, int)

    #######################################################################

    def test_be_cuda_type_property(self):
        """Test that the 'be_cuda_type' property returns a string."""
        result = self.api.be_cuda_type
        self.assertIsInstance(result, str)

    def test_be_cuda_enabled_property(self):
        """Test that the 'be_cuda_enabled' property returns a boolean."""
        result = self.api.be_cuda_enabled
        self.assertIsInstance(result, bool)

    def test_be_cuda_algo_property(self):
        """Test that the 'be_cuda_algo' property returns a string."""
        result = self.api.be_cuda_algo
        self.assertIsInstance(result, str)

    def test_be_cuda_profile_property(self):
        """Test that the 'be_cuda_profile' property returns a string."""
        result = self.api.be_cuda_profile
        self.assertIsInstance(result, str)

    def test_be_cuda_versions_property(self):
        """Test that the 'be_cuda_versions' property returns a dictionary."""
        result = self.api.be_cuda_versions
        self.assertIsInstance(result, dict)

    def test_be_cuda_runtime_property(self):
        """Test that the 'be_cuda_runtime' property returns a string."""
        result = self.api.be_cuda_runtime
        self.assertIsInstance(result, str)

    def test_be_cuda_driver_property(self):
        """Test that the 'be_cuda_driver' property returns a string."""
        result = self.api.be_cuda_driver
        self.assertIsInstance(result, str)

    def test_be_cuda_plugin_property(self):
        """Test that the 'be_cuda_plugin' property returns a string."""
        result = self.api.be_cuda_plugin
        self.assertIsInstance(result, str)

    def test_be_cuda_hashrates_property(self):
        """Test that the 'be_cuda_hashrates' property returns a list."""
        result = self.api.be_cuda_hashrates
        self.assertIsInstance(result, list)

    def test_be_cuda_hashrate_10s_property(self):
        """Test that the 'be_cuda_hashrate_10s' property returns a float or None."""
        result = self.api.be_cuda_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_hashrate_1m_property(self):
        """Test that the 'be_cuda_hashrate_1m' property returns a float or None."""
        result = self.api.be_cuda_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_hashrate_15m_property(self):
        """Test that the 'be_cuda_hashrate_15m' property returns a float or None."""
        result = self.api.be_cuda_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_property(self):
        """Test that the 'be_cuda_threads' property returns a dictionary."""
        result = self.api.be_cuda_threads
        self.assertIsInstance(result, dict)

    def test_be_cuda_threads_index_property(self):
        """Test that the 'be_cuda_threads_index' property returns an integer."""
        result = self.api.be_cuda_threads_index
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_amount_property(self):
        """Test that the 'be_cuda_threads_amount' property returns an integer."""
        result = self.api.be_cuda_threads_amount
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_blocks_property(self):
        """Test that the 'be_cuda_threads_blocks' property returns an integer."""
        result = self.api.be_cuda_threads_blocks
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_bfactor_property(self):
        """Test that the 'be_cuda_threads_bfactor' property returns an integer."""
        result = self.api.be_cuda_threads_bfactor
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_bsleep_property(self):
        """Test that the 'be_cuda_threads_bsleep' property returns an integer."""
        result = self.api.be_cuda_threads_bsleep
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_affinity_property(self):
        """Test that the 'be_cuda_threads_affinity' property returns an integer."""
        result = self.api.be_cuda_threads_affinity
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_dataset_host_property(self):
        """Test that the 'be_cuda_threads_dataset_host' property returns a boolean."""
        result = self.api.be_cuda_threads_dataset_host
        self.assertIsInstance(result, bool)

    def test_be_cuda_threads_hashrates_property(self):
        """Test that the 'be_cuda_threads_hashrates' property returns a list."""
        result = self.api.be_cuda_threads_hashrates
        self.assertIsInstance(result, list)

    def test_be_cuda_threads_hashrate_10s_property(self):
        """Test that the 'be_cuda_threads_hashrate_10s' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_hashrate_1m_property(self):
        """Test that the 'be_cuda_threads_hashrate_1m' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_hashrate_15m_property(self):
        """Test that the 'be_cuda_threads_hashrate_15m' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_name_property(self):
        """Test that the 'be_cuda_threads_name' property returns a string."""
        result = self.api.be_cuda_threads_name
        self.assertIsInstance(result, str)

    def test_be_cuda_threads_bus_id_property(self):
        """Test that the 'be_cuda_threads_bus_id' property returns a string."""
        result = self.api.be_cuda_threads_bus_id
        self.assertIsInstance(result, str)

    def test_be_cuda_threads_smx_property(self):
        """Test that the 'be_cuda_threads_smx' property returns an integer."""
        result = self.api.be_cuda_threads_smx
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_arch_property(self):
        """Test that the 'be_cuda_threads_arch' property returns an integer."""
        result = self.api.be_cuda_threads_arch
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_global_mem_property(self):
        """Test that the 'be_cuda_threads_global_mem' property returns an integer."""
        result = self.api.be_cuda_threads_global_mem
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_clock_property(self):
        """Test that the 'be_cuda_threads_clock' property returns an integer."""
        result = self.api.be_cuda_threads_clock
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_memory_clock_property(self):
        """Test that the 'be_cuda_threads_memory_clock' property returns an integer."""
        result = self.api.be_cuda_threads_memory_clock
        self.assertIsInstance(result, int)
    
    def test_config_property(self):
        """Test that the 'config' property returns a dictionary containing an 'api' key."""
        result = self.api.config
        self.assertIsInstance(result, dict)
        self.assertIn("api", result)

if __name__ == "__main__":
    unittest.main()