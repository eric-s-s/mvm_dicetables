# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
from __future__ import absolute_import



import os
import unittest
import dicetables as dt
import numpy as np

import file_handler as fh


def create_dice_table_data(table):
    text = str(table).replace('\n', ' \\ ')
    graph_data = dt.graph_pts(table)
    tuple_list = table.frequency_all()
    dice_list = table.get_list()
    return fh.DiceTableData(text, tuple_list, dice_list, graph_data)


def create_plot_object_old(table):
    '''converts the table into a PlotObject'''
    new_object = {}
    new_object['text'] = str(table).replace('\n', ' \\ ')
    graph_pts = dt.graph_pts(table, axes=False)
    y_vals = [pts[1] for pts in graph_pts]
    new_object['x_range'] = table.values_range()
    new_object['y_range'] = (min(y_vals), max(y_vals))
    new_object['pts'] = graph_pts
    new_object['tuple_list'] = table.frequency_all()
    new_object['dice'] = table.get_list()
    return new_object


class Testfh(unittest.TestCase):
    def assertArrayEqual(self, nparray_1, nparray_2):
        self.assertTrue((nparray_1.tolist() == nparray_2.tolist() and
                         nparray_1.dtype == nparray_2.dtype))

    def test_dice_table_data_get_graph_axes_empty_table(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertEqual([(0,), (100.0,)], data_obj.get_graph_axes())
    def test_dice_table_data_get_graph_axes_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual([(1, 2), (50.0, 50.0)], data_obj.get_graph_axes())
    def test_dice_table_data_get_graph_pts_empty_table(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertEqual([(0, 100.0)], data_obj.get_graph_pts())
    def test_dice_table_data_get_graph_pts(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual([(1, 50.0), (2, 50.0)], data_obj.get_graph_pts())
    def test_dice_table_data_get_x_range(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual((2, 4), data_obj.get_x_range())
    def test_dice_table_data_get_y_range(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual((25.0, 50.0), data_obj.get_y_range())
    def test_dice_tabel_data_get_tuple_list(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertEqual([(0, 1)], data_obj.get_tuple_list())
    def test_dice_table_data_get_tuple_list_does_not_mutate_original_list(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        new_tuple_list = data_obj.get_tuple_list()
        new_tuple_list[0] = 5
        self.assertEqual([(0, 1)], data_obj.get_tuple_list())
    def test_dice_table_data_get_text_on_empty_obj(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertEqual('', data_obj.get_text())
    def test_dice_table_data_get_text(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(1))
        table.add_die(3, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual('2D1 \\ 3D2', data_obj.get_text())
    def test_dice_table_data_get_dice_table(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        data_obj_table = data_obj.get_dice_table()
        self.assertNotEqual(data_obj_table, table)
        self.assertEqual(data_obj_table.frequency_all(), table.frequency_all())
        self.assertEqual(data_obj_table.get_list(), table.get_list())
    def test_dice_table_data_get_copy(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        new_data_obj = data_obj.get_copy()
        self.assertEqual(data_obj.get_text(), new_data_obj.get_text())
        self.assertEqual(data_obj.get_graph_axes(), new_data_obj.get_graph_axes())
        self.assertEqual(data_obj.get_tuple_list(), new_data_obj.get_tuple_list())
        self.assertEqual(data_obj.get_dice_table().get_list(), new_data_obj.get_dice_table().get_list())
    def test_dice_table_data_equality_test_true(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertTrue(data_obj == data_obj.get_copy())
    def test_dice_table_data_equality_test_false_by_text(self):
        table_1 = dt.DiceTable()
        table_1.add_die(1, dt.WeightedDie({1: 1, 2: 1}))
        data_obj = create_dice_table_data(table_1)
        table_2 = dt.DiceTable()
        table_2.add_die(1, dt.Die(2))
        other_data_obj = create_dice_table_data(table_2)
        self.assertEqual(data_obj.get_tuple_list(), other_data_obj.get_tuple_list())
        self.assertFalse(data_obj == other_data_obj)
    def test_dice_table_data_equality_test_false_by_tuple_list(self):
        table_1 = dt.DiceTable()
        table_1.add_die(1, dt.WeightedDie({1: 5, 2: 1}))
        data_obj = create_dice_table_data(table_1)
        table_2 = dt.DiceTable()
        table_2.add_die(1, dt.WeightedDie({1: 1, 2: 5}))
        other_data_obj = create_dice_table_data(table_2)
        self.assertEqual(data_obj.get_text(), other_data_obj.get_text())
        self.assertFalse(data_obj == other_data_obj)
    def test_dice_table_data_not_equal(self):
        table = dt.DiceTable()
        data_obj = create_dice_table_data(table)
        table.add_die(2, dt.Die(2))
        other_data_obj = create_dice_table_data(table)
        self.assertTrue(data_obj != other_data_obj)
    def test_dice_table_data_is_empty_object_true(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertTrue(data_obj.is_empty_object())
    def test_dice_table_data_is_empty_object_false(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertFalse(data_obj.is_empty_object())
    def test_dice_table_data_match_by_text_and_tuples_true(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertTrue(data_obj.match_by_text_and_tuples('1D2', [(1, 1), (2, 1)]))
    def test_dice_table_data_match_by_text_and_tuples_false_by_text(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertFalse(data_obj.match_by_text_and_tuples('2D2', [(1, 1), (2, 1)]))
    def test_dice_table_data_match_by_text_and_tuples_false_by_tuples(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertFalse(data_obj.match_by_text_and_tuples('1D2', [(1, 2), (2, 2)]))
    def test_dice_table_data_verify_all_data_empty_object(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        self.assertEqual(data_obj.verify_all_data(), '')
    def test_dice_table_data_verify_all_data_no_errors(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_dice_table_data(table)
        self.assertEqual(data_obj.verify_all_data(), '')
    def test_dice_table_data_verify_all_data_text_errors(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        data_obj._text = 2
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid text value')
    def test_dice_table_data_verify_all_data_tuple_errors(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        data_obj._tuple_list = 1
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid tuple list')
    def test_dice_table_data_verify_all_data_dice_list_errors(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        data_obj._dice_list = 1
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid dice list')
    def test_dice_table_data_verify_all_data_graph_axes_errors(self):
        data_obj = create_dice_table_data(dt.DiceTable())
        data_obj._graph_axes = 'a'
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid graph values')

    def test_python_2_to_3_control_for_longs_and_int_no_int(self):
        self.assertEqual((float, str), fh.python_2_to_3_control_for_longs_and_int((float, str)))
    def test_python_2_to_3_control_for_longs_and_int_with_int(self):
        try:
            self.assertEqual((int, float, long), fh.python_2_to_3_control_for_longs_and_int((int, float)))
        except NameError:
            self.assertEqual((int, float), fh.python_2_to_3_control_for_longs_and_int((int, float)))

    def test_check_datum_and_return_error_message_no_error_one_type(self):
        message = fh.check_datum_for_data_types(1., (float,), 'error')
        self.assertEqual(message, '')
    def test_check_datum_and_return_error_message_no_error_multi_type(self):
        message = fh.check_datum_for_data_types(1., (float, str, list), 'error')
        self.assertEqual(message, '')
    def test_check_datum_and_return_error_message_error(self):
        message = fh.check_datum_for_data_types(1., (str, list), 'error')
        self.assertEqual(message, 'error')
    def test_check_datum_edge_case_of_int_and_long(self):
        message = fh.check_datum_for_data_types(10 ** 1000, (int,), 'error')
        self.assertEqual(message, '')

    def test_check_list_for_data_type_no_error_one_type(self):
        message = fh.check_list_for_data_types((1., 2., 3.), (float,), 'error')
        self.assertEqual(message, '')
    def test_check_list_for_data_type_no_error_many_types_data(self):
        message = fh.check_list_for_data_types((1., 'hi', [1, 2]), (float, list, str), 'error')
        self.assertEqual(message, '')
    def test_check_list_for_data_type_no_error_many_data_types(self):
        message = fh.check_list_for_data_types(('a', 'b', 'c'), (float, list, str, tuple), 'error')
        self.assertEqual(message, '')
    def test_check_list_for_data_type_no_error_empty_list(self):
        message = fh.check_list_for_data_types([], (int, ), 'error')
        self.assertEqual(message, '')
    def test_check_list_for_data_type_with_error_one_type(self):
        message = fh.check_list_for_data_types((1., 2., 3.), (str,), 'error')
        self.assertEqual(message, 'error')
    def test_check_list_for_data_type_with_error_many_types(self):
        message = fh.check_list_for_data_types((1., 2., 'a'), (float, list), 'error')
        self.assertEqual(message, 'error')
    def test_check_list_for_data_type_edge_case_int_and_long(self):
        message = fh.check_list_for_data_types((1, 10 ** 1000), (int,), 'error')
        self.assertEqual(message, '')
    def test_check_list_for_data_type_returns_error_when_not_passed_iterable(self):
        message = fh.check_list_for_data_types(1, (int, ), 'error')
        self.assertEqual(message, 'error')

    def test_check_tuple_list_for_data_types_by_tuple_no_error(self):
        tuple_list = [(1, 2), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_no_error_multi_types(self):
        tuple_list = [(1, 2), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_no_error_multi_types_different_elements(self):
        tuple_list = [(1, 3., 10**1000), ([], 'hi', 'hi'), (2., 5., 0.23)]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_no_error_empty_list(self):
        empty_list = []
        empty_tuple_list = [()]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_tuple_list_for_data_types_by_tuple(empty_list, data_types_list, 'error'))
        self.assertEqual('', fh.check_tuple_list_for_data_types_by_tuple(empty_tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_one_error(self):
        tuple_list = [(1, 'oops'), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_multi_errors_one_tuple(self):
        tuple_list = [(1, 'oops'), ('a', 'hi'), (2., 'fuck')]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_multi_errors_multi_tuple(self):
        tuple_list = [(1, 'oops'), ('a', 2.), (2., 'fuck')]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_by_tuple_error_when_not_tuple_list(self):
        message = fh.check_tuple_list_for_data_types_by_tuple([1, 2], [(int, )], 'error')
        self.assertEqual(message, 'error')
        self.assertEqual('error', fh.check_tuple_list_for_data_types_by_tuple(1, [(int, )], 'error'))

    def test_check_tuple_list_for_data_types_within_each_tuple_no_error(self):
        tuple_list = [(1, 'a', 2.), (2, 'hi', 5.)]
        data_types_list = [(int,), (str,), (float,)]
        self.assertEqual('', fh.check_tuple_list_for_data_types_within_each_tuple(tuple_list, data_types_list, 'error'))
    def test_check_tuple_list_for_data_types_within_each_tuple_with_error(self):
        tuple_list = [(1, 'a', 'oops'), (2, 'hi', 5.)]
        data_types_list = [(int,), (str,), (float,)]
        self.assertEqual('error', fh.check_tuple_list_for_data_types_within_each_tuple(tuple_list, data_types_list,
                                                                                       'error'))
    def test_check_tuple_list_for_data_types_within_each_tuple_error_when_not_tuple_list(self):
        message = fh.check_tuple_list_for_data_types_within_each_tuple([1, 2], [(int, )], 'error')
        self.assertEqual(message, 'error')
        self.assertEqual('error', fh.check_tuple_list_for_data_types_within_each_tuple(1, [(int, )], 'error'))

    def test_check_data_objects_in_save_data_returns_first_error(self):
        obj1 = create_dice_table_data(dt.DiceTable())
        obj2 = create_dice_table_data(dt.DiceTable())
        obj1._tuple_list = [(2.0, 1)]
        obj2._text = 2
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_data_objects_in_save_data(save_data_array), 'error: invalid tuple list')
    def test_check_data_objects_in_save_data_finds_bad_objects(self):
        obj1 = []
        obj2 = create_dice_table_data(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_data_objects_in_save_data(save_data_array), 'error: wrong object in array')
    def test_check_data_objects_in_save_data_no_errors(self):
        obj1 = create_dice_table_data(dt.DiceTable())
        obj2 = create_dice_table_data(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_data_objects_in_save_data(save_data_array), '')
    def test_check_data_objects_in_save_data_empty_array(self):
        self.assertEqual(fh.check_data_objects_in_save_data(np.array([])), '')

    def test_check_data_array_is_correct_type_error(self):
        self.assertEqual(fh.check_data_array_is_correct_type(np.array([])), 'error: wrong array type')
    def test_check_data_array_is_correct_type_no_error(self):
        self.assertEqual(fh.check_data_array_is_correct_type(np.array([dt.DiceTable()])), '')

    def test_check_save_data_array_empty_array_correct_type(self):
        self.assertEqual(fh.check_save_data_array(np.array([], dtype=object)), 'ok: no saved data')
    def test_check_save_data_array_non_empty_array_correct_type(self):
        obj1 = create_dice_table_data(dt.DiceTable())
        obj2 = create_dice_table_data(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_save_data_array(save_data_array), 'ok')
    def test_check_save_data_array_wrong_array_type(self):
        self.assertEqual(fh.check_save_data_array(np.array([1, 2, 3])), 'error: wrong array type')
    def test_check_save_data_array_bad_array_data(self):
        self.assertEqual(fh.check_save_data_array(np.array([dt.DiceTable()])), 'error: wrong object in array')

    def test_read_message_and_return_original_or_empty_array_return_original(self):
        msg_and_obj = fh.read_message_and_return_original_or_empty_array('ok', 1)
        self.assertEqual(msg_and_obj, ('ok', 1))
    def test_read_message_and_return_original_or_empty_array_return_empty_array(self):
        msg, obj = fh.read_message_and_return_original_or_empty_array('error: omfg what did you do???', 1)
        self.assertEqual(msg, 'error: omfg what did you do???')
        self.assertArrayEqual(obj, np.array([], dtype=object))





















    def test_check_data_empty_table(self):
        table = dt.DiceTable()
        obj = create_plot_object_old(table)
        self.assertEqual(fh.check_data_old(obj), 'ok')
    def check_data_not_a_dictionary(self):
        self.assertEqual(fh.check_data_old('a'), 'error: not a dict')
    def test_check_data_missing_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object_old(table)
        del obj['pts']
        self.assertEqual(fh.check_data_old(obj), 'error: missing key')
    def test_check_data_incorrect_type_at_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object_old(table)
        obj['pts'] = 'a'
        #for difference in python2 and 3
        self.assertIn(fh.check_data_old(obj), ("error: pts not <type 'list'>",
                                           "error: pts not <class 'list'>"))
    def test_check_data_incorrect_x_range(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['x_range'] = (1.0, 2)
        self.assertEqual(fh.check_data_old(obj), 'error: incorrect x_range')
    def test_check_data_incorrect_y_range(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['y_range'] = (1.0, 2)
        self.assertEqual(fh.check_data_old(obj), 'error: incorrect y_range')
    def test_check_data_incorrect_freq_in_tuple_list(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['tuple_list'] = [(1.0, 2)]
        self.assertEqual(fh.check_data_old(obj), 'error: corrupted "tuple_list"')
    def test_check_data_long_in_freq_in_tuple_list_ok(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2)]
        self.assertEqual(fh.check_data_old(obj), 'ok')
    def test_check_data_incorrect_val_in_tuple_list(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2.0)]
        self.assertEqual(fh.check_data_old(obj), 'error: corrupted "tuple_list"')
    def test_check_data_incorrect_num_in_dice(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['dice'] = [(dt.Die(6), 2.0)]
        self.assertEqual(fh.check_data_old(obj), 'error: corrupted dice list')
    def test_check_data_incorrect_die_in_dice(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['dice'] = [('a', 2.)]
        self.assertEqual(fh.check_data_old(obj), 'error: corrupted dice list')
    def test_check_data_reports_multiple_errors(self):
        obj = create_plot_object_old(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2.0)]
        obj['dice'] = [('a', 2.)]
        self.assertEqual(
            fh.check_data_old(obj),
            'error: corrupted "tuple_list" corrupted dice list')
    def test_check_data_all_die_types_pass(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(4))
        table.add_die(1, dt.ModDie(4, 2))
        table.add_die(1, dt.WeightedDie({1:2}))
        table.add_die(1, dt.ModWeightedDie({1:2}, 3))
        table.add_die(1, dt.StrongDie(dt.Die(3), 3))
        obj = create_plot_object_old(table)
        self.assertEqual(fh.check_data_old(obj), 'ok')

    def test_check_history_breaks_at_first_error(self):
        obj1 = create_plot_object_old(dt.DiceTable())
        obj2 = create_plot_object_old(dt.DiceTable())
        obj1['tuple_list'] = [(2.0, 1)]
        del obj2['pts']
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history_old(hist),
                         'error: corrupted "tuple_list"')
    def test_check_history_ok_for_valid_hist(self):
        obj1 = create_plot_object_old(dt.DiceTable())
        obj2 = create_plot_object_old(dt.DiceTable())
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history_old(hist), 'ok')

    def test_read_write_hist_np_work_ok_for_normal_case(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object_old(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object_old(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np_old(hist)
        msg, new_hist = fh.read_history_np_old()
        self.assertEqual(msg, 'ok')
        self.assertArrayEqual(hist, new_hist)
    def test_read_np_returns_error_and_empty_if_check_hist_has_error(self):
        fh.write_history_np_old(np.array([1, 2, 3]))
        msg, hist = fh.read_history_np_old()
        self.assertEqual(msg, 'error: not a dict')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_hist_empty_and_wrong_type(self):
        fh.write_history_np_old(np.array([]))
        msg, hist = fh.read_history_np_old()
        self.assertEqual(msg, 'error: wrong array type')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_ok_and_empty_if_hist_empty_and_correct_type(self):
        fh.write_history_np_old(np.array([], dtype=object))
        msg, hist = fh.read_history_np_old()
        self.assertEqual(msg, 'ok: no history')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_no_file(self):
        os.remove('numpy_history.npy')
        msg, hist = fh.read_history_np_old()
        self.assertEqual(msg, 'error: no file')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_corrupted_file(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object_old(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object_old(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np_old(hist)
        #for differences between python2 and 3
        try:
            with open('numpy_history.npy', 'r') as f:
                to_write = f.read()[:-1]
        except UnicodeDecodeError:
            with open('numpy_history.npy', 'r', errors='ignore') as f:
                to_write = f.read()[:-1]
        with open('numpy_history.npy', 'w') as f:
            f.write(to_write)
        msg, hist = fh.read_history_np_old()
        self.assertEqual(msg, 'error: file corrupted')
        self.assertArrayEqual(hist, np.array([], dtype=object))

if __name__ == '__main__':
    unittest.main()
