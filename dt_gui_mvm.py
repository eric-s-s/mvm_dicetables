'''model and viewmodel for prototype'''

from __future__ import absolute_import

from decimal import Decimal

import dicetables as dt
import numpy as np
import filehandler as fh


class DiceTableManager(object):
    '''an object that controls the table'''

    def __init__(self):
        '''just a shell for table'''
        self._table = dt.DiceTable()

    def get_info(self, request):
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

    def get_stats(self, stat_list):
        '''returns stat info from a list of ints'''
        stat_info = list(dt.stats(self._table, stat_list))
        if stat_info[3] != 'infinity' and stat_info[4] == '0.0':
            tiny_percent = Decimal('1.0e+2') / Decimal(stat_info[3])
            stat_info[4] = '{:.3e}'.format(tiny_percent)
        return tuple(stat_info)

    def get_obj_to_save(self):
        """converts the table into a PlotObject"""
        text = self.get_info('text_one_line')
        graph_data = dt.graph_pts(self._table)
        tuple_list = self.get_info('tuple_list')
        dice_list = self.get_info('dice_list')
        return fh.SavedDiceTable(text, tuple_list, dice_list, graph_data)

    def request_reload(self, data_obj):
        """loads data_obj as the main die table"""
        self._table = data_obj.dice_table

    def request_add(self, number, die):
        '''adds dice to table. number is int>=0. die is child of dt.ProtoDie'''
        self._table.add_die(number, die)

    def request_remove(self, number, die):
        '''safely removes dice from table. if too many removed, removes all of
        that kind of dice. number is int>=0. die is child of dt.ProtoDie.'''
        max_allowed = self._table.number_of_dice(die)
        self._table.remove_die(min(number, max_allowed), die)

    def request_reset(self):
        """reset dice table"""
        self._table = dt.DiceTable()


class SavedTablesManager(object):
    """keeps track of plot history and writing"""

    def __init__(self):
        self._saved_tables = np.array([], dtype=object)

    def save_new(self, new_obj):
        """adds a new plot obj. will not add empty table or duplicates"""
        if not new_obj.is_empty() and new_obj not in self._saved_tables:
            self._saved_tables = np.append(self._saved_tables, new_obj)

    def get_old(self, text, tuple_list):
        """checks to see if any of the objects in history have tuple_list and
        text. returns that object or if not there, returns empty dict."""
        dummy_saved_table = fh.SavedDiceTable(text, tuple_list, [], [])
        for data_obj in self._saved_tables:
            if dummy_saved_table == data_obj:
                return data_obj
        return fh.SavedDiceTable.empty_object()

    def get_labels(self):
        """returns a list of tuples (plot_obj['text'], plot_obj['tuple_list'])
        for each plot_obj in history"""
        labels = []
        for obj in self._saved_tables:
            labels.append((obj.text, obj.tuple_list))
        return labels

    def get_graphs(self, get_axes_not_pts=True):
        """returns ((x_range of history), (y_range of history),
                    [(graph_text, [graph_values]), -> for each obj in history])
                    :param get_axes_not_pts:
        """
        list_of_graphs = []
        x_range = y_range = (float('inf'), float('-inf'))
        for obj in self._saved_tables:
            x_range = combine_ranges(obj.x_range, x_range)
            y_range = combine_ranges(obj.y_range, y_range)
            if get_axes_not_pts:
                graph_data = obj.graph_axes
            else:
                graph_data = obj.graph_pts
            list_of_graphs.append((obj.text, graph_data))
        return x_range, y_range, list_of_graphs

    def clear_all(self):
        """clear graph history"""
        self._saved_tables = np.array([], dtype=object)

    def clear_selected(self, obj_list):
        """clear listed items from graph history. obj_list is a list of plot
        objects"""
        new_data_array = np.array([], dtype=object)
        for obj in self._saved_tables:
            if obj not in obj_list:
                new_data_array = np.append(new_data_array, obj)
        self._saved_tables = new_data_array

    def write_to_file(self):
        '''overwrites graph history to 'numpy_history.npy' '''
        fh.write_saved_tables_array(self._saved_tables)

    def reload_from_file(self):
        '''reads from 'numpy_history.npy' and checks for errors. returns a msg
        that is either "ok" or begins with "error" '''
        msg, self._saved_tables = fh.read_saved_tables_array()
        return msg


