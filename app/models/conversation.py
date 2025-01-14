from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Conversation:
    def __init__(self, phone_number: str = ""):
        self.messages: List[Dict[str, str]] = []
        self.context: Dict[str, any] = {}
        self.last_updated: datetime = datetime.now()
        self.phone_number: str = phone_number
    
    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()
    
    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages
    
    def clear(self) -> None:
        self.messages = []
        self.context = {}

class ConversationManager:
    def __init__(self, max_age_hours: int = 24):
        self.conversations: Dict[str, Conversation] = {}
        self.max_age: timedelta = timedelta(hours=max_age_hours)
    
    def get_conversation(self, phone_number: str) -> Conversation:
        if phone_number not in self.conversations:
            self.conversations[phone_number] = Conversation(phone_number)
        return self.conversations[phone_number]
    
    def cleanup_old_conversations(self) -> None:
        current_time = datetime.now()
        expired_numbers = [
            number for number, conv in self.conversations.items()
            if current_time - conv.last_updated > self.max_age
        ]
        for number in expired_numbers:
            del self.conversations[number] 