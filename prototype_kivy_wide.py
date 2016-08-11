#TODO - check layout in .kv  take care of main()  move around stuff and comment

# pylint: disable=unused-argument, no-name-in-module, import-error
# pylint: disable=super-on-old-class
'''requires kivy and kivy garden graph'''
from itertools import cycle as itertools_cycle

import matplotlib.pyplot as plt

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.properties import (StringProperty, BooleanProperty,
                             ObjectProperty, ListProperty)
from kivy.clock import Clock
import dicetables as dt
import dt_gui_mvm as mvm
from kivy.garden.graph import MeshLinePlot


INTRO_TEXT = ('this is a platform for finding the probability of dice ' +
              'rolls for any set of dice. For example, the chance of ' +
              'rolling a 4 with 3 six-sided dice is 3 out of 216.\n\n' +

              'Swipe right ===> to get to the add box.  pick a die size, ' +
              'and pick a number of dice to add. Add as many kinds of ' +
              'dice as you want. You can also add a modifier to the die ' +
              '(for example 3-sided die +4), or you can make the die a ' +
              'weighted die (a 2-sided die with weights 1:3, 2:8 rolls ' +
              'a \'one\'  3 times out of every 11 times).\n\n' +

              'come back to this window to add or subtract ' +
              'dice already added.\n\n' +

              'The graph area is for getting a graph of the set of dice. ' +
              'It records every set of dice that have been graphed and ' +
              'you can reload those dice at any time.\n\n' +

              'The stats area will give you the stats of any set of ' +
              'rolls you choose. The last window gives you details of ' +
              'the raw data.')
#tools
def main():
    '''gets the current diceplatform so all can call it'''
    return App.get_running_app().root

# kv file line NONE
class FlashButton(Button):
    '''a button that flashes for delay_time=0.25 sec after pressed, so you know
    you done taht press real clear-like. assign on_press using self.delay OR
    make the function it calls use self.delay or you won't see the flash. can
    hold info about a die or list for keeping track of stuff.'''
    die = ObjectProperty(dt.Die(1))
    lst = ListProperty([])
    def __init__(self, delay_time=0.25, **kwargs):
        super(FlashButton, self).__init__(**kwargs)
        self.delay_time = delay_time

    def delay(self, function, *args):
        '''delays a function call so that button has time to flash.  use with
        on_press=self.delay(function, function_args)'''
        Clock.schedule_once(lambda delta_time: function(*args),
                            self.delay_time)
    def on_press(self, *args):
        '''sets background to flash on press'''
        self.color = [1, 0, 0, 1]
        self.background_color = [0.2, 0.2, 1, 1]
        Clock.schedule_once(self.callback, self.delay_time)
    def callback(self, delta_time):
        '''sets background to normal'''
        self.color = [1, 1, 1, 1]
        self.background_color = [1, 1, 1, 1]

# kv file line NONE
class FlashLabel(Button):
    '''a label that flashes for delay_time=0.5 sec when text is added by
    add_text. can be turned off with boolean do_flash'''
    def __init__(self, delay_time=0.5, **kwargs):
        super(FlashLabel, self).__init__(**kwargs)
        self.background_normal = ''
        self.delay_time = delay_time
        self.color = [1, 1, 1, 1]
        self.background_color = [0, 0, 0, 0]
    def flash_it(self, *args):
        '''flashes the label'''
        self.color = [1, 0, 0, 1]
        self.background_color = [0.2, 0.2, 1, 0.2]
        Clock.schedule_once(self.callback, self.delay_time)
    def add_text(self, text, do_flash=True):
        '''flahes (or not) when text is changed'''
        self.text = text
        self.color = [1, 1, 1, 1]
        self.background_color = [0, 0, 0, 0]
        if do_flash:
            self.color = [1, 0, 0, 1]
            self.background_color = [0.2, 0.2, 1, 0.2]
            Clock.schedule_once(self.callback, self.delay_time)
    def callback(self, delta_time):
        '''reset background and color after delay'''
        self.color = [1, 1, 1, 1]
        self.background_color = [0, 0, 0, 0]
