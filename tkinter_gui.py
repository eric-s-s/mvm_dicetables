
import matplotlib.pyplot as plt
from functools import partial
from itertools import cycle
from sys import version_info

from michaellange import ToolTip
import gui_model as mvm
from textcalc import safe_eval

if version_info[0] > 2:
    import tkinter as tk
    import tkinter.messagebox as msgbox
else:
    import Tkinter as tk
    import tkMessageBox as msgbox


HELP_TEXT = ('this is a platform for finding the probability of dice ' +
             'rolls for any set of dice. For example, the chance of ' +
             'rolling a 4 with 3 six-sided dice is 3 out of 216.\n\n' +

             'Start at the middle-top window.  pick a die size, ' +
             'and pick a number of dice to add. Add as many kinds of ' +
             'dice as you want. You can also add a modifier to the die ' +
             '(for example 3-sided die +4), or you can make the die a ' +
             'weighted die (a 2-sided die with weights 1:3, 2:8 rolls ' +
             'a \'one\'  3 times out of every 11 times).\n\n' +

             'Go to the left window to add or subtract ' +
             'dice already added. Mousing over a die label will give you ' +
             'details about the die.\n\n' +

             'The graph menu is for getting a graph of the set of dice. ' +
             'It records every set of dice that have been graphed in the ' +
             'history. The file menu allows you to edit the saved history' +
             'and reload_saved_dice_table those histories at any time.\n\n' +

             'The middle-bottom area will give you the stats of any set of ' +
             'rolls you choose. You can use the sliders to assign roll ' +
             'values, or use the inputs.  The inputs can use "+-* or 0-9".' +
             'The right window gives you details of the raw data.')



###### general tool #######
def make_lines(text, min_lines=1):
    """changes long title into multi-line title"""
    line_len = 30
    lines = []
    while len(text) > line_len:
        new_line = text[:line_len]
        text = text[line_len:]
        if '\\' in new_line:
            text = new_line[new_line.rfind('\\'):] + text
            new_line = new_line[:new_line.rfind('\\')]
        lines.append(new_line)

    lines.append(text)
    for _ in range(min_lines - len(lines)):
        lines.append(' ')
    return '\n'.join(lines)


def make_tool_tip_for_die(label, text, delay=300):
    return ToolTip(label, text, delay, wraplength=300, font=('courier', 7))


class NumberInput(tk.Entry):
    """a text entry that only allows digits and '+', '-', ' '. will calculate
    basic arithmetic"""
    def __init__(self, master, reset=True, *args, **kwargs):
        """exactly like entry, but reset decides if it will reset when mouse
        clicked"""
        tk.Entry.__init__(self, master, *args, **kwargs)
        vcmd = (self.register(self.validate), '%S')
        self.config(validate='key', validatecommand=vcmd)
        if reset:
            self.bind('<Button-1>', self.reset)

    def reset(self, event):
        """erases the entry on a mouse click inside box"""
        self.delete(0, tk.END)

    def validate(self, text):
        """checks to make sure each piece of the title is in acceptable list"""
        for element in text:
            if element not in '1234567890+-* ()':
                self.bell()
                return False
        return True

    def calculate(self):
        text = self.get()
        self.delete(0, tk.END)
        ans = int(safe_eval(text, '**', '^', '//', '/')[0])
        self.insert(tk.END, str(ans))
        return ans


#  AddBox  and widget########
class WeightPopup(object):
    """a popup that records weights for a weighted die"""
    def __init__(self, master, text_list):
        """need a list of texts of for "weight for <roll>". creates TopLevel
        and populates it. MASTER MUST HAVE "record_weights()" METHOD!!!"""
        self.master = master
        self.window = tk.Toplevel()
        self.add_weights(text_list)

    def add_weights(self, text_list):
        """the function that populate the toplevel"""
        max_cols = 12
        self.window.title('makin weights')
        for index, title in enumerate(text_list):
            col, row = divmod(index, max_cols)
            scale = tk.Scale(self.window, from_=0, to=10, label=title, length=120,
                             orient=tk.HORIZONTAL)
            scale.set(1)
            scale.grid(column=col, row=row)
        enter_weights = tk.Button(self.window, command=self.record_weights,
                                  text='RECORD\nWEIGHTS',
                                  bg='pale turquoise', fg='red')
        col_num, row_num = divmod(len(text_list), max_cols)
        enter_weights.grid(column=col_num, row=row_num)

    def record_weights(self):
        """records weights as tuples (title, weight_val) and passes to parent's
        record_weights()"""
        out = []
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Scale):
                out.append((widget.cget('label'), widget.get()))
        self.master.record_weights(out)
        self.window.destroy()


