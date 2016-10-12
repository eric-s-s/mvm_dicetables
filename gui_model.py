"""model and viewmodel for prototype"""

from __future__ import absolute_import

from decimal import Decimal

try:
    from itertools import izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest
import dicetables as dt
import numpy as np
import filehandler as fh
from textcalc import TextCalculator


class DiceTableManager(object):
    """easy management of a DiceTable

    :properties: stddev, mean, range, title\n
        title_one_line, full_text\n
        weights_info, tuple_list, dice_list"""

    def __init__(self):
        self._table = dt.DiceTable()

    @property
    def stddev(self):
        return self._table.stddev()

    @property
    def mean(self):
        return self._table.mean()

    @property
    def range(self):
        return self._table.values_range()

    @property
    def title(self):
        return str(self._table)

    @property
    def title_one_line(self):
        return str(self._table).replace('\n', ' \\ ')

    @property
    def full_text(self):
        return dt.full_table_string(self._table)

    @property
    def weights_info(self):
        return self._table.weights_info()

    @property
    def dice_list(self):
        return self._table.get_list()

    @property
    def tuple_list(self):
        return self._table.frequency_all()

    def get_description_range_mean_stddev(self):
        info_text = (
            'the range of numbers is {:,}-{:,}\n'.format(*self.range) +
            'the mean is {:,}\nthe stddev is {}'.format(round(self.mean, 4), self.stddev)
        )
        return info_text

    def get_stats(self, input_list):
        """

        :param input_list: list of ints
        :return: tuple of strings
            [input_list str, total combinations,
            input combinations, inverse chance,
            pct chance]
        """
        the_list, total, combinations, inv_chance, pct = dt.stats(self._table, input_list)
        if pct == '0.0' and inv_chance != 'infinity':
            tiny_pct = Decimal('1.0e+2') / Decimal(inv_chance)
            pct = '{:.3e}'.format(tiny_pct)
        return the_list, total, combinations, inv_chance, pct

    def get_obj_to_save(self):
        title = self.title_one_line
        graph_data = dt.graph_pts(self._table)
        tuple_list = self.tuple_list
        dice_list = self.dice_list
        return fh.SavedDiceTable(title, tuple_list, dice_list, graph_data)

    def request_reload(self, saved_dice_table):
        self._table = saved_dice_table.dice_table

    def request_add(self, number, die):
        self._table.add_die(number, die)

    def request_remove(self, number, die):
        max_allowed = self._table.number_of_dice(die)
        self._table.remove_die(min(number, max_allowed), die)

    def request_reset(self):
        self._table = dt.DiceTable()


class SavedTables(object):
    """manages all filehandler.SavedDiceTable

    read and write from 'save_data.npy' """

    def __init__(self):
        self._saved_tables = np.array([], dtype=object)

    def save_new(self, saved_dice_table):
        """won't save empties or duplicates"""
        if not saved_dice_table.is_empty() and saved_dice_table not in self._saved_tables:
            self._saved_tables = np.append(self._saved_tables, saved_dice_table)

    def has_requested(self, title, tuple_list):
        """
        :return: bool
        """
        return fh.SavedDiceTable(title, tuple_list, [], []) in self._saved_tables

    def get_requested(self, title, tuple_list):
        dummy_saved_table = fh.SavedDiceTable(title, tuple_list, [], [])
        for data_obj in self._saved_tables:
            if dummy_saved_table == data_obj:
                return data_obj
        return fh.SavedDiceTable.empty_object()

    def get_all(self):
        """
        :return: list
        """
        return self._saved_tables.tolist()

    def get_labels(self):
        """
        :return: [(saved_table.title., saved_table.tuple_list) ... ]
        """
        labels = []
        for saved_table in self._saved_tables:
            labels.append((saved_table.title, saved_table.tuple_list))
        return labels

    def delete_all(self):
        self._saved_tables = np.array([], dtype=object)

    def delete_requested(self, title_tuple_list_pairs):
        exclude_from_new = [fh.SavedDiceTable(title, tuple_list, [], [])
                            for title, tuple_list in title_tuple_list_pairs]
        new_data_array = np.array([], dtype=object)
        for saved_table in self._saved_tables:
            if saved_table not in exclude_from_new:
                new_data_array = np.append(new_data_array, saved_table)
        self._saved_tables = new_data_array

    def write_to_file(self):
        """overwrites old save to 'save_data.npy' """
        fh.write_saved_tables_array(self._saved_tables)

    def reload_from_file(self):
        """reads from 'save_data.npy' and checks for errors.

        :return: msg = 'ok', 'ok: no saved data', or 'error: ...'
        """
        msg, self._saved_tables = fh.read_saved_tables_array()
        return msg


