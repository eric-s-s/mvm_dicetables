'''for sending and retrieving main info to file'''

from cPickle import UnpicklingError
import dicetables as dt
import numpy as np

def _check_dictionary(plot_obj):
    '''checks to make sure that plot object is a dictionary with all appropriate
    keys. returns 'error: <details>' or 'ok'.'''
    expected = {'y_range':tuple, 'x_range': tuple, 'text':str,
                'tuple_list':list, 'pts':list, 'dice':list}
    if not isinstance(plot_obj, dict):
        return 'error: not a dict'
    try:
        for key, val_type in expected.items():
            if not isinstance(plot_obj[key], val_type):
                return 'error: {} not {}'.format(key, val_type)
        return 'ok'
    except KeyError:
        return 'error: missing key'
def _check_values(plot_obj):
    '''checks all the values are the right kinds.  returns 'error:<details>'
    or 'ok'.'''
    msg = 'error:'
    x_min, x_max = plot_obj['x_range']
    y_min, y_max = plot_obj['y_range']
    if (not isinstance(x_min, (int, long)) or
            not isinstance(x_max, (int, long))):
        msg += ' incorrect x_range'
    if not isinstance(y_min, float) or not isinstance(y_max, float):
        msg += ' incorrect y_range'
    for freq, val in plot_obj['tuple_list']:
        if (not isinstance(freq, (int, long)) or
                not isinstance(val, (int, long))):
            msg += ' corrupted "tuple_list"'
    for tuple_ in plot_obj['pts']:
        for val in tuple_:
            if not isinstance(val, (int, float)):
                msg += ' corrupted "pts"'
    for die, num in plot_obj['dice']:
        if not isinstance(die, dt.ProtoDie) or not isinstance(num, int):
            msg += ' dicelist at ({!r}, {})'.format(die, num)
    if msg == 'error:':
        msg = 'ok'
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
            IndexError):
        history = empty_hist
        msg = 'error: file corrupted'
    return msg, history