class AddBox(object):
    """a view for adding dice.  contains a frame for display"""
    def __init__(self, master):
        """master is an object that has master.frame."""
        self.master = master
        self.frame = tk.Frame(master.frame)

        self.frame.grid_columnconfigure(0, pad=20)
        self.frame.grid_columnconfigure(1, pad=20)
        self.frame.grid_columnconfigure(2, pad=20)
        self.frame.grid_columnconfigure(3, pad=20)

        self.view_model = mvm.AddBox(mvm.DiceTableManager())

        self.current = tk.StringVar()
        self.current.set('\n\n\n\n')
        tk.Label(self.frame, textvariable=self.current).grid(
            column=0, row=0, sticky=tk.W+tk.E+tk.S+tk.N,
            columnspan=4)

        any_size_lbl = tk.Label(self.frame, text='may input\nany size')
        any_size_lbl.grid(column=0, row=1)
        ToolTip(any_size_lbl,
                'type in a die size between 2 and 200 and press enter.', 250)
        weights = tk.Button(self.frame, text='make\nweights', bg='thistle1',
                            command=self.add_weights)
        weights.grid(column=1, row=1, rowspan=2)
        weights_text = ('A two-sided die with weights 1:4, 2:1 means that it ' +
                        'rolls a one 4 times as often as a 2')
        ToolTip(weights, weights_text, 200)
        strength_lbl = tk.Label(self.frame, text='strength')
        strength_lbl.grid(column=2, row=1)
        strength_text = 'A three-sided die X4 rolls 4, 8, 12 instead of 1, 2, 3'
        ToolTip(strength_lbl, strength_text, 200)
        mod_label = tk.Label(self.frame, text='die\nmodifier')
        mod_label.grid(column=3, row=1)
        ToolTip(mod_label, 'D3+2 rolls 3, 4, 5 instead of 1, 2, 3', 200)

        self.any_size = NumberInput(self.frame, width=10, bg='thistle1')
        self.any_size.bind('<Return>', self.assign_size_text)
        self.any_size.grid(column=0, row=2)

        multiplier = tk.StringVar()
        multiplier.set('X1')
        multiplier.trace('w', partial(self.assign_multiplier, multiplier))
        strength = tk.OptionMenu(self.frame, multiplier,
                                 *['X{}'.format(num) for num in range(1, 11)])
        strength.config(bg='thistle1', activebackground='thistle1')
        strength.grid(column=2, row=2)

        mod = tk.Scale(self.frame, from_=5, to=-5, command=self.assign_mod,
                       bg='thistle1', activebackground='thistle1')
        mod.grid(column=3, row=2, rowspan=2)

        preset = tk.Frame(self.frame)
        for index, preset_text in enumerate(self.view_model.presets):
            btn = tk.Button(preset, text=preset_text, bg='thistle1',
                            command=partial(self.assign_size_btn, preset_text))
            row_, col_ = divmod(index, 4)
            btn.grid(row=row_, column=col_, padx=5)
        preset.grid(column=0, row=3, sticky=tk.NSEW, columnspan=3)
        instruct = tk.Label(self.frame, text=50*'-', bg='PaleTurquoise1')
        instruct.grid(column=0, row=4, sticky=tk.NSEW, columnspan=4)
        instructions = ('Use buttons above to create the die you want. ' +
                        'Then use the "+" buttons below to add it to the table')
        ToolTip(instruct, instructions, 200)
        self.adder = tk.Frame(self.frame)
        self.adder.grid(column=0, row=5, sticky=tk.NSEW, columnspan=4)

        self.display_die()

    def update(self):
        """called by main app at dice change"""
        self.current.set(make_lines(self.view_model.display_current_table(),
                                    min_lines=5))
    def assign_size_btn(self, txt):
        """assigns the die size and die when a preset btn is pushed"""
        die_size = int(txt[1:])
        self.any_size.delete(0, tk.END)
        self.any_size.insert(tk.END, str(die_size))
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_size_text(self, event):
        """asigns the die size and die when title is entered"""
        top = 200
        bottom = 2
        die_size = event.widget.calculate()
        die_size = min(top, max(bottom, die_size))
        event.widget.delete(0, tk.END)
        event.widget.insert(tk.END, str(die_size))
        self.view_model.set_size(die_size)
        self.display_die()
    def assign_mod(self, mod_val):
        """assigns a die modifier and new die when slider is moved"""
        mod = int(mod_val)
        self.view_model.set_mod(mod)
        self.display_die()
    def assign_multiplier(self, multiplier_var, *args):
        """assigns a die multiplier and new_die based on spinner's title."""
        multiplier = int(multiplier_var.get()[1:])
        self.view_model.set_multiplier(multiplier)
        self.display_die()
    def display_die(self):
        """all changes to size, mod and weight call this function"""
        for widget in self.adder.winfo_children():
            widget.destroy()
        to_add = self.view_model.display_die()
        the_die = tk.Label(self.adder, text='  ' + to_add[0] + '  ',
                           bg='violet')
        the_die.pack(side=tk.LEFT)
        make_tool_tip_for_die(the_die, self.view_model.get_die_details())
        for add_val in to_add[1:]:
            widget = tk.Button(self.adder, text=add_val,
                               command=partial(self.add, add_val))
            widget.pack(side=tk.LEFT)
    def add_weights(self):
        """sends view_model info to a WeightPopup"""
        WeightPopup(self, self.view_model.get_weights_text())
    def record_weights(self, lst):
        """passes WeightPopup's infor to the view_model."""
        self.view_model.record_weights_text(lst)
        self.display_die()
    def add(self, txt):
        """uses btn title and die stored in view_model to add to current table"""
        self.view_model.add(int(txt))
        self.master.do_update()
