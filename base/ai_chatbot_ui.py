import tkinter as tk
from tkinter import scrolledtext
import requests
import json

# Function to send the user's input to the local Ollama server
def chat_with_ollama(prompt):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.2:latest",  # Ensure this matches the model you pulled
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"Content-Type": "application/json"}
    
    response_text = ""
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the response is valid
        if response.status_code == 200:
            content = response.text
            while content:
                try:
                    json_data = json.loads(content)
                    response_text += json_data.get("message", {}).get("content", "")
                    if json_data.get("done", False):
                        break
                    content = content[len(json.dumps(json_data)):]
                except json.JSONDecodeError:
                    continue
        else:
            response_text = f"Error: {response.status_code}, {response.text}"
    
    except requests.ConnectionError:
        response_text = "Error: Unable to connect to the Ollama server. Ensure it is running."
    except Exception as e:
        response_text = f"Error: {str(e)}"
    
    return response_text.strip()

# Function to handle the chat
def send_message():
    user_input = entry_field.get()  # Get the user's input
    if user_input.lower() == "exit":
        window.quit()  # Exit the application if the user types 'exit'
    
    chat_area.config(state=tk.NORMAL)  # Enable the chat area for editing
    chat_area.insert(tk.END, f"You: {user_input}\n")  # Display user's message
    entry_field.delete(0, tk.END)  # Clear the entry field
    
    response = chat_with_ollama(user_input)  # Get bot response
    chat_area.insert(tk.END, f"Bot: {response}\n")  # Display bot's message
    
    chat_area.config(state=tk.DISABLED)  # Disable the chat area to prevent manual editing
    chat_area.yview(tk.END)  # Scroll to the bottom to show the latest message

# Set up the main window
window = tk.Tk()
window.title("Local AI Chatbot")
window.geometry("500x500")  # Set the window size

# Create a scrollable text area for the chat
chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20, state=tk.DISABLED)
chat_area.grid(row=0, column=0, padx=10, pady=10)

# Create an entry field for user input
entry_field = tk.Entry(window, width=50)
entry_field.grid(row=1, column=0, padx=10, pady=10)

# Create a button to send the message
send_button = tk.Button(window, text="Send", command=send_message)
send_button.grid(row=2, column=0, padx=10, pady=10)

# Start the Tkinter event loop
window.mainloop()
