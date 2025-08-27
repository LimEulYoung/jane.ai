"""
Logging utilities
"""
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> None:
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = os.path.join(log_dir, f"jane_ai_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('jane_ai').setLevel(getattr(logging, log_level.upper()))
    
    logging.info(f"Logging initialized - Level: {log_level}, Log file: {log_filename}")

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f'jane_ai.{name}')