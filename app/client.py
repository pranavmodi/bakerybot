import requests

# SERVER_URL = "http://54.71.183.198:50000"
SERVER_URL = "http://localhost:8000"

def chat_with_bot():
    print("Welcome to the Bakery Chatbot! Type 'exit' to end the conversation.")
    
    # Dummy phone number for testing
    phone_number = "+1234567890"
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        try:
            response = requests.post(
                f'{SERVER_URL}/chat',
                json={
                    'message': user_input,
                    'phone_number': phone_number
                }
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            bot_response = response.json()['response']
            print(f"Bot: {bot_response}")
        except requests.exceptions.RequestException as e:
            print(f"Error: Could not connect to server. {str(e)}")

if __name__ == "__main__":
    chat_with_bot()