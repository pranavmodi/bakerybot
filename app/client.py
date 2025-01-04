from app.services.chatbot import ChatbotService

def chat_with_bot():
    chatbot = ChatbotService()
    print("Welcome to the Bakery Chatbot! Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = chatbot.generate_response(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    chat_with_bot() 