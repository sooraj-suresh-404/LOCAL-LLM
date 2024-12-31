import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import threading

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
        response = requests.post(url, json=payload, headers=headers, stream=True)
        
        # Debugging: Check the raw response text
        print("Response Text:", response.text)
        
        # Stream the response incrementally
        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line.decode('utf-8'))
                    print("Parsed Response:", json_data)  # Debugging: See the parsed JSON
                    response_text += json_data.get("message", {}).get("content", "")
                    if json_data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    
    except requests.ConnectionError:
        response_text = "Error: Unable to connect to the Ollama server. Ensure it is running."
    except Exception as e:
        response_text = f"Error: {str(e)}"
    
    return response_text.strip()

# Function to handle sending the message, this will run in a separate thread
def send_message():
    user_input = entry_field.get()  # Get the user's input
    if user_input.lower() == "exit":
        window.quit()  # Exit the application if the user types 'exit'
    
    chat_area.config(state=tk.NORMAL)  # Enable the chat area for editing
    chat_area.insert(tk.END, f"You: {user_input}\n")  # Display user's message
    entry_field.delete(0, tk.END)  # Clear the entry field
    
    # Run the API request in a separate thread
    threading.Thread(target=fetch_bot_response, args=(user_input,)).start()

# Function to fetch the bot response in a separate thread
def fetch_bot_response(user_input):
    response = chat_with_ollama(user_input)  # Get bot response
    
    # Use after() to safely update the UI from a separate thread
    window.after(0, update_chat, response)

# Function to update the chat area with the bot's response
def update_chat(response):
    chat_area.config(state=tk.NORMAL)  # Enable the chat area for editing
    chat_area.insert(tk.END, f"Bot: {response}\n")  # Display bot's message
    chat_area.config(state=tk.DISABLED)  # Disable the chat area to prevent manual editing
    chat_area.yview(tk.END)  # Scroll to the bottom to show the latest message

    # Focus back to the input field
    entry_field.focus()

# Set up the main window
window = tk.Tk()
window.title("Local AI Chatbot")
window.geometry("500x400")  # Set the window size
window.resizable(False, False)  # Disable resizing to maintain layout consistency

# Create a scrollable text area for the chat
chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=15, state=tk.DISABLED)
chat_area.grid(row=0, column=0, padx=10, pady=10)

# Create an entry field for user input
entry_field = tk.Entry(window, width=50)
entry_field.grid(row=1, column=0, padx=10, pady=10)

# Create a button to send the message
send_button = tk.Button(window, text="Send", command=send_message)
send_button.grid(row=2, column=0, padx=10, pady=10)

# Bind the Enter key to send the message as well
window.bind('<Return>', lambda event: send_message())

# Start the Tkinter event loop
window.mainloop()
