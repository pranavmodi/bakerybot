import requests
import xml.etree.ElementTree as ET

SERVER_URL = "http://54.71.183.198:50000"
# SERVER_URL = "http://localhost:8000"

def parse_twilio_response(xml_text: str) -> str:
    root = ET.fromstring(xml_text)
    message = root.find('Message')
    if message is not None:
        return message.text
    return "No response message found"

def chat_with_bot():
    print("Welcome to the Bakery Chatbot! Type 'exit' to end the conversation.")
    
    # Dummy phone number for testing
    phone_number = "whatsapp:+1234567890"
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        try:
            response = requests.post(
                f'{SERVER_URL}/chat',
                data={
                    'Body': user_input,
                    'From': phone_number
                }
            )
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('text/xml'):
                bot_response = parse_twilio_response(response.text)
            else:
                bot_response = response.json().get('response', 'No response found')
            
            print(f"Bot: {bot_response}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Could not connect to server. {str(e)}")
        except ET.ParseError as e:
            print(f"Error parsing XML response: {str(e)}")
            print(f"Raw response: {response.text}")

if __name__ == "__main__":
    chat_with_bot()