def remove_duplicates_from_list(some_list):
    no_duplicates = []
    for element in some_list:
        if element not in no_duplicates:
            no_duplicates.append(element)
    return no_duplicates


class CurrentAndSavedInterface(object):
    def __init__(self, table_manager, saved_tables):
        self._saved_tables = saved_tables
        self._current_table = table_manager

    def get_and_save_current(self):
        new_to_save = self._current_table.get_obj_to_save()
        self._saved_tables.save_new(new_to_save)
        self._saved_tables.write_to_file()
        return new_to_save

    def get_label_current(self):
        return (self._current_table.title_one_line,
                self._current_table.tuple_list)

    def get_label_saved(self):
        return self._saved_tables.get_labels()

    def get_labels(self):
        return self.get_label_current(), self.get_label_saved()

    def is_current_table(self, title, tuple_list):
        return (title, tuple_list) == self.get_label_current()

    def current_is_empty(self):
        return self.get_label_current() == ('', [(0, 1)])

    def get_requested(self, title_tuple_list_pairs):
        no_duplicates = remove_duplicates_from_list(title_tuple_list_pairs)
        requested = []
        for title, tuple_list in no_duplicates:
            if self._saved_tables.has_requested(title, tuple_list):
                requested.append(self._saved_tables.get_requested(title, tuple_list))
            elif self.is_current_table(title, tuple_list):
                requested.append(self.get_and_save_current())
        return requested

    def get_all(self):
        if not self.current_is_empty() and not self._saved_tables.has_requested(*self.get_label_current()):
            self.get_and_save_current()
        return self._saved_tables.get_all()

    def delete_all(self):
        self._saved_tables.delete_all()
        self._saved_tables.write_to_file()

    def delete_requested(self, title_tuple_list_pairs):
        self._saved_tables.delete_requested(title_tuple_list_pairs)
        self._saved_tables.write_to_file()

    def reload_requested_as_current(self, title, tuple_list):
        to_reload = self._saved_tables.get_requested(title, tuple_list)
        if not to_reload.is_empty():
            self._current_table.request_reload(to_reload)


def combine_ranges(range_1, range_2):
    new_range = (min(range_2[0], range_1[0]),
                 max(range_2[1], range_1[1]))
    return new_range


def get_graphs(saved_table_list, get_axes_not_pts=True):
    """
    :return: (x_range tuple, y_range tuple,
        [ ('obj title', [obj graph data]) , (...)]
    """
    list_of_graphs = []
    x_range = y_range = (float('inf'), float('-inf'))
    for saved_table in saved_table_list:
        x_range = combine_ranges(saved_table.x_range, x_range)
        y_range = combine_ranges(saved_table.y_range, y_range)
        if get_axes_not_pts:
            graph_data = saved_table.graph_axes
        else:
            graph_data = saved_table.graph_pts
        list_of_graphs.append((saved_table.title, graph_data))
    return x_range, y_range, list_of_graphs


class GraphBox(object):
    """now a wrapper for CurrentSavedInterface and function: get_graphs"""

    def __init__(self, table_manager, saved_tables, get_axes_not_pts):
        """
        :param table_manager: DiceTableManager
        :param saved_tables: SavedTables
        :param get_axes_not_pts: bool"""
        self.interface = CurrentAndSavedInterface(table_manager, saved_tables)
        self._get_axes_not_pts = get_axes_not_pts

    def get_and_save_current(self):
        return self.interface.get_and_save_current()

    def get_requested_graphs(self, title_tuple_list_pairs):
        """
        :returns: ( (x_range), (y_range), [(title, [graphing_values])...] )
        """
        return get_graphs(self.interface.get_requested(title_tuple_list_pairs), self._get_axes_not_pts)

    def get_all_graphs(self):
        """
        :returns: ( (x_range), (y_range), [(title, [graphing_values])...] )
        """
        return get_graphs(self.interface.get_all(), self._get_axes_not_pts)

    def delete_requested(self, title_tuple_list_pairs):
        self.interface.delete_requested(title_tuple_list_pairs)

    def delete_all(self):
        self.interface.delete_all()

    def display_current_table(self):
        return self.interface.get_label_current()

    def display_saved_tables(self):
        return self.interface.get_label_saved()

    def display(self):
        """

        :return: ( (current title, current tuple_list), [(save1 txt, save1 tuple_list), ..] )
        """
        return self.interface.get_labels()

    def reload_saved_dice_table(self, title, tuple_list):
        self.interface.reload_requested_as_current(title, tuple_list)


def get_die_roll_details(die):
    details = '{} rolls:'.format(die)
    len_for_roll_value_strings = [len(str(pair[0])) for pair in die.tuple_list()]
    rjust_value = max(len_for_roll_value_strings)
    for roll_value, freq in die.tuple_list():
        details += '\n  {:>{}} with frequency: {}'.format(roll_value, rjust_value, freq)
    return details