# kv file line NONE
class NumberInput(Button):
    '''a button that opens a number pad for input. fire input events using
    on_changed to always fire when pressing enter or on_text to only fire when
    the value actually changes. on_changed specifically written for resetting
    assigned weights.'''
    changed = BooleanProperty(True)
    def __init__(self, **kwargs):
        super(NumberInput, self).__init__(**kwargs)
        pad = StackLayout(orientation='lr-tb')
        texts = itertools_cycle(['+', '-', '='])
        for digit in range(1, 10):
            pad.add_widget(Button(text=str(digit), size_hint=(0.29, 0.25),
                                  on_press=self.add_digit))
            if digit % 3 == 0:
                pad.add_widget(Button(text=next(texts), size_hint=(0.1, 0.25),
                                      on_press=self.plus_minus))
        pad.add_widget(Button(text='<-BS-', size_hint=(0.29, 0.25),
                              on_press=self.back_space))
        pad.add_widget(Button(text='0', size_hint=(0.29, 0.25),
                              on_press=self.add_digit))
        pad.add_widget(Button(text='ENT', size_hint=(0.39, 0.25),
                              on_press=self.enter_val))
        self.num_pad = Popup(title='', content=pad, size_hint=(0.4, 0.5),
                             pos_hint={'x':0.3, 'y':0})
        self.text = ''
        self.background_color = (0.4, 0.2, 1.0, 0.8)
        self.bind(on_release=self.open_pad)
        self.to_add = 0
        self.sign = 1
    def add_digit(self, btn):
        '''fired when 0-9 is pressed'''
        if self.num_pad.title == ' ':
            self.num_pad.title = btn.text
        else:
            self.num_pad.title += btn.text
    def back_space(self, btn):
        '''fired when BS is pressed'''
        if self.num_pad.title != ' ':
            if self.num_pad.title[:-1]:
                self.num_pad.title = self.num_pad.title[:-1]
            else:
                self.num_pad.title = ' '
    def open_pad(self, btn):
        '''no new info'''
        self.to_add = 0
        self.sign = 1
        self.num_pad.open(self)
        self.num_pad.title = ' '
        self.num_pad.title_size = self.num_pad.height/8
    def plus_minus(self, btn):
        '''uses self.to_add and self.sign to do plus, minus, equals.  on equals,
        makes title to self.to_add and resets'''
        if self.num_pad.title != ' ':
            self.to_add += int(self.num_pad.title) * self.sign
        if btn.text == '-':
            self.sign = -1
        if btn.text == '+':
            self.sign = 1
        if btn.text == '=':
            self.num_pad.title = str(self.to_add)
            self.to_add = 0
            self.sign = 1
        else:
            self.num_pad.title = ' '
    def enter_val(self, btn):
        '''when you press enter, always changes changed, you can use it to fire
        events'''
        self.num_pad.dismiss()
        if self.num_pad.title != ' ':
            self.text = self.num_pad.title
            #pressing enter can fire event with changed.
            self.changed = not self.changed

#for weightpopup
# kv file line NONE
class NumberSelect(BoxLayout):
    '''makes a grid of numbers to choose from'''
    def __init__(self, start, stop, **kwargs):
        '''start and stop are ints.  range of numbers that select displays'''
        super(NumberSelect, self).__init__(**kwargs)
        self.the_range = range(start, stop + 1)
    def open_pad(self, *args):
        '''creates a popup pad and opens it'''
        pad = SelectPad(self, size_hint=(0.4, 0.5), pos_hint={'x':0.3, 'y':0})
        pad.open()
    def get_values(self):
        '''gets info from numberselect for getting weights'''
        return (self.ids['title'].text, int(self.ids['number'].text))
    def set_text(self, title, number):
        '''title is string, number is int. sets both internal buttons'''
        self.ids['title'].text = title
        self.ids['number'].text = str(number)