###### ChangeBox no extra classes #######
class ChangeBox(object):
    """a view for changing dice.  contains a frame for display"""
    def __init__(self, master):
        """master is an object that has master.frame."""
        self.master = master
        self.frame = tk.Frame(master.frame)
        self.view_model = mvm.ChangeBox(mvm.DiceTableManager())
    def add_rm(self, text, die):
        """uses die stored in button and btn title to request add or rm"""
        self.view_model.add_rm(int(text), die)
        self.master.do_update()
    def reset(self):
        """resets current table back to empty and display instructions"""
        self.view_model.reset()
        self.master.do_update()
    def update(self):
        """updates the current dice after add, rm or clear"""
        button_list = self.view_model.display()
        die_tool_tip_list = self.view_model.get_dice_details()
        for widget in self.frame.winfo_children():
            widget.destroy()
        if button_list:
            reset = tk.Button(self.frame, text='reset table', command=self.reset)
            reset.pack()
        else:
            label = tk.Label(self.frame, text='EMPTY TABLE')
            label.pack()
            text = ('Once you add dice, they will show up here. '+
                    'Hover over a die to see its details.')
            ToolTip(label, text, 100)
        # for labels, die_ in button_list:
        for index, tool_tip_text in enumerate(die_tool_tip_list):
            labels, die_ = button_list[index]
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
                    label = tk.Label(box, text=label, bg='violet')
                    label.pack(side=tk.LEFT, expand=True)
                    make_tool_tip_for_die(label, tool_tip_text)

########## StatBox #########
class StatBox(object):
    """a view for changing dice.  contains a frame for display"""
    def __init__(self, master, view_model):
        """master is an object that has master.frame."""
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

        help_text = ('You may input numbers or any expression like:\n' +
                     '"1 + -5 *3"\nThen press "Enter".')

        left = tk.Label(self.frame, text='input\nleft value')
        left.grid(row=1, column=0)
        ToolTip(left, help_text, 250)
        left_var = tk.IntVar()
        left_input = NumberInput(self.frame, width=10, bg='light yellow')
        left_input.grid(row=2, column=0)

        right = tk.Label(self.frame, text='input\nright value')
        right.grid(row=3, column=0)
        ToolTip(right, help_text, 250)
        right_var = tk.IntVar()
        right_input = NumberInput(self.frame, width=10, bg='ivory')
        right_input.grid(row=4, column=0)
        def set_reset(int_var, event):
            """gets the int from a NumberInput from the event
            and assigns to IntVar. resets NumberInput"""
            int_var.set(event.widget.calculate())
            event.widget.reset(event)
            self.assign_slider_value()
        left_input.bind('<Return>', partial(set_reset, left_var))
        right_input.bind('<Return>', partial(set_reset, right_var))

        self.left = tk.Scale(self.frame, from_=1, to=0, variable=left_var,
                             command=lambda val: self.assign_slider_value(),
                             bg='light yellow', activebackground='light yellow')
        self.left.grid(row=1, column=1, rowspan=4)
        self.right = tk.Scale(self.frame, from_=1, to=0, variable=right_var,
                              command=lambda val: self.assign_slider_value(),
                              bg='ivory', activebackground='ivory')
        self.right.grid(row=1, column=2, rowspan=4)
        stat = tk.Label(self.frame, textvariable=self.stat_text)
        stat.grid(row=5, column=0, columnspan=3, sticky=tk.EW)
    def update(self):
        """called when dice list changes."""
        val_1 = int(self.left.get())
        val_2 = int(self.right.get())
        info_text, stat_text, vals, min_max = self.view_model.display(val_1,
                                                                      val_2)
        self.info_text.set(info_text)
        self.left.config(from_=min_max[1])
        self.left.config(to=min_max[0])
        self.right.config(from_=min_max[1])
        self.right.config(to=min_max[0])
        self.display_stats(stat_text, vals)
    def display_stats(self, stat_text, vals):
        """takes a stat title and two values, and displays them."""
        self.stat_text.set(stat_text)
        self.left.set(vals[0])
        self.right.set(vals[1])
    def assign_slider_value(self):
        """the main function. displays stats of current slider values."""
        val_1 = self.left.get()
        val_2 = self.right.get()
        self.display_stats(*self.view_model.display_stats(val_1, val_2))

