# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
# pylint: disable=too-few-public-methods, protected-access, no-member
'''tests for the longintmath.py module'''

from __future__ import absolute_import

import unittest

import numpy as np
import dicetables as dt
import dt_gui_mvm as mvm
import file_handler as fh


class DummyParent(object):
    def __init__(self):
        self.dictionary = {
            'weights_info': '1D1  W: 3\n    a roll of 1 has a weight of 3',
            'full_text': '\n'.join([str(num) for num in range(10)]),
            'mean': 12345.6,
            'stddev': 12.34,
            'range': (10, 1000),
            'text': 'text'}

    def request_info(self, key):
        return self.dictionary[key]


class TestMVM(unittest.TestCase):
    def setUp(self):
        self.TM = mvm.TableManager()
        self.DM = mvm.DataManager()
        self.GB = mvm.GraphBox(self.TM, self.DM, True)
        self.CB = mvm.ChangeBox(self.TM)
        self.SB = mvm.StatBox(self.TM)
        self.AB = mvm.AddBox(self.TM)
        self.IB = mvm.InfoBox(DummyParent())

    def tearDown(self):
        del self.TM
        del self.DM
        del self.GB
        del self.CB
        del self.SB
        del self.AB
        del self.IB

    def test_table_manager_request_info_range(self):
        self.assertEqual(self.TM.request_info('range'), (0, 0))

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
        self.assertEqual(self.TM.request_info('tuple_list'), [(0, 1)])

    def test_table_manager_request_stats_true_zero_chance(self):
        self.assertEqual(self.TM.request_stats([1, 2, 3]),
                         ('1-3', '0.0', '1', 'infinity', '0.0'))

    def test_table_manager_request_stats_tiny_tiny_chance(self):
        self.TM.request_add(1, dt.WeightedDie({1: 1, 2: 10 ** 1000}))
        self.assertEqual(self.TM.request_stats([1]),
                         ('1', '1', '1.000e+1000', '1.000e+1000', '1.000e-998'))

    def test_table_manager_request_stats_normal_case(self):
        self.assertEqual(self.TM.request_stats([0]),
                         ('0', '1', '1', '1.000', '100.0'))

    def test_table_manager_request_plot_obj(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        expected_object_data = {'text': '1D2 \\ 1D4', 'x_range': (2, 6),
                                'y_range': (12.5, 25.0),
                                'dice': [(dt.Die(2), 1), (dt.Die(4), 1)],
                                'tuple_list': [(2, 1), (3, 2), (4, 2), (5, 2), (6, 1)],
                                'graph_axes': [(2, 3, 4, 5, 6), (12.5, 25.0, 25.0, 25.0, 12.5)]}
        data_object = self.TM.request_data_obj()
        self.assertEqual(data_object.text, expected_object_data['text'])
        self.assertEqual(data_object.x_range, expected_object_data['x_range'])
        self.assertEqual(data_object.y_range, expected_object_data['y_range'])
        self.assertEqual(data_object.dice_table.get_list(), expected_object_data['dice'])
        self.assertEqual(data_object.tuple_list, expected_object_data['tuple_list'])
        self.assertEqual(data_object.graph_axes, expected_object_data['graph_axes'])

    def test_table_manager_request_reload(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        table.add_die(1, dt.Die(4))
        data_obj = fh.DiceTableData('1D2 \\ 1D4', table.frequency_all(), table.get_list(), [])
        self.TM.request_reload(data_obj)
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
        self.assertEqual(self.TM.request_info('tuple_list'), [(1, 1), (2, 1)])

    def test_table_manager_request_remove_only_removes_max_dice(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(1, dt.Die(4))
        self.TM.request_remove(1000, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2')
        self.assertEqual(self.TM.request_info('tuple_list'), [(1, 1), (2, 1)])

    def test_table_manager_request_remove_doesnt_remove_if_not_there(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_remove(1, dt.Die(4))
        self.assertEqual(self.TM.request_info('text'), '1D2')
        self.assertEqual(self.TM.request_info('tuple_list'), [(1, 1), (2, 1)])

    def test_table_manager_request_reset(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_reset()
        self.assertEqual(self.TM.request_info('text'), '')
        self.assertEqual(self.TM.request_info('tuple_list'), [(0, 1)])

    def test_data_manager_inits_as_empty(self):
        self.assertEqual(self.DM._data_array.size, 0)

    def test_data_manager_adds_plot_obj(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.assertEqual(self.DM._data_array[0], obj)

    def test_data_manager_wont_add_empty_plot_obj(self):
        self.DM.add_data_obj(fh.DiceTableData.empty_object())
        self.assertEqual(self.DM._data_array.size, 0)

    def test_data_manager_add_plot_obj__wont_add_duplicates(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.DM.add_data_obj(obj)
        self.assertEqual(self.DM._data_array.size, 1)
        self.assertEqual(self.DM._data_array[0], obj)

    def test_data_manager_get_obj_returns_obj(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.assertEqual(self.DM.retrieve_obj('1D2', [(1, 1), (2, 1)]), obj)

    def test_data_manager_get_obj_returns_empty_if_not_pts(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.assertTrue(self.DM.retrieve_obj('hi', [(1, 1), (2, 1)]).is_empty_object())

    def test_data_manager_get_obj_returns_empty_if_not_text(self):
        self.TM.request_add(1, dt.Die(2))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.assertTrue(self.DM.retrieve_obj('hi', [(1, 1), (2, 1)]).is_empty_object())

    def test_data_manager_get_labels_returns_empty_for_empty_hist(self):
        self.assertEqual(self.DM.get_labels(), [])

    def test_data_manager_get_labels_returns_as_expected(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.assertEqual(
            self.DM.get_labels(),
            [('1D1', [(1, 1)]), ('1D1 \\ 1D2', [(2, 1), (3, 1)])])

    def test_data_manager_clear_all(self):
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.DM.clear_all()
        self.assertEqual(self.DM.get_labels(), [])

    def test_data_manager_clear_selected__empty_list_does_nothing(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.DM.clear_selected([])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_data_manager_clear_selected__not_present_does_nothing(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        bad_data_obj = fh.DiceTableData('wrong', [(1, 1)], [], [])
        self.DM.clear_selected([bad_data_obj])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_data_manager_clear_selected__works_as_expected(self):
        self.TM.request_add(1, dt.Die(1))
        obj_1 = self.TM.request_data_obj()
        self.TM.request_add(1, dt.Die(2))
        obj_2 = self.TM.request_data_obj()
        self.TM.request_add(1, dt.Die(3))
        obj_3 = self.TM.request_data_obj()
        self.DM.add_data_obj(obj_1)
        self.DM.add_data_obj(obj_2)
        self.DM.add_data_obj(obj_3)
        self.DM.clear_selected([obj_1, obj_3])
        self.assertEqual(self.DM.get_labels(),
                         [(obj_2.text, obj_2.tuple_list)])

    def test_data_manager_write_save_data(self):
        self.TM.request_add(2, dt.Die(1))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.DM.write_save_data()
        save_data = np.load('save_data.npy')
        self.assertEqual(save_data[0], obj)
        self.assertEqual(save_data.size, 1)

    def test_data_manager_read_save_data(self):
        self.TM.request_add(1, dt.Die(1))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.DM.write_save_data()
        to_test = mvm.DataManager()
        msg = to_test.read_save_data()
        self.assertEqual(msg, 'ok')
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_data_manager_get_graphs_on_empty_save_data(self):
        self.assertEqual(
            self.DM.get_graphs(True),
            (
                (float('inf'), float('-inf')),
                (float('inf'), float('-inf')),
                []
            )
        )

    def test_data_manager_get_graphs_x_range(self):
        self.TM.request_add(1, dt.ModDie(1, -101))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.ModDie(1, 199))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.assertEqual(self.DM.get_graphs(True)[0], (-100, 100))

    def test_data_manager_get_graphs_y_range(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.assertEqual(self.DM.get_graphs(True)[1], (50.0, 100.0))

    def test_data_manager_get_graphs(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.assertEqual(
            self.DM.get_graphs(True),
            (
                (1, 2),
                (100.0, 100.0),
                [('1D1', [(1,), (100.0,)]), ('2D1', [(2,), (100.0,)])]
            )
        )

    def test_graph_box_graph_it_returns_empty_grapher_info(self):
        self.assertEqual(
            self.GB.get_requested_graphs([]),
            (
                (float('inf'), float('-inf')),
                (float('inf'), float('-inf')),
                []
            )
        )

    def test_graph_box_graph_it_empty_doesnt_mutate_HM(self):
        self.GB.get_requested_graphs([])
        self.assertEqual(self.DM.get_labels(), [])

    def test_graph_box_graph_it_adds_new_to_save_data(self):
        self.assertEqual(self.DM.get_labels(), [])
        self.TM.request_add(1, dt.Die(1))
        self.GB.get_requested_graphs([('1D1', [(1, 1)])])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_graph_box_graph_it_writes_new_to_file(self):
        # resetting file to empty array
        self.DM.write_save_data()
        save_data = np.load('save_data.npy')
        self.assertEqual(save_data.size, 0)
        self.TM.request_add(1, dt.Die(1))
        self.GB.get_requested_graphs([('1D1', [(1, 1)])])
        save_data = np.load('save_data.npy')
        self.assertEqual(save_data.size, 1)
        self.assertEqual(save_data[0], self.TM.request_data_obj())

    def test_graph_box_graph_it_retrieves_from_DM_not_TM(self):
        self.TM.request_add(1, dt.Die(2))
        table_manager_object = self.TM.request_data_obj()
        data_manager_object = fh.DiceTableData('1D2', [(1, 1), (2, 1)], [], [('this came from',), ('the DM',)])
        self.DM.add_data_obj(data_manager_object)
        self.assertEqual(table_manager_object, data_manager_object)
        text_pts = self.GB.get_requested_graphs([('1D2', [(1, 1), (2, 1)])])[2]
        self.assertEqual(text_pts, [('1D2', [('this came from',), ('the DM',)])])

    def test_graph_box_graph_it_retrieves_according_to_use_axes(self):
        self.TM.request_add(1, dt.Die(1))
        data_obj = self.TM.request_data_obj()
        axes_data = (data_obj.text, data_obj.graph_axes)
        pts_data = (data_obj.text, data_obj.graph_pts)
        pts_GB = mvm.GraphBox(self.TM, mvm.DataManager(), False)

        self.assertEqual(
            pts_GB.get_requested_graphs([('1D1', [(1, 1)])]),
            ((1, 1), (100.0, 100.0), [pts_data])
        )
        self.assertEqual(
            self.GB.get_requested_graphs([('1D1', [(1, 1)])]),
            ((1, 1), (100.0, 100.0), [axes_data])
        )

    def test_graph_box_clear_selected_does_nothing_with_empty_list(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.GB.clear_selected([])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_graph_box_clear_selected_does_nothing_with_nonsense_list(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.GB.clear_selected([('dur', [(1, 2)])])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_graph_box_clear_selected_works_as_expected(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.GB.clear_selected([('2D1', [(2, 1)]),
                                ('2D1 \\ 1D2', [(3, 1), (4, 1)])])
        self.assertEqual(self.DM.get_labels(), [('1D1', [(1, 1)])])

    def test_graph_box_clear_selected_writes_save_data(self):
        self.TM.request_add(1, dt.Die(1))
        expected_for_hist = self.TM.request_data_obj()
        self.DM.add_data_obj(expected_for_hist)
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.GB.clear_selected([('2D1', [(2, 1)]),
                                ('2D1 \\ 1D2', [(3, 1), (4, 1)])])
        save_data = np.load('save_data.npy')
        self.assertEqual(save_data.size, 1)
        self.assertEqual(save_data[0], expected_for_hist)

    def test_graph_box_clear_all_works_and_writes_empty_save_data(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.GB.clear_all()
        self.assertEqual(self.DM.get_labels(), [])
        self.assertEqual(np.load('save_data.npy').size, 0)

    def test_graph_box_display_returns_empty(self):
        self.assertEqual(self.GB.display(), (('', [(0, 1)]), []))

    def test_graph_box_display_returns_as_expected(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(2))
        expected = (('2D1 \\ 1D2', [(3, 1), (4, 1)]),
                    [('1D1', [(1, 1)]), ('2D1', [(2, 1)])])
        self.assertEqual(self.GB.display(), expected)

    def test_graph_box_reload_saved_dice_table_does_nothing_if_obj_not_in_hist(self):
        self.TM.request_add(1, dt.Die(1))
        self.DM.add_data_obj(self.TM.request_data_obj())
        self.TM.request_add(1, dt.Die(1))
        current_state = self.TM.request_data_obj()
        self.GB.reload_saved_dice_table('abc', [(1, 2)])
        self.assertEqual(self.TM.request_data_obj(), current_state)

    def test_graph_box_reload_saved_dice_table_works_as_expected(self):
        self.TM.request_add(1, dt.Die(1))
        obj = self.TM.request_data_obj()
        self.DM.add_data_obj(obj)
        self.TM.request_add(1, dt.Die(2))
        self.GB.reload_saved_dice_table('1D1', [(1, 1)])
        self.assertEqual(self.TM.request_data_obj(), obj)

    def test_get_die_roll_details_min_die(self):
        self.assertEqual(mvm.get_die_roll_details(dt.Die(1)), 'D1 rolls:\n  1 with frequency: 1')

    def test_get_die_roll_details_with_negative_number_as_longest(self):
        expected_text = ('(D3-2)X10 rolls:\n' +
                         '  -10 with frequency: 1\n' +
                         '    0 with frequency: 1\n' +
                         '   10 with frequency: 1')
        self.assertEqual(expected_text, mvm.get_die_roll_details(dt.StrongDie(dt.ModDie(3, -2), 10)))

    def test_get_die_roll_details_with_pos_number_as_longest(self):
        expected_text = ('D100  W:11 rolls:\n' +
                         '    1 with frequency: 1\n' +
                         '  100 with frequency: 10')
        self.assertEqual(expected_text, mvm.get_die_roll_details(dt.WeightedDie({1: 1, 100: 10})))

    def test_get_add_list_lt_size6(self):
        self.assertEqual(mvm.get_add_list(dt.Die(5)), [1, 5, 10, 50, 100, 500])

    def test_get_add_list_size6(self):
        self.assertEqual(mvm.get_add_list(dt.WeightedDie({6: 2})), [1, 5, 10, 50, 100, 500])

    def test_get_add_list_mid_size(self):
        self.assertEqual(mvm.get_add_list(dt.ModDie(25, 10)), [1, 5, 10, 50])

    def test_get_add_list_huge_size(self):
        self.assertEqual(mvm.get_add_list(dt.Die(1000000)), [])

    def test_get_add_and_remove_labels_number_is_zero_no_remove(self):
        self.assertEqual(
            mvm.get_add_and_remove_labels(dt.Die(50), 0, False),
            ['D50', '+1', '+5', '+10'])

    def test_get_add_and_remove_labels_number_is_zero_enable_remove(self):
        self.assertEqual(
            mvm.get_add_and_remove_labels(dt.Die(99), 0, True),
            ['-5', '-1', 'D99', '+1', '+5'])

    def test_get_add_and_remove_labels_with_number_not_zero(self):
        self.assertEqual(
            mvm.get_add_and_remove_labels(dt.Die(99), 5, True),
            ['-5', '-1', '5D99', '+1', '+5'])

    def test_change_box_get_dice_details_empty_table(self):
        self.assertEqual(self.CB.get_dice_details(), [])

    def test_change_box_get_dice_detail_normal(self):
        self.TM.request_add(1, dt.Die(1))
        self.TM.request_add(1, dt.Die(2))
        self.assertEqual(self.CB.get_dice_details(),
                         ['D1 rolls:\n  1 with frequency: 1',
                          'D2 rolls:\n  1 with frequency: 1\n  2 with frequency: 1'])

    def test_change_box_display_at_empty_table(self):
        self.assertEqual(self.CB.display(), [])

    def test_change_box_display_normal(self):
        self.TM.request_add(2, dt.Die(100))
        self.TM.request_add(1, dt.Die(101))
        expected = [
            (['-5', '-1', '2D100', '+1', '+5'], dt.Die(100)),
            (['-1', '1D101', '+1'], dt.Die(101))]
        self.assertEqual(self.CB.display(), expected)

    def test_change_box_add_rm_at_zero(self):
        self.CB.add_rm(0, dt.Die(5))
        self.assertEqual(self.TM.request_info('tuple_list'), [(0, 1)])
        self.assertEqual(self.TM.request_info('dice_list'), [])

    def test_change_box_add_rm_pos_number(self):
        self.CB.add_rm(2, dt.Die(1))
        self.assertEqual(self.TM.request_info('tuple_list'), [(2, 1)])
        self.assertEqual(self.TM.request_info('dice_list'), [(dt.Die(1), 2)])

    def test_change_box_add_rm_neg_number(self):
        self.CB.add_rm(2, dt.Die(1))
        self.CB.add_rm(-1, dt.Die(1))
        self.assertEqual(self.TM.request_info('tuple_list'), [(1, 1)])
        self.assertEqual(self.TM.request_info('dice_list'), [(dt.Die(1), 1)])

    def test_change_box_reset(self):
        self.CB.add_rm(1, dt.Die(2))
        self.CB.reset()
        self.assertEqual(self.TM.request_info('tuple_list'), [(0, 1)])
        self.assertEqual(self.TM.request_info('dice_list'), [])

    def test_make_die_input_die__die_empty_dict(self):
        self.assertEqual(mvm.make_die(3, 0, 0, {}), dt.Die(3))

    def test_make_die_input_die__die_dict_all_ones(self):
        self.assertEqual(mvm.make_die(3, 0, 1, {1: 1, 2: 1, 3: 1}), dt.Die(3))

    def test_make_die_input_die__die_dict_all_zeros(self):
        self.assertEqual(mvm.make_die(3, 0, 1, {1: 0, 2: 0, 3: 0}), dt.Die(3))

    def test_make_die_input_die__moddie(self):
        self.assertEqual(mvm.make_die(3, 1, 0, {1: 1, 2: 1, 3: 1}),
                         dt.ModDie(3, 1))

    def test_make_die_input_die__weighteddie(self):
        self.assertEqual(mvm.make_die(6, 0, 0, {1: 1, 2: 0, 3: 1}),
                         dt.WeightedDie({1: 1, 2: 0, 3: 1}))

    def test_make_die_input_die__modweighteddie(self):
        self.assertEqual(mvm.make_die(6, 1, 0, {1: 1, 2: 0, 3: 1}),
                         dt.ModWeightedDie({1: 1, 2: 0, 3: 1}, 1))

    def test_make_die_input_die__strong_modweighteddie(self):
        self.assertEqual(mvm.make_die(6, 1, 5, {1: 1, 2: 0, 3: 1}),
                         dt.StrongDie(dt.ModWeightedDie({1: 1, 2: 0, 3: 1}, 1), 5))

    def test_make_die_input_die__strong_d6(self):
        self.assertEqual(mvm.make_die(7, 0, 5, {1: 0, 2: 0, 3: 0}),
                         dt.StrongDie(dt.Die(7), 5))

    def test_add_box_inits_with_die_and_presets(self):
        self.assertEqual(self.AB.presets,
                         ['D2', 'D4', 'D6', 'D8', 'D10', 'D12', 'D20', 'D100'])
        self.assertEqual(self.AB._die, dt.Die(6))

    def test_add_box_get_die_details(self):
        self.assertEqual(self.AB.get_die_details(),
                         ('D6 rolls:\n  1 with frequency: 1\n  2 with frequency: 1\n' +
                          '  3 with frequency: 1\n  4 with frequency: 1\n' +
                          '  5 with frequency: 1\n  6 with frequency: 1'))

    def test_add_box_display_die(self):
        self.assertEqual(self.AB.display_die(),
                         ['D6', '+1', '+5', '+10', '+50', '+100', '+500'])

    def test_add_box_display_current(self):
        self.TM.request_add(1, dt.Die(2))
        self.TM.request_add(2, dt.Die(1))
        self.assertEqual(self.AB.display_current(), '2D1 \\ 1D2')

    def test_add_box_add(self):
        self.AB._die = dt.Die(2)
        self.AB.add(2)
        self.assertEqual(self.TM.request_info('tuple_list'),
                         [(2, 1), (3, 2), (4, 1)])
        self.assertEqual(self.TM.request_info('dice_list'), [(dt.Die(2), 2)])

    def test_add_box_set_size_resets_dictionary(self):
        self.AB._dictionary = {1: 2}
        self.AB.set_size(5)
        self.assertEqual(self.AB._dictionary, {})

    def test_add_box_set_size_works(self):
        self.AB.set_size(10)
        self.assertEqual(self.AB._die, dt.Die(10))

    def test_add_box_set_size_doesnot_affect_mod_or_multiplier(self):
        self.AB._mod = 100
        self.AB._multiplier = 50
        self.AB.set_size(2)
        self.assertEqual(self.AB._mod, 100)
        self.assertEqual(self.AB._multiplier, 50)
        self.assertEqual(self.AB._die, dt.StrongDie(dt.ModDie(2, 100), 50))

    def test_add_box_set_mod_changes_mod_and_gets_new_die(self):
        self.AB._dictionary = {1: 1, 2: 2}
        self.AB.set_mod(5)
        self.assertEqual(self.AB._die, dt.ModWeightedDie({1: 1, 2: 2}, 5))

    def test_add_box_multiplier_sets_new_multiplier_and_gets_new_die(self):
        self.AB.set_multiplier(10)
        self.assertEqual(self.AB._die, dt.StrongDie(dt.Die(6), 10))

    def test_add_box_get_weights_text_works(self):
        self.assertEqual(self.AB.get_weights_text(),
                         ['weight for 1', 'weight for 2', 'weight for 3',
                          'weight for 4', 'weight for 5', 'weight for 6'])

    def test_add_box_record_weights_empty_list(self):
        self.AB.record_weights_text([])
        self.assertEqual(self.AB._dictionary, {})

    def test_add_box_record_weights_updates_die(self):
        self.AB._size = 10
        self.AB.record_weights_text([])
        self.assertEqual(self.AB._die, dt.Die(10))

    def test_add_box_record_weights_works_as_expected(self):
        self.AB.record_weights_text([('weight for 1', 3), ('weight for 2', 1)])
        self.assertEqual(self.AB._die, dt.WeightedDie({1: 3, 2: 1}))

    def test_stat_box_display_stats_val_lt_min_range(self):
        self.TM.request_add(2, dt.Die(2))
        stat_text = ('\n    2-4 occurred 4 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 1.000 chance\n' +
                     '    or 100.0 percent')
        self.assertEqual(self.SB.display_stats(-1, 4), [stat_text, (2, 4)])

    def test_stat_box_display_stats_val_gt_max_range(self):
        self.TM.request_add(2, dt.Die(2))
        stat_text = ('\n    2-4 occurred 4 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 1.000 chance\n' +
                     '    or 100.0 percent')
        self.assertEqual(self.SB.display_stats(8, 2), [stat_text, (4, 2)])

    def test_stat_box_display_stats_val_1_val_2_equal(self):
        self.TM.request_add(2, dt.Die(2))
        stat_text = ('\n    4 occurred 1 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 4.000 chance\n' +
                     '    or 25.00 percent')
        self.assertEqual(self.SB.display_stats(4, 4), [stat_text, (4, 4)])

    def test_stat_box_display(self):
        self.TM.request_add(2, dt.Die(2))
        stat_text = ('\n    2-4 occurred 4 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 1.000 chance\n' +
                     '    or 100.0 percent')
        info_text = (
            'the range of numbers is 2-4\n' +
            'the mean is 3.0\nthe stddev is 0.7071'
        )
        self.assertEqual(self.SB.display(8, 2),
                         [info_text, stat_text, (4, 2), (2, 4)])

    def test_stat_box_display_formatting(self):
        self.TM.request_add(1, dt.WeightedDie({1: 1000, 10000: 1000}))
        stat_text = ('\n    1,000-10,000 occurred 1,000 times\n' +
                     '    out of 2,000 total combinations\n\n' +
                     '    that\'s a one in 2.000 chance\n' +
                     '    or 50.00 percent')
        info_text = (
            'the range of numbers is 1-10,000\n' +
            'the mean is 5,000.5\nthe stddev is 4999.5'
        )
        self.assertEqual(self.SB.display(1000, 10000),
                         [info_text, stat_text, (1000, 10000), (1, 10000)])

    def test_stat_box_display_empty_table(self):
        stat_text = ('\n    0 occurred 1 times\n' +
                     '    out of 1 total combinations\n\n' +
                     '    that\'s a one in 1.000 chance\n' +
                     '    or 100.0 percent')
        info_text = (
            'the range of numbers is 0-0\n' +
            'the mean is 0.0\nthe stddev is 0.0'
        )
        self.assertEqual(self.SB.display(1000, 10000),
                         [info_text, stat_text, (0, 0), (0, 0)])

    def test_info_box_display_current_page_weights_info_formatting(self):
        self.assertEqual(self.IB.display_current_page('weights_info', 2),
                         ('1D1  W: 3\n    1 has weight: 3', 1, 1))

    def test_info_box_display_current_page_full_text_formatting(self):
        self.assertEqual(self.IB.display_current_page('full_text', 2),
                         ('0\n1', 1, 5))

    def test_info_box_make_pages(self):
        self.IB.make_pages('full_text', 2)
        expected = ['0\n1', '2\n3', '4\n5', '6\n7', '8\n9']
        self.assertEqual(self.IB._pages['full_text'], expected)

    def test_info_box_make_pages_with_remainder(self):
        self.IB.make_pages('full_text', 6)
        expected = ['0\n1\n2\n3\n4\n5', '6\n7\n8\n9\n \n ']
        self.assertEqual(self.IB._pages['full_text'], expected)

    def test_info_box_display_current_page_checks_page_size_change(self):
        self.IB.make_pages('full_text', 6)
        old = self.IB._pages['full_text']
        self.IB.display_current_page('full_text', 3)
        self.assertNotEqual(old, self.IB._pages['full_text'])

    def test_info_box_display_current_page_middle_page(self):
        self.IB._current_page['full_text'] = 2
        self.assertEqual(self.IB.display_current_page('full_text', 3),
                         ('3\n4\n5', 2, 4))

    def test_info_box_display_current_page_last_page(self):
        self.IB._current_page['full_text'] = 2
        self.assertEqual(self.IB.display_current_page('full_text', 5),
                         ('5\n6\n7\n8\n9', 2, 2))

    def test_info_box_display_current_page_page_not_in_range(self):
        self.IB._current_page['full_text'] = 17
        self.assertEqual(self.IB.display_current_page('full_text', 3),
                         ('0\n1\n2', 1, 4))

    def test_info_box_display_current_page_adjusts_current_page_variable(self):
        self.IB._current_page['full_text'] = 18
        self.IB.display_current_page('full_text', 3)
        self.assertEqual(self.IB._current_page,
                         {'weights_info': 1, 'full_text': 2})

    def test_info_box_display_next_page_last_page_goes_to_first_page(self):
        self.IB._current_page['full_text'] = 4
        self.assertEqual(self.IB.display_next_page('full_text', 3),
                         ('0\n1\n2', 1, 4))

    def test_info_box_display_next_page_normal_case(self):
        self.assertEqual(self.IB.display_next_page('full_text', 3),
                         ('3\n4\n5', 2, 4))

    def test_info_box_display_previous_page_last_page_goes_to_last_page(self):
        self.assertEqual(self.IB.display_previous_page('full_text', 3),
                         ('9\n \n ', 4, 4))

    def test_info_box_display_previous_page_normal_case(self):
        self.IB._current_page['full_text'] = 3
        self.assertEqual(self.IB.display_previous_page('full_text', 3),
                         ('3\n4\n5', 2, 4))

    def test_info_box_display_chosen_page_works_as_expected(self):
        self.assertEqual(self.IB.display_chosen_page(2, 'full_text', 3),
                         ('3\n4\n5', 2, 4))

    def test_info_box_display_chosen_page_works_out_of_range(self):
        self.assertEqual(self.IB.display_chosen_page(-2, 'full_text', 3),
                         ('3\n4\n5', 2, 4))

    def test_info_box_display_paged_general_info_formatting(self):
        general_info = ('the range of numbers is 10-1,000\n' +
                        'the mean is 12,345.6\nthe stddev is 12.34')
        self.assertEqual(self.IB.display_paged(1, 1)[0], general_info)

    def test_info_box_display_paged_works_as_expected(self):
        general_info = ('the range of numbers is 10-1,000\n' +
                        'the mean is 12,345.6\nthe stddev is 12.34')
        self.assertEqual(self.IB.display_paged(1, 1),
                         [general_info, 'text', ('1D1  W: 3', 1, 2),
                          ('0', 1, 10)])

    def test_info_box_display_updates_pages(self):
        self.IB.make_pages('full_text', 2)
        self.IB._pages['full_text'][0] = 'should not\nbe this'
        self.assertEqual(self.IB.display_paged(2, 2)[3], ('0\n1', 1, 5))

    def test_info_box_display_works_as_expected(self):
        general_info = ('the range of numbers is 10-1,000\n' +
                        'the mean is 12,345.6\nthe stddev is 12.34')
        self.assertEqual(self.IB.display(),
                         [general_info, 'text',
                          '1D1  W: 3\n    1 has weight: 3',
                          '0\n1\n2\n3\n4\n5\n6\n7\n8\n9'])


if __name__ == '__main__':
    unittest.main()
