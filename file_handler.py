'''for sending and retrieving main info to file. '''

# numpy python2 uses cPickle and numpy in python3 uses pickle
from sys import version_info
if version_info[0] > 2:
    from pickle import UnpicklingError
else:
    from cPickle import UnpicklingError
from itertools import cycle

import dicetables as dt
import numpy as np

class DiceTableData(object):
    def __init__(self, text, tuple_list, dice_list, graph_axes_data):
        """
        text = string, name of table. dice_list = tuple list [(die, number)].
        tuple_list = tuple list of table.frequency_all(), graph_axes_data =  [(x-axis data), (y-axis data)]
        """
        self._text = text
        self._tuple_list = tuple_list
        self._dice_list = dice_list
        self._graph_axes = graph_axes_data
    @classmethod
    def empty_object(cls):
        return cls('', [(0, 1)], [], [])
    def get_graph_axes(self):
        return self._graph_axes[:]
    def get_graph_pts(self):
        return list(zip(*self._graph_axes))
    def get_x_range(self):
        return min(self._graph_axes[0]), max(self._graph_axes[0])
    def get_y_range(self):
        return min(self._graph_axes[1]), max(self._graph_axes[1])
    def get_tuple_list(self):
        return self._tuple_list[:]
    def get_text(self):
        return self._text
    def get_copy(self):
        return DiceTableData(self._text, self._tuple_list[:], self._dice_list[:], self._graph_axes[:])
    def get_dice_table(self):
        new_table = dt.DiceTable()
        new_table.add(1, self._tuple_list)
        for die, number in self._dice_list:
            new_table.update_list(number, die)
        return new_table
    def __eq__(self, other):
        return self.get_text() == other.get_text() and self.get_tuple_list() == other.get_tuple_list()
    def __ne__(self, other):
        return not self == other
    def is_empty_object(self):
        return self == DiceTableData.empty_object()
    def match_by_text_and_tuples(self, text, tuple_list):
        return self.get_text() == text and self.get_tuple_list() == tuple_list
    def verify_all_data(self):
        msg = 'error:'
        msg += check_datum_for_data_types(self._text, (str,), ' invalid text value')
        msg += check_tuple_list_for_data_types_within_each_tuple(self._tuple_list, [(int,), (int,)],
                                                                 ' invalid tuple list')
        msg += check_tuple_list_for_data_types_within_each_tuple(self._dice_list, [(dt.ProtoDie,), (int,)],
                                                                 ' invalid dice list')
        msg += check_tuple_list_for_data_types_by_tuple(self._graph_axes, [(int,), (float,)], ' invalid graph values')
        if msg == 'error:':
            return ''
        else:
            return msg

def python_2_to_3_control_for_longs_and_int(data_type_tuple):
    if version_info[0] < 3 and int in data_type_tuple:
        return data_type_tuple + (long,)
    else:
        return data_type_tuple

def check_datum_for_data_types(datum, data_types_tuple, error_msg):
    data_types = python_2_to_3_control_for_longs_and_int(data_types_tuple)
    if not isinstance(datum, data_types):
        return error_msg
    return ''

def check_list_for_data_types(data_list, data_type_tuple, error_msg):
    if not np.iterable(data_list):
        return error_msg
    for datum in data_list:
        msg_result = check_datum_for_data_types(datum, data_type_tuple, 'error')
        if msg_result == 'error':
            return error_msg
    return ''

def check_tuple_list_for_data_types_by_tuple(tuple_list, data_types_for_each_tuple, error_msg):
    if not np.iterable(tuple_list):
        return error_msg
    data_types_cycle = cycle(data_types_for_each_tuple)
    for element_tuple in tuple_list:
        msg_result = check_list_for_data_types(element_tuple, next(data_types_cycle), 'error')
        if msg_result == 'error':
            return error_msg
    return ''

def check_tuple_list_for_data_types_within_each_tuple(tuple_list, data_types_within_each_tuple, error_msg):
    """checks each element of tuple against data_types in list returns error or '' """
    try:
        iterable_uniform_tuples = zip(*tuple_list)
    except TypeError:
        return error_msg
    return check_tuple_list_for_data_types_by_tuple(iterable_uniform_tuples, data_types_within_each_tuple, error_msg)


def check_data_objects_in_save_data(save_data_array):
    for data_obj in save_data_array:
        if not isinstance(data_obj, DiceTableData):
            return 'error: wrong object in array'
        msg = data_obj.verify_all_data()
        if msg:
            return msg
    return ''

def check_data_array_is_correct_type(save_data_array):
    if save_data_array.dtype != np.dtype('O'):
        return 'error: wrong array type'
    return ''

def check_save_data_array(save_data_array):
    msg = check_data_array_is_correct_type(save_data_array)
    if msg:
        return msg
    msg = check_data_objects_in_save_data(save_data_array)
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


def write_save_data(save_data_array):
    '''takes a numpy array and writes it'''
    np.save('save_data', save_data_array)


def read_save_data():
    '''tries to find the np file and read it returns a np array and a message'''
    try:
        save_data_array = np.load('save_data.npy')
        msg = check_save_data_array(save_data_array)
    except IOError:
        save_data_array = []
        msg = 'error: no file'
    except (UnpicklingError, AttributeError, EOFError, ImportError,
            IndexError, ValueError):
        save_data_array = []
        msg = 'error: file corrupted'
    return read_message_and_return_original_or_empty_array(msg, save_data_array)