# kv file line NONE
class SelectPad(Popup):
    '''a popup that is called by NumberSelect.  creates a number pad of number
    choices.'''
    def __init__(self, parent_btn, **kwargs):
        '''parent_btn is the NumberSelect associated with this select pad'''
        super(SelectPad, self).__init__(**kwargs)
        self.parent_btn = parent_btn

        self.content = StackLayout(orientation='lr-tb', size_hint=(1, 1))
        y_hint_ = 0.01* int(100 /(1 + len(self.parent_btn.the_range)//3))
        for number in self.parent_btn.the_range:
            self.content.add_widget(Button(text=str(number),
                                           size_hint=(0.33, y_hint_),
                                           on_press=self.record_number))
        self.title = self.parent_btn.ids['title'].text
        self.title_align = 'center'
    def record_number(self, btn):
        '''assigns button's number to parent'''
        self.parent_btn.ids['number'].text = btn.text
        self.dismiss()
# kv file line 9
class WeightsPopup(Popup):
    '''the popup called when weighting a die'''
    def __init__(self, parent_obj, text_list, **kwargs):
        '''parent_obj is the owner of the popup where the weights will be
        recorded. text_list is a list of strings for NumberSelect titles.'''
        super(WeightsPopup, self).__init__(**kwargs)
        self.parent_obj = parent_obj
        self.pack(text_list)
    def pack(self, text_list):
        '''sizes popup appropiately and packs with right number of weights'''
        spacing = 10.
        cols_within_frame = 3
        die_size = len(text_list)
        col_width = int(self.parent_obj.width / cols_within_frame)
        add_drag = False
        cols = ((die_size)//10 +1)
        if cols > cols_within_frame:
            cols = ((die_size+2)//10 +1)
            add_drag = True
            drag_it = Label(text='DRAG\n====>', bold=True)
        height = int(self.parent_obj.height* 0.9)
        sz_hint = ((col_width - spacing)/(cols*col_width),
                   0.1 * (height-spacing)/height)

        self.size = (min(1.1 * cols*col_width, self.parent_obj.width),
                     self.parent_obj.height)
        contents = self.ids['contents']
        contents.clear_widgets()
        contents.size = (cols*col_width*0.88, height)
        contents.spacing = spacing
        if add_drag:
            drag_it.size_hint = sz_hint
            contents.add_widget(drag_it)
            contents.add_widget(Button(on_press=self.record_weights,
                                       text='record\nweights',
                                       size_hint=sz_hint))

        for text in text_list:
            weighter = NumberSelect(0, 10, size_hint=sz_hint)
            weighter.set_text(text, 1)
            contents.add_widget(weighter)
        contents.add_widget(Button(on_press=self.record_weights,
                                   text='record\nweights', size_hint=sz_hint))

    def record_weights(self, button):
        '''records the weights from the weight popup'''
        out = []
        for child in self.ids['contents'].children[:]:
            if isinstance(child, NumberSelect):
                out.append(child.get_values())
        self.parent_obj.record_weights(out)
        self.dismiss()


# kv file line NONE
class ObjectButton(Button):
    '''simply a button with an object attached'''
    obj = ObjectProperty({})
# kv file line 22
class PlotPopup(Popup):
    '''popup containing the graph'''
    def __init__(self, **kwargs):
        super(PlotPopup, self).__init__(**kwargs)
        self._plot_list = []
        self.legend = DropDown(dismiss_on_select=False)
    def add_list(self, new_list):
        '''main funciton to make a graph'''
        self._plot_list = new_list[:]
        self.make_graph()
        self.make_legend()
    def make_graph(self):
        '''makes a graph and plots'''
        colors = itertools_cycle([
            [0.2, 1.0, 0, 1], [1, 0, 0.2, 1], [0, 0.2, 1, 1],
            [0.6, 0, 0.8, 1], [1, 0.4, 0.2, 1], [1, 0.8, 0, 1],
            [0.8, 1.0, 0.1, 1]
            ])
        x_range = []
        y_range = []
        y_ticks = [0.05, 0.1, 0.2, 0.5, 1, 5, 10]
        x_ticks = [1, 2, 5, 10, 20, 30, 50, 100, 200,
                   300, 500, 1000, 2000, 5000]
        for plot_obj in self._plot_list:
            plot_obj['color'] = next(colors)
            self.ids['graph'].add_plot(MeshLinePlot(points=plot_obj['pts'],
                                                    color=plot_obj['color']))
            if x_range:
                x_range[0] = min(x_range[0], plot_obj['x_min'])
                x_range[1] = max(x_range[1], plot_obj['x_max'])
            else:
                x_range = [plot_obj['x_min'], plot_obj['x_max']]
            if y_range:
                y_range[1] = max(y_range[1], plot_obj['y_max'])
            else:
                y_range = [0, plot_obj['y_max']]
        x_tick_num = (x_range[1]-x_range[0])/9.
        for tick in x_ticks:
            if x_tick_num < tick:
                x_tick_num = tick
                break
        y_tick_num = (y_range[1]-y_range[0])/20.
        for tick in y_ticks:
            if y_tick_num < tick:
                y_tick_num = tick
                break
        x_range[0] -= x_range[0] % x_tick_num
        current = self.ids['graph'].font_size
        factor = 1.
        if x_tick_num > 49:
            factor = 0.75
        if x_tick_num > 99:
            factor = 0.66
        if x_tick_num > 499:
            factor = 0.5

        self.ids['graph'].font_size = int(factor * current)
        self.ids['graph'].x_ticks_major = x_tick_num
        self.ids['graph'].y_ticks_major = y_tick_num
        self.ids['graph'].xmin = x_range[0]
        self.ids['graph'].ymin = -y_tick_num
        self.ids['graph'].xmax = x_range[1]
        self.ids['graph'].ymax = y_range[1]

    def make_legend(self):
        '''created the dropdown menu that's called by 'legend' button'''
        for plot_obj in self._plot_list:

            btn = ObjectButton(text=plot_obj['text'], size_hint=(None, None),
                               height=80, obj=plot_obj, color=plot_obj['color'],
                               valign='middle')
            btn.bind(on_release=lambda btn: self.legend.select(btn.obj))
            self.legend.add_widget(btn)
        self.legend.on_select = self.flash_plot
        self.ids['legend'].bind(on_release=self.legend.open)
        self.ids['legend'].bind(on_release=self.resize)
        self.legend.bind(on_dismiss=self.shrink_button)
    def shrink_button(self, event):
        '''make legend button small again after dismiss drop down'''
        self.ids['legend'].width = self.ids['legend'].texture_size[0]
    def resize(self, *args):
        '''on release, resize drop down to fit widest button'''
        widths = [self.ids['legend'].texture_size[0]]
        for btn in self.legend.children[0].children:
            raw_lines = (btn.texture_size[0] + 10.)/main().width
            single_line_ht = btn.texture_size[1]
            lines = int(raw_lines)
            if lines < raw_lines:
                lines += 1
            split_at = len(btn.text)/lines
            if len(btn.text) % lines:
                split_at += 1
            #make long btn.text multiline
            new_text_lst = []
            copy = btn.text
            while len(copy) > split_at:
                new_text_lst.append(copy[:split_at])
                copy = copy[split_at:]
            new_text_lst.append(copy)
            btn.text = '\n'.join(new_text_lst)

            btn.width = min(btn.texture_size[0] + 10, main().width)
            btn.height = max(self.ids['legend'].height, single_line_ht * lines)
            widths.append(btn.width)
        self.ids['legend'].width = max(widths)
    def flash_plot(self, obj, second_time=False, flash_time=0.5):
        '''on press, highlight selected graph'''
        for plot in self.ids['graph'].plots:
            if plot.points == obj['pts']:
                temp_color = [1, 1, 1, 1]
                self.ids['graph'].remove_plot(plot)
                new_plot = MeshLinePlot(points=obj['pts'], color=temp_color)
                self.ids['graph'].add_plot(new_plot)
        if second_time:
            Clock.schedule_once(
                lambda dt: self._callback(obj, flash_time, True),
                flash_time)
        else:
            Clock.schedule_once(lambda dt: self._callback(obj, flash_time),
                                flash_time)
    def _callback(self, obj, flash_time, second_time=False):
        '''resets graph to original color'''
        for plot in self.ids['graph'].plots:
            if plot.points == obj['pts']:
                plot.color = obj['color']
        if not second_time:
            Clock.schedule_once(lambda dt: self.flash_plot(obj, True),
                                flash_time)

# kv file line 51



# kv file line 146
class ChangeBox(GridLayout):
    '''displays current dice and allows to change. parent app is what's called
    for dice actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    view_model = ObjectProperty(mvm.ChangeBox(mvm.TableManager()))
    def __init__(self, **kwargs):
        super(ChangeBox, self).__init__(**kwargs)
        self.cols = 1
        self.old_dice = []
    def add_rm(self, btn):
        '''uses die stored in button and btn text to request add or rm'''
        self.view_model.add_rm(int(btn.text), btn.die)
        self.parent.do_update()
    def reset(self, btn):
        '''resets current table back to empty and display instructions'''
        self.view_model.reset()
        self.parent.do_update()
        self.clear_widgets()
        self.add_widget(Label(text=INTRO_TEXT, text_size=self.size,
                              valign='top', halign='center'))
    def update(self):
        '''updates the current dice after add, rm or clear'''
        new_dice = []
        button_list = self.view_model.display()
        self.clear_widgets()
        max_height = self.height/10
        reset = Button(text='reset table', on_press=self.reset,
                       size_hint=(1, None), height=0.75*max_height)
        self.add_widget(reset)
        if button_list:
            new_height = min((self.height - reset.height) / len(button_list),
                             max_height)
        for labels, die_ in button_list:
            box = BoxLayout(size_hint=(0.8, None), height=new_height,
                            orientation='horizontal')
            self.add_widget(box)
            x_hint = round(1./(len(labels) + 2), 2)
            for label in labels:
                if label[0] == '-' or label[0] == '+':
                    btn = FlashButton(
                        text=label, size_hint=(x_hint, 1), die=die_,
                        on_press=lambda btn: btn.delay(self.add_rm, btn)
                        )
                    box.add_widget(btn)
                else:
                    flash = FlashLabel(text=label, size_hint=(3 * x_hint, 1))
                    box.add_widget(flash)
                    new_dice.append(label)
                    if label not in self.old_dice:
                        Clock.schedule_once(flash.flash_it, 0.01)
        self.old_dice = new_dice
#
# kv file line 154
class AddBox(BoxLayout):
    '''box for adding new dice.  parent app is what's called for dice actions
    and info updates. all calls are self.parent_app.request_something(*args).'''
    view_model = ObjectProperty(mvm.AddBox(mvm.TableManager()))
    def __init__(self, **kwargs):
        super(AddBox, self).__init__(**kwargs)
    def initialize(self):
        '''called at main app init. workaround for kv file loading after py'''
        for preset_text in self.view_model.presets:
            btn = Button(text=preset_text, on_press=self.assign_size_btn)
            self.ids['presets'].add_widget(btn)
        self.ids['multiplier'].bind(text=self.assign_multiplier)
        self.display_die()
    def update(self):
        '''called by main app at dice change'''
        self.ids['current'].text = (self.view_model.display_current())
    def assign_size_btn(self, btn):
        '''assigns the die size and die when a preset btn is pushed'''
        die_size = int(btn.text[1:])
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_size_text(self, text):
        '''asigns the die size and die when text is entered'''
        top = 200
        bottom = 2
        int_string = text
        if int_string:
            die_size = int(text)
            die_size = min(top, max(bottom, die_size))
        if text != str(die_size):
            self.ids['custom_input'].text = str(die_size)
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_mod(self):
        '''assigns a die modifier and new die when slider is moved'''
        mod = int(self.ids['modifier'].value)
        self.view_model.set_mod(mod)
        self.display_die()
    def assign_multiplier(self, spinner, text):
        '''assigns a die multiplier and new_die based on spinner's text.'''
        multiplier = int(text[1:])
        self.view_model.set_multiplier(multiplier)
        self.display_die()
    def display_die(self):
        '''all changes to size, mod and weight call this function'''
        self.ids['add_it'].clear_widgets()
        to_add = self.view_model.display_die()
        x_hint = round(1./(len(to_add) + 1), 2)
        flash = FlashLabel(text=to_add[0], size_hint=(2*x_hint, 1))
        self.ids['add_it'].add_widget(flash)
        flash.flash_it()
        for add_val in to_add[1:]:
            btn = FlashButton(text=add_val, size_hint=(x_hint, 1),
                              on_press=lambda btn: btn.delay(self.add, btn))
            self.ids['add_it'].add_widget(btn)
    def add(self, btn):
        '''uses btn text and die stored in view_model to add to current table'''
        self.view_model.add(int(btn.text))
        self.parent.do_update()
    def record_weights(self, text_val_lst):
        '''takes a list of [('weight for <roll>', int=the_weight)...] and makes
        a weighted die with it.'''
        self.view_model.record_weights_text(text_val_lst)
        self.display_die()
    def add_weights(self):
        '''opens the weightpopup and sizes accordingly'''
        popup = WeightsPopup(self, self.view_model.get_weights_text())
        popup.open()

# kv file line 77
class PageBox(BoxLayout):
    '''a box to display pages and buttons and slider to move through them.
    parent_obj is the top-level owner of the box that it accepts changes from'''
    parent_obj = ObjectProperty(BoxLayout)
    def __init__(self, **kwargs):
        '''inits the same as a boxlayout'''
        super(PageBox, self).__init__(**kwargs)
    def reset_sizes(self, ratios):
        '''reset font_size = f_size,
        [title ratio, , slider ratio, button ratio, text ratio] = ratios'''
        self.ids['page_box_title'].size_hint_y = ratios[0]
        #self.ids['choose'].size_hint_y = ratios[1]
        self.ids['buttons_container'].size_hint_y = ratios[1]
        self.ids['text_shell'].size_hint_y = ratios[2]
    def set_title(self, title):
        '''title is a string. sets the title of the box.'''
        self.ids['page_box_title'].text = title
    def get_lines_number(self, fudge_factor=0.83):
        '''returns an int.  the number of lines the pagebox can display'''
        return int(self.ids['text_container'].height * fudge_factor/
                   float(self.ids['text_container'].font_size))
    def set_text(self, page, page_num, total_pages):
        '''sets displays according page=str-text to display, page_num=int-
        current page, total_pages=int'''
        self.ids['text_container'].text = page
        self.ids['text_container'].text_size = self.ids['text_container'].size
        self.ids['pages'].text = '{}/{}'.format(page_num, total_pages)
        #in order to reverse slider movement,the value used by slider (having
        #the same max and min as the pages) is the opposite
        slider_val = total_pages + 1 - page_num
        self.ids['choose'].max = total_pages
        self.ids['choose'].value = slider_val
class StatBox(BoxLayout):
    '''box for getting and displaying stats about rolls. parent app is what's
    called for dice actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    view_model = ObjectProperty(mvm.StatBox(mvm.TableManager()))
    def __init__(self, **kwargs):
        super(StatBox, self).__init__(**kwargs)

    def display_stats(self, stat_text, vals):
        '''takes a stat text and two values, and displays them.'''
        self.ids['stat_text'].text = stat_text
        self.ids['slider_1'].value = vals[0]
        self.ids['slider_2'].value = vals[1]
        self.ids['slider_1_text'].text = '{:,}'.format(vals[0])
        self.ids['slider_2_text'].text = '{:,}'.format(vals[1])

    def update(self):
        '''called when dice list changes.'''
        val_1 = int(self.ids['slider_1'].value)
        val_2 = int(self.ids['slider_2'].value)
        info_text, stat_text, vals, min_max = self.view_model.display(val_1,
                                                                      val_2)
        self.ids['info_text'].text = info_text
        self.display_stats(stat_text, vals)
        self.ids['slider_1'].min = self.ids['slider_2'].min = min_max[0]
        self.ids['slider_1'].max = self.ids['slider_2'].max = min_max[1]
    def assign_text_value(self):
        '''called by text_input to assign that value to sliders and
        show stats'''
        val_1 = int(self.ids['slider_1_text'].text.replace(',', ''))
        val_2 = int(self.ids['slider_2_text'].text.replace(',', ''))
        self.display_stats(*self.view_model.display_stats(val_1, val_2))
    def assign_slider_value(self):
        '''the main function. displays stats of current slider values.'''
        val_1 = int(self.ids['slider_1'].value)
        val_2 = int(self.ids['slider_2'].value)
        self.display_stats(*self.view_model.display_stats(val_1, val_2))
# kv file line 231
class InfoBox(BoxLayout):
    '''displays basic info about the die.'''
    view_model = ObjectProperty(mvm.InfoBox(mvm.TableManager()))
    def __init__(self, **kwargs):
        super(InfoBox, self).__init__(**kwargs)
    def initialize(self):
        '''called at main app init. workaround for kv file loading after py'''
        self.ids['full_text'].set_title(
            'here are all the rolls and their frequency'
            )
        self.ids['full_text'].ids['page_box_title'].font_size *= 0.75
        self.ids['weights_info'].reset_sizes([0.1, 0.1, 0.80])
        self.ids['weights_info'].set_title('full weight info')
    def choose(self, slider, key):
        '''chooses a page for pagebox with key=string-which box to display in.
        value=int-page number.'''
        lines = self.ids[key].get_lines_number()
        #reversing the slider
        page = int(slider.max) + int(slider.min) - int(slider.value)
        self.ids[key].set_text(*self.view_model.display_chosen_page(page,
                                                                    key, lines))
    def previous(self, key):
        '''displays previous page and updates view for pagebox[key=string]'''
        lines = self.ids[key].get_lines_number()
        self.ids[key].set_text(*self.view_model.display_previous_page(key,
                                                                      lines))
    def next(self, key):
        '''displays next page and updates view for pagebox[key=string]'''
        lines = self.ids[key].get_lines_number()
        self.ids[key].set_text(*self.view_model.display_next_page(key, lines))
    def update(self):
        '''updates views for all parts of the box.'''
        all_info = self.view_model.display_paged(
            self.ids['weights_info'].get_lines_number(),
            self.ids['full_text'].get_lines_number()
            )
        self.ids['general_info'].text = all_info[0]
        self.ids['table_str'].text = all_info[1]
        self.ids['weights_info'].set_text(*all_info[2])
        self.ids['full_text'].set_text(*all_info[3])
# kv file line 253
class PlotCheckBox(BoxLayout):
    '''a checkbox with associated label and function to return label if box
    checked'''
    #parent_obj = ObjectProperty(BoxLayout)
    tuple_list = ObjectProperty([(0, 1)])
    text = StringProperty('')
    active = BooleanProperty(False)
    def __init__(self, reloader=True, **kwargs):
        super(PlotCheckBox, self).__init__(**kwargs)
        self.ids['check_box'].bind(active=self._change_active)
        self.bind(text=self.split_text)
    def _change_active(self, checkbox, value):
        '''a helper function to bind checkbox active to main active'''
        self.active = self.ids['check_box'].active
    def split_text(self, instance, text, split_char='\\'):
        '''makes a new two-line display label while preserving original in'''
        cut_off = 30
        if len(self.text) <= cut_off:
            self.ids['label'].text = text
        else:
            line_1 = text[:len(self.text)/2]
            line_2 = text[len(self.text)/2:].replace(split_char, '\n', 1)
            self.ids['label'].text = (line_1 + line_2)

class GraphBox(BoxLayout):
    '''buttons for making graphs.  parent app is what's called for dice actions
    and info updates. all calls are self.parent_app.request_something(*args).'''
    view_model = ObjectProperty(mvm.GraphBox(mvm.TableManager(),
                                             mvm.HistoryManager(), True))
    def __init__(self, **kwargs):
        super(GraphBox, self).__init__(**kwargs)
        self.confirm = Popup(title='Delete everything?', content=BoxLayout(),
                             size_hint=(0.8, 0.4), title_align='center',
                             title_size=75)
        self.confirm.content.add_widget(Button(text='EVERY\nTHING!!!',
                                               on_press=self.clear_all,
                                               texture_size=self.size))
        self.confirm.content.add_widget(Button(text='never\nmind',
                                               on_press=self.confirm.dismiss))

    def initialize(self):
        '''called at main app init. workaround for kv file loading after py'''
        self.ids['graph_space'].add_widget(PlotCheckBox(size_hint=(1, 0.5),
                                                        parent_obj=self))
        self.update()
    def update(self):
        '''updates the current window to display new graph history and current
        table to graph'''
        current, history = self.view_model.display()
        #sz_hint for 'past graphs' label to take up all the space
        #base_y make sure other widgets fit
        rows = len(history) + 3
        base_y = .99/rows
        if base_y > 0.1:
            base_y = 0.1
        sz_hint = (1, 1 - (rows - 1) * base_y)

        self.ids['graph_space'].clear_widgets()
        self.ids['graph_space'].add_widget(Label(text='past graphs',
                                                 halign='center',
                                                 size_hint=sz_hint))
        for text_, tuple_list_ in history:
            check = PlotCheckBox(size_hint=(0.8, base_y), active=False,
                                 tuple_list=tuple_list_)
            reload_ = FlashButton(
                size_hint=(0.2, base_y), lst=[text_, tuple_list_], max_lines=1,
                text='reload', valign='middle', halign='center',
                on_press=lambda btn: btn.delay(self.reload, btn)
                )
            self.ids['graph_space'].add_widget(check)
            self.ids['graph_space'].add_widget(reload_)
            check.text = text_



        self.ids['graph_space'].add_widget(Label(text='new table',
                                                 size_hint=(1, base_y)))
        check = PlotCheckBox(size_hint=(1, base_y), active=True,
                             tuple_list=current[1])
        self.ids['graph_space'].add_widget(check)
        check.text = current[0]
        Clock.schedule_once(lambda dt: check.ids['label'].flash_it(), 0.01)
    def reload(self, btn):
        '''reloads from history to current table'''
        self.view_model.reload(btn.lst[0], btn.lst[1])
        self.parent.do_update()
    def graph_it(self):
        '''prepares plot and calls PlotPopup'''
        to_plot = []
        for item in self.ids['graph_space'].children[:]:
            if isinstance(item, PlotCheckBox):
                if item.active:
                    to_plot.append((item.text, item.tuple_list))
        plots = self.view_model.graph_it(to_plot)
        self.update()
        if plots[2]:
            #plotter = PlotPopup()
            #plotter.add_list(to_plot)
            #plotter.open()

            #for line in plt.figure(1).axes[0].lines:
            #    if line.get_label() == 'hi':
            #        print line.get_ydata()
            #        line.set_zorder(10)
            plt.figure(1)
            plt.clf()
            plt.ion()
            plt.ylabel('pct of the total occurences')
            plt.xlabel('values')
            pt_style = itertools_cycle(['o', '<', '>', 'v', 's', 'p', '*',
                                        'h', 'H', '+', 'x', 'D', 'd'])
            colors = itertools_cycle(['b', 'g', 'y', 'r', 'c', 'm', 'y', 'k'])
            for text, pts in plots[2]:
                style = '{}-{}'.format(next(pt_style), next(colors))
                plt.plot(pts[0], pts[1], style, label=text)
            plt.legend(loc='best')
            plt.show()
    def clear_all(self, btn):
        '''clear graph history'''
        self.confirm.dismiss()
        self.view_model.clear_all()
        self.update()
    def clear_selected(self):
        '''clear selected checked items from graph history'''
        to_clear = []
        for item in self.ids['graph_space'].children[1:]:
            if isinstance(item, PlotCheckBox):
                if item.active:
                    to_clear.append((item.text, item.tuple_list))
        self.view_model.clear_selected(to_clear)
        self.update()
    
    


# kv file line 362
class DicePlatform(BoxLayout):
    '''the main box.  the parent_app.'''
    def __init__(self, **kwargs):
        super(DicePlatform, self).__init__(**kwargs)
        self.direction = 'right'
        self.loop = 'true'

        table = mvm.TableManager()
        history = mvm.HistoryManager()
        self._read_hist_msg = history.read_history()
        change = mvm.ChangeBox(table)
        add = mvm.AddBox(table)
        stat = mvm.StatBox(table)
        graph = mvm.GraphBox(table, history, True)
        info = mvm.InfoBox(table)
        self.ids['change_box'].view_model = change
        self.ids['add_box'].view_model = add
        self.ids['stat_box'].view_model = stat
        self.ids['graph_box'].view_model = graph
        self.ids['info_box'].view_model = info
        self.initializer()
    def initializer(self):
        '''initializes various values that couldn't be written before both .py
        file and .kv file were called'''
        self.ids['add_box'].initialize()
        self.ids['graph_box'].initialize()
        self.ids['info_box'].initialize()
        if self._read_hist_msg == 'ok':
            header = ('IF YOU GO TO THE GRAPH AREA,\n'+
                      'YOU\'LL FIND YOUR PREVIOUS HISTORY\n\n')
        elif self._read_hist_msg in ['ok: no history', 'error: no file']:
            header = ''
        else:
            header = ('TRIED TO LOAD HISTORY BUT\nTHE FILE HAD AN ERROR\n'+
                      'whatcha gonna do about it?  cry?\n\n')
        self.ids['change_box'].ids['intro'].text = header + INTRO_TEXT

    def do_update(self):
        '''updates appropriate things for any die add or remove'''
        self.ids['change_box'].update()
        self.ids['add_box'].update()
        self.ids['stat_box'].update()
        self.ids['graph_box'].update()
        self.ids['info_box'].update()

# kv file line NONE
class DiceTableWideApp(App):
    '''the main app'''
    def build(self):
        '''builds app'''
        bob = DicePlatform()
        Window.size = (1500, 700)
        return bob

    def on_pause(self):
        '''allows pausing on android'''
        return True
    def on_resume(self):
        '''required with on_pause()'''
        pass
if __name__ == '__main__':
    DiceTableWideApp().run()

