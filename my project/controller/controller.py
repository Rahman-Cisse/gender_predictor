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
                #make clear all previous searches that are currently being displayed
                self.predict_view.clear_labels()
                #validate the user's input
                if len(entered_name) < 2 or not entered_name.isalpha():
                    showerror(title='Error', message='Please enter a valid name containing only alphabetic characters.')
                    return
                #to show the loading gif
                self.predict_view.start_loading_animation()
                #getting the information using requests
                response = self.model.predict_gender(entered_name)
                name = response['name']
                gender = response['gender']
                probability = 100 * response['probability']
                #to display the information to the user
                self.predict_view.update_labels(name, gender, probability)
                #the current date
                date_today = datetime.now().strftime('%Y-%m-%d')
                #updating the history listbox
                self.model.session_history.append((name, gender, probability, date_today))
                #storing the information gotten
                self.model.save_history()
                #displaying the information stored in the listbox
                self.update_history_listbox()
            except Exception as e:
                showerror(title='Error', message=f'An error occurred: Please make sure you have entered a correct name and are connected to the internet')
            finally:
                self.root.after(0, self.predict_view.stop_loading_animation)

        threading.Thread(target=fetch_data).start()
    #to allow only one history window to be opened at a time
    def show_history(self):
        if not self.is_running:
            self.history_view = HistoryWindow(self.root, self)
            self.history_view.display_history()
            self.is_running = True
    #to display stored information in the listbox on the main window
    def update_history_listbox(self):
        self.predict_view.update_history_listbox()
    #to make suer the user wants to close the program by asking a yes or no question to the user
    def on_closing(self):
        if askyesno(title="Quit", message="Quit?"):
            self.root.destroy()
    #function to clear all infoemation in the json file storing the history
    def clear_history(self):
        try:
            with open('model\history.json', 'w') as file:
                pass
            self.update_history_listbox()
            self.predict_view.clear_labels()
            self.predict_view.clear_entrybox()
            self.predict_view.show_prediction_tab()
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while clearing the history: {str(e)}')
    # function to prepare stored info
    def load_history(self):
        return self.model.load_history()
    #main command to run programme
    def run(self):
        self.root.mainloop()