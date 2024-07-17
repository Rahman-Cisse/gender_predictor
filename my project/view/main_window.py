from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from datetime import datetime

class MainWindow:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("Gender Calculator")
        self.root.geometry("410x520")
        self.root.resizable(False, False)
        self.root.configure(bg='#0080ff')
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=BOTH)

        self.predict_frame = Frame(self.notebook, bg='#0080ff')
        self.history_frame = Frame(self.notebook)

        self.notebook.add(self.predict_frame, text="Predictions")
        self.notebook.add(self.history_frame, text="History")

        self.top_image = PhotoImage(file='images/top_image.png')
        self.bottom_image = PhotoImage(file='images/name_frame.png')
        self.male_image = PhotoImage(file='images/male.png')
        self.female_image = PhotoImage(file='images/female.png')
        self.loading_gif = Image.open('images/loading.gif')
        self.loading_frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.loading_gif)]
        self.new_image = PhotoImage(file='images/history_image.png')

        self.loading_animation_running = False
        self.loading_animation_index = 0
        
        self.create_widgets()

    def create_widgets(self):
        self.top_image_label = Label(self.predict_frame, image=self.top_image, bg='#0080ff')
        self.top_image_label.place(x=-10, y=-10)
        
        Label(self.predict_frame, text='Please insert your name here👇👇', font='Arial 12', bg=None).place(x=81, y=213)
        self.name_entry = Entry(self.predict_frame, width=20, font=('Poppins 15 bold'), justify=CENTER)
        self.name_entry.place(x=88, y=237)
        self.name_entry.bind('<Return>', self.controller.on_predict)
        
        self.predict_button = Button(self.predict_frame, text="PREDICT", bg='blue', bd='5', font=('Poppins 10 bold'), command=self.controller.on_predict)
        self.predict_button.place(x=155, y=269)
        
        self.bottom_image_label = Label(self.predict_frame, bg='#0080ff')
        self.bottom_image_label.place(x=200, y=304)
        
        self.name_label = Label(self.predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
        self.name_label.place(x=233, y=330)

        self.gender_label = Label(self.predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
        self.gender_label.place(x=233, y=360)

        self.probability_label = Label(self.predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
        self.probability_label.place(x=233, y=390)

        self.loading_label = Label(self.predict_frame, bg='#0080ff')
        
        self.gender_image_label = Label(self.predict_frame, bg='#0080ff')
        self.gender_image_label.place(x=23, y=307)

        self.create_history_widgets()

    def create_history_widgets(self):
        self.history_image_label = Label(self.history_frame, image=self.new_image)
        self.history_image_label.pack(side=TOP, fill=BOTH)

        self.listbox = Listbox(self.history_frame, width=60, height=20, bg='#ffffe6', fg='#000080', font='georgia 12')
        self.listbox.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.listbox, orient=VERTICAL, command=self.listbox.yview, bg='#ffffe6')
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        Label(self.history_frame, text='Recent history', font='Arial 15').place(x=140, y=1)

        self.history_button = Button(self.history_frame, text="FULL HISTORY", bg='#F2EC9B', bd='5', font=('Poppins 10 bold'), command=self.controller.show_history)
        self.history_button.place(x=295, y=6)

        self.update_history_listbox()

    def clear_labels(self):
        self.name_label.config(text='')
        self.gender_label.config(text='')
        self.probability_label.config(text='')
        self.gender_image_label.config(image='')
        self.bottom_image_label.config(image='')

    def start_loading_animation(self):
        if not self.loading_animation_running:
            self.loading_animation_running = True
            self.loading_label.place(x=160, y=400)
            self.animate_loading_gif()

    def stop_loading_animation(self):
        self.loading_animation_running = False
        self.loading_label.place_forget()

    def animate_loading_gif(self):
        if self.loading_animation_running:
            self.loading_animation_index = (self.loading_animation_index + 1) % len(self.loading_frames)
            self.loading_label.config(image=self.loading_frames[self.loading_animation_index])
            self.root.after(100, self.animate_loading_gif)

    def update_labels(self, name, gender, probability):
        self.name_label.config(text='Name: ' + name.upper())
        self.gender_label.config(text='Gender: ' + (gender.upper() if gender else 'N/A'))
        self.probability_label.config(text='Accuracy: ' + str(probability) + '%')
        self.bottom_image_label.config(image=self.bottom_image)
        self.gender_image_label.config(image=self.male_image if gender == 'male' else self.female_image if gender == 'female' else '')

    def update_history_listbox(self):
        self.listbox.delete(0, END)
        today_date = datetime.now().strftime('%Y-%m-%d')
        history = self.controller.load_history()
        for prediction in history:
            if prediction['date'] == today_date:
                self.listbox.insert(0, f"Name: {prediction['name']}, Gender: {prediction['gender']}, Accuracy: {prediction['probability']:.2f}%")