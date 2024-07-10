from tkinter import Toplevel, Label, Listbox, Scrollbar, VERTICAL, END, BOTH, RIGHT, Y, LEFT, Button, TOP
from tkinter.messagebox import askyesno, showerror
import json

class HistoryWindow:
    def __init__(self, root, controller):
        self.controller = controller
        self.history_window = Toplevel(root)
        self.history_window.title("Prediction History")
        self.history_window.geometry("410x520")
        self.history_window.resizable(False, False)
        self.history_window.configure(bg='#E3CCB2')

        Label(self.history_window, text='ALL PREDICTIONS', font='Papyrus 17', bg='#E3CCB2', fg='#CB625F').pack()

        self.listbox = Listbox(self.history_window, width=60, height=20, fg='#3B5BA5', bg='#E3CCB2', font='Garamond 13')
        self.listbox.pack(side=TOP, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.listbox, orient=VERTICAL, command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.refresh_button = Button(self.history_window, text=" REFRESH ", bg='#67C2D4', fg='#3988A4', bd='5', font=('Poppins 10 bold'), command=self.display_history)
        self.refresh_button.pack(pady=5, side=LEFT)
        self.clear_button = Button(self.history_window, text='   CLEAR   ', bg='#67C2D4', bd='5', fg='#3988A4', font=('Poppins 10 bold'), command=self.clear_full_history)
        self.clear_button.pack(pady=5, side=RIGHT)

        self.history_window.protocol("WM_DELETE_WINDOW", self.close_history_window)

    def close_history_window(self):
        self.history_window.destroy()
        self.controller.is_running = False

    def display_history(self):
        self.listbox.delete(0, END)
        try:
            with open('model\history.json', 'r') as file:
                for line in file:
                    prediction = json.loads(line.strip())
                    self.listbox.insert(0, f"Name: {prediction['name']}, Gender: {prediction['gender']}, Accuracy: {prediction['probability']:.2f}%, Date: {prediction['date']}")
        except FileNotFoundError:
            showerror(title='Error', message='No history file found.')
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while loading the history: {str(e)}')

    def clear_full_history(self):
        if askyesno(title="Clear History", message="Are you sure you want to clear your history?"):
            self.controller.clear_history()
            self.display_history()
            self.close_history_window()