def get_add_and_remove_labels(die, number_of_dice, enable_remove):
    """
    get_add_and_remove_labels(dt.Die(50), 2, True)

    :return: ['-10', '-5', '-1', '2D50', '+1', '+5', '+10']
    """
    display = []
    add_choices = get_add_choices(die)
    if enable_remove:
        display += ['-{}'.format(number) for number in add_choices[::-1]]

    display += [get_die_label(die, number_of_dice)]

    display += ['{:+}'.format(number) for number in add_choices]
    return display


def get_add_choices(die):
    max_size_for_add_choice = [(10000, 1), (100, 5), (50, 10), (25, 50), (16, 100), (6, 500)]
    available_choices = []
    for max_size, add_choice in max_size_for_add_choice:
        if die.get_size() <= max_size:
            available_choices.append(add_choice)
    return available_choices


def get_die_label(die, number_of_dice):
    if number_of_dice:
        return die.multiply_str(number_of_dice)
    return str(die)


class ChangeBox(object):
    """controls changing the number of dice already in the table"""

    def __init__(self, table_manager):
        """table_manager is a DiceTableManager"""
        self._table = table_manager

    def get_dice_details(self):
        return [get_die_roll_details(pair[0]) for pair in self._table.dice_list]

    def display(self):
        """
        for 3D100, ...other dice

        :return: [ (['-5', '-1', '3D100', '+1', '+5'], dt.Die(100)), ...]
        """
        display = []
        for die, number in self._table.dice_list:
            add_rm_display = get_add_and_remove_labels(die, number, enable_remove=True)
            display.append((add_rm_display, die))
        return display

    def add_rm(self, number, die):
        """number is an int  die is a child of dt.ProtoDie"""
        if number < 0:
            self._table.request_remove(abs(number), die)
        else:
            self._table.request_add(number, die)

    def reset(self):
        """resets the table back to empty"""
        self._table.request_reset()


def make_die(size, modifier, multiplier, dictionary):
    """
    if is_dictionary_for_weigted_die, then dictionary supercedes size

    :return: Die, ModDie, WeightedDie, ModWeightedDie or StrongDie
    """
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
            if value != 1:
                return True
    return False


class AddBox(object):
    """selects and adds new dice to a table"""
    presets = ['D{}'.format(die) for die in
               (2, 4, 6, 8, 10, 12, 20, 100)]

    def __init__(self, dice_table_manager):
        """self.presets is a list of
        preset die labels"""
        self._table = dice_table_manager
        self._size = 6
        self._mod = 0
        self._multiplier = 0
        self._dictionary = {}
        self._die = dt.Die(6)

    def get_die_details(self):
        return get_die_roll_details(self._die)

    def display_die(self):
        """
        for D100,

        :return: ['D100', '+1', '+5']
        """
        return get_add_and_remove_labels(self._die, 0, enable_remove=False)

    def display_current_table(self):
        """displays the table info"""
        return self._table.title_one_line

    def add(self, number):
        self._table.request_add(number, self._die)

    def _update_die(self):
        self._die = make_die(self._size, self._mod, self._multiplier,
                             self._dictionary)

    def set_size(self, new_size):
        """size is int >=1 sets new size and refreshes the die"""
        self._dictionary = {}
        self._size = new_size
        self._update_die()

    def set_mod(self, new_mod):
        """mod is an int. sets new die modifier and refreshes the die"""
        self._mod = new_mod
        self._update_die()

    def set_multiplier(self, new_val):
        """new_val is an int >=0 sets new multiplier and refreshes the die"""
        self._multiplier = new_val
        self._update_die()

    def get_weights_text(self):
        """returns a list of texts for making a weights popup"""
        texts = []
        for roll in range(1, self._size + 1):
            texts.append('weight for {}'.format(roll))
        return texts

    def record_weights_text(self, text_val_lst):
        """

        :param text_val_lst:
            [('weight for {}.'.format(roll),\n
            val=int - weight for roll) ..]
        """
        self._dictionary = {}
        for text, weight in text_val_lst:
            roll = int(text[len('weight for '):])
            self._dictionary[roll] = weight
        self._update_die()


