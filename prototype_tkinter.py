from sys import version_info
if version_info[0] > 2:
    import tkinter as tk
else:
    import Tkinter as tk
from functools import partial
from decimal import Decimal
from itertools import cycle as itertools_cycle

import dicetables as dt

import numpy as np
import matplotlib.pyplot as plt

from michaellange import ToolTip
import dt_gui_mvm as mvm
import file_handler as fh

INTRO_TEXT = ('this is a platform for finding the probability of dice\n' +
              'rolls for any set of dice. For example, the chance of\n' +
              'rolling a 4 with 3 six-sided dice is 3 out of 216.\n\n' +

              'Swipe right ===> to get to the add box.  pick a die size,\n' +
              'and pick a number of dice to add. Add as many kinds of\n' +
              'dice as you want. You can also add a modifier to the die\n' +
              '(for example 3-sided die +4), or you can make the die a\n' +
              'weighted die (a 2-sided die with weights 1:3, 2:8 rolls\n' +
              'a \'one\'  3 times out of every 11 times).\n\n' +

              'come back to this window to add or subtract\n' +
              'dice already added.\n\n' +

              'The graph area is for getting a graph of the set of dice.\n' +
              'It records every set of dice that have been graphed and\n' +
              'you can reload those dice at any time.\n\n' +

              'The stats area will give you the stats of any set of\n' +
              'rolls you choose. The last window gives you details of\n' +
              'the raw data.')

###### general tool #######
class NumberInput(tk.Entry):
    '''a text entry that only allows digits and '+', '-', ' '. will calculate
    basic arithmatic'''
    def __init__(self, master, reset=True, *args, **kwargs):
        '''exactly like entry, but reset decides if it will reset when mouse
        clicked'''
        tk.Entry.__init__(self, master, *args, **kwargs)
        vcmd = (self.register(self.validate), '%S')
        self.config(validate='key', validatecommand=vcmd)
        if reset:
            self.bind('<Button-1>', self.reset)
    def reset(self, event):
        '''erases the entry on a mouse click inside box'''
        self.delete(0, tk.END)
    def validate(self, text):
        '''checks to make sure each piece of the text is in acceptable list'''
        for element in text:
            if element not in '1234567890+- ':
                self.bell()
                return False
        return True
    def calculate(self):
        '''parses text to calculatefinal value'''
        text = self.get()
        #make list of numbers and signs
        elements = []
        number_str = ''
        for element in text:
            if element in '0123456789':
                number_str += element
            elif element in ['+', '-']:
                if number_str:
                    elements.append(number_str)
                    number_str = ''
                elements.append(element)
        if number_str:
            elements.append(number_str)
        #caluculates elements
        answer = 0
        sign = 1
        for element in elements:
            if element.isdigit():
                answer += sign * int(element)
                sign = 1
            if element == '-':
                sign *= -1
        return answer        
#######  AddBox widgets ########
class WeightPopup(object):
    '''a popup that records weights for a weighted die'''
    def __init__(self, master, text_list):
        '''need a list of texts of for "weight for <roll>". creates TopLevel
        and populates it. MASTER MUST HAVE "record_weights()" METHOD!!!'''
        self.master = master
        self.window = tk.Toplevel()
        self.add_weights(text_list)
    def add_weights(self, text_list):
        '''the function that populate the toplevel'''   
        max_cols = 12
        self.window.title('makin weights')
        for index, title in enumerate(text_list):
            col, row = divmod(index, max_cols)
            scale = tk.Scale(self.window, from_=0, to=10, label=title,
                             orient=tk.HORIZONTAL)
            scale.set(1)
            scale.grid(column=col, row=row)
        enter_weights = tk.Button(self.window, command=self.record_weights,
                                  text='RECORD\nWEIGHTS',
                                  bg='pale turquoise', fg='red')
        col, row = divmod(len(text_list), max_cols)
        enter_weights.grid(column=col, row=row)
    def record_weights(self):
        '''records weights as tuples (text, weight_val) and passes to parent's
        record_weights()'''
        out = []
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Scale):
                out.append((widget.cget('label'), widget.get()))
        self.master.record_weights(out)
        self.window.destroy()    
