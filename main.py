#!/usr/bin/env python3
"""
Jane.ai - Email-based Assistant System
Main entry point
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import load_config
from jane_ai.utils.logging_utils import setup_logging
from jane_ai.core.application import JaneAIApplication

def main():
    """Main entry point"""
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config.log_level)
        
        # Create and start application
        app = JaneAIApplication(config)
        app.start()
        
    except Exception as e:
        print(f"애플리케이션 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()