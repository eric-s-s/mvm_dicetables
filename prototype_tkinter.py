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
        
            
    
class App(object):
    def __init__(self, master):
        master.minsize(width=666, height=666)
        self.frame = tk.Frame(master)
        
        #self.frame.config(height=50, width=50)
        self.frame.pack()
        table = mvm.TableManager()
        history = mvm.HistoryManager()
        
        self._read_hist_msg = history.read_history()
        
        change = mvm.ChangeBox(table)
        add = mvm.AddBox(table)
        stat = mvm.StatBox(table)
        graph = mvm.GraphBox(table, history, False)
        info = mvm.InfoBox(table)
        
        self.add_box = AddBox(self)
        self.add_box.view_model = add
        self.add_box.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.add_box.frame.config(borderwidth=5, relief=tk.GROOVE)
    def do_update(self):
        self.add_box.update()



if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)

    root.mainloop()
    root.destroy()
