import json
import tkinter as tk
from tkinter import messagebox
from tkinter import *
import app_closer
import time
import operator
import browser_history
import uuid
from tkinter import ttk
class pages():


    def green(self, x):

        self.gren = tk.Label(self, background="green",font = ("Courier", 10, 'bold'), fg="white", text='filler')
        self.gren.grid(row=2, column=1, rowspan=6, columnspan=2, sticky="nsew")
        x.chatt('green')

    def blue(self, x):
        self.gren = tk.Label(self, background="blue",font = ("Courier", 10, 'bold'), fg="white", text='filler')
        self.gren.grid(row=2, column=1, rowspan=6, columnspan=2, sticky="nsew")
        x.chatt('blue')

    def red(self, x):
        self.gren =tk.Label(self, background="red",font = ("Courier", 10, 'bold'), fg="white", text='filler')
        self.gren.grid(row=2, column=1, rowspan=6, columnspan=2, sticky="nsew")
        x.chatt('red')

    def close(self,x, root):
        root.destroy()
        x.chatt('exit')

    def closee(self,x, root):
        root.destroy()
        x.chatt('exitt')

        # הפונקציה שמתחילה את התהליך
    def open(self, x, root):
        print("Requesting running apps list...")
        x.chatt('close')  # שולח את הפקודה לשרת
        # מתחיל את הבדיקה ברקע
        pages.check_apps_response(self, x, root)


    def check_apps_response(self, x, root):
        y = x.get_hold()
        if type(y) != list:
            print("Apps list not ready, checking again in 1s...")
            root.after(1000, lambda: pages.check_apps_response(self, x, root))
            return
        print("Got apps list!")
        print(y)
        try:
            app_closer.open(y, x)
        except Exception as e:
            print(f"Error opening app closer: {e}")

    def on_closing(x, root):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            x.chatt('exit')
            root.destroy()

    def force_lock(self, x, root):
            win = Toplevel()
            win.title('warning')
            message = "do you want to lock the pc, shot it down or cancel"
            Label(win, text=message).pack()
            Button(win, text='lock', command=lambda:x.chatt('lock')).pack()
            Button(win, text='close', command=lambda:x.chatt('shotdown')).pack()
            Button(win, text='cancel', command=win.destroy).pack()

    def res(self, x, root):
        win = Toplevel()
        win.title('restrict')
        message = "do you want to block the pc, release it or cancel"

        Label(win, text=message).pack()
        Button(win, text='restrict', command=lambda: x.chatt('block')).pack()
        Button(win, text='release', command=lambda: x.chatt('release')).pack()
        Button(win, text='cancel', command=win.destroy).pack()

    def digitalclock(self):
        #text_input = time.strftime("%H:%M:%S")
        tk.Label.config(text=time.strftime("%H:%M:%S"))
        tk.Label.after(200, self.digitalclock(self))


    def add(self, x):
        x.chatt('add')
        win = Tk()
        # Set the geometry of Tkinter frame
        win.geometry("750x250")
        global entry
        def display_text(x):
            string = entry.get()
            print('the string is: ' + string)
            x.chatt(string)

        # Create an Entry widget to accept User Input
        entry = Entry(win, width=40)
        entry.focus_set()
        entry.pack()

        label = Label(win, text="enter a site name to block", font=("Courier 22 bold"))
        label.pack()
        # Create a Button to validate Entry Widget
        ttk.Button(win, text="Okay", width=20, command=lambda:display_text(x)).pack(pady=20)
        def dead(win, x):
            x.chatt('done')
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", lambda:dead(win, x))
        win.mainloop()


    def get(self):
        print('gety')
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

    def history(self, x, root):
        print("Sending request for history...")
        x.chatt('get_history')

        # --- תיקון השגיאה כאן ---
        # במקום self.check_history... אנחנו קוראים למחלקה pages
        pages.check_history_response(self, x, root)

    def check_history_response(self, x, root):
        # מנסים לקבל נתונים
        y = x.get_hold()

        # בודקים אם הנתונים לא מוכנים
        is_waiting = (y is None or type(y) != str or y == '' or y == 'locked' or y == 'shot down')

        if is_waiting:
            print("History not ready, checking again in 2s...")
            # --- תיקון השגיאה גם כאן ---
            # קריאה ל-pages בתוך ה-after
            root.after(2000, lambda: pages.check_history_response(self, x, root))
            return

            # הנתונים הגיעו!
        print("Got history data!")
        try:
            y = json.loads(y)
            # --- וגם כאן ---
            pages.alternate(self, y)
        except Exception as e:
            print(f"Error displaying history: {e}")

    def send(self, msg, socket):
        print('1')
        length = len(msg)
        print('2')
        message = str(length) + msg
        print('3')
        socket.send(message.encode())
        print('4')
    def txt_to_array(self, site):
        my_file = open(site, "r")
        content = my_file.read()
        text = content.split(",")
        my_file.close()
        print(text)
        return text
#pages.add('x', 'x')