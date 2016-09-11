'''for sending and retrieving main info to file. '''

# numpy python2 uses cPickle and numpy in python3 uses pickle
from sys import version_info

if version_info[0] > 2:
    from pickle import UnpicklingError
else:
    from cPickle import UnpicklingError

import dicetables as dt
import numpy as np


class SavedDiceTable(object):
    """a read-only object holding expensive-to-generate DiceTable info"""
    def __init__(self, text, tuple_list, dice_list, graph_axes):
        """
        text = string, name of table. dice_list = tuple list [(die, number)].
        tuple_list = tuple list of table.frequency_all(), graph_axes =  [(x-axis data), (y-axis data)]
        """
        self._text = text
        self._tuple_list = tuple_list
        self._dice_list = dice_list
        self._graph_axes = graph_axes

    @classmethod
    def empty_object(cls):
        return cls('', [(0, 1)], [], [(0,), (100.0,)])

    @property
    def graph_axes(self):
        return self._graph_axes[:]

    @property
    def graph_pts(self):
        return list(zip(*self._graph_axes))

    @property
    def x_range(self):
        return min(self._graph_axes[0]), max(self._graph_axes[0])

    @property
    def y_range(self):
        return min(self._graph_axes[1]), max(self._graph_axes[1])

    @property
    def tuple_list(self):
        return self._tuple_list[:]

    @property
    def text(self):
        return self._text

    @property
    def dice_table(self):
        new_table = dt.DiceTable()
        new_table.add(1, self._tuple_list)
        for die, number in self._dice_list:
            new_table.update_list(number, die)
        return new_table

    def __eq__(self, other):
        return self.text == other.text and self.tuple_list == other.tuple_list

    def __ne__(self, other):
        return not self == other

    def is_empty(self):
        return self == SavedDiceTable.empty_object()

    def verify_all_types(self):
        msg = 'error:'
        msg += check_datum_for_types(self._text, (str,), ' invalid text value')
        msg += check_tuples_in_list_for_type_sequence(self._tuple_list, [(int,), (int,)], ' invalid tuple list')
        msg += check_tuples_in_list_for_type_sequence(self._dice_list, [(dt.ProtoDie,), (int,)],
                                                             ' invalid dice list')
        msg += check_tuples_in_list_for_types(self._graph_axes, [(int,), (float,)], ' invalid graph values')
        if msg == 'error:':
            return ''
        else:
            return msg


def add_long_to_data_type_for_python_2(data_type_tuple):
    if version_info[0] < 3 and int in data_type_tuple:
        return data_type_tuple + (long,)
    else:
        return data_type_tuple


def check_datum_for_types(datum, data_types_tuple, error_msg):
    data_types = add_long_to_data_type_for_python_2(data_types_tuple)
    if not isinstance(datum, data_types):
        return error_msg
    return ''


def check_list_or_tuple_for_types(data_list, data_type_tuple, error_msg):
    if not is_list_or_tuple(data_list):
        return error_msg
    for datum in data_list:
        msg_result = check_datum_for_types(datum, data_type_tuple, 'error')
        if msg_result == 'error':
            return error_msg
    return ''


def check_tuples_in_list_for_types(tuple_list, types_for_each_element, error_msg):
    if not is_list_or_tuple(tuple_list):
        return error_msg
    if tuple_list and not iterable_and_types_same_len(tuple_list, types_for_each_element):
        return error_msg
    for index, element_tuple in enumerate(tuple_list):
        msg_result = check_list_or_tuple_for_types(element_tuple, types_for_each_element[index], 'error')
        if msg_result == 'error':
            return error_msg
    return ''


def check_tuples_in_list_for_type_sequence(tuple_list, data_types_within_each_tuple, error_msg):
    """checks each element of tuple against data_types in list returns error or '' """
    try:
        list_of_uniform_tuples = list(zip(*tuple_list))
    except TypeError:
        return error_msg
    return check_tuples_in_list_for_types(list_of_uniform_tuples, data_types_within_each_tuple, error_msg)


def is_list_or_tuple(iterable):
    return isinstance(iterable, (list, tuple))


def iterable_and_types_same_len(iterable, types_list):
    return len(iterable) == len(types_list)


def check_saved_tables_within_array(save_data_array):
    for data_obj in save_data_array:
        if not isinstance(data_obj, SavedDiceTable):
            return 'error: wrong object in array'
        msg = data_obj.verify_all_types()
        if msg:
            return msg
    return ''


def check_array_is_correct_type(save_data_array):
    if save_data_array.dtype != np.dtype('O'):
        return 'error: wrong array type'
    return ''


def check_saved_tables_array(save_data_array):
    msg = check_array_is_correct_type(save_data_array)
    if msg:
        return msg
    msg = check_saved_tables_within_array(save_data_array)
    if msg:
        return msg
    if save_data_array.size:
        return 'ok'
    else:
        return 'ok: no saved data'


def read_message_and_return_original_or_empty_array(msg, original_object):
    if 'error' in msg:
        return msg, np.array([], dtype=object)
    else:
        return msg, original_object


def write_saved_tables_array(save_data_array):
    """takes a numpy array and writes it"""
    np.save('save_data', save_data_array)


def read_saved_tables_array():
    """tries to find the np file and read it returns a np array and a message"""
    try:
        save_data_array = np.load('save_data.npy')
        msg = check_saved_tables_array(save_data_array)
    except IOError:
        save_data_array = []
        msg = 'error: no file'
    except (UnpicklingError, AttributeError, EOFError, ImportError,
            IndexError, ValueError):
        save_data_array = []
        msg = 'error: file corrupted'
    return read_message_and_return_original_or_empty_array(msg, save_data_array)
