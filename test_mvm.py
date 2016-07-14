# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''


from __future__ import absolute_import

import unittest

import numpy as np
import dicetables as dt
import mvm


class TestMVM(unittest.TestCase):
    def setUp(self):
        self.TM = mvm.TableManager()
        self.HM = mvm.HistoryManager()
        self.DM = mvm.DieManager()
        self.GB = mvm.GraphBox(self.TM, self.HM, True)
    def tearDown(self):
        del self.TM
        del self.HM
        del self.DM
        del self.GB
    def test_table_manager_request_info_range(self):
        self.assertEqual(self.TM.request_info('range'), (0,0))
    def test_table_manager_request_info_mean(self):
        self.assertEqual(self.TM.request_info('mean'), 0.0)
    def test_table_manager_request_info_stddev(self):
        self.assertEqual(self.TM.request_info('stddev'), 0.0)
    def test_table_manager_request_info_text(self):
        self.TM.request_add(1, dt.Die(3))
        self.assertEqual(self.TM.request_info('text'), '1D3')
    def test_table_manager_request_info_text_one_line(self):
        self.TM.request_add(1, dt.Die(3))
        self.TM.request_add(1, dt.Die(4))
        self.assertEqual(self.TM.request_info('text_one_line'), '1D3 \\ 1D4')
    def test_table_manager_request_info_weights(self):
        self.TM.request_add(1, dt.Die(3))
        self.assertEqual(self.TM.request_info('weights_info'), 
                        '1D3\n    No weights')
    def test_table_manager_request_info_dice_list(self):
        self.TM.request_add(1, dt.Die(3))
        self.assertEqual(self.TM.request_info('dice_list'), 
                        [(dt.Die(3), 1)])
    def test_table_manager_request_info_full_text(self):
        self.assertEqual(self.TM.request_info('full_text'), '0: 1\n')
    def test_table_manager_request_info_tuple_list(self):
        self.assertEqual(self.TM.request_info('tuple_list'), [(0,1)])
    def test_table_manager_request_stats_true_zero_chance(self):
        self.assertEqual(self.TM.request_stats([1,2,3]), 
                         ('1-3', '0.0', '1', 'infinity', '0.0'))
    def test_table_manager_request_stats_tiny_tiny_chance(self):
        self.TM.request_add(1, dt.WeightedDie({1:1, 2:10**1000}))
        self.assertEqual(self.TM.request_stats([1]), 
                         ('1', '1', '1.000e+1000', '1.000e+1000', '1.000e-998'))
    def test_table_manager_request_stats_normal_case(self):
        self.assertEqual(self.TM.request_stats([0]),
                         ('0', '1', '1', '1.000', '100.0'))
    def test_table_manager_request_plot_obj_use_axes(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        plot_obj = {'text': '1D2 \\ 1D4', 'x_min': 2, 'x_max': 6,
                    'y_min': 12.5, 'y_max': 25.0,
                    'dice': [(dt.Die(2), 1), (dt.Die(4), 1)],
                    'tuple_list': [(2, 1), (3, 2), (4, 2), (5, 2), (6, 1)],
                    'pts': [(2, 3, 4, 5, 6), (12.5, 25.0, 25.0, 25.0, 12.5)]}
        self.assertEqual(self.TM.request_plot_obj(True), plot_obj)
    def test_table_manager_request_plot_obj_not_use_axes(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        plot_obj = {'text': '1D2 \\ 1D4', 'x_min': 2, 'x_max': 6,
                    'y_min': 12.5, 'y_max': 25.0,
                    'dice': [(dt.Die(2), 1), (dt.Die(4), 1)],
                    'tuple_list': [(2, 1), (3, 2), (4, 2), (5, 2), (6, 1)],
                    'pts': [(2, 12.5), (3, 25.0), (4, 25.0),
                            (5, 25.0), (6, 12.5)]}
        self.assertEqual(self.TM.request_plot_obj(False), plot_obj)
    def test_table_manager_request_reload(self):
        plot_obj = {'text': '1D2 \\ 1D4', 'x_min': 2, 'x_max': 6,
                    'y_min': 12.5, 'y_max': 25.0,
                    'dice': [(dt.Die(2), 1), (dt.Die(4), 1)],
                    'tuple_list': [(2, 1), (3, 2), (4, 2), (5, 2), (6, 1)],
                    'pts': ([2, 3, 4, 5, 6], [12.5, 25.0, 25.0, 25.0, 12.5])}
        self.TM.request_reload(plot_obj)
        self.assertEqual(self.TM.request_info('text'), '1D2\n1D4')
        self.assertEqual(self.TM.request_info('full_text'), 
                         '2: 1\n3: 2\n4: 2\n5: 2\n6: 1\n')
    def test_table_manager_request_add(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2\n1D4')
        self.assertEqual(self.TM.request_info('full_text'), 
                         '2: 1\n3: 2\n4: 2\n5: 2\n6: 1\n')
    def test_table_manager_request_remove_normal_case(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        self.TM.request_remove(1, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2')
        self.assertEqual(self.TM.request_info('tuple_list'), [(1,1), (2,1)])
    def test_table_manager_request_remove_only_removes_max_dice(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        self.TM.request_remove(1000, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2')
        self.assertEqual(self.TM.request_info('tuple_list'), [(1,1), (2,1)])
    def test_table_manager_request_remove_doesnt_remove_if_not_there(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_remove(1, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2')
        self.assertEqual(self.TM.request_info('tuple_list'), [(1,1), (2,1)])
    def test_table_manager_request_reset(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_reset()
        self.assertEqual(self.TM.request_info('text'), '')
        self.assertEqual(self.TM.request_info('tuple_list'), [(0, 1)])
        
    def test_history_manager_inits_as_empty(self):
        self.assertEqual(self.HM._history.size, 0)
    def test_history_manager_add_plot_obj(self):
        obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj)
        self.assertEqual(self.HM._history[0], obj)
    def test_history_manager_add_plot_obj__wont_add_duplicates(self):
        obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj)
        self.HM.add_plot_obj(obj)
        self.assertEqual(self.HM._history.size, 1)
        self.assertEqual(self.HM._history[0], obj)
    def test_history_manager_get_obj_returns_obj(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj)           
        self.assertEqual(self.HM.get_obj('1D2', [(1, 1), (2,1)]), obj)
    def test_history_manager_get_obj_returns_empty_if_not_pts(self):
        obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj)           
        self.assertEqual(self.HM.get_obj('', [(2, 1)]), {})    
    def test_history_manager_get_obj_returns_empty_if_not_text(self):
        obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj)           
        self.assertEqual(self.HM.get_obj('hi', [(0, 1)]), {})
    def test_hist_mgr_get_obj__mutate_returned_obj_wont_mutate_tuple_list(self):
        self.TM.request_add(1, dt.Die(2))
        self.HM.add_plot_obj(self.TM.request_plot_obj(True))       
        from_tst = self.HM.get_obj('1D2', [(1, 1), (2,1)])
        expected = {'dice': [(dt.Die(2), 1)],
                    'tuple_list': [(1, 1), (2, 1)],
                    'pts': [(1, 2), (50.0, 50.0)],
                    'text': '1D2',
                    'x_max': 2,
                    'x_min': 1,
                    'y_max': 50.0,
                    'y_min': 50.0}
        for key in from_tst.keys():
            if key in ['dice', 'tuple_list', 'pts']:
                from_tst[key].append(5)
            else:
                from_tst[key] = ''
        self.assertEqual(self.HM.get_obj('1D2', [(1, 1), (2,1)]), expected)
    def test_history_manager_get_labels_returns_empty_for_empty_hist(self):
        self.assertEqual(self.HM.get_labels(), [])
    def test_history_manager_get_labels_returns_as_expected(self):
        self.HM.add_plot_obj(self.TM.request_plot_obj(True))
        self.TM.request_add(1, dt.Die(2))
        self.HM.add_plot_obj(self.TM.request_plot_obj(True))
        self.assertEqual(self.HM.get_labels(), [('', [(0,1)]),
                                                ('1D2', [(1,1), (2,1)])])
    def test_history_manager_clear_all(self):
        self.TM.request_add(1, dt.Die(2))
        self.HM.add_plot_obj(self.TM.request_plot_obj(True))
        self.HM.clear_all()
        self.assertEqual(self.HM._history.size, 0)
    def test_history_manager_clear_selected__empty_list_does_nothing(self):
        empty_obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(empty_obj)
        self.HM.clear_selected([])
        self.assertEqual(len(self.HM._history), 1)
        self.assertEqual(self.HM._history[0], empty_obj) 
    def test_history_manager_clear_selected__not_present_does_nothing(self):
        empty_obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(empty_obj)
        self.HM.clear_selected([{'text': 'wrong'}])
        self.assertEqual(len(self.HM._history), 1)
        self.assertEqual(self.HM._history[0], empty_obj)
    def test_history_manager_clear_selected__works_as_expected(self):
        obj_1 = self.TM.request_plot_obj(True)
        self.TM.request_add(1, dt.Die(2))
        obj_2 = self.TM.request_plot_obj(True)
        self.TM.request_add(1, dt.Die(3))
        obj_3 = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(obj_1)
        self.HM.add_plot_obj(obj_2)
        self.HM.add_plot_obj(obj_3)
        self.HM.clear_selected([obj_1, obj_3])
        self.assertEqual(len(self.HM._history), 1)
        self.assertEqual(self.HM._history[0], obj_2)
    def test_history_manager_write_history(self):
        empty_obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(empty_obj)
        self.HM.write_history()
        history = np.load('numpy_history.npy')
        self.assertEqual(history.size, 1)
        self.assertEqual(history[0], empty_obj)
    def test_history_manager_read_history(self):
        empty_obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(empty_obj)
        self.HM.write_history()
        to_test = mvm.HistoryManager()
        msg = to_test.read_history()
        self.assertEqual(msg, 'ok')
        self.assertEqual(to_test._history.size, 1)
        self.assertEqual(to_test._history[0], empty_obj)
        
    def test_die_manager_inits_with_d6(self):
        self.assertEqual(self.DM._die, dt.Die(6))
    def test_die_manager_get_die(self):
        self.assertEqual(self.DM.get_die(), dt.Die(6))
    def test_die_manager_input_die__die_empty_dict(self):
        self.DM.input_die(3, 0, 0, {})
        self.assertEqual(self.DM.get_die(), dt.Die(3))
    def test_die_manager_input_die__die_dict_all_ones(self):
        self.DM.input_die(3, 0, 0, {1:1, 2:1, 3:1})
        self.assertEqual(self.DM.get_die(), dt.Die(3))
    def test_die_manager_input_die__die_dict_all_zeros(self):
        self.DM.input_die(3, 0, 0, {1:0, 2:0, 3:0})
        self.assertEqual(self.DM.get_die(), dt.Die(3))
    def test_die_manager_input_die__moddie(self):
        self.DM.input_die(3, 1, 0, {1:1, 2:1, 3:1})
        self.assertEqual(self.DM.get_die(), dt.ModDie(3,1))
    def test_die_manager_input_die__weighteddie(self):
        self.DM.input_die(6, 0, 0, {1:1, 2:0, 3:1})
        self.assertEqual(self.DM.get_die(), dt.WeightedDie({1:1, 2:0, 3:1}))
    def test_die_manager_input_die__modweighteddie(self):
        self.DM.input_die(6, 1, 0, {1:1, 2:0, 3:1})
        self.assertEqual(self.DM.get_die(),
                         dt.ModWeightedDie({1:1, 2:0, 3:1}, 1))
    def test_die_manager_input_die__strong_modweighteddie(self):
        self.DM.input_die(6, 1, 5, {1:1, 2:0, 3:1})
        self.assertEqual(self.DM.get_die(),
                         dt.StrongDie(dt.ModWeightedDie({1:1, 2:0, 3:1}, 1), 5))
    def test_die_manager_input_die__strong_d6(self):
        self.DM.input_die(7, 0, 5, {1:0, 2:0, 3:0})
        self.assertEqual(self.DM.get_die(), dt.StrongDie(dt.Die(7), 5))

    def test_graph_box_graph_it_returns_empty_list(self):
        self.assertEqual(self.GB.graph_it([]), [])
    def test_graph_box_graph_it_empty_doesnt_mutate_HM(self):
        self.GB.graph_it([])
        self.assertEqual(self.HM._history.size, 0)
    def test_graph_box_graph_it_adds_new_to_history_and_writes(self):
        self.GB.graph_it([([(0,1)], '')])
        self.assertEqual(self.HM._history.size, 1)
        self.assertEqual(self.HM._history[0], self.TM.request_plot_obj(True))
        history = np.load('numpy_history.npy')
        self.assertEqual(history.size, 1)
        self.assertEqual(history[0], self.TM.request_plot_obj(True))
    def test_graph_box_graph_it_not_add_to_HM_if_thinks_already_there(self):
        not_empty_obj = self.TM.request_plot_obj(True)
        not_empty_obj['pts'] = [(1,2,3), (4,5,6)]
        self.HM.add_plot_obj(not_empty_obj)
        self.GB.graph_it([(not_empty_obj['text'], not_empty_obj['tuple_list'])])
        self.assertEqual(self.HM._history.size, 1)
        self.assertEqual(self.HM._history[0], not_empty_obj)
    def test_graph_box_graph_it_retrieves_from_HM(self):
        empty_obj = self.TM.request_plot_obj(True)
        self.HM.add_plot_obj(empty_obj)
        self.TM.request_add(1, dt.Die(3))
        obj_list = self.GB.graph_it([('', [(0,1)])])
        self.assertEqual(obj_list, [empty_obj])
    def test_graph_box_graph_it_retrieves_according_to_use_axes(self):
        axes_obj = self.TM.request_plot_obj(True)
        pts_obj = self.TM.request_plot_obj(False)
        pts_GB = mvm.GraphBox(self.TM, mvm.HistoryManager(), False)
        self.assertNotEqual(axes_obj, pts_obj)
        self.assertEqual(pts_GB.graph_it([('', [(0,1)])]), [pts_obj])
        self.assertEqual(self.GB.graph_it([('', [(0,1)])]), [axes_obj])
   
   
   
   
if __name__ == '__main__':
    unittest.main()
