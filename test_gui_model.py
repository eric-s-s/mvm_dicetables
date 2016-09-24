# pylint: disable=missing-docstring, invalid-name, too-many-public-methods
# pylint: disable=too-few-public-methods, protected-access, no-member
"""tests for the gui_model.py module"""

from __future__ import absolute_import

import unittest

import numpy as np
import dicetables as dt
import gui_model as mvm
import filehandler as fh


class TestMVM(unittest.TestCase):
    def setUp(self):
        self.DTM = mvm.DiceTableManager()
        self.ST = mvm.SavedTables()
        self.interface = mvm.CurrentAndSavedInterface(self.DTM, self.ST)
        self.GB = mvm.GraphBox(self.DTM, self.ST, True)
        self.CB = mvm.ChangeBox(self.DTM)
        self.SB = mvm.StatBox(self.DTM)
        self.AB = mvm.AddBox(self.DTM)
        self.IB = mvm.InfoBox(self.DTM)

    def tearDown(self):
        del self.DTM
        del self.ST
        del self.interface
        del self.GB
        del self.CB
        del self.SB
        del self.AB
        del self.IB

    def test_DiceTableManager_stddev(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.stddev, 0.5)

    def test_DiceTableManager_mean(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.mean, 1.5)

    def test_DiceTableManager_range(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.range, (1, 2))

    def test_DiceTableManager_title(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(3))
        self.assertEqual(self.DTM.title, '1D2\n1D3')

    def test_DiceTableManager_title_one_line(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(3))
        self.assertEqual(self.DTM.title_one_line, '1D2 \\ 1D3')

    def test_DiceTableManager_full_text(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.full_text, '1: 1\n2: 1\n')

    def test_DiceTableManager_weights_info(self):
        self.DTM.request_add(1, dt.Die(3))
        self.assertEqual(self.DTM.weights_info,
                         '1D3\n    No weights')

    def test_DiceTableManager_dice_list(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.dice_list, [(dt.Die(2), 1)])

    def test_DiceTableManager_tuple_list(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.tuple_list, [(1, 1), (2, 1)])

    def test_DiceTableManager_get_description_range_mean_stddev(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.DTM.get_description_range_mean_stddev(),
                         ('the range of numbers is 1-2\n' +
                          'the mean is 1.5\nthe stddev is 0.5'))

    def test_DiceTableManager_get_description_range_mean_stddev_formatting(self):
        self.DTM.request_add(1, dt.WeightedDie({1000: 1, 3000: 2}))
        self.assertEqual(self.DTM.get_description_range_mean_stddev(),
                         ('the range of numbers is 1,000-3,000\n' +
                          'the mean is 2,333.3333\nthe stddev is 942.809'))

    def test_DiceTableManager_get_stats_true_zero_chance(self):
        self.assertEqual(self.DTM.get_stats([1, 2, 3]),
                         ('1-3', '0.0', '1', 'infinity', '0.0'))

    def test_DiceTableManager_get_stats_tiny_tiny_chance(self):
        self.DTM.request_add(1, dt.WeightedDie({1: 1, 2: 10 ** 1000}))
        self.assertEqual(self.DTM.get_stats([1]),
                         ('1', '1', '1.000e+1000', '1.000e+1000', '1.000e-998'))

    def test_DiceTableManager_get_stats_normal_case(self):
        self.assertEqual(self.DTM.get_stats([0]),
                         ('0', '1', '1', '1.000', '100.0'))

    def test_DiceTableManager_get_obj_to_save(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(4))
        expected_object_data = {'title': '1D2 \\ 1D4', 'x_range': (2, 6),
                                'y_range': (12.5, 25.0),
                                'dice': [(dt.Die(2), 1), (dt.Die(4), 1)],
                                'tuple_list': [(2, 1), (3, 2), (4, 2), (5, 2), (6, 1)],
                                'graph_axes': [(2, 3, 4, 5, 6), (12.5, 25.0, 25.0, 25.0, 12.5)]}
        data_object = self.DTM.get_obj_to_save()
        self.assertEqual(data_object.title, expected_object_data['title'])
        self.assertEqual(data_object.x_range, expected_object_data['x_range'])
        self.assertEqual(data_object.y_range, expected_object_data['y_range'])
        self.assertEqual(data_object.dice_table.get_list(), expected_object_data['dice'])
        self.assertEqual(data_object.tuple_list, expected_object_data['tuple_list'])
        self.assertEqual(data_object.graph_axes, expected_object_data['graph_axes'])

    def test_DiceTableManager_request_reload(self):
        table = dt.DiceTable()
        table.add_die(1, dt.Die(2))
        table.add_die(1, dt.Die(4))
        data_obj = fh.SavedDiceTable('1D2 \\ 1D4', table.frequency_all(), table.get_list(), [])
        self.DTM.request_reload(data_obj)
        self.assertEqual(self.DTM.title, '1D2\n1D4')
        self.assertEqual(self.DTM.full_text,
                         '2: 1\n3: 2\n4: 2\n5: 2\n6: 1\n')

    def test_DiceTableManager_request_add(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(4))
        self.assertEqual(self.DTM.title, '1D2\n1D4')
        self.assertEqual(self.DTM.full_text,
                         '2: 1\n3: 2\n4: 2\n5: 2\n6: 1\n')

    def test_DiceTableManager_request_remove_normal_case(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(4))
        self.DTM.request_remove(1, dt.Die(4))
        self.assertEqual(self.DTM.title, '1D2')
        self.assertEqual(self.DTM.tuple_list, [(1, 1), (2, 1)])

    def test_DiceTableManager_request_remove_only_removes_max_dice(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(1, dt.Die(4))
        self.DTM.request_remove(1000, dt.Die(4))
        self.assertEqual(self.DTM.title, '1D2')
        self.assertEqual(self.DTM.tuple_list, [(1, 1), (2, 1)])

    def test_DiceTableManager_request_remove_doesnt_remove_if_not_there(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_remove(1, dt.Die(4))
        self.assertEqual(self.DTM.title, '1D2')
        self.assertEqual(self.DTM.tuple_list, [(1, 1), (2, 1)])

    def test_DiceTableManager_request_reset(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_reset()
        self.assertEqual(self.DTM.title, '')
        self.assertEqual(self.DTM.tuple_list, [(0, 1)])

    def test_SavedTables_inits_as_empty(self):
        self.assertEqual(self.ST._saved_tables.size, 0)

    def test_SavedTables_saves_new(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertEqual(self.ST._saved_tables[0], obj)

    def test_SavedTables_wont_save_empty_obj(self):
        self.ST.save_new(fh.SavedDiceTable.empty_object())
        self.assertEqual(self.ST._saved_tables.size, 0)

    def test_SavedTables_save_new_wont_add_duplicates(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.ST.save_new(obj)
        self.assertEqual(self.ST._saved_tables.size, 1)
        self.assertEqual(self.ST._saved_tables[0], obj)

    def test_SavedTables_has_requested_true(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertTrue(self.ST.has_requested('1D2', [(1, 1), (2, 1)]))

    def test_SavedTables_has_requested_false(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertFalse(self.ST.has_requested('ooops', [(1, 1), (2, 1)]))
        self.assertFalse(self.ST.has_requested('1D2', [(1, 1)]))

    def test_SavedTables_get_requested_returns_correct_one(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertEqual(self.ST.get_requested('1D2', [(1, 1), (2, 1)]), obj)

    def test_SavedTables_get_requested_returns_empty_if_not_pts(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertTrue(self.ST.get_requested('hi', [(1, 1), (2, 1)]).is_empty())

    def test_SavedTables_get_requested_returns_empty_if_not_title(self):
        self.DTM.request_add(1, dt.Die(2))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertTrue(self.ST.get_requested('hi', [(1, 1), (2, 1)]).is_empty())

    def test_SavedTables_get_all_works(self):
        self.assertEqual(self.ST.get_all(), [])
        self.DTM.request_add(1, dt.Die(2))
        obj_1 = self.DTM.get_obj_to_save()
        self.ST.save_new(obj_1)
        self.DTM.request_add(1, dt.Die(2))
        obj_2 = self.DTM.get_obj_to_save()
        self.ST.save_new(obj_2)
        self.assertEqual(self.ST.get_all(), [obj_1, obj_2])

    def test_SavedTables_get_labels_returns_empty_list_when_empty(self):
        self.assertEqual(self.ST.get_labels(), [])

    def test_SavedTables_get_labels_returns_as_expected(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(2))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(
            self.ST.get_labels(),
            [('1D1', [(1, 1)]), ('1D1 \\ 1D2', [(2, 1), (3, 1)])])

    def test_SavedTables_delete_all(self):
        self.DTM.request_add(1, dt.Die(2))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.ST.delete_all()
        self.assertEqual(self.ST.get_labels(), [])

    def test_SavedTables_delete_selected__empty_list_does_nothing(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.ST.delete_requested([])
        self.assertEqual(self.ST.get_labels(), [('1D1', [(1, 1)])])

    def test_SavedTables_delete_selected__not_present_does_nothing(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.ST.delete_requested([('no', [(1, 1)])])
        self.assertEqual(self.ST.get_labels(), [('1D1', [(1, 1)])])

    def test_SavedTables_delete_selected_works_as_expected(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(2))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(3))
        self.ST.save_new(self.DTM.get_obj_to_save())
        del_1, keep, del_2 = self.ST.get_labels()
        self.ST.delete_requested([del_1, del_2])
        self.assertEqual(self.ST.get_labels(), [keep])

    def test_SavedTables_write_to_file(self):
        self.DTM.request_add(2, dt.Die(1))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.ST.write_to_file()
        save_data = np.load('save_data.npy')
        self.assertEqual(save_data[0], obj)
        self.assertEqual(save_data.size, 1)

    def test_SavedTables_reload_from_file(self):
        self.DTM.request_add(1, dt.Die(1))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.ST.write_to_file()
        self.ST = mvm.SavedTables()
        self.assertEqual(self.ST.get_labels(), [])
        msg = self.ST.reload_from_file()
        self.assertEqual(msg, 'ok')
        self.assertEqual(self.ST.get_labels(), [('1D1', [(1, 1)])])

    def test_SavedTables_reload_from_file_overwrites(self):
        self.ST.write_to_file()
        self.DTM.request_add(1, dt.Die(1))
        obj = self.DTM.get_obj_to_save()
        self.ST.save_new(obj)
        self.assertEqual(self.ST.get_labels(), [('1D1', [(1, 1)])])
        msg = self.ST.reload_from_file()
        self.assertEqual(msg, 'ok: no saved data')
        self.assertEqual(self.ST.get_labels(), [])

    def test_remove_duplicates_from_list_no_duplicates(self):
        self.assertEqual(mvm.remove_duplicates_from_list([1, 2, 3]), [1, 2, 3])

    def test_remove_duplicates_from_list_has_duplicates(self):
        self.assertEqual(mvm.remove_duplicates_from_list([2, 1, 2, 3, 1, 3, 2, 3, 1, 2, 3]),
                         [2, 1, 3])

    def test_CurrentAndSavedInterface_get_and_save_current_empty(self):
        self.ST.write_to_file()
        self.assertTrue(self.interface.get_and_save_current().is_empty())
        self.ST.reload_from_file()
        self.assertEqual(self.ST.get_labels(), [])

    def test_CurrentAndSavedInterface_get_and_save_current_gets(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.interface.get_and_save_current(),
                         fh.SavedDiceTable('1D2', [(1, 1), (2, 1)], [], []))

    def test_CurrentAndSavedInterface_get_and_save_current_saves(self):
        self.DTM.request_add(1, dt.Die(2))
        self.interface.get_and_save_current()
        self.assertEqual(self.ST.get_labels(), [('1D2', [(1, 1), (2, 1)])])

    def test_CurrentAndSavedInterface_get_and_save_current_writes(self):
        self.ST.write_to_file()
        self.DTM.request_add(1, dt.Die(2))
        self.interface.get_and_save_current()
        self.ST.reload_from_file()
        self.assertEqual(self.ST.get_labels(), [('1D2', [(1, 1), (2, 1)])])

    def test_CurrentAndSavedInterface_get_label_current(self):
        self.assertEqual(self.interface.get_label_current(), ('', [(0, 1)]))
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.interface.get_label_current(), ('1D2', [(1, 1), (2, 1)]))

    def test_CurrentAndSavedInterface_get_label_saved_empty(self):
        self.assertEqual(self.interface.get_label_saved(), [])

    def test_CurrentAndSavedInterface_get_label_non_empty(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(self.interface.get_label_saved(),
                         [('1D1', [(1, 1)]), ('2D1', [(2, 1)])])

    def test_CurrentAndSavedInterface_get_labels(self):
        self.DTM.request_add(1, dt.Die(1))
        self.assertEqual(self.interface.get_labels(), (('1D1', [(1, 1)]), []))

    def test_CurrentAndSavedInterface_is_current_table_true(self):
        self.DTM.request_add(1, dt.Die(1))
        self.assertTrue(self.interface.is_current_table('1D1', [(1, 1)]))

    def test_CurrentAndSavedInterface_is_current_table_false(self):
        self.DTM.request_add(1, dt.Die(1))
        self.assertFalse(self.interface.is_current_table('you shall not pass!', [(1, 1)]))
        self.assertFalse(self.interface.is_current_table('1D1', [(2, 1)]))

    def test_CurrentAndSavedInterface_current_is_empty_true(self):
        self.assertTrue(self.interface.current_is_empty())

    def test_CurrentAndSavedInterface_current_is_empty_false(self):
        self.DTM.request_add(1, dt.Die(1))
        self.assertFalse(self.interface.current_is_empty())

    def test_CurrentAndSavedInterface_get_requested_gets_saved_not_current(self):
        self.DTM.request_add(1, dt.Die(1))
        from_current = self.DTM.get_obj_to_save()
        asserts_equal_but_isnt = fh.SavedDiceTable('1D1', [(1, 1)], [], [(789, 1.234)])
        self.assertEqual(from_current, asserts_equal_but_isnt)
        self.ST.save_new(asserts_equal_but_isnt)

        self.assertEqual(len(self.interface.get_requested([('1D1', [(1, 1)])])), 1)
        from_interface = self.interface.get_requested([('1D1', [(1, 1)])])[0]
        self.assertEqual(from_interface.graph_pts, asserts_equal_but_isnt.graph_pts)
        self.assertEqual(from_interface.dice_table.get_list(),
                         asserts_equal_but_isnt.dice_table.get_list())
        self.assertNotEqual(from_current.graph_pts, asserts_equal_but_isnt.graph_pts)
        self.assertNotEqual(from_current.dice_table.get_list(),
                            asserts_equal_but_isnt.dice_table.get_list())

    def test_CurrentAndSavedInterface_get_requested_doesnt_get_not_there(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        from_interface = self.interface.get_requested([('1D1', [(1, 1)]), ('not there', [(1, 1)])])
        self.assertEqual(from_interface, [fh.SavedDiceTable('1D1', [(1, 1)], [], [])])

    def test_CurrentAndSavedInterface_get_requested_gets_current(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        from_interface = self.interface.get_requested([('1D1', [(1, 1)]), ('2D1', [(2, 1)])])
        self.assertEqual(from_interface, [fh.SavedDiceTable('1D1', [(1, 1)], [], []),
                                          fh.SavedDiceTable('2D1', [(2, 1)], [], [])])

    def test_CurrentAndSavedInterface_get_requested_doesnt_get_duplicates(self):
        self.DTM.request_add(1, dt.Die(1))
        to_test = self.interface.get_requested([('1D1', [(1, 1)])] * 3)
        self.assertEqual(to_test, [self.DTM.get_obj_to_save()])

    def test_CurrentAndSavedInterface_get_all_empty(self):
        self.assertEqual(self.interface.get_all(), [])

    def test_CurrentAndSavedInterface_get_all_current_empty(self):
        saved = fh.SavedDiceTable('saved', [(1, 1)], [], [])
        self.ST.save_new(saved)
        self.assertTrue(self.interface.current_is_empty())
        self.assertEqual(self.interface.get_all(), [saved])

    def test_CurrentAndSavedInterface_get_all_current_in_saved(self):
        self.DTM.request_add(1, dt.Die(1))
        from_current = self.DTM.get_obj_to_save()
        asserts_equal_but_isnt = fh.SavedDiceTable('1D1', [(1, 1)], [], [(789, 1.234)])
        self.assertEqual(from_current, asserts_equal_but_isnt)
        self.ST.save_new(asserts_equal_but_isnt)
        expect_from_saved = self.interface.get_all()[0]
        self.assertEqual(expect_from_saved.graph_axes, asserts_equal_but_isnt.graph_axes)
        self.assertNotEqual(expect_from_saved.graph_axes, from_current.graph_axes)
        self.assertEqual(self.interface.get_all(), [asserts_equal_but_isnt])

    def test_CurrentAndSavedInterface_get_all_current_not_empty_not_in_saved(self):
        self.DTM.request_add(1, dt.Die(1))
        current = self.DTM.get_obj_to_save()
        saved = fh.SavedDiceTable('saved', [(1, 1)], [], [])
        self.ST.save_new(saved)
        self.assertEqual(self.ST.get_all(), [saved])
        self.assertEqual(self.interface.get_all(), [saved, current])

    def test_CurrentAndSavedInterface_delete_all_saves_to_file(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.interface.delete_all()
        self.ST.reload_from_file()
        self.assertEqual(self.ST.get_all(), [])

    def test_CurrentAndSavedInterface_delete_requested_writes_to_file(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.interface.delete_requested([('1D1', [(1, 1)])])
        self.ST.reload_from_file()
        self.assertEqual(self.ST.get_labels(), [('2D1', [(2, 1)])])

    def test_CurrentAndSavedInterface_reload_requested_as_current_not_in_saved(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.interface.reload_requested_as_current('3D1', [(1, 1)])
        self.assertEqual(self.interface.get_label_current(), ('2D1', [(2, 1)]))

    def test_CurrentAndSavedInterface_reload_requested_as_current_is_in_saved(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.interface.reload_requested_as_current('1D1', [(1, 1)])
        self.assertEqual(self.interface.get_label_current(), ('1D1', [(1, 1)]))

    def test_combine_ranges_first_range_wins(self):
        self.assertEqual(mvm.combine_ranges((0, 5), (1, 2)), (0, 5))

    def test_combine_ranges_second_range_wins(self):
        self.assertEqual(mvm.combine_ranges((0, 5), (-1, 12)), (-1, 12))

    def test_combine_ranges_mixed(self):
        self.assertEqual(mvm.combine_ranges((0, 5), (1, 12)), (0, 12))

    def test_get_graphs_empty(self):
        self.assertEqual(mvm.get_graphs([]),
                         ((float('inf'), float('-inf')),
                          (float('inf'), float('-inf')),
                          []))

    def test_get_graphs_x_range(self):
        self.DTM.request_add(1, dt.ModDie(1, -101))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.ModDie(1, 199))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(mvm.get_graphs(self.ST.get_all())[0], (-100, 100))

    def test_get_graphs_y_range(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(2))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(mvm.get_graphs(self.ST.get_all())[1], (50.0, 100.0))

    def test_get_graphs_axes(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(mvm.get_graphs(self.ST.get_all(), get_axes_not_pts=True),
                         ((1, 2), (100.0, 100.0),
                          [('1D1', [(1,), (100.0,)]), ('2D1', [(2,), (100.0,)])]))

    def test_get_graphs_pts(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.assertEqual(mvm.get_graphs(self.ST.get_all(), get_axes_not_pts=False),
                         ((1, 2), (100.0, 100.0),
                          [('1D1', [(1, 100.0)]), ('2D1', [(2, 100.0)])]))

    def test_GraphBox_get_requested_graphs_empty(self):
        self.assertEqual(self.GB.get_requested_graphs([]),
                         ((float('inf'), float('-inf')),
                          (float('inf'), float('-inf')),
                          []))

    def test_GraphBox_get_requested_graphs_non_empty(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        to_test = self.GB.get_requested_graphs([('2D1', [(2, 1)]), ('not there', [(1, 1)])])
        self.assertEqual(to_test, ((2, 2),
                                   (100.0, 100.0),
                                   [('2D1', [(2, ), (100.0, )])]))

    def test_GraphBox_get_all_graphs(self):
        self.DTM.request_add(1, dt.Die(1))
        self.ST.save_new(self.DTM.get_obj_to_save())
        self.DTM.request_add(1, dt.Die(1))
        to_test = self.GB.get_all_graphs()
        self.assertEqual(to_test, ((1, 2),
                                   (100.0, 100.0),
                                   [('1D1', [(1, ), (100.0, )]),
                                    ('2D1', [(2,), (100.0,)])]))

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

    def test_get_add_choices_lt_size6(self):
        self.assertEqual(mvm.get_add_choices(dt.Die(5)), [1, 5, 10, 50, 100, 500])

    def test_get_add_choices_size6(self):
        self.assertEqual(mvm.get_add_choices(dt.WeightedDie({6: 2})), [1, 5, 10, 50, 100, 500])

    def test_get_add_choices_mid_size(self):
        self.assertEqual(mvm.get_add_choices(dt.ModDie(25, 10)), [1, 5, 10, 50])

    def test_get_add_choices_huge_size(self):
        self.assertEqual(mvm.get_add_choices(dt.Die(1000000)), [])

    def test_get_die_label_zero(self):
        self.assertEqual(mvm.get_die_label(dt.Die(1), 0), 'D1')

    def test_get_die_label_non_zero(self):
        self.assertEqual(mvm.get_die_label(dt.ModDie(1, 3), 5), '5D1+15')

    def test_get_add_and_remove_labels_no_remove(self):
        self.assertEqual(
            mvm.get_add_and_remove_labels(dt.Die(50), 0, False),
            ['D50', '+1', '+5', '+10'])

    def test_get_add_and_remove_labels_enable_remove(self):
        self.assertEqual(
            mvm.get_add_and_remove_labels(dt.Die(99), 0, True),
            ['-5', '-1', 'D99', '+1', '+5'])

    def test_ChangeBox_get_dice_details_empty_table(self):
        self.assertEqual(self.CB.get_dice_details(), [])

    def test_ChangeBox_get_dice_details_normal(self):
        self.DTM.request_add(1, dt.Die(1))
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.CB.get_dice_details(),
                         ['D1 rolls:\n  1 with frequency: 1',
                          'D2 rolls:\n  1 with frequency: 1\n  2 with frequency: 1'])

    def test_ChangeBox_display_at_empty_table(self):
        self.assertEqual(self.CB.display(), [])

    def test_ChangeBox_display_normal(self):
        self.DTM.request_add(2, dt.Die(100))
        self.DTM.request_add(1, dt.Die(101))
        expected = [
            (['-5', '-1', '2D100', '+1', '+5'], dt.Die(100)),
            (['-1', '1D101', '+1'], dt.Die(101))]
        self.assertEqual(self.CB.display(), expected)

    def test_ChangeBox_add_rm_at_zero(self):
        self.CB.add_rm(0, dt.Die(5))
        self.assertEqual(self.DTM.tuple_list, [(0, 1)])
        self.assertEqual(self.DTM.dice_list, [])

    def test_ChangeBox_add_rm_pos_number(self):
        self.CB.add_rm(2, dt.Die(1))
        self.assertEqual(self.DTM.tuple_list, [(2, 1)])
        self.assertEqual(self.DTM.dice_list, [(dt.Die(1), 2)])

    def test_ChangeBox_add_rm_neg_number(self):
        self.CB.add_rm(2, dt.Die(1))
        self.CB.add_rm(-1, dt.Die(1))
        self.assertEqual(self.DTM.tuple_list, [(1, 1)])
        self.assertEqual(self.DTM.dice_list, [(dt.Die(1), 1)])

    def test_ChangeBox_reset(self):
        self.CB.add_rm(1, dt.Die(2))
        self.CB.reset()
        self.assertEqual(self.DTM.tuple_list, [(0, 1)])
        self.assertEqual(self.DTM.dice_list, [])

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

    def test_AddBox_inits_with_die_and_presets(self):
        self.assertEqual(self.AB.presets,
                         ['D2', 'D4', 'D6', 'D8', 'D10', 'D12', 'D20', 'D100'])
        self.assertEqual(self.AB._die, dt.Die(6))

    def test_AddBox_get_die_details(self):
        self.assertEqual(self.AB.get_die_details(),
                         ('D6 rolls:\n  1 with frequency: 1\n  2 with frequency: 1\n' +
                          '  3 with frequency: 1\n  4 with frequency: 1\n' +
                          '  5 with frequency: 1\n  6 with frequency: 1'))

    def test_AddBox_display_die(self):
        self.assertEqual(self.AB.display_die(),
                         ['D6', '+1', '+5', '+10', '+50', '+100', '+500'])

    def test_AddBox_display_current(self):
        self.DTM.request_add(1, dt.Die(2))
        self.DTM.request_add(2, dt.Die(1))
        self.assertEqual(self.AB.display_current_table(), '2D1 \\ 1D2')

    def test_AddBox_add(self):
        self.AB._die = dt.Die(2)
        self.AB.add(2)
        self.assertEqual(self.DTM.tuple_list,
                         [(2, 1), (3, 2), (4, 1)])
        self.assertEqual(self.DTM.dice_list, [(dt.Die(2), 2)])

    def test_AddBox_set_size_resets_dictionary(self):
        self.AB._dictionary = {1: 2}
        self.AB.set_size(5)
        self.assertEqual(self.AB._dictionary, {})

    def test_AddBox_set_size_works(self):
        self.AB.set_size(10)
        self.assertEqual(self.AB._die, dt.Die(10))

    def test_AddBox_set_size_doesnot_affect_mod_or_multiplier(self):
        self.AB._mod = 100
        self.AB._multiplier = 50
        self.AB.set_size(2)
        self.assertEqual(self.AB._mod, 100)
        self.assertEqual(self.AB._multiplier, 50)
        self.assertEqual(self.AB._die, dt.StrongDie(dt.ModDie(2, 100), 50))

    def test_AddBox_set_mod_changes_mod_and_gets_new_die(self):
        self.AB._dictionary = {1: 1, 2: 2}
        self.AB.set_mod(5)
        self.assertEqual(self.AB._die, dt.ModWeightedDie({1: 1, 2: 2}, 5))

    def test_AddBox_multiplier_sets_new_multiplier_and_gets_new_die(self):
        self.AB.set_multiplier(10)
        self.assertEqual(self.AB._die, dt.StrongDie(dt.Die(6), 10))

    def test_AddBox_get_weights_text_works(self):
        self.assertEqual(self.AB.get_weights_text(),
                         ['weight for 1', 'weight for 2', 'weight for 3',
                          'weight for 4', 'weight for 5', 'weight for 6'])

    def test_AddBox_record_weights_empty_list(self):
        self.AB.record_weights_text([])
        self.assertEqual(self.AB._dictionary, {})

    def test_AddBox_record_weights_updates_die(self):
        self.AB._size = 10
        self.AB.record_weights_text([])
        self.assertEqual(self.AB._die, dt.Die(10))

    def test_AddBox_record_weights_works_as_expected(self):
        self.AB.record_weights_text([('weight for 1', 3), ('weight for 2', 1)])
        self.assertEqual(self.AB._die, dt.WeightedDie({1: 3, 2: 1}))

    def test_StatBox__adjust_value_to_within_min_max_empty_table(self):
        self.assertEqual(self.SB._adjust_value_to_within_min_max(5), 0)

    def test_StatBox__adjust_value_to_within_min_max_gt_max(self):
        self.DTM.request_add(1, dt.Die(6))
        self.assertEqual(self.SB._adjust_value_to_within_min_max(15), 6)

    def test_StatBox__adjust_value_to_within_min_max_lt_min(self):
        self.DTM.request_add(1, dt.Die(6))
        self.assertEqual(self.SB._adjust_value_to_within_min_max(-1), 1)

    def test_StatBox__adjust_value_to_within_min_max_val_within_range(self):
        self.DTM.request_add(1, dt.Die(6))
        self.assertEqual(self.SB._adjust_value_to_within_min_max(2), 2)
        self.assertEqual(self.SB._adjust_value_to_within_min_max(1), 1)
        self.assertEqual(self.SB._adjust_value_to_within_min_max(6), 6)

    def test_StatBox_display_stats_expected_output(self):
        self.DTM.request_add(2, dt.Die(2))
        stat_text = ('\n    2-4 occurred 4 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 1.000 chance\n' +
                     '    or 100.0 percent')
        self.assertEqual(self.SB.display_stats(8, 2), [stat_text, (4, 2)])

    def test_StatBox_display_stats_val_1_val_2_equal(self):
        self.DTM.request_add(2, dt.Die(2))
        stat_text = ('\n    4 occurred 1 times\n' +
                     '    out of 4 total combinations\n\n' +
                     '    that\'s a one in 4.000 chance\n' +
                     '    or 25.00 percent')
        self.assertEqual(self.SB.display_stats(4, 4), [stat_text, (4, 4)])

    def test_StatBox_display(self):
        self.DTM.request_add(2, dt.Die(2))
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

    def test_StatBox_display_formatting(self):
        self.DTM.request_add(1, dt.WeightedDie({1: 1000, 10000: 1000}))
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

    def test_StatBox_display_empty_table(self):
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

    def test_InfoBox__get_text_full_text(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.IB._get_text('full_text'), '1: 1\n2: 1')

    def test_InfoBox__get_text_weights_info(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.IB._get_text('weights_info'), '1D2\n    No weights')

    def test_InfoBox__get_formatted_text_with_full_text(self):
        self.DTM.request_add(1, dt.Die(2))
        self.assertEqual(self.IB._get_formatted_text('full_text'), '1: 1\n2: 1')

    def test_InfoBox__get_formatted_text_with_weights_info(self):
        self.DTM.request_add(1, dt.WeightedDie({1: 2}))
        self.assertEqual(self.IB._get_formatted_text('weights_info'), '1D1  W:2\n    1 has weight: 2')

    def test_InfoBox_make_pages_empty_table_with_full_text(self):
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB._pages['full_text'], ['0: 1\n '])

    def test_InfoBox_make_pages_empty_table_with_weights_info(self):
        self.IB.make_pages('weights_info', 1)
        self.assertEqual(self.IB._pages['weights_info'], [''])

    def test_InfoBox_make_pages_no_fill(self):
        self.DTM.request_add(1, dt.Die(4))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB._pages['full_text'], ['1: 1\n2: 1', '3: 1\n4: 1'])

    def test_InfoBox_make_pages_with_fill(self):
        self.DTM.request_add(1, dt.Die(3))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB._pages['full_text'], ['1: 1\n2: 1', '3: 1\n '])

    def test_InfoBox_make_pages_with_weights_info(self):
        self.DTM.request_add(1, dt.Die(3))
        self.DTM.request_add(1, dt.WeightedDie({1: 2}))
        self.IB.make_pages('weights_info', 2)
        self.assertEqual(self.IB._pages['weights_info'], ['1D1  W:2\n    1 has weight: 2',
                                                          '\n1D3',
                                                          '    No weights\n '])

    def test_InfoBox_display_current_page_defaults_page_one(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB.display_current_page('full_text'),
                         (' 1: 1\n 2: 1', 1, 5))

    def test_InfoBox_display_current_page_other_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 3
        self.assertEqual(self.IB.display_current_page('full_text'),
                         (' 5: 1\n 6: 1', 3, 5))

    def test_InfoBox_display_current_page_last_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 5
        self.assertEqual(self.IB.display_current_page('full_text'),
                         (' 9: 1\n10: 1', 5, 5))

    def test_InfoBox_display_current_page_page_number_outside_pages_range(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 12
        self.assertEqual(self.IB.display_current_page('full_text'),
                         (' 3: 1\n 4: 1', 2, 5))

    def test_InfoBox_display_current_page_adjusts_current_page_variable(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 12
        self.IB.display_current_page('full_text')
        self.assertEqual(self.IB._current_page,
                         {'weights_info': 1, 'full_text': 2})

    def test_InfoBox_display_next_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB.display_previous_page('full_text'),
                         (' 9: 1\n10: 1', 5, 5))

    def test_InfoBox_display_next_page_last_page_goes_to_first_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 5
        self.assertEqual(self.IB.display_next_page('full_text'),
                         (' 1: 1\n 2: 1', 1, 5))

    def test_InfoBox_display_previous_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.IB._current_page['full_text'] = 5
        self.assertEqual(self.IB.display_previous_page('full_text'),
                         (' 7: 1\n 8: 1', 4, 5))

    def test_InfoBox_display_previous_page_first_page_goes_to_last_page(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB.display_previous_page('full_text'),
                         (' 9: 1\n10: 1', 5, 5))

    def test_InfoBox_display_chosen_page_works_as_expected(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB.display_chosen_page(2, 'full_text'),
                         (' 3: 1\n 4: 1', 2, 5))

    def test_InfoBox_display_chosen_page_works_out_of_range(self):
        self.DTM.request_add(1, dt.Die(10))
        self.IB.make_pages('full_text', 2)
        self.assertEqual(self.IB.display_chosen_page(-3, 'full_text'),
                         (' 3: 1\n 4: 1', 2, 5))

    def test_InfoBox_display_paged_empty_table(self):
        general_info = ('the range of numbers is 0-0\n' +
                        'the mean is 0.0\nthe stddev is 0.0')
        self.assertEqual(self.IB.display_paged(2, 2),
                         [general_info, '', ('\n ', 1, 1), ('0: 1\n ', 1, 1)])

    def test_InfoBox_display_paged_works_as_expected(self):
        self.DTM.request_add(1, dt.Die(10))
        general_info = ('the range of numbers is 1-10\n' +
                        'the mean is 5.5\nthe stddev is 2.8723')
        self.assertEqual(self.IB.display_paged(2, 2),
                         [general_info, '1D10', ('1D10\n    No weights', 1, 1),
                          (' 1: 1\n 2: 1', 1, 5)])

    def test_InfoBox_display_works_as_expected(self):
        self.DTM.request_add(1, dt.Die(2))
        general_info = ('the range of numbers is 1-2\n' +
                        'the mean is 1.5\nthe stddev is 0.5')
        self.assertEqual(self.IB.display(),
                         [general_info, '1D2', '1D2\n    No weights', '1: 1\n2: 1'])


if __name__ == '__main__':
    unittest.main()