class AddBox(object):
    '''a view for adding dice.  contains a frame for display'''
    def __init__(self, master):
        '''master is an object that has master.frame.'''
        self.master = master
        self.frame = tk.Frame(master.frame)
        
        self.frame.grid_columnconfigure(0, pad=20)
        self.frame.grid_columnconfigure(1, pad=20)
        self.frame.grid_columnconfigure(2, pad=20)
        self.frame.grid_columnconfigure(3, pad=20)

        self.view_model = mvm.AddBox(mvm.TableManager())
        
        self.current = tk.StringVar()
        self.current.set('\n\n\n\n')
        tk.Label(self.frame, textvariable=self.current).grid(
            column=0, row=0, sticky=tk.W+tk.E+tk.S+tk.N, 
            columnspan=4)
        
        tk.Label(self.frame, text='may input\nany size').grid(column=0, row=1)
        tk.Button(
            self.frame, text='make\nweights', command=self.add_weights
            ).grid(column=1, row=1, rowspan=2)
        tk.Label(self.frame, text='strength').grid(column=2, row=1)
        tk.Label(self.frame, text='die\nmodifier').grid(column=3, row=1)
        
        self.any_size = NumberInput(self.frame, width=10)
        self.any_size.bind('<Return>', self.assign_size_text)
        self.any_size.grid(column=0, row=2)
        
        multiplier = tk.StringVar()
        multiplier.set('X1')
        multiplier.trace('w', partial(self.assign_multiplier, multiplier))
        strength = tk.OptionMenu(self.frame, multiplier, 
                                 *['X{}'.format(num) for num in range(1, 11)])
        strength.grid(column=2, row=2)
        
        mod = tk.Scale(self.frame, from_=5, to=-5, command=self.assign_mod)
        mod.grid(column=3, row=2, rowspan=2)
        
        preset = tk.Frame(self.frame)
        for index, preset_text in enumerate(self.view_model.presets):
            btn = tk.Button(preset, text=preset_text,
                            command=partial(self.assign_size_btn, preset_text))
            row_, col_ = divmod(index, 4)
            btn.grid(row=row_, column=col_)
        preset.grid(column=0, row=3, sticky=tk.W+tk.E+tk.S+tk.N, columnspan=3)
        
        
        self.adder = tk.Frame(self.frame)
        self.adder.grid(column=0, row=4, sticky=tk.W+tk.E+tk.S+tk.N, columnspan=4)

        self.display_die()
    
    def update(self):
        '''called by main app at dice change'''
        def make_lines(text):
            '''changes long text into multi-line text'''
            line_len = 30
            num_lines = 5
            lines = []
            while len(text) > line_len:
                new_line = text[:line_len]
                text = text[line_len:]
                if '\\' in new_line:
                    text = new_line[new_line.rfind('\\'):] + text
                    new_line = new_line[:new_line.rfind('\\')]    
                lines.append(new_line)
                
            lines.append(text)
            for _ in range(num_lines - len(lines)):
                lines.append(' ')
            return '\n'.join(lines)
        self.current.set(make_lines(self.view_model.display_current()))
    def assign_size_btn(self, txt):
        '''assigns the die size and die when a preset btn is pushed'''
        die_size = int(txt[1:])
        self.any_size.delete(0, tk.END)
        self.any_size.insert(tk.END, str(die_size))
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_size_text(self, event):
        '''asigns the die size and die when text is entered'''
        top = 200
        bottom = 2
        die_size = self.any_size.calculate()
        die_size = min(top, max(bottom, die_size))
        self.any_size.delete(0, tk.END)
        self.any_size.insert(tk.END, str(die_size))
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_mod(self, mod_val):
        '''assigns a die modifier and new die when slider is moved'''
        mod = int(mod_val)
        self.view_model.set_mod(mod)
        self.display_die()
    def assign_multiplier(self, multiplier_var, *args):
        '''assigns a die multiplier and new_die based on spinner's text.'''       
        multiplier = int(multiplier_var.get()[1:])
        self.view_model.set_multiplier(multiplier)
        self.display_die()
    def display_die(self):
        '''all changes to size, mod and weight call this function'''
        for widget in self.adder.winfo_children():
            widget.destroy()
        to_add = self.view_model.display_die()
        tk.Label(self.adder, text=to_add[0]).grid(row=0, column=0, columnspan=2)
        for col, add_val in enumerate(to_add[1:]):
            widget = tk.Button(self.adder, text=add_val,
                               command=partial(self.add, add_val))
            widget.grid(row=0, column=col + 2)
    def add_weights(self):      
        '''sends view_model info to a WeightPopup'''
        WeightPopup(self, self.view_model.get_weights_text())
    def record_weights(self, lst):
        '''passes WeightPopup's infor to the view_model.'''
        self.view_model.record_weights_text(lst)
        self.display_die()            
    def add(self, txt):
        '''uses btn text and die stored in view_model to add to current table'''
        self.view_model.add(int(txt))
        self.master.do_update()
