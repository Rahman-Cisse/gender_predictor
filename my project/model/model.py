#model
import json
import requests

from tkinter.messagebox import showerror

class Model:
    def __init__(self):
        self.session_history = []

    def predict_gender(self, name):
        response = requests.get(f'https://api.genderize.io/?name={name}').json()
        return response

    def save_history(self):
        try:
            with open('model\history.json', 'a') as file:
                for name, gender, probability, date_today in self.session_history:
                    json.dump({'name': name, 'gender': gender, 'probability': probability, 'date': date_today}, file)
                    file.write('\n')
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while saving the history: {str(e)}')

    def load_history(self):
        history = []
        try:
            with open('model\history.json', 'r') as file:
                for line in file:
                    prediction = json.loads(line.strip())
                    history.append(prediction)
        except FileNotFoundError:
            showerror(title='Error', message='No history file found.')
        except Exception as e:
            showerror(title='Error', message=f'An error occurred while loading the history: {str(e)}')
        return history