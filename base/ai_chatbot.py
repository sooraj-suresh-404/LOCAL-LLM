import requests
import json

def chat_with_ollama(prompt):
    """
    Sends a prompt to the Ollama local server and returns the combined response.
    Handles multiple JSON objects in the response.
    """
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.2:latest",  # Ensure this matches the model you pulled
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"Content-Type": "application/json"}
    
    response_text = ""
    
    try:
        # Send the request and get the response as a stream
        response = requests.post(url, json=payload, headers=headers, stream=True)
        
        # Process the response content incrementally
        content = ""
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk.decode('utf-8')

            # Try to parse the content as JSON if it is a complete JSON object
            try:
                while content:
                    # Attempt to load the JSON content
                    json_data = json.loads(content)
                    
                    # Add the content from the response
                    response_text += json_data.get("message", {}).get("content", "")
                    
                    # If done, break
                    if json_data.get("done", False):
                        break
                    
                    # Remove the processed content from the string
                    content = content[len(json.dumps(json_data)):]
            except json.JSONDecodeError:
                # Wait for more data if JSON is not complete yet
                continue
            
    except requests.ConnectionError:
        return "Error: Unable to connect to the Ollama server. Ensure it is running."
    except Exception as e:
        return f"Error: {str(e)}"
    
    return response_text.strip()

def main():
    print("Welcome to the Local AI Chatbot!")
    print("Type 'exit' to end the chat.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        response = chat_with_ollama(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()
