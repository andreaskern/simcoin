from unittest import TestCase
from mock import patch
from mock import mock_open
from stats import Stats
from mock import MagicMock
import config
from textwrap import dedent
import stats
import numpy as np


class TestStats(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestStats, self).__init__(*args, **kwargs)

    def setUp(self):
        self.executor = MagicMock()
        self.stats = Stats(self.executor)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_consensus_chain_first_node_no_block(self, mock):
        node_0 = MagicMock()
        node_0.get_block_hash_silent.return_value = -1
        self.executor.first_block_height = 10
        self.executor.all_bitcoin_nodes = {'0': node_0}

        self.stats.save_consensus_chain()

        mock.assert_called_with(config.consensus_chain_csv, 'w')
        handle = mock()
        handle.write.assert_called_once_with('height;block_hash\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_consensus_chain_one_node(self, mock):
        node_0 = MagicMock()
        node_0.get_block_hash_silent.side_effect = [0, -1]
        node_0.get_block_hash.return_value = 'hash'

        self.executor.first_block_height = 10
        self.executor.all_bitcoin_nodes = {'0': node_0}

        self.stats.save_consensus_chain()

        handle = mock()
        self.assertEqual(handle.write.call_count, 2)
        self.assertEqual(handle.write.call_args_list[0][0][0], 'height;block_hash\n')
        self.assertEqual(handle.write.call_args_list[1][0][0], '10;hash\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_consensus_chain_multiple_nodes(self, mock):
        node_0 = MagicMock()
        node_0.get_block_hash_silent.side_effect = [0, 0, 1]
        node_0.get_block_hash.side_effect = ['hash1', 'hash2']
        node_1 = MagicMock()
        node_1.get_block_hash_silent.side_effect = [0, 0, 1]
        node_1.get_block_hash.side_effect = ['hash1', 'hash2']

        self.executor.first_block_height = 10
        self.executor.all_bitcoin_nodes = {'0': node_0, '1': node_1}

        self.stats.save_consensus_chain()

        handle = mock()
        lines = [line[0][0] for line in handle.write.call_args_list]
        self.assertEqual(len(lines), 3)
        self.assertTrue('10;hash1\n' in lines)
        self.assertTrue('11;hash2\n' in lines)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_consensus_chain_one_node_trailing_back(self, mock):
        node_0 = MagicMock()
        node_0.get_block_hash_silent.side_effect = [0, 0]
        node_0.get_block_hash.side_effect = ['hash1', 'hash2']
        node_1 = MagicMock()
        node_1.get_block_hash_silent.side_effect = [0, 1]
        node_1.get_block_hash.side_effect = ['hash1']

        self.executor.first_block_height = 10
        self.executor.all_bitcoin_nodes = {'0': node_0, '1': node_1}

        self.stats.save_consensus_chain()

        handle = mock()
        lines = [line[0][0] for line in handle.write.call_args_list]
        self.assertEqual(len(lines), 2)
        self.assertTrue('10;hash1\n' in lines)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_chains(self, mock):
        self.stats.save_chains()

        mock.assert_called_with(config.chains_csv, 'w')
        handle = mock()
        handle.write.assert_called_once_with('node;block_hashes\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_chains_with_nodes(self, mock):
        node_0 = MagicMock()
        node_0.name = 'node-0'
        node_0.get_block_count.return_value = 6
        node_0.get_block_hash.side_effect = ['hash1', 'hash2']
        node_1 = MagicMock()
        node_1.name = 'node-1'
        node_1.get_block_count.return_value = 7
        node_1.get_block_hash.side_effect = ['hash11', 'hash22', 'hash33']
        self.executor.first_block_height = 5
        self.executor.all_bitcoin_nodes = {'0': node_0, '1': node_1}

        self.stats.save_chains()

        handle = mock()
        lines = [line[0][0] for line in handle.write.call_args_list]
        self.assertEqual(len(lines), 3)
        self.assertTrue('node-1;hash11;hash22;hash33\n' in lines)
        self.assertTrue('node-0;hash1;hash2\n' in lines)

    @patch('builtins.open', new_callable=mock_open)
    @patch('bash.check_output_without_log')
    @patch('stats.prefix_log')
    def test_aggregate_logs(self, m_prefix, m_bash, m_open):
        node_0 = MagicMock()
        self.executor.all_nodes = {'0': node_0}
        m_prefix.return_value = ['1', '2']

        self.stats.aggregate_logs()

        self.assertEqual(m_open.call_args[0][0], config.aggregated_log)
        handle = m_open()
        self.assertEqual(handle.write.call_args[0][0], '1\n2\n')

        self.assertEqual(m_bash.call_count, 3)

    @patch('builtins.open', new_callable=mock_open)
    @patch('bash.check_output_without_log')
    @patch('stats.prefix_log')
    def test_aggregate_logs_two_nodes(self, m_prefix, m_bash, m_open):
        node_0 = MagicMock()
        node_1 = MagicMock()
        self.executor.all_nodes = {'0': node_0, '1': node_1}
        m_prefix.side_effect = [['1', '2'], ['11', '22']]

        self.stats.aggregate_logs()

        handle = m_open()
        contents = [line[0][0] for line in handle.write.call_args_list]
        self.assertEqual(len(contents), 2)
        self.assertTrue('1\n2\n' in contents)
        self.assertTrue('11\n22\n' in contents)

        self.assertEqual(m_bash.call_count, 4)

    def test_update_tx_csv(self):
        data = dedent("""
            node;block
            node-0;hash1
            node-1;hash2
        """).strip()

        with patch('builtins.open', mock_open(read_data=data)) as m_open:
            node_0 = MagicMock()
            self.executor.all_bitcoin_nodes = {'node-0': node_0, 'node-1': node_0}
            self.stats.tx_propagation = MagicMock()
            self.stats.tx_propagation.return_value = {'values': np.array([1]), 'len': 1, 'median': 11, 'std': 22}

            self.stats.update_tx_csv()

            m_open.assert_called_with(config.tx_csv, 'r+')
            self.assertTrue(m_open.called)
            handle = m_open()
            self.assertEqual(handle.write.call_count, 3)
            self.assertEqual(handle.write.call_args_list[1][0][0], 'node-0;hash1;1;11;22\n')
            self.assertEqual(handle.write.call_args_list[2][0][0], 'node-1;hash2;1;11;22\n')

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.loads')
    @patch('stats.tips_statistics')
    def test_node_stats(self, m_calc_tips_stats, _, m_open):
        node_0 = MagicMock()
        node_0.name = 'name'
        node_0.mined_blocks = 45
        self.executor.all_bitcoin_nodes = {'0': node_0}
        m_calc_tips_stats.return_value = {'total': {'len': 1, 'median': 2, 'std': 3},
                                          'valid-headers': {'len': 11, 'median': 22, 'std': 33},
                                          'valid-fork': {'len': 111, 'median': 222, 'std': 333},
                                          'headers-only': {'len': 1111, 'median': 2222, 'std': 3333,}}
        self.stats.node_stats()

        m_open.assert_called_with(config.nodes_csv, 'w')
        handle = m_open()
        self.assertEqual(handle.write.call_count, 2)
        self.assertEqual(handle.write.call_args_list[0][0][0],
                         'name;'
                         'total_tips;total_tips_median_branchlen;tips_std_branchlen;'
                         'valid_headers;valid_headers_median_branchlen;valid_headers_std_branchlen;'
                         'valid_fork;valid_fork_median_branchlen;valid_fork_std_branchlen;'
                         'headers_only;headers_only_median_branchlen;headers_only_std_branchlen;\n')
        self.assertEqual(handle.write.call_args_list[1][0][0], 'name;1;2;3;11;22;33;111;222;333;1111;2222;3333\n')

    def test_prefix_log_no_changes(self):
        lines = ['2017-07-05 14:33:35.324000 test', '2017-07-05 14:33:35.324000 test']
        received = stats.prefix_log(lines, 'node-0')

        expected = ['2017-07-05 14:33:35.324000 node-0 test', '2017-07-05 14:33:35.324000 node-0 test']
        self.assertEqual(received, expected)

    def test_prefix_log(self):
        lines = ['2017-07-05 14:33:35.324000 test', 'test']
        received = stats.prefix_log(lines, 'node-0')

        expected = ['2017-07-05 14:33:35.324000 node-0 test', '2017-07-05 14:33:35.324000 node-0 test']
        self.assertEqual(received, expected)

    @patch('stats.calc_median_std')
    def test_tips_statistics_unknown_status(self, mock):
        tips = [{'status': 'unknown'}]
        with self.assertRaises(Exception) as context:
            stats.tips_statistics(tips)

        self.assertTrue('Unknown tip type=unknown' in str(context.exception))

    @patch('stats.calc_median_std')
    def test_tips_statistics_both(self, mock):
        tips = [{'status': 'active'}, {'status': 'valid-headers', 'branchlen': 2},
                {'status': 'valid-fork', 'branchlen': 3}, {'status': 'headers-only', 'branchlen': 4}]
        stats.tips_statistics(tips)

        self.assertEqual(mock.call_args_list[0][0][0], [2])
        self.assertEqual(mock.call_args_list[1][0][0], [3])
        self.assertEqual(mock.call_args_list[2][0][0], [4])
        self.assertTrue(item in [2, 3, 4] for item in mock.call_args_list[3][0][0])

    @patch('stats.calc_median_std')
    def test_block_propagation(self, mock):
        node_1 = MagicMock()
        node_1.block_is_new_tip.return_value = 11
        node_1.name = 'node_1'
        node_2 = MagicMock()
        node_2.block_is_new_tip.return_value = -1
        node_2.name = 'node_2'

        self.executor.all_bitcoin_nodes = {'node_1': node_1, 'node_2': node_2}

        self.stats.block_propagation('node_0', 'hash', 1)

        self.assertEqual(mock.call_args[0][0], np.array([10]))

    @patch('stats.calc_median_std')
    def test_tx_propagation(self, mock):
        node_1 = MagicMock()
        node_1.tx_received.return_value = 11
        node_1.name = 'node_1'
        node_2 = MagicMock()
        node_2.tx_received.return_value = -1
        node_2.name = 'node_2'

        self.executor.all_bitcoin_nodes = {'node_1': node_1, 'node_2': node_2}

        self.stats.tx_propagation('node-0', 'hash0', 1)

        self.assertEqual(mock.call_args[0][0], np.array([10]))

    def test_calc_median_std_no_values(self):
        array = np.array([])
        statistics = stats.calc_median_std(array)

        self.assertTrue(np.isnan(statistics['median']))
        self.assertTrue(np.isnan(statistics['std']))
        self.assertEqual(statistics['len'], 0)
        self.assertTrue((statistics['values'] == array).all())

    def test_calc_median_std(self):
        array = np.array([1, 2])
        statistics = stats.calc_median_std(array)

        self.assertEqual(statistics['median'], 1.5)
        self.assertEqual(statistics['std'], 0.5)
        self.assertEqual(statistics['len'], 2)
        self.assertTrue((statistics['values'] == array).all())