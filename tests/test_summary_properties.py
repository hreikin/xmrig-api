import unittest, json
from xmrig_api import XMRigAPI

class TestSummaryProperties(unittest.TestCase):
    """
    Tests that ensure the properties relating to the summary endpoint return the expected value. 
    These tests require a running instance of XMRig to be configured but are run against cached 
    data.
    """
    def setUp(self):
        """
        Instantiate the XMRig API client and feed it cached data to run the tests with.
        """
        self.api = XMRigAPI(ip="127.0.0.1", port="37841", access_token="SECRET")

        ##### Comment this block out to run against live data.
        with open("example-api/example-summary.json", "r") as f:
            self.mock_summary = json.load(f)
        self.api._summary_response = self.mock_summary
        #####

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


if __name__ == "__main__":
    unittest.main()
