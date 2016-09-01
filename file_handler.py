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
        return self == DiceTableData('', [(0, 1)], [], [])
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










def _check_dictionary_old(plot_obj):
    '''checks to make sure that plot object is a dictionary with all appropriate
    keys. returns 'error: <details>' or 'ok'.'''
    expected = {'y_range': tuple, 'x_range': tuple, 'text': str,
                'tuple_list': list, 'pts': list, 'dice': list}
    if not isinstance(plot_obj, dict):
        return 'error: not a dict'
    try:
        for key, val_type in expected.items():
            if not isinstance(plot_obj[key], val_type):
                return 'error: {} not {}'.format(key, val_type)
        return 'ok'
    except KeyError:
        return 'error: missing key'


def _check_values_old(plot_obj):
    '''checks all the values are the right kinds.  returns 'error:<details>'
    or 'ok'.'''
    msg = 'error:'

    msg += check_list_for_data_types(plot_obj['x_range'], (int,), ' incorrect x_range')
    msg += check_list_for_data_types(plot_obj['y_range'], (float,), ' incorrect y_range')
    msg += check_tuple_list_for_data_types_within_each_tuple(plot_obj['tuple_list'], [(int,), (int,)],
                                                             ' corrupted "tuple_list"')
    msg += check_tuple_list_for_data_types_within_each_tuple(plot_obj['pts'], [(int,), (float,)],
                                                             ' corrupted "tuple_list"')
    msg += check_tuple_list_for_data_types_within_each_tuple(plot_obj['dice'], [(dt.ProtoDie,), (int,)],
                                                             ' corrupted dice list')

    if msg == 'error:':
        msg = 'ok'
    return msg


def check_data_old(plot_obj):
    '''checks history to see if plot_obj has expected data.  if ok, returns 'ok'
    else returns a msg starting with 'error:' '''
    msg = _check_dictionary_old(plot_obj)
    if msg == 'ok':
        msg = _check_values_old(plot_obj)
    return msg


def check_history_old(history):
    '''checks a history(a non-empty iterable containing plot_objects. to make
    sure it has the correct kind of data. if ok, returns 'ok' else returns a msg
    starting with 'error' '''
    for plot_obj in history:
        msg = check_data_old(plot_obj)
        if 'error:' in msg:
            break
    return msg


def write_history_np_old(history):
    '''takes a numpy array and writes it'''
    np.save('numpy_history', history)


def read_history_np_old():
    '''tries to find the np file and read it returns a np array and a message'''
    empty_hist = np.array([], dtype=object)
    try:
        history = np.load('numpy_history.npy')
        if history.size:
            msg = check_history_old(history)
            if 'error:' in msg:
                history = empty_hist
        else:
            if history.dtype != np.dtype('O'):
                msg = 'error: wrong array type'
                history = empty_hist
            else:
                msg = 'ok: no history'
    except IOError:
        history = empty_hist
        msg = 'error: no file'
    except (UnpicklingError, AttributeError, EOFError, ImportError,
            IndexError, ValueError):
        history = empty_hist
        msg = 'error: file corrupted'
    return msg, history
