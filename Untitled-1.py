from tkinter import *
from tkinter import ttk
import requests
from tkinter.messagebox import showerror, askyesno
from PIL import Image, ImageTk, ImageSequence
import threading
import json
from datetime import datetime

# List to store the history of predictions for the current session
session_history = []
is_running = False

# Function to predict gender based on name input
def predict_gender(Event=None):
    def fetch_data():
        try:
            entered_name = name_entry.get().strip()
            clear_labels()

            if len(entered_name) < 2 or not entered_name.isalpha():
                showerror(title='Error', message='Please enter a valid name containing only alphabetic characters.')
                return

            start_loading_animation()

            response = requests.get(f'https://api.genderize.io/?name={entered_name}').json()
            name = response.get('name')
            gender = response.get('gender')
            probability = 100 * response.get('probability', 0)

            if name and gender:
                update_labels(name, gender, probability)
                session_history.append((name, gender, probability, datetime.now().strftime('%Y-%m-%d')))
                save_history()
                update_history_listbox()
            else:
                showerror(title='Error', message='Unexpected response format: please enter a correct name')
        except requests.exceptions.RequestException:
            showerror(title='Error', message='Network error: Make sure you are connected to the internet')
        except Exception as e:
            showerror(title='Error', message=f'An error occurred: {str(e)}')
        finally:
            gui.after(0, stop_loading_animation)

    threading.Thread(target=fetch_data).start()

def clear_labels():
    name_label.config(text='')
    gender_label.config(text='')
    probability_label.config(text='')
    gender_image.config(image='')
    bottom_image.config(image='')

def update_labels(name, gender, probability):
    stop_loading_animation()
    name_label.config(text='Name: ' + name.upper())
    gender_label.config(text='Gender: ' + gender.upper())
    probability_label.config(text='Accuracy: ' + str(probability) + '%')
    bottom_image.config(image=bottom)
    gender_image.config(image=male_image if gender.lower() == 'male' else female_image)

def save_history():
    try:
        with open('history.json', 'a') as file:
            for name, gender, probability, date in session_history:
                json.dump({'name': name, 'gender': gender, 'probability': probability, 'date': date}, file)
                file.write('\n')
    except Exception as e:
        showerror(title='Error', message=f'An error occurred while saving the history: {str(e)}')

def start_loading_animation():
    loading_label.place(x=160, y=400)
    loading_label.lift()
    animate_loading_gif()

def stop_loading_animation():
    loading_label.place_forget()

def animate_loading_gif():
    def animate():
        for img in loading_frames:
            loading_label.config(image=img)
            gui.update_idletasks()
            gui.after(100)
    threading.Thread(target=animate).start()

