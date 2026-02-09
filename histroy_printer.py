import json

import browser_history
import operator
from tkinter import *
import uuid
import tkinter as tk
from tkinter import ttk



class history_printer():
    def get(self):
        outputs = browser_history.get_history()
        x = str(outputs.to_csv())
        x=x.splitlines()
        x=x[1:]
        for i in range(len(x)):
            x[i]=x[i][34:]
        sits= {}

        for line in x:
            name=line[:line.find('/')]
            if (name) in sits:
                sits[name]+=1
            else:
                sits.update({name: int(1)})



        sits = sorted(sits.items(), key=operator.itemgetter(1), reverse=True)
        sits=dict(sits)
        return sits





    def json_tree(self,tree, parent, dictionary):
        for key in dictionary:
            uid = uuid.uuid4()
            if isinstance(dictionary[key], dict):
                tree.insert(parent, 'end', uid, text=key)
                self.json_tree(tree, uid, dictionary[key])
            elif isinstance(dictionary[key], list):
                tree.insert(parent, 'end', uid, text=key + '[]')
                self.json_tree(tree,
                          uid,
                          dict([(i, x) for i, x in enumerate(dictionary[key])]))
            else:
                value = dictionary[key]
                if value is None:
                    value = 'None'
                tree.insert(parent, 'end', uid, text=key, value=value)


    def show_data(self,data):
        # Setup the root UI
        root = tk.Tk()
        root.title("browser history")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Setup the Frames
        tree_frame = ttk.Frame(root, padding="3")
        tree_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # Setup the Tree
        tree = ttk.Treeview(tree_frame, columns='Values')
        yscrollbar = ttk.Scrollbar(orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=yscrollbar.set)

        tree.grid(row=0, column=0, sticky="nsew")
        yscrollbar.grid(row=0, column=1, sticky='nse')
        yscrollbar.configure(command=tree.yview)

        tree.column('Values', width=100, anchor='center')
        tree.heading('Values', text='times visited')
        self.json_tree(tree, '', data)
        tree.pack(fill=tk.BOTH, expand=1)

        # Limit windows minimum dimensions
        root.update_idletasks()
        root.minsize(800, 800)
        root.mainloop()

    def alternate(self, data):
        root = Tk()
        root.geometry('350x450+700+200')
        scrollbar = Scrollbar(root)
        scrollbar.pack(side=RIGHT, fill=Y)
        mylist = Listbox(root, yscrollcommand=scrollbar.set,height=20,width=55)
        for k,v in data.items():
            mylist.insert(END, str(k) + ' ' + str(v))
        mylist.pack(side=LEFT, fill=BOTH)
        scrollbar.config(command=mylist.yview)
        mainloop()

#history_printer().alternate(history_printer().get())
#x= history_printer().get()
#history_printer().show_data(json.loads(json.dumps(x)))
#print(x)
#print(type(x))
#print(json.dumps(x))
#print(type(json.dumps(x)))
#print(type(json.loads(json.dumps(x))))
##
