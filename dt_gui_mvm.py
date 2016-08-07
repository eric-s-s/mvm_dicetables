'''model and viewmodel for prototype'''

from __future__ import absolute_import


from decimal import Decimal

import dicetables as dt
import numpy as np
import file_handler as fh

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
        '''returns stat info from a list of ints'''
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
        new_object['x_range'] = self._table.values_range()
        if use_axes:
            y_pts = graph_pts[1]
        else:
            y_pts = [pair[1] for pair in graph_pts]
        new_object['y_range'] = (min(y_pts), max(y_pts))
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
        '''adds dice to table. number is int>=0. die is child of dt.ProtoDie'''
        self._table.add_die(number, die)
    def request_remove(self, number, die):
        '''safely removes dice from table. if too many removed, removes all of
        that kind of dice. number is int>=0. die is child of dt.ProtoDie.'''
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
        '''adds a new plot obj. will not add empty table or duplicates'''
        def not_empty_obj(obj):
            '''returns bool. tests if plot_object is empty'''
            return bool(obj['text']) and obj['tuple_list'] != [(0, 1)]
        if new_obj not in self._history and not_empty_obj(new_obj):
            self._history = np.append(self._history, new_obj)
    def get_obj(self, text, tuple_list):
        '''checks to see if any of the objects in history have tuple_list and
        text. returns that object or if not there, returns empty dict.'''
        new_plot_obj = {}
        for plot_obj in self._history:
            if (text == plot_obj['text'] and
                    tuple_list == plot_obj['tuple_list']):
                for key, val in plot_obj.items():
                    if isinstance(val, list):
                        val = val[:]
                    new_plot_obj[key] = val
        return new_plot_obj
    def get_labels(self):
        '''returns a list of tuples (plot_obj['text'], plot_obj['tuple_list'])
        for each plot_obj in history'''
        labels = []
        for obj in self._history:
            labels.append((obj['text'], obj['tuple_list'][:]))
        return labels
    def get_graphs(self):
        '''returns ((x_range of history), (y_range of history),
                    [(graph_text, [graph_values]), -> for each obj in history])
        '''
        out = []
        x_range = y_range = (float('inf'), float('-inf'))
        for obj in self._history:
            x_range = (min(x_range[0], obj['x_range'][0]),
                       max(x_range[1], obj['x_range'][1]))
            y_range = (min(y_range[0], obj['y_range'][0]),
                       max(y_range[1], obj['y_range'][1]))
            out.append((obj['text'], obj['pts'][:]))
        return (x_range, y_range, out)
    def clear_all(self):
        '''clear graph history'''
        self._history = np.array([], dtype=object)
    def clear_selected(self, obj_list):
        '''clear listed items from graph history. obj_list is a list of plot
        objects'''
        new_history = []
        for obj in self._history:
            if obj not in obj_list:
                new_history.append(obj)
        self._history = np.array(new_history[:], dtype=object)
    def write_history(self):
        '''overwrites graph history to 'numpy_history.npy' '''
        fh.write_history_np(self._history)
    def read_history(self):
        '''reads from 'numpy_history.npy' and checks for errors. returns a msg
        that is either "ok" or begins with "error" '''
        msg, self._history = fh.read_history_np()
        return msg

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
        '''gets passed a list of tuples containing (text, tuple_list).
        text=str of table, tuple_list=[(roll=int, val=int), ...]
        returns ( (x_range), (y_range), [(text, [graphing_values])...] )'''
        #history manager has built-in measures for duplicates and empties
        temp = HistoryManager()
        for text, tuple_list  in text_tuple_list_lst:
            to_plot = self._history.get_obj(text, tuple_list)
            if not to_plot:
                to_plot = self._table.request_plot_obj(self.use_axes)
                self._history.add_plot_obj(to_plot)
                self._history.write_history()
            temp.add_plot_obj(to_plot)
        return temp.get_graphs()
    def clear_selected(self, text_tuple_list_lst):
        '''gets passed a list of tuples containing 'tuple_list' and txt.
        'tuple_list' is the 'tuple_list' key in a plot object or a
        tuple_list of a table. clears the objects from history and writes
        the history'''
        remove = []
        for text, tuple_list in text_tuple_list_lst:
            to_rm = self._history.get_obj(text, tuple_list)
            if to_rm:
                remove.append(to_rm)
        if remove:
            self._history.clear_selected(remove)
            self._history.write_history()
    def clear_all(self):
        '''clears the history'''
        self._history.clear_all()
        self._history.write_history()
    def display(self):
        '''returns a tuple for a display output.
        (table_manager_text_and_tuple_list, history_manager.get_labels())'''
        current = (self._table.request_info('text_one_line'),
                   self._table.request_info('tuple_list'))
        return current, self._history.get_labels()
    def reload(self, text, tuple_list):
        '''takes a text, tuple_list and reloads that to table_manager'''
        plot_obj = self._history.get_obj(text, tuple_list)
        if plot_obj:
            self._table.request_reload(plot_obj)


