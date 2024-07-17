import threading
from tkinter import Tk
from tkinter.messagebox import showerror, askyesno
from model.model import Model
from view.main_window import MainWindow
from view.history_window import HistoryWindow
from datetime import datetime
class Controller:
    def __init__(self):
        self.model = Model()
        self.root = Tk()
        self.is_running = False
        self.predict_view = MainWindow(self.root, self)
        self.history_view = None

    def on_predict(self, event=None):
        def fetch_data():
            try:
                entered_name = self.predict_view.name_entry.get().strip()
                self.predict_view.clear_labels()
                if len(entered_name) < 2 or not entered_name.isalpha():
                    showerror(title='Error', message='Please enter a valid name containing only alphabetic characters.')
                    return

                self.predict_view.start_loading_animation()
                response = self.model.predict_gender(entered_name)
                name = response['name']
                gender = response['gender']
                probability = 100 * response['probability']

                self.predict_view.update_labels(name, gender, probability)

                date_today = datetime.now().strftime('%Y-%m-%d')
                self.model.session_history.append((name, gender, probability, date_today))
                self.model.save_history()

                self.update_history_listbox()
            except Exception as e:
                showerror(title='Error', message=f'An error occurred: Please make sure you have entered a correct name and are connected to the internet')
            finally:
                self.root.after(0, self.predict_view.stop_loading_animation)

        threading.Thread(target=fetch_data).start()

    def show_history(self):
        if not self.is_running:
            self.history_view = HistoryWindow(self.root, self)
            self.history_view.display_history()
            self.is_running = True

    def update_history_listbox(self):
        self.predict_view.update_history_listbox()

    def on_closing(self):
        if askyesno(title="Quit", message="Quit?"):
            self.root.destroy()

    def clear_history(self):
        try:
            with open('model\history.json', 'w') as file:
                pass
            self.update_history_listbox()
            self.predict_view.clear_labels()
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while clearing the history: {str(e)}')

    def load_history(self):
        return self.model.load_history()

    def run(self):
        self.root.mainloop()