class StatBox(object):
    """gets stats for table and displays."""

    def __init__(self, table_manager):
        """simply inits with a DiceTableManager"""
        self._table = table_manager

    def display(self, val_1, val_2):
        """


        :return: [ info text: range, mean, stddev,\n
            stat text: \n
            values: tuple of what values are displayed\n
            min_max: tuple of min and max for slider
        """
        val_min, val_max = self._table.range
        info_text = self._table.get_description_range_mean_stddev()
        stat_text, values = self.display_stats(val_1, val_2)
        return [info_text, stat_text, values, (val_min, val_max)]

    def _adjust_value_to_within_min_max(self, value):
        val_min, val_max = self._table.range
        return min(val_max, max(val_min, value))

    def display_stats(self, val_1, val_2):
        """
        :return: [ str: stat info\n
            tuple: the two input vals adjusted for min/max
        """
        val_1 = self._adjust_value_to_within_min_max(val_1)
        val_2 = self._adjust_value_to_within_min_max(val_2)

        stat_list = list(range(min(val_1, val_2), max(val_1, val_2) + 1))
        stat_info = self._table.get_stats(stat_list)
        stat_text = ('\n' +
                     '    {stat[0]} occurred {stat[1]} times\n' +
                     '    out of {stat[2]} total combinations\n\n' +
                     '    that\'s a one in {stat[3]} chance\n' +
                     '    or {stat[4]} percent')
        return [stat_text.format(stat=stat_info), (val_1, val_2)]


class InfoBox(object):
    """displays long info about object. can also display long info as page
    views."""

    def __init__(self, table_manager):
        """simply inits with a DiceTableManager"""
        self._table = table_manager
        self._current_page = {'full_text': 1, 'weights_info': 1}
        self._lines_per_page = {'full_text': 1, 'weights_info': 1}
        self._pages = {'full_text': [''], 'weights_info': ['']}

    def _get_text(self, key):
        """
        :param key: 'weights_info' or 'full_text'
        """
        text_selector = {'weights_info': self._table.weights_info,
                         'full_text': self._table.full_text}
        return text_selector[key].rstrip('\n')

    def _get_formatted_text(self, key):
        """
        :param key: 'weights_info' or 'full_text'
        """
        text = self._get_text(key)
        if key == 'weights_info':
            text = text.replace('a roll of ', '')
            text = text.replace(' a ', ' ')
            text = text.replace(' of ', ': ')
        return text

    def make_pages(self, key, lines_per_page):
        """

        :param key: 'weights_info' or ''full_text'
        :param lines_per_page: int >=1
        :return: list of pages
        """
        self._lines_per_page[key] = lines_per_page
        text = self._get_formatted_text(key)
        lines = text.split('\n')
        grouping_into_pages_tool = [iter(lines)] * lines_per_page
        grouped_lines = zip_longest(*grouping_into_pages_tool, fillvalue=' ')
        self._pages[key] = ['\n'.join(page) for page in grouped_lines]

    def display_current_page(self, key):
        """
        :param key: 'weights_info' or 'full_text'
        """
        total_pages = len(self._pages[key])
        page_num = self._current_page[key] % total_pages
        if page_num == 0:
            page_num = total_pages
        page = self._pages[key][page_num - 1]
        self._current_page[key] = page_num
        return page, page_num, total_pages

    def display_next_page(self, key):
        self._current_page[key] += 1
        return self.display_current_page(key)

    def display_previous_page(self, key):
        self._current_page[key] -= 1
        return self.display_current_page(key)

    def display_chosen_page(self, page_number, key):
        self._current_page[key] = page_number
        return self.display_current_page(key)

    def display_paged(self, lines_per_weight_page, lines_per_full_text_page):
        """
        :return: [range-mean-stddev-str, table_str, (weights_info), (full_text)]"""
        self.make_pages('weights_info', lines_per_weight_page)
        self.make_pages('full_text', lines_per_full_text_page)
        return [self._table.get_description_range_mean_stddev(), self._table.title,
                self.display_current_page('weights_info'),
                self.display_current_page('full_text')]

    def display(self):
        """
        :return: [range-mean-stddev-str, table title, weights_info, full_text]
        """
        return [self._table.get_description_range_mean_stddev(), self._table.title,
                self._get_formatted_text('weights_info'), self._get_formatted_text('full_text')]


class VirtualCalculator(object):
    def __init__(self, mean, stddev):
        self._specials_map = {'mean': '{:.1f}'.format(mean),
                              'stddev': '{:.1f}'.format(stddev)}
        self._back_space = '<BS'
        self._digits = '1234567890'
        self._operators = '+-*'
        excluded_operators = ['/', '//', '**', '^', '%']
        self._calculator = TextCalculator(excluded_operators)
        self._display = ''

    def reset(self):
        self._display = ''

    def calculate(self):
        return int(self._calculator.safe_eval(self._display)[0])

    def push(self, button_value):
        if button_value in self._digits:
            pass
        if button_value in self._operators:
            pass
        if button_value == '<BS':
            pass
        if button_value in self._specials_map.keys():
            pass

    def do_back_space(self):
        pass