def combine_ranges(range_1, range_2):
    new_range = (min(range_2[0], range_1[0]),
                 max(range_2[1], range_1[1]))
    return new_range


class GraphBox(object):
    '''manages graphing and history'''

    def __init__(self, table_manager, saved_tables, use_axes):
        '''history is a SavedTablesManager, table_manager is a DiceTableManager.
        _use_axes is a boolean - True if the graph uses axes. False if the graph
        uses pts.'''
        self._saved_tables = saved_tables
        self._table = table_manager
        self._use_axes = use_axes

    def get_requested_graphs(self, list_of_texts_and_tuple_lists):
        """gets passed a list of tuples containing (text, tuple_list).
        text=str of table, tuple_list=[(roll=int, val=int), ...]
        returns ( (x_range), (y_range), [(text, [graphing_values])...] )"""
        manage_empties_and_duplicates = SavedTablesManager()
        for text, tuple_list in list_of_texts_and_tuple_lists:
            to_plot = self._saved_tables.get_old(text, tuple_list)
            if to_plot.is_empty():
                to_plot = self.verify_current_and_retrieve(text, tuple_list)
            manage_empties_and_duplicates.save_new(to_plot)
        return manage_empties_and_duplicates.get_graphs(self._use_axes)

    def verify_current_and_retrieve(self, text, tuple_list):
        if (text, tuple_list) == self.display_current_table():
            return self.get_and_save_current_table()
        return fh.SavedDiceTable.empty_object()

    def get_and_save_current_table(self):
        new_to_save = self._table.get_obj_to_save()
        self._saved_tables.save_new(new_to_save)
        self._saved_tables.write_to_file()
        return new_to_save

    def clear_selected(self, text_tuple_list_lst):
        '''gets passed a list of tuples containing 'tuple_list' and txt.
        'tuple_list' is the 'tuple_list' key in a plot object or a
        tuple_list of a table. clears the objects from history and writes
        the history'''
        remove = []
        for text, tuple_list in text_tuple_list_lst:
            remove.append(fh.SavedDiceTable(text, tuple_list, [], []))
        self._saved_tables.clear_selected(remove)
        self._saved_tables.write_to_file()

    def clear_all(self):
        '''clears the history'''
        self._saved_tables.clear_all()
        self._saved_tables.write_to_file()

    def display_current_table(self):
        return self._table.get_info('text_one_line'), self._table.get_info('tuple_list')

    def display_save_data(self):
        return self._saved_tables.get_labels()

    def display(self):
        '''returns a tuple for a display output.
        (table_manager_text_and_tuple_list, history_manager.get_labels())'''
        return self.display_current_table(), self.display_save_data()

    def reload_saved_dice_table(self, text, tuple_list):
        '''takes a text, tuple_list and reloads that to table_manager'''
        data_obj = self._saved_tables.get_old(text, tuple_list)
        if not data_obj.is_empty():
            self._table.request_reload(data_obj)


def get_die_roll_details(die):
    details = '{} rolls:'.format(die)
    lengths_of_strings_for_rolls = [len(str(pair[0])) for pair in die.tuple_list()]
    max_number_length = max(lengths_of_strings_for_rolls)
    for roll, freq in die.tuple_list():
        details += '\n  {:>{}} with frequency: {}'.format(roll, max_number_length, freq)
    return details


def get_add_and_remove_labels(die, number, enable_remove):
    """returns a list of texts in appropriate order for display on buttons
    and labels. die is a child of dt.ProtoDie. number is an int>=0.
    enable_remove is a bool. see AddBox.display_die and ChangeBox.display"""
    display = []
    add_choices = get_add_list(die)
    if enable_remove:
        for num in add_choices[::-1]:
            display.append(str(-1 * num))
    if number == 0:
        display.append(str(die))
    else:
        display.append(die.multiply_str(number))

    for num in add_choices:
        display.append('{:+}'.format(num))
    return display


def get_add_list(die):
    max_size_for_add_choice = [(10000, 1), (100, 5), (50, 10), (25, 50), (16, 100), (6, 500)]
    available_choices = []
    for max_size, add_choice in max_size_for_add_choice:
        if die.get_size() <= max_size:
            available_choices.append(add_choice)
    return available_choices


