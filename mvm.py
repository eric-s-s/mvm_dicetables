'''model and viewmodel for prototype'''

'''heirarchy = 
TableManager  & DieManager & HistoryManager

GraphBox - TM and self calls update
            depends on HM and TM for display  can affect HM !!! calls GM

ChangeBox - TM calls update
            depends on TM for display  can affect TM
            
AddBox - TM DM calls update
         calls to DM to create and TM to add
         
StatBox - TM calls update
          number choice calls to TM
          
InfoBox - TM calls update'''


from itertools import cycle
from decimal import Decimal

import numpy as np
import matplotlib.pyplot as plt
import file_handler as fh
import dicetables as dt

class TableManager(object):
    '''an object that controls the table'''
    def __init__(self):
        '''just a shell for table'''
        self._table = dt.DiceTable()        
    def request_info(self, request):
        '''returns requested info to child widget'''
        requests = {'range': [self._table.values_range, ()],
                    'mean': [self._table.mean, ()],
                    'stddev': [self._table.stddev, ()],
                    'text': [str, (self._table,)],
                    'text_one_line': [str(self._table).replace, ('\n', ' \\ ')],
                    'weights_info': [self._table.weights_info, ()],
                    'dice_list': [self._table.get_list, ()],
                    'full_text': [dt.full_table_string, (self._table,)],
                    'tuple_list': [self._table.frequency_all, ()]}
        command, args = requests[request]
        return command(*args)
    def request_stats(self, stat_list):
        '''returns stat info from a list'''
        stat_info = list(dt.stats(self._table, stat_list))
        if stat_info[3] != 'infinity' and stat_info[4] == '0.0':
            new_pct = str(100/Decimal(stat_info[3])).split('E')
            stat_info[4] = '{:.3f}e{}'.format(float(new_pct[0]), new_pct[1])
        return tuple(stat_info)            
    def request_plot_obj(self, use_axes):
        '''converts the table into a PlotObject'''
        new_object = {}
        new_object['text'] = self.request_info('text_one_line')        
        graph_pts = dt.graph_pts(self._table, axes=use_axes, exact=False)        
        new_object['x_min'], new_object['x_max'] = self._table.values_range()
        if use_axes:
            y_pts = graph_pts[1]
        else:
            y_pts = [pair[1] for pair in graph_pts]
        new_object['y_min'] = min(y_pts)
        new_object['y_max'] = max(y_pts)
        
        new_object['pts'] = graph_pts
        new_object['tuple_list'] = self.request_info('tuple_list')
        new_object['dice'] = self._table.get_list()
        return new_object
    def request_reload(self, plot_obj):
        '''loads plot_obj as the main die table'''
        self._table = dt.DiceTable()
        for die, number in plot_obj['dice']:
            self._table.update_list(number, die)
        self._table.add(1, plot_obj['tuple_list'])
    def request_add(self, number, die):
        '''adds dice to table'''
        self._table.add_die(number, die)
    def request_remove(self, number, die):
        '''safely removes dice from table. if too many removed, removes all of
        that kind of dice'''
        current = self._table.number_of_dice(die)
        if number > current:
            self._table.remove_die(current, die)
        else:
            self._table.remove_die(number, die)
    def request_reset(self):
        '''reset dice table'''
        self._table = dt.DiceTable()

class HistoryManager(object):
    '''keeps track of plot history and writing'''
    def __init__(self):
        self._history = np.array([], dtype=object)
        
    def add_plot_obj(self, new_obj):
        '''adds a new plot obj'''
        if new_obj not in self._history:
            self._history = np.append(self._history, new_obj)
    def get_obj(self, text, tuple_list):
        '''checks to see if any of the objects in history have tuple_list and text.
        returns that object or if not there, returns empty dict.'''
        new_plot_obj = {}
        for plot_obj in self._history:
            if text == plot_obj['text'] and tuple_list == plot_obj['tuple_list']:
                for key, val in plot_obj.items():
                    if isinstance(val, list):
                        val = val[:]
                    new_plot_obj[key] = val  
        return new_plot_obj   
    def get_labels(self):
        '''returns a list of tuples (plot_obj['text'], plot_obj['tuple_list']) for 
        each plot_obj in history'''
        labels = []
        for obj in self._history:
            labels.append((obj['text'], obj['tuple_list'][:]))
        return labels
    def clear_all(self):
        '''clear graph history'''
        self._history = np.array([], dtype=object)
    def clear_selected(self, obj_list):
        '''clear listed items from graph history'''
        new_history = []
        for obj in self._history:
            if obj not in obj_list:
                new_history.append(obj)
        self._history = np.array(new_history[:], dtype=object)
    def write_history(self):
        fh.write_history_np(self._history)
    def read_history(self):
        msg, self._history = fh.read_history_np()
        return msg