###### ChangeBox no extra classes #######        
class ChangeBox(object):
    '''a view for changing dice.  contains a frame for display'''
    def __init__(self, master):
        '''master is an object that has master.frame.'''
        self.master = master
        self.frame = tk.Frame(master.frame)
        self.view_model = mvm.ChangeBox(mvm.TableManager())            
    def add_rm(self, text, die):
        '''uses die stored in button and btn text to request add or rm'''
        self.view_model.add_rm(int(text), die)
        self.master.do_update()
    def reset(self):
        '''resets current table back to empty and display instructions'''
        self.view_model.reset()
        self.master.do_update()
        for widget in self.frame.winfo_children():
            widget.destroy()
        tk.Label(self.frame, text=INTRO_TEXT).pack()
    def update(self):
        '''updates the current dice after add, rm or clear'''
        button_list = self.view_model.display()
        for widget in self.frame.winfo_children():
            widget.destroy()
        reset = tk.Button(self.frame, text='reset table', command=self.reset)
        reset.pack()
        for labels, die_ in button_list:
            temp = labels[:]
            labels = []
            for label in temp:
                if '50' not in label or 'D' in label:
                    labels.append(label)
            box = tk.Frame(self.frame)
            box.pack(fill=tk.X)
            for label in labels:
                if label[0] == '-' or label[0] == '+':
                    btn = tk.Button(box, text=label, 
                                    command=partial(self.add_rm, label, die_))
                    btn.pack(side=tk.LEFT)
                else:
                    label = tk.Label(box, text=label)
                    text = die_.weight_info().replace('a roll of ', '')
                    text = text.replace('a weight of ', 'weight: ')
                    ToolTip(label, text, 100)
                    label.pack(side=tk.LEFT, expand=True)
class StatBox(object):
    '''a view for changing dice.  contains a frame for display'''
    def __init__(self, master, view_model):
        '''master is an object that has master.frame.'''
        self.master = master
        self.frame = tk.Frame(master.frame)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)
        self.view_model = view_model
        
        self.info_text = tk.StringVar()
        self.stat_text = tk.StringVar()
        
        info = tk.Label(self.frame, textvariable=self.info_text)
        info.grid(row=0, column=0, columnspan=3, sticky=tk.EW)
        
        tk.Label(self.frame, text='input\nleft value').grid(row=1, column=0)
        left_var = tk.IntVar()
        left_input = NumberInput(self.frame, width=10)
        left_input.grid(row=2, column=0)
        
        tk.Label(self.frame, text='input\nright value').grid(row=3, column=0)
        right_var = tk.IntVar()
        right_input = NumberInput(self.frame, width=10)
        right_input.grid(row=4, column=0)
        def set_reset(int_var, event):
            '''gets the int from a NumberInput from the event 
            and assigns to IntVar. resets NumberInput'''
            int_var.set(event.widget.calculate())
            event.widget.reset(event)
            self.assign_slider_value(1)
        left_input.bind('<Return>', partial(set_reset, left_var))
        right_input.bind('<Return>', partial(set_reset, right_var))

        self.left = tk.Scale(self.frame, from_=1, to=0, variable=left_var,
                             command=self.assign_slider_value)
        self.left.grid(row=1, column=1, rowspan=4)
        self.right = tk.Scale(self.frame, from_=1, to=0, variable=right_var,
                             command=self.assign_slider_value)
        self.right.grid(row=1, column=2, rowspan=4)
        stat = tk.Label(self.frame, textvariable=self.stat_text)
        stat.grid(row=5, column=0, columnspan=3, sticky=tk.EW)
    def update(self):
        '''called when dice list changes.'''
        val_1 = int(self.left.get())
        val_2 = int(self.right.get())
        info_text, stat_text, vals, min_max = self.view_model.display(val_1,
                                                                      val_2)
        self.info_text.set(info_text)
        self.left.config(from_ =min_max[1])
        self.left.config(to =min_max[0])
        self.right.config(from_ =min_max[1])
        self.right.config(to =min_max[0])
        self.display_stats(stat_text, vals)
    def display_stats(self, stat_text, vals):
        '''takes a stat text and two values, and displays them.'''
        self.stat_text.set(stat_text)
        self.left.set(vals[0])
        self.right.set(vals[1])
    def assign_slider_value(self, val):
        '''the main function. displays stats of current slider values.'''
        val_1 = self.left.get()
        val_2 = self.right.get()
        self.display_stats(*self.view_model.display_stats(val_1, val_2))