def show_history():
    global is_running
    if not is_running:
        history_window = Toplevel(gui)
        history_window.title("Prediction History")
        history_window.geometry("410x520")
        history_window.resizable(False, False)
        history_window.configure(bg='#E3CCB2')
        Label(history_window, text='ALL PREDICTIONS', font='Papyrus 17', bg='#E3CCB2', fg='#CB625F').pack()
        listboxa = Listbox(history_window, width=60, height=20, fg='#3B5BA5', bg='#E3CCB2', font='Garamond 13')
        listboxa.pack(side=TOP, fill=BOTH, expand=True)
        scrollbar = Scrollbar(listboxa, orient=VERTICAL, command=listboxa.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listboxa.config(yscrollcommand=scrollbar.set)
        display_history(listboxa)
        refresh_button = Button(history_window, text=" REFRESH ", bg='#67C2D4', fg='#3988A4', bd='5', font=('Poppins 10 bold'), command=lambda: display_history(listboxa))
        refresh_button.pack(pady=5, side=LEFT)
        clear_button = Button(history_window, text='   CLEAR   ', bg='#67C2D4', bd='5', fg='#3988A4', font=('Poppins 10 bold'), command=clear_full_history)
        clear_button.pack(pady=5, side=RIGHT)
        history_window.protocol("WM_DELETE_WINDOW", lambda: close_history(history_window))
        is_running = True
    else:
        return

def display_history(listbox):
    listbox.delete(0, END)
    try:
        with open('history.json', 'r') as file:
            for line in file:
                prediction = json.loads(line.strip())
                listbox.insert(END, f"Name: {prediction['name']}, Gender: {prediction['gender']}, Accuracy: {prediction['probability']:.2f}%, Date: {prediction['date']}")
    except FileNotFoundError:
        showerror(title='Error', message='No history file found.')
    except Exception as e:
        showerror(title='Error', message=f'An error occurred while loading the history: {str(e)}')

def clear_full_history():
    if askyesno(title="Clear History", message="Are you sure you want to clear your history?"):
        try:
            with open('history.json', 'w') as file:
                pass
            display_history()
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while clearing the history: {str(e)}')

def close_history(history_window):
    global is_running
    is_running = False
    history_window.destroy()

def update_history_listbox():
    listbox.delete(0, END)
    today_date = datetime.now().strftime('%Y-%m-%d')
    try:
        with open('history.json', 'r') as file:
            for line in file:
                prediction = json.loads(line.strip())
                if prediction['date'] == today_date:
                    listbox.insert(0, f"Name: {prediction['name']}, Gender: {prediction['gender']}, Accuracy: {prediction['probability']:.2f}%")
    except FileNotFoundError:
        showerror(title='Error', message='No history file found.')
    except Exception as e:
        showerror(title='Error', message=f'An error occurred while loading the history: {str(e)}')

def on_closing():
    if askyesno(title="Quit", message="Quit?"):
        gui.destroy()

gui = Tk()
gui.geometry("410x520")
gui.resizable(False, False)
gui.title("Gender Calculator")
gui.configure(bg='#0080ff')
gui.protocol("WM_DELETE_WINDOW", on_closing)

icon = PhotoImage(file="images/icon.png")
gui.iconphoto(gui, icon)

notebook = ttk.Notebook(gui)
notebook.pack(expand=True, fill=BOTH)

predict_frame = Frame(notebook, bg='#0080ff')
history_frame = Frame(notebook)

notebook.add(predict_frame, text="Predictions")
notebook.add(history_frame, text="History")

listbox = Listbox(history_frame, width=60, height=20, bg='#ffffe6', fg='#000080', font='georgia 12')
listbox.pack(side=BOTTOM, fill=BOTH, expand=True)
scrollbar = Scrollbar(listbox, orient=VERTICAL, command=listbox.yview, bg='#ffffe6')
scrollbar.pack(side=RIGHT, fill=Y)
listbox.config(yscrollcommand=scrollbar.set)
update_history_listbox()

top = PhotoImage(file='images/top_image.png')
top_image = Label(predict_frame, image=top, bg='#0080ff')
top_image.place(x=-10, y=-10)

bottom = PhotoImage(file='images/name_frame.png')
bottom_image = Label(predict_frame, bg='#0080ff')
bottom_image.place(x=200, y=304)

new = PhotoImage(file='images/history_image.png')
new_image = Label(history_frame, image=new)
new_image.pack(side=TOP, fill=BOTH)

Label(predict_frame, text='Please insert your name here👇👇', font='Arial 12', bg=None).place(x=81, y=213)
name_entry = Entry(predict_frame, width=20, font=('Poppins 15 bold'), justify=CENTER)
name_entry.place(x=88, y=237)
name_entry.bind('<Return>', predict_gender)

Label(history_frame, text='Recent history', font='Arial 15').place(x=140, y=1)

name_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
name_label.place(x=233, y=330)

gender_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
gender_label.place(x=233, y=360)

probability_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
probability_label.place(x=233, y=390)

loading_gif = Image.open('images/loading.gif')
loading_frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(loading_gif)]
loading_label = Label(predict_frame, bg='#0080ff')

male_image = PhotoImage(file='images/male.png')
female_image = PhotoImage(file='images/female.png')

gender_image = Label(predict_frame, bg='#0080ff')
gender_image.place(x=23, y=307)

predict_button = Button(predict_frame, text="PREDICT", bg='blue', bd='5', font=('Poppins 10 bold'), command=predict_gender)
predict_button.place(x=155, y=269)

history_button = Button(history_frame, text="FULL HISTORY", bg='#F2EC9B', bd='5', font=('Poppins 10 bold'), command=show_history)
history_button.place(x=295, y=6)

gui.mainloop()