import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import openpyxl
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from tkinter import PhotoImage
from PIL import Image, ImageTk

# Initialize GPT-2 tokenizer without padding
if 'tokenizer' not in globals():
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium", pad_token='<pad>')

# Load responses from an Excel file
def load_responses_from_excel(file_path):
    responses = {}
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        input_text, response_text = row
        responses[input_text.lower()] = response_text
    return responses

# Define responses by loading from Excel
responses = load_responses_from_excel("ashtech.xlsx")

translator = Translator()

# Initialize GPT-2 model
gpt_model = GPT2LMHeadModel.from_pretrained("gpt2-medium")

def generate_gpt_response(user_input, conversation_history):
    input_text = " ".join(conversation_history + [user_input])
    
    # Tokenize the input text
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # Generate response
    output = gpt_model.generate(input_ids, max_length=150, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    
    # Decode the generated output
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response

# Function to handle user input and generate responses
def get_response(user_input, conversation_history):
    if user_input.lower() == "open youtube":
        open_youtube()
        return "Opening YouTube..."
    elif user_input.lower().startswith("translate"):
        word_to_translate = user_input.split(" ", 1)[1]  # Get the word to translate
        translation = translate_word(word_to_translate)
        return translation
    else:
        # Check if the input contains a question about a specific topic
        if '?' in user_input:
            return generate_gpt_response(user_input)
        else:
            return "I'm sorry, I didn't understand that."

# Function to open YouTube in the default web browser
def open_youtube():
    webbrowser.open("https://www.youtube.com")

# Function to translate a word to Tamil
def translate_word(word):
    translated_word = translator.translate(word, dest='ta').text
    return f"The Tamil translation of '{word}' is '{translated_word}'."

# Function to search online for user input
def search_online(user_input):
    query = "https://www.google.com/search?q=" + user_input.replace(" ", "+")
    webbrowser.open_new_tab(query)
    return "I'm sorry, I don't have the answer to that. You can check online."

def send_message(event=None):
    user_input = user_entry.get()
    if user_input.strip() != "":
        response = get_response(user_input, conversation_history)
        response_str = str(response)
        speak("Ashtech reporting: " + response_str)
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "You: " + user_input + "\n")
        chat_history.insert(tk.END, "Ashtech: " + response_str + "\n")
        chat_history.config(state=tk.DISABLED)
        chat_history.see(tk.END)
        conversation_history.append(user_input)  # Move this line to after displaying the response
        user_entry.delete(0, tk.END)

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle voice input
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        user_input = recognizer.recognize_google(audio)
        print("User input:", user_input)
        user_entry.delete(0, tk.END)
        user_entry.insert(0, user_input)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

# Create main application window
root = tk.Tk()
root.title("Ashtech")

# Set background color
root.configure(bg="#f0f0f0")

# Create scrolled text widget to display chat history
chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="white", fg="black", font=("Helvetica", 10))
chat_history.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.85)

# Create entry widget for user input
user_entry = tk.Entry(root, bg="white", fg="black", font=("Helvetica", 10))
user_entry.place(relx=0.02, rely=0.9, relwidth=0.90, relheight=0.08)


# Load the image
original_image = Image.open("microphone.png")  # Replace "voice_button_image.png" with your image file

# Resize the image
width, height = 40, 40  # Set the desired width and height
resized_image = original_image.resize((width, height), Image.LANCZOS)

# Convert the resized image to Tkinter PhotoImage
voice_img = ImageTk.PhotoImage(resized_image)

# Create a button with the image
voice_button = tk.Button(root, image=voice_img, command=voice_input, bg="#f0f0f0", borderwidth=0)
voice_button.place(x=1260, y=630)


# Bind Enter key press event to send_message function
user_entry.bind("<Return>", send_message)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize conversation history
conversation_history = []

# Start the Tkinter event loop
root.mainloop()
