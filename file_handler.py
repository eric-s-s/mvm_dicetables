'''for sending and retrieving main info to file'''

# numpy python2 uses cPickle and numpy in python3 uses pickle
from sys import version_info

if version_info[0] > 2:
    from pickle import UnpicklingError
else:
    from cPickle import UnpicklingError

import dicetables as dt
import numpy as np


def _check_dictionary(plot_obj):
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


def is_long(num):
    '''workaround so python2 tests ints and longs and python3 tests ints'''
    try:
        return isinstance(num, (int, long))
    except NameError:
        return isinstance(num, int)


def _check_values(plot_obj):
    '''checks all the values are the right kinds.  returns 'error:<details>'
    or 'ok'.'''
    msg = 'error:'

    msg += confirm_x_range_contains_long_or_int(plot_obj)
    msg += confirm_y_range_contains_floats(plot_obj)
    msg += confirm_tuple_list_contains_long_or_int(plot_obj)
    msg += confirm_pts_contains_int_or_float(plot_obj)
    msg += confirm_dice_contains_int_and_die_obj(plot_obj)
    if msg == 'error:':
        msg = 'ok'
    return msg


def confirm_dice_contains_int_and_die_obj(plot_obj):
    msg = ''
    for die, num in plot_obj['dice']:
        if not isinstance(die, dt.ProtoDie) or not isinstance(num, int):
            msg += ' corrupted dice list'
    return msg


def flatten_tuple_list(data):
    out = []
    for tuples in data:
        out.extend(tuples)
    return out


def confirm_pts_contains_int_or_float(plot_obj):
    msg = ''
    to_test = flatten_tuple_list(plot_obj['pts'])
    for number in to_test:
        if not isinstance(number, (int, float)):
            msg = ' corrupted "pts"'
            break
    return msg


def confirm_tuple_list_contains_long_or_int(plot_obj):
    to_test = flatten_tuple_list(plot_obj['tuple_list'])
    msg = ''
    for number in to_test:
        if not is_long(number):
            msg = ' corrupted "tuple_list"'
            break
    return msg


def confirm_y_range_contains_floats(plot_obj):
    msg = ''
    y_range = plot_obj['y_range']
    for number in y_range:
        if not isinstance(number, float):
            msg = ' incorrect y_range'
            break
    return msg


def confirm_x_range_contains_long_or_int(plot_obj):
    msg = ''
    x_range = plot_obj['x_range']
    for number in x_range:
        if not is_long(number):
            msg = ' incorrect x_range'
            break
    return msg


def check_data(plot_obj):
    '''checks history to see if plot_obj has expected data.  if ok, returns 'ok'
    else returns a msg starting with 'error:' '''
    msg = _check_dictionary(plot_obj)
    if msg == 'ok':
        msg = _check_values(plot_obj)
    return msg


def check_history(history):
    '''checks a history(a non-empty iterable containing plot_objects. to make
    sure it has the correct kind of data. if ok, returns 'ok' else returns a msg
    starting with 'error' '''
    for plot_obj in history:
        msg = check_data(plot_obj)
        if 'error:' in msg:
            break
    return msg


def write_history_np(history):
    '''takes a numpy array and writes it'''
    np.save('numpy_history', history)


def read_history_np():
    '''tries to find the np file and read it returns a np array and a message'''
    empty_hist = np.array([], dtype=object)
    try:
        history = np.load('numpy_history.npy')
        if history.size:
            msg = check_history(history)
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