#####  GraphBox  #########
#popup choice for graph/history menus
class HistoryChooser(object):
    """makes a popup of choices from master's history.  does the action passed
    to it."""
    def __init__(self, master, partial_action, button_name, add_current=False):
        """creates a popup of check boxes.  and a button with title=button_name.
        when button is pressed, makes a list of all chosen histories and does
        the partial action on the list. add_current includes the current table
        in the list."""
        self.master = master
        self.action = partial_action
        self.choices = []
        self.window = tk.Toplevel()
        self.window.title('Check boxes and push that button!')
        self.pack_window(add_current)
        tk.Button(self.window, text=button_name, bg='CadetBlue1',
                  command=self.do_action).pack(side=tk.LEFT, fill=tk.X)
        tk.Button(self.window, text='Cancel', bg='RosyBrown1',
                  command=self.window.destroy).pack(side=tk.RIGHT, fill=tk.X)
    def pack_window(self, add_current):
        """packs the window.  if add_current=True, makes a special box for the
        current table."""
        current, old = self.master.view_model.display()
        for text, tuples in old:
            do_it = tk.IntVar()
            tk.Checkbutton(
                self.window, variable=do_it, text=make_lines(text),
                borderwidth=5, relief=tk.GROOVE, anchor=tk.W
                ).pack(side=tk.TOP, fill=tk.X)
            self.choices.append((do_it, (text, tuples)))
        if add_current and current[0]:
            do_it = tk.IntVar()
            btn = tk.Checkbutton(
                self.window, variable=do_it, borderwidth=5, bg='pale turquoise',
                relief=tk.GROOVE, anchor=tk.W, text=make_lines(current[0])
                )
            btn.pack(fill=tk.X)
            btn.select()
            self.choices.append((do_it, current))
    def do_action(self):
        """makes a list of all chosen title/tuples and does the action on them"""
        chosen = []
        for do_it, to_act in self.choices:
            if do_it.get():
                chosen.append(to_act)
        self.action(chosen)
        self.window.destroy()
