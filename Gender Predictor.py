from tkinter import *
from tkinter import ttk
import requests
from tkinter.messagebox import showerror, askyesno
from PIL import Image, ImageTk, ImageSequence
import threading
# List to store the history of predictions for the current session
session_history = []
is_running = False

# Function to predict gender based on name input
def predict_gender(Event=None):
    def fetch_data():
        try:
            # Getting the input from entry
            entered_name = name_entry.get().strip()
            # Clear previous results
            name_label.config(text='')
            gender_label.config(text='')
            probability_label.config(text='')
            gender_image.config(image='')
            bottom_image.config(image='')
            #validating
            if len(entered_name) < 2:
                showerror(title='Error', message='Please enter a valid name.')
                return
            if not entered_name.isalpha():
                showerror(title='Error', message='Please enter a valid name containing only alphabetic characters.')
                return
            #displaying the gif
            start_loading_animation()
            
            # Making a request to the API
            response = requests.get(f'https://api.genderize.io/?name={entered_name}').json()
            name = response['name']
            gender = response['gender']
            probability = 100 * response['probability']
            
            # Updating labels with the response data
            name_label.config(text='Name: ' + name.upper())
            gender_label.config(text='Gender: ' + gender.upper())
            probability_label.config(text='Accuracy: ' + str(probability) + '%')
            bottom_image.config(image=bottom)
            the_gender = gender.lower()
            if the_gender == 'male':
                gender_image.config(image=male_image)
            elif the_gender == 'female':
                gender_image.config(image=female_image)
            
            # Adding to session history and writing to file
            session_history.append((name, gender, probability))
            with open('history.txt', 'a') as file:
                file.write(f"{name},{gender},{probability}\n")
                
                
            # Update the history listbox with the new entry
            update_history_listbox()
        #catching all exceptions
        except requests.exceptions.RequestException:
            showerror(title='Error', message='Network error: Make sure you are connected to the internet')
        except KeyError:
            showerror(title='Error', message='Unexpected response format: please enter a correct name')
        except Exception as e:
            showerror(title='Error', message=f'An error occurred: Please make sure you have entered a correct name and connected to the internet')
        finally:
            gui.after(0, stop_loading_animation)
    threading.Thread(target=fetch_data).start()
# Function to start the loading animation
def start_loading_animation():
    loading_label.place(x=160, y=400)
    loading_label.lift()
    animate_loading_gif()

# Function to stop the loading animation
def stop_loading_animation():
    loading_label.place_forget()


def animate_loading_gif():
    for img in loading_frames:
        loading_label.config(image=img)
        gui.update_idletasks()
        gui.after(100)