class ChangeBox(object):
    '''controls changing the number of dice already in the table'''

    def __init__(self, table_manager):
        '''table_manager is a DiceTableManager'''
        self._table = table_manager

    def get_dice_details(self):
        info_list = []
        for pair in self._table.get_info('dice_list'):
            info_list.append(get_die_roll_details(pair[0]))
        return info_list

    def display(self):
        '''returns a list of tuples (list_of_button/labels, die associated with
        that list) derived from current stat of table'''
        display = []
        for die, number in self._table.get_info('dice_list'):
            add_rm_display = get_add_and_remove_labels(die, number, True)
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
    if not dictionary:
        dictionary = {1: 0}
    dice = {'Die': dt.Die(size),
            'ModDie': dt.ModDie(size, modifier),
            'WeightedDie': dt.WeightedDie(dictionary),
            'ModWeightedDie': dt.ModWeightedDie(dictionary, modifier)}
    die_key = 'Die'
    if is_dictionary_for_weighted_die(dictionary):
        die_key = 'WeightedDie'
    if modifier:
        die_key = 'Mod' + die_key

    if multiplier > 1:
        return dt.StrongDie(dice[die_key], multiplier)
    else:
        return dice[die_key]


def is_dictionary_for_weighted_die(dictionary):
    if sum(dictionary.values()) != 0:
        for value in dictionary.values():
            if not value == 1:
                return True
    return False


class AddBox(object):
    '''selects and adds new dice to a table'''

    def __init__(self, table_manager):
        '''takes a DiceTableManager and a DieManager.  self.presets is a list of
        preset die labels'''
        self._table = table_manager
        self._size = 6
        self._mod = 0
        self._multiplier = 0
        self._dictionary = {}
        self._die = dt.Die(6)
        self.presets = ['D{}'.format(die) for die in
                        (2, 4, 6, 8, 10, 12, 20, 100)]

    def get_die(self):
        '''returns the die object'''
        return self._die

    def get_die_details(self):
        return get_die_roll_details(self._die)

    def display_die(self):
        '''returns a set of add values and str(die) for the bottom display
        [die_sting, '+number' strings]'''
        return get_add_and_remove_labels(self._die, 0, False)

    def display_current(self):
        '''displays the table info'''
        return self._table.get_info('text_one_line')

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
        '''simply inits with a DiceTableManager'''
        self._table = table_manager

    def display(self, val_1, val_2):
        '''val_1 and val_2 are ints passed from the stat sliders.
        returns a list of info. [info_text, stat_text,(new_val_1, new_val_2)
                                 (val_min, val_max)]
        for displaying updates when info changes.'''
        val_min, val_max = self._table.get_info('range')
        mean = self._table.get_info('mean')
        stddev = self._table.get_info('stddev')
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
        val_min, val_max = self._table.get_info('range')

        val_1 = min(val_max, max(val_min, val_1))
        val_2 = min(val_max, max(val_min, val_2))

        stat_list = list(range(min(val_1, val_2), max(val_1, val_2) + 1))
        stat_info = self._table.get_stats(stat_list)
        stat_text = ('\n    {stat[0]} occurred {stat[1]} times\n' +
                     '    out of {stat[2]} total combinations\n\n' +
                     '    that\'s a one in {stat[3]} chance\n' +
                     '    or {stat[4]} percent')
        return [stat_text.format(stat=stat_info), (val_1, val_2)]


class InfoBox(object):
    '''displays long info about object. can also display long info as page
    views.'''

    def __init__(self, table_manager):
        '''simply inits with a DiceTableManager'''
        self._table = table_manager
        self._current_page = {'full_text': 1, 'weights_info': 1}
        self._lines_per_page = {'full_text': 1, 'weights_info': 1}
        self._pages = {'full_text': [''], 'weights_info': ['']}

    def _parse_info(self, key):
        '''key = 'weights_info' or 'full_text'. preps text. returns new text'''
        text = self._table.get_info(key).rstrip('\n')
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
        vals_min, vals_max = self._table.get_info('range')
        mean = self._table.get_info('mean')
        stddev = self._table.get_info('stddev')
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
        return [self._general_info(), self._table.get_info('text'),
                self.display_current_page('weights_info', weights_lines),
                self.display_current_page('full_text', full_text_lines)]

    def display(self):
        '''returns [general_info, table_str, weights_info, full_text].
        here weights_info and full_text are not page_views.  this is for a
        scrolling display.'''
        return [self._general_info(), self._table.get_info('text'),
                self._parse_info('weights_info'), self._parse_info('full_text')]