class GraphMenu(object):
    """a view for changing dice.  contains a frame for display"""
    def __init__(self, master, view_model):
        """master is an object that has master.frame."""
        self.master = master
        self.view_model = view_model
        menubar = tk.Menu(root)
        self.reloader = tk.Menu(menubar, tearoff=0)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Current", command=self.save)
        filemenu.add_cascade(label='Reload File', menu=self.reloader)

        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        graph_menu = tk.Menu(menubar, tearoff=0)
        graph_menu.add_command(label="Graph Current", command=self.graph_current)
        graph_menu.add_command(label="Graph All", command=self.graph_all)
        graph_menu.add_command(label="Select Graphs", command=self.open_grapher)
        menubar.add_cascade(label="Graph", menu=graph_menu)

        history = tk.Menu(menubar, tearoff=0)
        history.add_command(label="Clear History", command=self.clear_hist)
        history.add_command(label="Edit History", command=self.edit_hist)
        filemenu.insert_cascade(2, label='Manage History', menu=history)

        about = tk.Menu(menubar, tearoff=0)
        def show_help():
            """opens a help window"""
            help_window = tk.Toplevel()
            text = tk.Text(help_window, wrap=tk.WORD)
            text.insert(tk.END, HELP_TEXT)
            text.config(state=tk.DISABLED)
            text.pack()
            tk.Button(help_window, text='Done', command=help_window.destroy,
                      bg='light yellow').pack(side=tk.BOTTOM, fill=tk.X)
        about.add_command(label='Help', command=show_help)

        menubar.add_cascade(label="About", menu=about)
        root.config(menu=menubar)
        self.pack_reloader()

    def pack_reloader(self):
        """populates the "Reload File" cascade"""
        self.reloader.delete(0, tk.END)
        for text, tuple_list in self.view_model.display()[1]:
            self.reloader.add_command(label=make_lines(text),
                                      command=partial(self.reload, text,
                                                      tuple_list))
    def reload(self, text, tuple_list):
        """reloads a table and calls update"""
        self.view_model.reload_saved_dice_table(text, tuple_list)
        self.master.do_update()
    def save(self):
        """saves the current table in history"""
        self.view_model.get_and_save_current()
        self.pack_reloader()
    def graph_current(self):
        """graphs the current table and saves to history"""
        plots = [self.view_model.display()[0]]
        self.graph(plots)
    def graph_all(self):
        """graphs entire history"""
        current, old = self.view_model.display()
        old.append(current)
        self.graph(old)
    def open_grapher(self):
        """called by Select graphs.  makes a popup choice list"""
        current, old = self.view_model.display()
        if current[0] or old:
            HistoryChooser(self, partial(self.graph), 'Graph\nSelected',
                           add_current=True)
        else:
            msgbox.showinfo('Empty', 'No graphs to select')
    def graph(self, plot_lst):
        """all graph functions call this base function to graph. plot_list is
        a list of tuples (title, pts)"""
        plots = self.view_model.get_requested_graphs(plot_lst)
        self.pack_reloader()
        if plots[2]:
            plt.figure(1)
            plt.clf()
            plt.ion()
            plt.ylabel('pct of the total occurences')
            plt.xlabel('values')
            pt_style = cycle(['o', '<', '>', 'v', 's', 'p', '*',
                              'h', 'H', '+', 'x', 'D', 'd'])
            colors = cycle(['b', 'g', 'y', 'r', 'c', 'm', 'y', 'k'])
            for text, pts in plots[2]:
                style = '{}-{}'.format(next(pt_style), next(colors))
                plt.plot(pts[0], pts[1], style, label=text)
            plt.legend(loc='best')
            plt.show()
        else:
            msgbox.showinfo('No graphs', 'Your selection\ncontains no graphs')
    def clear_hist(self):
        """clears the history"""
        if self.view_model.display()[1]:
            if msgbox.askquestion('delete', 'Delete All?') == 'yes':
                self.view_model.delete_all()
                self.pack_reloader()
    def clear_selected(self, text_tuples_lst):
        """gets passed a list of (title, tuple_list).  clears those tables from
        history"""
        self.view_model.delete_requested(text_tuples_lst)
        self.pack_reloader()
    def edit_hist(self):
        """calls a popup to get a list for self.delete_requested"""
        if self.view_model.display()[1]:
            HistoryChooser(self, partial(self.clear_selected),
                           'Clear\nSelected')
        else:
            msgbox.showinfo('Empty', 'The history is empty')

class App(object):
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.columnconfigure(0, minsize=300, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.pack()
        table = mvm.DiceTableManager()
        history = mvm.SavedTables()

        #reloads history file.  if corrupted, notifies and writes an empty hist
        hist_msg = history.reload_from_file()
        if 'ok' not in hist_msg and hist_msg != 'error: no file':
            msgbox.showinfo('Error', 'Error loading history:\n' + hist_msg)
            history.write_to_file()
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
        label_btn = tk.Frame(info_frame)
        label_btn.pack(fill=tk.X)
        info_lbl = tk.Label(label_btn, fg='white', bg='blue',
                            text='here are all the rolls\nand their frequency')
        info_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Button(label_btn, text='Weights\ninfo', bg='light yellow',
                  command=self.weight_info).pack(side=tk.LEFT, padx=5, pady=5)
        text_scrollbar = tk.Scrollbar(info_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text = tk.Text(info_frame, yscrollcommand=text_scrollbar.set,
                                 width=20)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.info_text.yview)

        self.frame.columnconfigure(0, minsize=300, weight=1)
        self.do_update()
    def do_update(self):
        self.add_box.update()
        self.change_box.update()
        self.stat_box.update()
        self.update_info_box()
        #self.menus.update()
    def weight_info(self):
        weights = tk.Toplevel()
        done = tk.Button(weights, text='Done', command=weights.destroy,
                         bg='light yellow')
        done.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar = tk.Scrollbar(weights)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        weight_info = tk.Text(weights, yscrollcommand=scrollbar.set,
                              wrap=tk.NONE, width=20)
        weight_info.insert(tk.END, self.info.display()[2])
        weight_info.config(state=tk.DISABLED)
        weight_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=weight_info.yview)

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
    root.title('Dice Tables!')
    root.mainloop()
    root.destroy()