def get_add_rm(die, number, enable_remove):
    '''returns a list of texts in appropriate order for display on buttons
    and labels. die is a child of dt.ProtoDie. number is an int>=0.
    enable_remove is a bool. see AddBox.display_die and ChangeBox.display'''
    display = []
    size_and_max = [(6, 500), (16, 100), (50, 50), (100, 5), (10000, 1)]
    add_choices = [1, 5, 10, 50, 100, 500]
    for size, add_num in size_and_max:
        if die.get_size() <= size:
            max_add = add_num
            break
    if enable_remove:
        for num in add_choices[::-1]:
            if num <= max_add:
                display.append(str(-1 * num))

    if number == 0:
        display.append(str(die))
    else:
        display.append(die.multiply_str(number))

    for num in add_choices:
        if num <= max_add:
            display.append('{:+}'.format(num))
    return display

class ChangeBox(object):
    '''controls changing the number of dice already in the table'''
    def __init__(self, table_manager):
        '''table_manager is a TableManager'''
        self._table = table_manager
    def display(self):
        '''returns a list of tuples (list_of_button/labels, die associated with
        that list) derived from current stat of table'''
        display = []
        for die, number in self._table.request_info('dice_list'):
            add_rm_display = get_add_rm(die, number, True)
            display.append((add_rm_display, die))
        return display
    def add_rm(self, number, die):
        '''number is an int  die is a child of dt.ProtoDie'''
        if number < 0:
            self._table.request_remove(abs(number), die)
        else:
            self._table.request_add(number, die)
    def reset(self):
        '''resets the table back to empty'''
        self._table.request_reset()


def make_die(size, modifier, multiplier, dictionary):
    '''makes the die into a new die. IMPORTANT!! dictionary supercedes size
    so if size is 6 and dictionary is {1:1, 2:4}, then die is made according
    to dictionary.  size-int>0, modifier-int, multiplier-int>=0.'''
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

    if multiplier > 1:
        return dt.StrongDie(dice[die_key], multiplier)
    else:
        return dice[die_key]

class AddBox(object):
    '''selects and adds new dice to a table'''
    def __init__(self, table_manager):
        '''takes a TableManager and a DieManager.  self.presets is a list of
        preset die labels'''
        self._table = table_manager
        self._size = 6
        self._mod = 0
        self._multiplier = 0
        self._dictionary = {}
        self._die = dt.Die(6)
        self.presets = ['D{}'.format(die) for die in
                        (2, 4, 6, 8, 10, 12, 20, 100)]
    def display_die(self):
        '''returns a set of add values and str(die) for the bottom display
        [die_sting, '+number' strings]'''
        return get_add_rm(self._die, 0, False)
    def display_current(self):
        '''displays the table info'''
        return self._table.request_info('text_one_line')
    def add(self, number):
        '''number is an int >=0. adds to the table_manager'''
        self._table.request_add(number, self._die)
    def _update_die(self):
        '''updates the die. make_die at line 233'''
        self._die = make_die(self._size, self._mod, self._multiplier,
                             self._dictionary)
    def set_size(self, new_size):
        '''size is int >=1 sets new size and refreshes the die'''
        self._dictionary = {}
        self._size = new_size
        self._update_die()
    def set_mod(self, new_mod):
        '''mod is an int. sets new die modifier and refreshes the die'''
        self._mod = new_mod
        self._update_die()
    def set_multiplier(self, new_val):
        '''new_val is an int >=0 sets new multiplier and refreshes the die'''
        self._multiplier = new_val
        self._update_die()
    def get_weights_text(self):
        '''returns a list of texts for making a weights popup'''
        texts = []
        for roll in range(1, self._size + 1):
            texts.append('weight for {}'.format(roll))
        return texts
    def record_weights_text(self, text_val_lst):
        '''takes a list of tuples(text, weightvalues) and makes a dictionary.
        text is format 'weight for {}'.format(roll).  weightvalue is int >=0
        roll is int >= 1'''
        self._dictionary = {}
        for text, weight in text_val_lst:
            roll = int(text[len('weight for '):])
            self._dictionary[roll] = weight
        self._update_die()