# Function to show prediction history in a new window
def show_history():
    #to prevent history window from being opened more than once
    def boolean():
        history_window.destroy()
        global is_running
        is_running=False
    
    
    
    global is_running
    if is_running == False:
        #creating the history window
        history_window = Toplevel(gui)
        history_window.title("Prediction History")#window name
        history_window.geometry("410x520")#window size
        history_window.resizable(False,False)#preventing window size from changing
        history_window.configure(bg='#E3CCB2')#window colour
        
        Label(history_window, text='ALL PREDICTIONS', font='Papyrus 17', bg='#E3CCB2',fg='#CB625F').pack()

        
        # Create a listbox to display the history
        listboxa = Listbox(history_window, width=60, height=20,fg='#3B5BA5',bg='#E3CCB2',font='Garamond 13')
        listboxa.pack(side=TOP, fill=BOTH, expand=True)

        # Add a scrollbar to the listbox
        scrollbar = Scrollbar(listboxa, orient=VERTICAL, command=listboxa.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listboxa.config(yscrollcommand=scrollbar.set)
        
        #function for inserting information from the file to the list   
        def display_history():
            listboxa.delete(0, END)
            try:
                with open('history.txt', 'r') as file:
                    for line in file:
                        name, gender, probability = line.strip().split(',')
                        listboxa.insert(END, f"Name: {name}, Gender: {gender}, Accuracy: {float(probability):.2f}%")
            except FileNotFoundError:
                showerror(title='Error', message='No history file found.')
                
                
        #asking before clearing history
        def clear_full_history():
            if askyesno(title="Clear History", message="Are you sure you want to clear your history?"):
                clear_history()
                
        #clearing all history
        def clear_history():
            with open("history.txt", "w") as file:
                pass  # Empty the file content
            display_history()
            
        display_history()
        
        #all buttons in history window
        refresh_button = Button(history_window, text=" REFRESH ", bg='#67C2D4',fg='#3988A4' ,bd='5', font=('Poppins 10 bold'), command=display_history)
        refresh_button.pack(pady=5, side=LEFT)
        clear_button = Button(history_window, text='   CLEAR   ', bg='#67C2D4', bd='5',fg='#3988A4', font=('Poppins 10 bold'), command=clear_full_history)
        clear_button.pack(pady=5, side=RIGHT)
        history_window.protocol("WM_DELETE_WINDOW", boolean)
        is_running=True
    
    else:
        return

    
    

        
# Function to update the history listbox in the history_frame with session history
def update_history_listbox():
    listbox.delete(0, END)
    for name, gender, probability in session_history:
        listbox.insert(0, f"Name: {name}, Gender: {gender}, Accuracy: {probability:.2f}%")
        
#function to show a message when exiting
def on_closing():
        if askyesno(title="Quit", message="Quit?"):
            gui.destroy()
            
# Setting up the main GUI window
gui = Tk()
gui.geometry("410x520")
gui.resizable(False, False)
gui.title("Gender Calculator")
gui.configure(bg='#0080ff')
gui.protocol("WM_DELETE_WINDOW", on_closing)

#changing icon
icon = PhotoImage(file="images/icon.png")
gui.iconphoto(gui, icon)

# Adding new tabs
notebook = ttk.Notebook(gui)
notebook.pack(expand=True, fill=BOTH)

# Creating frames for the tabs
predict_frame = Frame(notebook, bg='#0080ff')
history_frame = Frame(notebook)

# Adding tabs to the notebook
notebook.add(predict_frame, text="Predictions")
notebook.add(history_frame, text="History")






#creating the listbox in history_frame
listbox = Listbox(history_frame, width=60, height=20,bg='#ffffe6',fg='#000080',font='georgia 12')
listbox.pack(side=BOTTOM, fill=BOTH, expand=True)

#creating a scrollbar on listbox
scrollbar = Scrollbar(listbox, orient=VERTICAL, command=listbox.yview,bg='#ffffe6')
scrollbar.pack(side=RIGHT, fill=Y)
listbox.config(yscrollcommand=scrollbar.set)


# Initial population of the listbox with session history
update_history_listbox()

# Inserting images
top = PhotoImage(file='images/top_image.png')
top_image = Label(predict_frame, image=top, bg='#0080ff')
top_image.place(x=-10, y=-10)

bottom = PhotoImage(file='images/name_frame.png')
bottom_image = Label(predict_frame, bg='#0080ff')
bottom_image.place(x=200, y=304)

new = PhotoImage(file='images/history_image.png')
new_image = Label(history_frame, image=new)
new_image.pack(side=TOP, fill=BOTH)



# Label and entry for name input
Label(predict_frame, text='Please insert your name here👇👇', font='Arial 12', bg=None).place(x=81, y=213)
#creating a name entry box
name_entry = Entry(predict_frame, width=20, font=('Poppins 15 bold'), justify=CENTER)
name_entry.place(x=88, y=237)

#binding the enter key to the maun function
name_entry.bind('<Return>', predict_gender) 

#label to display recent history in history frame
Label(history_frame, text='Recent history', font='Arial 15').place(x=140,y=1)

# Labels to display the prediction results
name_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
name_label.place(x=233, y=330)

gender_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
gender_label.place(x=233, y=360)

probability_label = Label(predict_frame, text='', bg='#0080ff', font=('Poppins 10 bold', 9))
probability_label.place(x=233, y=390)

#loading the gif
loading_gif = Image.open('images/loading.gif')
loading_frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(loading_gif)]
loading_label = Label(predict_frame, bg='#0080ff')

# Load gender images
male_image = PhotoImage(file='images/male.png')
female_image = PhotoImage(file='images/female.png')

# Label to display the gender image according to the prediction
gender_image = Label(predict_frame, bg='#0080ff')
gender_image.place(x=23, y=307)

# Buttons for prediction and showing history
predict_button = Button(predict_frame, text="PREDICT", bg='blue', bd='5', font=('Poppins 10 bold'), command=predict_gender)
predict_button.place(x=155, y=269)

history_button = Button(history_frame, text="FULL HISTORY", bg='#F2EC9B', bd='5', font=('Poppins 10 bold'), command=show_history)
history_button.place(x=295, y=6)

# Running the GUI application
gui.mainloop()