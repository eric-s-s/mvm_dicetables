# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
from __future__ import absolute_import



import os
import unittest
import dicetables as dt
import numpy as np

import filehandler as fh


def create_saved_dice_table(table):
    text = str(table).replace('\n', ' \\ ')
    graph_data = dt.graph_pts(table)
    tuple_list = table.frequency_all()
    dice_list = table.get_list()
    return fh.SavedDiceTable(text, tuple_list, dice_list, graph_data)


class Testfh(unittest.TestCase):
    def assertArrayEqual(self, nparray_1, nparray_2):
        self.assertTrue((nparray_1.tolist() == nparray_2.tolist() and
                         nparray_1.dtype == nparray_2.dtype))

    def test_saved_dice_table_get_graph_axes_empty_table(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertEqual([(0,), (100.0,)], data_obj.graph_axes)
    def test_saved_dice_table_get_graph_axes_non_empty_table(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual([(1, 2), (50.0, 50.0)], data_obj.graph_axes)
    def test_saved_dice_table_get_graph_pts_empty_table(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertEqual([(0, 100.0)], data_obj.graph_pts)
    def test_saved_dice_table_get_graph_pts(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual([(1, 50.0), (2, 50.0)], data_obj.graph_pts)
    def test_saved_dice_table_get_x_range(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual((2, 4), data_obj.x_range)
    def test_saved_dice_table_get_y_range(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual((25.0, 50.0), data_obj.y_range)
    def test_dice_tabel_data_get_tuple_list(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertEqual([(0, 1)], data_obj.tuple_list)
    def test_saved_dice_table_get_tuple_list_does_not_mutate_original_list(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        new_tuple_list = data_obj.tuple_list
        new_tuple_list[0] = 5
        self.assertEqual([(0, 1)], data_obj.tuple_list)
    def test_saved_dice_table_get_text_on_empty_obj(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertEqual('', data_obj.text)
    def test_saved_dice_table_get_text(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(1))
        table.add_die(3, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual('2D1 \\ 3D2', data_obj.text)
    def test_saved_dice_table_get_dice_table(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        data_obj_table = data_obj.dice_table
        self.assertNotEqual(data_obj_table, table)
        self.assertEqual(data_obj_table.frequency_all(), table.frequency_all())
        self.assertEqual(data_obj_table.get_list(), table.get_list())
    def test_saved_dice_table_equality_test_true(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        not_really_equal_data_obj = fh.SavedDiceTable('2D2', [(2, 1), (3, 2), (4, 1)], [], [])
        self.assertTrue(data_obj == not_really_equal_data_obj)
    def test_saved_dice_table_equality_test_false_by_text(self):
        table_1 = dt.DiceTable()
        table_1.add_die(1, dt.WeightedDie({1: 1, 2: 1}))
        data_obj = create_saved_dice_table(table_1)
        table_2 = dt.DiceTable()
        table_2.add_die(1, dt.Die(2))
        other_data_obj = create_saved_dice_table(table_2)
        self.assertEqual(data_obj.tuple_list, other_data_obj.tuple_list)
        self.assertFalse(data_obj == other_data_obj)
    def test_saved_dice_table_equality_test_false_by_tuple_list(self):
        table_1 = dt.DiceTable()
        table_1.add_die(1, dt.WeightedDie({1: 5, 2: 1}))
        data_obj = create_saved_dice_table(table_1)
        table_2 = dt.DiceTable()
        table_2.add_die(1, dt.WeightedDie({1: 1, 2: 5}))
        other_data_obj = create_saved_dice_table(table_2)
        self.assertEqual(data_obj.text, other_data_obj.text)
        self.assertFalse(data_obj == other_data_obj)
    def test_saved_dice_table_not_equal(self):
        table = dt.DiceTable()
        data_obj = create_saved_dice_table(table)
        table.add_die(2, dt.Die(2))
        other_data_obj = create_saved_dice_table(table)
        self.assertTrue(data_obj != other_data_obj)
    def test_saved_dice_table_is_empty_true(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertTrue(data_obj.is_empty())
    def test_saved_dice_table_is_empty_false(self):
        table = dt.DiceTable()
        table.add_die(2, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertFalse(data_obj.is_empty())
    def test_saved_dice_table_verify_all_data_empty_object(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        self.assertEqual(data_obj.verify_all_data(), '')
    def test_saved_dice_table_empty_object_passes_verify_all_data(self):
        self.assertEqual(fh.SavedDiceTable.empty_object().verify_all_data(), '')
    def test_saved_dice_table_verify_all_data_no_errors(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        data_obj = create_saved_dice_table(table)
        self.assertEqual(data_obj.verify_all_data(), '')
    def test_saved_dice_table_verify_all_data_text_errors(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        data_obj._text = 2
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid text value')
    def test_saved_dice_table_verify_all_data_tuple_errors(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        data_obj._tuple_list = 1
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid tuple list')
    def test_saved_dice_table_verify_all_data_dice_list_errors(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        data_obj._dice_list = 1
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid dice list')
    def test_saved_dice_table_verify_all_data_graph_axes_errors(self):
        data_obj = create_saved_dice_table(dt.DiceTable())
        data_obj._graph_axes = 'a'
        self.assertEqual(data_obj.verify_all_data(), 'error: invalid graph values')

    def test_add_long_to_data_type_for_python_2_no_int(self):
        self.assertEqual((float, str), fh.add_long_to_data_type_for_python_2((float, str)))
    def test_add_long_to_data_type_for_python_2_with_int(self):
        try:
            self.assertEqual((int, float, long), fh.add_long_to_data_type_for_python_2((int, float)))
        except NameError:
            self.assertEqual((int, float), fh.add_long_to_data_type_for_python_2((int, float)))

    def test_check_datum_and_return_error_message_no_error_one_type(self):
        message = fh.check_datum_for_types(1., (float,), 'error')
        self.assertEqual(message, '')
    def test_check_datum_and_return_error_message_no_error_multi_type(self):
        message = fh.check_datum_for_types(1., (float, str, list), 'error')
        self.assertEqual(message, '')
    def test_check_datum_and_return_error_message_error(self):
        message = fh.check_datum_for_types(1., (str, list), 'error')
        self.assertEqual(message, 'error')
    def test_check_datum_edge_case_of_int_and_long(self):
        message = fh.check_datum_for_types(10 ** 1000, (int,), 'error')
        self.assertEqual(message, '')

    def test_check_iterable_for_types_no_error_one_type(self):
        message = fh.check_iterable_for_types((1., 2., 3.), (float,), 'error')
        self.assertEqual(message, '')
    def test_check_iterable_for_types_no_error_many_types_data(self):
        message = fh.check_iterable_for_types((1., 'hi', [1, 2]), (float, list, str), 'error')
        self.assertEqual(message, '')
    def test_check_iterable_for_types_no_error_many_data_types(self):
        message = fh.check_iterable_for_types(('a', 'b', 'c'), (float, list, str, tuple), 'error')
        self.assertEqual(message, '')
    def test_check_iterable_for_types_no_error_empty_list(self):
        message = fh.check_iterable_for_types([], (int,), 'error')
        self.assertEqual(message, '')
    def test_check_iterable_for_types_with_error_one_type(self):
        message = fh.check_iterable_for_types((1., 2., 3.), (str,), 'error')
        self.assertEqual(message, 'error')
    def test_check_iterable_for_types_with_error_many_types(self):
        message = fh.check_iterable_for_types((1., 2., 'a'), (float, list), 'error')
        self.assertEqual(message, 'error')
    def test_check_iterable_for_types_edge_case_int_and_long(self):
        message = fh.check_iterable_for_types((1, 10 ** 1000), (int,), 'error')
        self.assertEqual(message, '')
    def test_check_iterable_for_types_returns_error_when_not_passed_iterable(self):
        message = fh.check_iterable_for_types(1, (int,), 'error')
        self.assertEqual(message, 'error')

    def test_iterable_and_types_same_len_true(self):
        self.assertTrue(fh.iterable_and_types_same_len([1, 2], [(int, ), (str, )]))
    def test_iterable_and_types_same_len_true(self):
        self.assertFalse(fh.iterable_and_types_same_len([1], [(int, ), (str, )]))

    def test_is_strictly_iterable(self):
        self.assertTrue(fh.is_strictly_iterable([]))
        self.assertTrue(fh.is_strictly_iterable({1}))
        self.assertTrue(fh.is_strictly_iterable((1,2)))
        self.assertTrue(fh.is_strictly_iterable({1:2}))
        self.assertFalse(fh.is_strictly_iterable('hello'))
        self.assertFalse(fh.is_strictly_iterable(1))
        self.assertFalse(fh.is_strictly_iterable(fh.SavedDiceTable.empty_object()))

    def test_is_empty_iterable_simple_true(self):
        self.assertTrue(fh.is_empty_iterable([]))
    def test_is_empty_iterable_complex_true(self):
        self.assertTrue(fh.is_empty_iterable([([[[]]], [], ([], []))]))
    def test_is_empty_iterable_string_false(self):
        self.assertFalse(fh.is_empty_iterable(''))
    def test_is_empty_iterable_dict_true(self):
        self.assertTrue(fh.is_empty_iterable({(): [[], [[]]]}))
    def test_is_empty_iterable_false(self):
        self.assertFalse(fh.is_empty_iterable([([[[]]], [2], ([], []))]))

    def test_check_iterables_in_iterable_for_types_no_error(self):
        tuple_list = [(1, 2), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_no_error_multi_types(self):
        tuple_list = [(1, 2), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_no_error_multi_types_different_elements(self):
        tuple_list = [(1, 3., 10**1000), ([], 'hi', 'hi'), (2., 5., 0.23)]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_no_error_empty_list(self):
        empty_list = []
        empty_tuple_list = [()]
        data_types_list = [(int, float), (str, list), (float, )]
        self.assertEqual('', fh.check_iterables_in_iterable_for_types(empty_list, data_types_list, 'error'))
        self.assertEqual('', fh.check_iterables_in_iterable_for_types(empty_tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_one_error(self):
        tuple_list = [(1, 'oops'), ('a', 'hi'), (2., 5.)]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_multi_errors_one_tuple(self):
        tuple_list = [(1, 'oops'), ('a', 'hi'), (2., 'fuck')]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_multi_errors_multi_tuple(self):
        tuple_list = [(1, 'oops'), ('a', 2.), (2., 'fuck')]
        data_types_list = [(int, ), (str, ), (float, )]
        self.assertEqual('error', fh.check_iterables_in_iterable_for_types(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_types_error_when_not_tuple_list(self):
        message = fh.check_iterables_in_iterable_for_types([1, 2], [(int,)], 'error')
        self.assertEqual(message, 'error')
        self.assertEqual('error', fh.check_iterables_in_iterable_for_types(1, [(int,)], 'error'))

    def test_check_iterables_in_iterable_for_type_sequence_no_error(self):
        tuple_list = [(1, 'a', 2.), (2, 'hi', 5.)]
        data_types_list = [(int,), (str,), (float,)]
        self.assertEqual('', fh.check_iterables_in_iterable_for_type_sequence(tuple_list, data_types_list, 'error'))
    def test_check_iterables_in_iterable_for_type_sequence_with_error(self):
        tuple_list = [(1, 'a', 'oops'), (2, 'hi', 5.)]
        data_types_list = [(int,), (str,), (float,)]
        self.assertEqual('error', fh.check_iterables_in_iterable_for_type_sequence(tuple_list, data_types_list,
                                                                                       'error'))
    def test_check_iterables_in_iterable_for_type_sequence_error_when_not_tuple_list(self):
        message = fh.check_iterables_in_iterable_for_type_sequence([1, 2], [(int,)], 'error')
        self.assertEqual(message, 'error')
        self.assertEqual('error', fh.check_iterables_in_iterable_for_type_sequence(1, [(int,)], 'error'))

    def test_check_saved_tables_within_array_returns_first_error(self):
        obj1 = create_saved_dice_table(dt.DiceTable())
        obj2 = create_saved_dice_table(dt.DiceTable())
        obj1._tuple_list = [(2.0, 1)]
        obj2._text = 2
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_saved_tables_within_array(save_data_array), 'error: invalid tuple list')
    def test_check_saved_tables_within_array_finds_bad_objects(self):
        obj1 = []
        obj2 = create_saved_dice_table(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_saved_tables_within_array(save_data_array), 'error: wrong object in array')
    def test_check_saved_tables_within_array_no_errors(self):
        obj1 = create_saved_dice_table(dt.DiceTable())
        obj2 = create_saved_dice_table(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_saved_tables_within_array(save_data_array), '')
    def test_check_saved_tables_within_array_empty_array(self):
        self.assertEqual(fh.check_saved_tables_within_array(np.array([])), '')

    def test_check_array_is_correct_type_error(self):
        self.assertEqual(fh.check_array_is_correct_type(np.array([])), 'error: wrong array type')
    def test_check_array_is_correct_type_no_error(self):
        self.assertEqual(fh.check_array_is_correct_type(np.array([dt.DiceTable()])), '')

    def test_check_saved_tables_array_empty_array_correct_type(self):
        self.assertEqual(fh.check_saved_tables_array(np.array([], dtype=object)), 'ok: no saved data')
    def test_check_saved_tables_array_non_empty_array_correct_type(self):
        obj1 = create_saved_dice_table(dt.DiceTable())
        obj2 = create_saved_dice_table(dt.DiceTable())
        save_data_array = np.array([obj1, obj2])
        self.assertEqual(fh.check_saved_tables_array(save_data_array), 'ok')
    def test_check_saved_tables_array_wrong_array_type(self):
        self.assertEqual(fh.check_saved_tables_array(np.array([1, 2, 3])), 'error: wrong array type')
    def test_check_saved_tables_array_bad_array_data(self):
        self.assertEqual(fh.check_saved_tables_array(np.array([dt.DiceTable()])), 'error: wrong object in array')

    def test_read_message_and_return_original_or_empty_array_return_original(self):
        msg_and_obj = fh.read_message_and_return_original_or_empty_array('ok', 1)
        self.assertEqual(msg_and_obj, ('ok', 1))
    def test_read_message_and_return_original_or_empty_array_return_empty_array(self):
        msg, obj = fh.read_message_and_return_original_or_empty_array('error: omfg what did you do???', 1)
        self.assertEqual(msg, 'error: omfg what did you do???')
        self.assertArrayEqual(obj, np.array([], dtype=object))


    def test_read_write_saved_tables_array_work_ok_for_normal_case(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_saved_dice_table(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_saved_dice_table(table)
        save_data = np.array([obj1, obj2])
        fh.write_saved_tables_array(save_data)
        msg, new_save_data = fh.read_saved_tables_array()
        self.assertEqual(msg, 'ok')
        self.assertArrayEqual(save_data, new_save_data)
    def test_read_saved_tables_array_returns_error_and_empty_if_check_hist_has_error(self):
        fh.write_saved_tables_array(np.array([1, 2, 3]))
        msg, save_data = fh.read_saved_tables_array()
        self.assertEqual(msg, 'error: wrong array type')
        self.assertArrayEqual(save_data, np.array([], dtype=object))
    def test_read_saved_tables_array_returns_ok_and_empty_if_hist_empty_and_correct_type(self):
        fh.write_saved_tables_array(np.array([], dtype=object))
        msg, save_data = fh.read_saved_tables_array()
        self.assertEqual(msg, 'ok: no saved data')
        self.assertArrayEqual(save_data, np.array([], dtype=object))
    def test_read_saved_tables_array_returns_error_and_empty_if_no_file(self):
        os.remove('save_data.npy')
        msg, save_data = fh.read_saved_tables_array()
        self.assertEqual(msg, 'error: no file')
        self.assertArrayEqual(save_data, np.array([], dtype=object))

    def test_read_saved_tables_array_returns_error_and_empty_if_corrupted_file(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_saved_dice_table(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_saved_dice_table(table)
        save_data_array = np.array([obj1, obj2])
        fh.write_saved_tables_array(save_data_array)
        #for differences between python2 and 3
        try:
            with open('save_data.npy', 'r') as f:
                to_write = f.read()[:-1]
        except UnicodeDecodeError:
            with open('save_data.npy', 'r', errors='ignore') as f:
                to_write = f.read()[:-1]
        with open('save_data.npy', 'w') as f:
            f.write(to_write)
        msg, new_data = fh.read_saved_tables_array()
        self.assertEqual(msg, 'error: file corrupted')
        self.assertArrayEqual(new_data, np.array([], dtype=object))

