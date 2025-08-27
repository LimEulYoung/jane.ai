"""
Email data models
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from email.message import Message

@dataclass
class EmailInfo:
    """Email information data model"""
    uid: str
    subject: str
    sender: str
    date: str
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: Optional[str] = None

@dataclass
class EmailContent:
    """Email content data model"""
    current_message: str
    thread_history: str
    full_body: str
    
    @classmethod
    def from_raw_body(cls, raw_body: str) -> 'EmailContent':
        """Create EmailContent from raw email body"""
        from ..utils.email_utils import separate_current_message_from_thread
        current, history = separate_current_message_from_thread(raw_body)
        return cls(
            current_message=current,
            thread_history=history,
            full_body=raw_body
        )

@dataclass
class ProcessingContext:
    """Context information for email processing"""
    email_info: EmailInfo
    email_content: EmailContent
    original_email_obj: Optional[Message] = None
    sender_email: Optional[str] = None
    
    def __post_init__(self):
        if self.sender_email is None and self.email_info:
            # Extract sender email from sender string
            sender = self.email_info.sender
            if '<' in sender and '>' in sender:
                self.sender_email = sender.split('<')[1].split('>')[0]
            else:
                self.sender_email = sender