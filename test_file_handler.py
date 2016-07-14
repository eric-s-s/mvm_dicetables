# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
'''tests for the longintmath.py module'''
from __future__ import absolute_import
import os
import unittest
import dicetables as dt
import numpy as np

import file_handler as fh

def create_plot_object(table):
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

    def test_check_data_empty_table(self):
        table = dt.DiceTable()
        obj = create_plot_object(table)
        self.assertEqual(fh.check_data(obj), 'ok')
    def check_data_not_a_dictionary(self):
        self.assertEqual(fh.check_data('a'), 'error: not a dict')
    def test_check_data_missing_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object(table)
        del obj['pts']
        self.assertEqual(fh.check_data(obj), 'error: missing key')
    def test_check_data_incorrect_type_at_key(self):
        table = dt.DiceTable()
        table.add_die(3, dt.Die(6))
        obj = create_plot_object(table)
        obj['pts'] = 'a'
        self.assertEqual(fh.check_data(obj), "error: pts not <type 'list'>")
    def test_check_data_incorrect_x_range(self):
        obj = create_plot_object(dt.DiceTable())
        obj['x_range'] = (1.0, 2)
        self.assertEqual(fh.check_data(obj), 'error: incorrect x_range')
    def test_check_data_incorrect_y_range(self):
        obj = create_plot_object(dt.DiceTable())
        obj['y_range'] = (1.0, 2)
        self.assertEqual(fh.check_data(obj), 'error: incorrect y_range')
    def test_check_data_incorrect_freq_in_tuple_list(self):
        obj = create_plot_object(dt.DiceTable())
        obj['tuple_list'] = [(1.0, 2)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "tuple_list"')
    def test_check_data_long_in_freq_in_tuple_list_ok(self):
        obj = create_plot_object(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2)]
        self.assertEqual(fh.check_data(obj), 'ok')
    def test_check_data_incorrect_val_in_tuple_list(self):
        obj = create_plot_object(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2.0)]
        self.assertEqual(fh.check_data(obj), 'error: corrupted "tuple_list"')
    def test_check_data_incorrect_num_in_dice(self):
        obj = create_plot_object(dt.DiceTable())
        obj['dice'] = [(dt.Die(6), 2.0)]
        self.assertEqual(fh.check_data(obj), 'error: dicelist at (Die(6), 2.0)')
    def test_check_data_incorrect_die_in_dice(self):
        obj = create_plot_object(dt.DiceTable())
        obj['dice'] = [('a', 2.)]
        self.assertEqual(fh.check_data(obj), 'error: dicelist at (\'a\', 2.0)')
    def test_check_data_reports_multiple_errors(self):
        obj = create_plot_object(dt.DiceTable())
        obj['tuple_list'] = [(10*1000, 2.0)]
        obj['dice'] = [('a', 2.)]
        self.assertEqual(
            fh.check_data(obj),
            'error: corrupted "tuple_list" dicelist at (\'a\', 2.0)')
    def test_check_data_all_die_types_pass(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(4))
        table.add_die(1, dt.ModDie(4, 2))
        table.add_die(1, dt.WeightedDie({1:2}))
        table.add_die(1, dt.ModWeightedDie({1:2}, 3))
        table.add_die(1, dt.StrongDie(dt.Die(3), 3))
        obj = create_plot_object(table)
        self.assertEqual(fh.check_data(obj), 'ok')

    def test_check_history_breaks_at_first_error(self):
        obj1 = create_plot_object(dt.DiceTable())
        obj2 = create_plot_object(dt.DiceTable())
        obj1['tuple_list'] = [(2.0, 1)]
        del obj2['pts']
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history(hist),
                         'error: corrupted "tuple_list"')
    def test_check_history_ok_for_valid_hist(self):
        obj1 = create_plot_object(dt.DiceTable())
        obj2 = create_plot_object(dt.DiceTable())
        hist = np.array([obj1, obj2])
        self.assertEqual(fh.check_history(hist), 'ok')

    def test_read_write_hist_np_work_ok_for_normal_case(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np(hist)
        msg, new_hist = fh.read_history_np()
        self.assertEqual(msg, 'ok')
        self.assertArrayEqual(hist, new_hist)
    def test_read_np_returns_error_and_empty_if_check_hist_has_error(self):
        fh.write_history_np(np.array([1, 2, 3]))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: not a dict')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_hist_empty_and_wrong_type(self):
        fh.write_history_np(np.array([]))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: wrong array type')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_ok_and_empty_if_hist_empty_and_correct_type(self):
        fh.write_history_np(np.array([], dtype=object))
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'ok: no history')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_no_file(self):
        os.remove('numpy_history.npy')
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: no file')
        self.assertArrayEqual(hist, np.array([], dtype=object))
    def test_read_np_returns_error_and_empty_if_corrupted_file(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(3))
        obj1 = create_plot_object(table)
        table.add_die(2, dt.Die(5))
        obj2 = create_plot_object(table)
        hist = np.array([obj1, obj2])
        fh.write_history_np(hist)
        with open('numpy_history.npy', 'r') as f:
            to_write = f.read()[:-1]
        with open('numpy_history.npy', 'w') as f:
            f.write(to_write)
        msg, hist = fh.read_history_np()
        self.assertEqual(msg, 'error: file corrupted')
        self.assertArrayEqual(hist, np.array([], dtype=object))

if __name__ == '__main__':
    unittest.main()
