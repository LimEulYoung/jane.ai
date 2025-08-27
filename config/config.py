"""
Configuration management for Jane.ai
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class EmailConfig:
    """Email service configuration"""
    address: str = ""
    app_password: str = ""
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

@dataclass
class AIConfig:
    """AI service configuration"""
    openai_api_key: str = ""
    model: str = "gpt-4o"
    max_tokens: int = 1000
    temperature: float = 0.7

@dataclass
class AppConfig:
    """Main application configuration"""
    email: EmailConfig = None
    ai: AIConfig = None
    check_interval: int = 10  # seconds
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.email is None:
            self.email = EmailConfig()
        if self.ai is None:
            self.ai = AIConfig()

def load_config() -> AppConfig:
    """Load configuration from environment variables or defaults"""
    email_config = EmailConfig(
        address=os.getenv('JANE_EMAIL_ADDRESS', "jane.ai@kdis.ac.kr"),
        app_password=os.getenv('JANE_EMAIL_PASSWORD', ""),
        imap_server=os.getenv('JANE_IMAP_SERVER', EmailConfig.imap_server),
        imap_port=int(os.getenv('JANE_IMAP_PORT', str(EmailConfig.imap_port))),
        smtp_server=os.getenv('JANE_SMTP_SERVER', EmailConfig.smtp_server),
        smtp_port=int(os.getenv('JANE_SMTP_PORT', str(EmailConfig.smtp_port)))
    )
    
    ai_config = AIConfig(
        openai_api_key=os.getenv('OPENAI_API_KEY', ""),
        model=os.getenv('JANE_AI_MODEL', AIConfig.model),
        max_tokens=int(os.getenv('JANE_AI_MAX_TOKENS', str(AIConfig.max_tokens))),
        temperature=float(os.getenv('JANE_AI_TEMPERATURE', str(AIConfig.temperature)))
    )
    
    return AppConfig(
        email=email_config,
        ai=ai_config,
        check_interval=int(os.getenv('JANE_CHECK_INTERVAL', '10')),
        log_level=os.getenv('JANE_LOG_LEVEL', 'INFO')
    )