class StatBox(object):
    '''gets stats for table and displays.'''
    def __init__(self, table_manager):
        '''simply inits with a TableManager'''
        self._table = table_manager
    def display(self, val_1, val_2):
        '''val_1 and val_2 are ints passed from the stat sliders.
        returns a list of info. [info_text, stat_text,(new_val_1, new_val_2)
                                 (val_min, val_max)]
        for displaying updates when info changes.'''
        val_min, val_max = self._table.request_info('range')
        mean = self._table.request_info('mean')
        stddev = self._table.request_info('stddev')
        info_text = (
            'the range of numbers is {:,}-{:,}\n'.format(val_min, val_max) +
            'the mean is {:,}\nthe stddev is {}'.format(round(mean, 4), stddev)
            )
        stat_text, values = self.display_stats(val_1, val_2)
        return [info_text, stat_text, values, (val_min, val_max)]
    def display_stats(self, val_1, val_2):
        '''val_1 and val_2 are ints. returns a list
        [text showing stats for all rolls between and including vals,
         (new_val_1, new_val_2), (val_min, val_max)]'''
        val_min, val_max = self._table.request_info('range')

        val_1 = min(val_max, max(val_min, val_1))
        val_2 = min(val_max, max(val_min, val_2))

        stat_list = list(range(min(val_1, val_2), max(val_1, val_2) + 1))
        stat_info = self._table.request_stats(stat_list)
        stat_text = ('\n    {stat[0]} occurred {stat[1]} times\n'+
                     '    out of {stat[2]} total combinations\n\n'+
                     '    that\'s a one in {stat[3]} chance\n'+
                     '    or {stat[4]} percent')
        return [stat_text.format(stat=stat_info), (val_1, val_2)]

class InfoBox(object):
    '''displays long info about object. can also display long info as page
    views.'''
    def __init__(self, table_manager):
        '''simply inits with a TableManager'''
        self._table = table_manager
        self._current_page = {'full_text': 1, 'weights_info': 1}
        self._lines_per_page = {'full_text': 1, 'weights_info': 1}
        self._pages = {'full_text': [''], 'weights_info': ['']}
    def _parse_info(self, key):
        '''key = 'weights_info' or 'full_text'. preps text. returns new text'''
        text = self._table.request_info(key).rstrip('\n')
        if key == 'weights_info':
            text = text.replace('a roll of ', '')
            text = text.replace(' a ', ' ')
            text = text.replace(' of ', ': ')
        return text
    def make_pages(self, key, lines_per_page):
        '''makes a list of pages so that pages can be quickly referenced'''
        text = self._parse_info(key)
        lines = text.split('\n')
        self._lines_per_page[key] = lines_per_page
        self._pages[key] = []
        while len(lines) > lines_per_page:
            self._pages[key].append('\n'.join(lines[:lines_per_page]))
            lines = lines[lines_per_page:]
        for _ in range(lines_per_page - len(lines)):
            lines.append(' ')
        if lines:
            self._pages[key].append('\n'.join(lines))
    def display_current_page(self, key, lines_per_page):
        '''key is 'full_text' or 'weights_info'.  lines_per_page = int > 1.
        checks if the number of pages changed, if so recalculates pages.
        current page uses modulo, so can loop through any values.
        returns (page_text, current_page_number, total_pages_number).'''
        if self._lines_per_page[key] != lines_per_page:
            self.make_pages(key, lines_per_page)
        total_pages = len(self._pages[key])
        if total_pages == 0:
            total_pages = 1
        page_num = self._current_page[key] % total_pages
        if page_num == 0:
            page_num = total_pages
        page = self._pages[key][page_num - 1]
        self._current_page[key] = page_num
        return (page, page_num, total_pages)

    def display_next_page(self, key, lines_per_page):
        '''lines_per_page is int > 1. key is 'weights_info' or 'full_text'.
        updates current_page += 1. loops from last to first page.
        returns new self.display_current_page.'''
        self._current_page[key] += 1
        return self.display_current_page(key, lines_per_page)
    def display_previous_page(self, key, lines_per_page):
        '''lines_per_page is int > 1. key is 'weights_info' or 'full_text'.
        updates current_page += 1. loops from first to last page.
        returns new self.display_current_page.'''
        self._current_page[key] -= 1
        return self.display_current_page(key, lines_per_page)
    def display_chosen_page(self, page_number, key, lines_per_page):
        '''lines_per_page is int > 1. key is 'weights_info' or 'full_text'.
        self._current_page[key] = page_number
        return self.display_current_page(key, lines_per_page)'''
        self._current_page[key] = page_number
        return self.display_current_page(key, lines_per_page)

    def _general_info(self):
        '''returns a string of some general info'''
        vals_min, vals_max = self._table.request_info('range')
        mean = self._table.request_info('mean')
        stddev = self._table.request_info('stddev')
        text = (
            'the range of numbers is {:,}-{:,}\n'.format(vals_min, vals_max) +
            'the mean is {:,}\nthe stddev is {}'.format(round(mean, 4), stddev)
            )
        return text
    def display_paged(self, weights_lines, full_text_lines):
        '''weights_lines and full_text_lines are ints > 1 = lines_per_page
        for weights_info and full_text.  updates pages and
        returns [general_info, table_str, (weights_info), (full_text)]'''
        self.make_pages('weights_info', weights_lines)
        self.make_pages('full_text', full_text_lines)
        return [self._general_info(), self._table.request_info('text'),
                self.display_current_page('weights_info', weights_lines),
                self.display_current_page('full_text', full_text_lines)]
    def display(self):
        '''returns [general_info, table_str, weights_info, full_text].
        here weights_info and full_text are not page_views.  this is for a
        scrolling display.'''
        return [self._general_info(), self._table.request_info('text'),
                self._parse_info('weights_info'), self._parse_info('full_text')]

