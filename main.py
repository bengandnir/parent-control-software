import threading
from tkinter import *
import tkinter as tk
import datetime
import threading
import time
from app_closer import *
from datetime import datetime
from pages import *
import client
class main_window(tk.Frame):

    def __init__(self, parent):

        self.x = client.client()

        tk.Frame.__init__(self, parent)

        self.font = ("Courier", 10, 'bold')
        self.buttons = []
        self.restrict = 'released'
        self.status= 'on'
        self.main = tk.Frame(self, background="green")

        self.logo = Label(self, background="black",font = self.font, fg = "white", text='logo')
        self.logo.grid(row=0, column=0, rowspan=2, sticky="nsew")

        #e7238da72f42d4254e8b85ba518930eb

        text = pages.txt_to_array(self, 'strings.txt')

        clock = tk.Label(self, font=self.font, bg="gray12", fg="white")
        clock.grid(row=0, column=2, sticky="nsew")

        def digitalclock():
            clock.config(text=time.strftime("%H:%M:%S"))
            clock.after(200, digitalclock)

        digitalclock()
        self.date=datetime.today().strftime('%Y-%m-%d')

        self.filler = Label(self, background="black", font = self.font, fg = "white", text='filler')
        self.filler.grid(row=2, column=1, rowspan=6, columnspan=2, sticky="nsew")

        self.other2 = tk.Label(self,font=self.font, background="gray14", fg="white", text = self.restrict)
        self.other3 = tk.Label(self,font=self.font, background="gray16", fg="white", text = self.status)
        self.other4 = tk.Label(self,font=self.font, background="gray18", fg="white", text = self.date)

        self.other2.grid(row=0, column=1, sticky="nsew")
        self.other3.grid(row=1, column=1, sticky="nsew")
        self.other4.grid(row=1, column=2, sticky="nsew")

        self.window_1 = tk.Button(self, font=self.font, text=text[4], command=lambda: pages.force_lock(self, self.x, root), background="gray10", fg="white")
        self.window_2 = tk.Button(self, font=self.font, text=text[3], command=lambda: pages.history(self, self.x, root),background="gray10", fg="white")
        self.window_3 = tk.Button(self, font=self.font, text=text[2], command=lambda: pages.open(self, self.x, root),background="gray10", fg="white")
        self.window_4 = tk.Button(self, font=self.font, text=text[1], command=lambda: pages.res(self, self.x, root),background="gray10", fg="white")
        self.window_5 = tk.Button(self, font=self.font, text=text[0], command=lambda: pages.add(self, self.x),background="gray10", fg="white")
        self.distract = tk.Button(self, font=self.font, text=text[5], command=lambda: pages.close(self,self.x, root), background="gray10", fg="white")

        for i in range(4):
            self.buttons.append(tk.Button(self, font=self.font, text="Button %s" % (i + 1,), background="gray10" , fg="white"))

        self.window_5.grid(row=2, column=0, sticky="nsew")
        self.window_4.grid(row=3, column=0, sticky="nsew")
        self.window_3.grid(row=4, column=0, sticky="nsew")
        self.window_2.grid(row=5, column=0, sticky="nsew")
        self.window_1.grid(row=6, column=0, sticky="nsew")
        self.distract.grid(row=7, rowspan=1,column=0, sticky="nsew")
        self.main.grid(row=2, column=2, columnspan=2, rowspan=6)

        for row in range(8):
            self.grid_rowconfigure(row, weight=1)
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

        root.protocol("WM_DELETE_WINDOW", lambda: pages.on_closing(self.x, root))





def raise_frame(frame):
    frame.tkraise()




if __name__ == "__main__":

    root = tk.Tk()
    main_window(root).pack(fill="both", expand=True)
    root.geometry("800x400")
    root.mainloop()