class DieManager(object):
    '''holds a die.  takes input to change it and returns it on request.'''
    def __init__(self):
        '''inits with a 6 sided regular die'''
        self._die = dt.Die(6)
    def input_die(self, size, modifier, multiplier, dictionary):
        '''makes the die into a new die'''
        dice = {'die':dt.Die(size), 'moddie': dt.ModDie(size, modifier)}
        die_key = 'die'
        if dictionary:
            if sum(dictionary.values()) != 0:
                for value in dictionary.values():
                    if value != 1:
                        die_key = 'weighteddie'
                        dice['weighteddie'] = dt.WeightedDie(dictionary)
                        dice['modweighteddie'] = dt.ModWeightedDie(dictionary,
                                                                   modifier)
                        break
        if modifier:
            die_key = 'mod' + die_key
    
        if multiplier:
            self._die =  dt.StrongDie(dice[die_key], multiplier)
        else:
            self._die = dice[die_key]
    def get_die(self):
        '''returns the die as an object'''
        return self._die
    def display_die(self):
        '''returns a string of the die for display'''
        return str(self._die)
    
class GraphBox(object):
    '''manages graphing and history'''
    def __init__(self, table_manager, history_manager, use_axes):
        '''history is a HistoryManager, table_manager is a TableManager.
        use_axes is a boolean - True if the graph uses axes. False if the graph
        uses pts.'''
        self._history = history_manager
        self._table = table_manager
        self.use_axes = use_axes
    def graph_it(self, text_tuple_list_lst):
        '''gets passed a list of tuples containing 'tuple_list' and txt. 'tuple_list' is the 
        'tuple_list' key in a plot object or a tuple_list of a table.  returns objects
        for plotting.  objects are plot_objects.  they are dictionaries.
        to plot, use key=pts and key=text.  also have key=x_min, x_max, y_min,
        y_max'''
        plots = []
        for text, tuple_list  in text_tuple_list_lst:
            to_plot = self._history.get_obj(text, tuple_list)
            if not to_plot:
                to_plot = self._table.request_plot_obj(self.use_axes)
                self._history.add_plot_obj(to_plot)
                self._history.write_history()
            plots.append(to_plot)
        return plots
    def clear_selected(self, text_tuple_list_lst):
        '''gets passed a list of tuples containing 'tuple_list' and txt. 'tuple_list' is the 
        'tuple_list' key in a plot object or a tuple_list of a table. clears the 
        objects from history and writes the history'''
        remove = []
        for text, tuple_list in text_tuple_list_lst:
            to_rm = self._history.get_obj(text, tuple_list)
            if to_rm:
                remove.append(to_rm)
        if remove:
            self._history.clear_selected(remove)
            self._history.write_history()
    def clear_all(self):
        self._history.clear_all()
    def display(self):
        '''returns a tuple for a display output.
        (table_manager_text_and_tuple_list, history_manager.get_labels())'''
        current = (self._table.request_info('text_one_line'), 
                   self._table.request_info(''))

def GraphPopup(object):
    def __init__(self, plot_lst, color_list, style_list):
        '''creates alll the stuff for a plot program'''
        if color_list:
            self.colors = cycle(color_list)
        else:
            self.colors = cycle([''])
        
        if style_list:
            self.styles = cycle(style_list)
        else:
            self.styles = cycle([''])
        
        self.x_range = []
        self.y_range = []
        self.plots = []
        for obj in plot_lst:
            new_obj = {}
            new_obj['pts'] = obj['pts'][:]
        
        

    
            
        
        
            