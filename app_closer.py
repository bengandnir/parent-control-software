import tkinter as tk
from tkinter import Toplevel, Listbox, Scrollbar, Button, Label, messagebox, END, RIGHT, LEFT, Y, BOTH
import time


def open(data, client):
    """
    data: רשימת האפליקציות שהגיעה מהשרת.
    client: האובייקט שדרכו שולחים פקודות לשרת.
    """

    # שימוש ב-Toplevel כדי לפתוח חלון מעל החלון הראשי (ולא חלון חדש נפרד)
    win = Toplevel()
    win.title("Close Applications")
    win.geometry("500x500")

    # כותרת
    Label(win, text="Select application to close:", font=("Courier", 12, "bold")).pack(pady=10)

    # --- יצירת רשימה נגללת (הרבה יותר טוב מכפתורים) ---
    frame = tk.Frame(win)
    frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

    scrollbar = Scrollbar(frame)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Listbox שמכיל את האפליקציות
    mylist = Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))

    # הכנסת הנתונים לרשימה (דילוג על שורות הכותרת של PowerShell אם צריך)
    for line in data:
        # מסננים שורות ריקות או קצרות מדי
        if len(line.strip()) > 2:
            mylist.insert(END, line.strip())

    mylist.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.config(command=mylist.yview)

    # --- הפונקציה ששולחת את הפקודה לשרת ---
    def send_kill_command():
        try:
            # 1. משיגים את השורה שהמשתמש בחר
            selection_index = mylist.curselection()[0]
            selected_text = mylist.get(selection_index)

            # 2. חילוץ ה-PID (המספר הראשון בשורה)
            # הפלט מ-PowerShell הוא בדרך כלל: "PID   Name"
            # הפקודה split() לוקחת את האיבר הראשון
            pid = selected_text.split()[0]

            # בדיקה שזה אכן מספר
            if not pid.isdigit():
                messagebox.showerror("Error", "Could not extract PID")
                return

            print(f"Killing PID: {pid}")

            # 3. שליחה לשרת לפי הפרוטוקול הנכון!
            client.chatt('kill')  # קודם כל אומרים לשרת "תהרוג"
            time.sleep(0.1)  # נותנים לשרת רגע להתכונן
            client.chatt(pid)  # שולחים את המספר

            # מחיקה ויזואלית מהרשימה כדי לתת תחושה שזה עבד
            mylist.delete(selection_index)
            messagebox.showinfo("Sent", f"Command sent to kill PID {pid}")

        except IndexError:
            messagebox.showwarning("Warning", "Please select an app first.")
        except Exception as e:
            print(f"Error: {e}")

    # --- כפתורים למטה ---
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    # כפתור ההריגה
    kill_btn = Button(btn_frame, text="KILL SELECTED", bg="red", fg="white", font=("Arial", 10, "bold"),
                      command=send_kill_command)
    kill_btn.pack(side=LEFT, padx=10)

    # כפתור יציאה
    close_btn = Button(btn_frame, text="Close", command=win.destroy)
    close_btn.pack(side=LEFT, padx=10)