class GraphMenu(object):
    '''a view for changing dice.  contains a frame for display'''
    def __init__(self, master, view_model):
        '''master is an object that has master.frame.'''
        self.master = master
        self.view_model = view_model
        
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Reload", command=self.update)
        filemenu.add_command(label="Save Current", command=self.update)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Graph Current", command=self.update)
        editmenu.add_command(label="Graph All", command=self.update)
        editmenu.add_command(label="Select Graphs", command=self.update)
        menubar.add_cascade(label="Graph", menu=editmenu)
        
        history = tk.Menu(menubar, tearoff=0)
        history.add_command(label="Clear History", command=self.update)
        history.add_command(label="Edit History", command=self.update)
        filemenu.insert_cascade(2, label='Manage History', menu=history)

        root.config(menu=menubar)
    def update(self):
        pass
class App(object):
    def __init__(self, master):
        #master.minsize(width=666, height=666)
        self.frame = tk.Frame(master)
        self.frame.columnconfigure(0, minsize=300, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        #self.frame.columnconfigure(1, minsize=300, weight=1)
        #self.frame.config(height=50, width=50)
        self.frame.pack()
        table = mvm.TableManager()
        history = mvm.HistoryManager()
        
        hist_msg = history.read_history()
        
        change = mvm.ChangeBox(table)
        add = mvm.AddBox(table)
        stat = mvm.StatBox(table)
        self.menus = GraphMenu(self, mvm.GraphBox(table, history, True))
        self.info = mvm.InfoBox(table)
        self.change_box = ChangeBox(self)
        self.change_box.view_model = change
        self.add_box = AddBox(self)
        self.add_box.view_model = add
        self.stat_box = StatBox(self, stat)
        #self.stat_box.view_model = stat
        
        
        self.change_box.frame.grid(row=0, column=0, rowspan=2, sticky=tk.NSEW)
        self.change_box.frame.config(borderwidth=5, relief=tk.GROOVE)
        self.add_box.frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.add_box.frame.config(borderwidth=5, relief=tk.GROOVE)
        self.stat_box.frame.grid(row=1, column=1, sticky=tk.NSEW)
        self.stat_box.frame.config(borderwidth=5, relief=tk.GROOVE)
        
        
        #the info frame
        info_frame = tk.Frame(self.frame, borderwidth=5, relief=tk.GROOVE)
        info_frame.grid(row=0, column=3, rowspan=2, sticky=tk.NSEW)
        tk.Label(info_frame, text='here are all the rolls\nand their frequency',
                 fg='white', bg='blue').pack()
        text_scrollbar = tk.Scrollbar(info_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text = tk.Text(info_frame, yscrollcommand=text_scrollbar.set,
                                 width=20)
        self.info_text.pack(side=tk.LEFT, fill=tk.Y)
        text_scrollbar.config(command=self.info_text.yview)
        
        self.frame.columnconfigure(0, minsize=300, weight=1)
        self.do_update()
    def do_update(self):
        self.add_box.update()
        self.change_box.update()
        self.stat_box.update()
        self.update_info_box()
        self.menus.update()
    def update_info_box(self):
        info = self.info.display()[3]
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    root.minsize(width=800, height=666)
    root.mainloop()
    root.destroy()
