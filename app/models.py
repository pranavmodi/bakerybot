from typing import Dict, List, Any
from datetime import datetime

class Conversation:
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.history: List[Dict[str, Any]] = []
        self.last_active: datetime = datetime.now()
        self.context: Dict[str, Any] = {}

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.max_inactive_minutes = 60
        
    def get_conversation(self, phone_number: str) -> Conversation:
        if phone_number not in self.conversations:
            self.conversations[phone_number] = Conversation(phone_number)
        conv = self.conversations[phone_number]
        conv.last_active = datetime.now()
        return conv
        
    def cleanup_old_conversations(self):
        now = datetime.now()
        to_remove = []
        for phone, conv in self.conversations.items():
            if (now - conv.last_active).total_seconds() / 60 > self.max_inactive_minutes:
                to_remove.append(phone)
        for phone in to_remove:
            del self.conversations[phone] 