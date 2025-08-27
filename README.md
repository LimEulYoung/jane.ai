# Jane.ai - Intelligent Email Assistant for KDI School

Jane.ai is a sophisticated AI-powered email assistant system designed specifically for KDI School (Korea Development Institute School of Public Policy and Management). It provides intelligent, context-aware responses to emails with seamless conversation threading and professional communication standards.

## 🚀 Key Features

- **🤖 Advanced AI Integration**: Powered by OpenAI GPT-4o with custom-tuned prompts for educational institution needs
- **📧 Email Thread Management**: Intelligent conversation threading with full context awareness
- **🔍 Smart Intent Recognition**: Accurately identifies user requests while filtering out signatures and metadata
- **📋 Administrative Support**: Specialized assistance for vacation requests, business trip forms, and external activity reports
- **🌐 Multilingual Support**: Primary Korean with English support when needed
- **🔒 Security-First**: Environment-based configuration with no hardcoded credentials
- **⚡ Real-time Processing**: IMAP-based continuous email monitoring

## 🛠 Technical Architecture

### Core Components
- **Email Monitor**: IMAP-based monitoring with UID tracking
- **AI Service**: Context-aware response generation with principle-based prompting
- **Email Sender**: SMTP with proper threading and formatting
- **Configuration Management**: Environment-based secure configuration

### Technology Stack
- **Python 3.8+**: Core application language
- **OpenAI GPT-4o**: AI response generation
- **Gmail IMAP/SMTP**: Email service integration
- **python-dotenv**: Environment configuration management

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Gmail account with App Password enabled
- OpenAI API key

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/LimEulYoung/jane.ai.git
   cd jane.ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env .env.local
   # Edit .env.local with your actual credentials
   ```

4. **Set up environment variables**
   ```bash
   # Required
   JANE_EMAIL_PASSWORD=your_gmail_app_password
   OPENAI_API_KEY=your_openai_api_key
   
   # Optional (with defaults)
   JANE_EMAIL_ADDRESS=jane.ai@kdis.ac.kr
   JANE_LOG_LEVEL=INFO
   JANE_CHECK_INTERVAL=10
   ```

## 🚀 Usage

### Starting the Application
```bash
python main.py
```

### Development Mode
```bash
# Debug logging
JANE_LOG_LEVEL=DEBUG python main.py

# Custom check interval (5 seconds)
JANE_CHECK_INTERVAL=5 python main.py
```

## 💡 How It Works

1. **Email Monitoring**: Continuously monitors the configured Gmail inbox for new messages
2. **Context Analysis**: Separates current messages from thread history for accurate context understanding
3. **AI Processing**: Uses advanced prompting techniques to generate contextually appropriate responses
4. **Response Generation**: Creates professional, helpful replies maintaining conversation continuity
5. **Email Threading**: Preserves standard email threading with proper headers and formatting

## 🎯 Use Cases

### Administrative Tasks
- **Vacation Requests (휴가기안문)**: Automated form assistance and guidance
- **Business Trip Forms (출장기안문)**: Travel request documentation support
- **External Activities (대외활동신고서)**: Activity reporting assistance
- **Employment Certificates**: Document generation guidance

### General Support
- **Information Queries**: Answers about school policies, procedures, and general knowledge
- **Document Interpretation**: Explains complex documents and regulations
- **Translation Services**: Korean-English translation support
- **Cultural Information**: Provides context about Korean traditions and customs

## 🔧 Configuration Options

### Email Settings
- `JANE_EMAIL_ADDRESS`: Email address for the bot (default: jane.ai@kdis.ac.kr)
- `JANE_EMAIL_PASSWORD`: Gmail App Password (required)
- `JANE_IMAP_SERVER`: IMAP server (default: imap.gmail.com)
- `JANE_SMTP_SERVER`: SMTP server (default: smtp.gmail.com)

### AI Settings
- `OPENAI_API_KEY`: OpenAI API key (required)
- `JANE_AI_MODEL`: AI model (default: gpt-4o)
- `JANE_AI_MAX_TOKENS`: Max response tokens (default: 1000)
- `JANE_AI_TEMPERATURE`: Response creativity (default: 0.7)

### Application Settings
- `JANE_LOG_LEVEL`: Logging level (default: INFO)
- `JANE_CHECK_INTERVAL`: Email check frequency in seconds (default: 10)

## 📁 Project Structure

```
jane.ai/
├── src/jane_ai/              # Main source code
│   ├── core/                 # Core application logic
│   ├── services/             # Business logic services
│   ├── models/               # Data models
│   └── utils/                # Utility functions
├── config/                   # Configuration management
├── .env                      # Environment template
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔒 Security

- **No Hardcoded Secrets**: All sensitive data managed via environment variables
- **Gmail App Passwords**: Uses secure Gmail App Password authentication
- **API Key Protection**: OpenAI API keys stored securely in environment
- **Input Sanitization**: Filters out sensitive information from email signatures

## 📈 Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes in appropriate service modules
3. Update configuration if needed
4. Test thoroughly with various email scenarios
5. Submit pull request

### Debugging
- Set `JANE_LOG_LEVEL=DEBUG` for detailed logging
- Check `logs/` directory for application logs
- Monitor email processing in real-time

## 📄 License

This project is proprietary software developed for KDI School internal use.

## 🤝 Support

For technical support or feature requests, please contact:
- **Email**: jane.ai@kdis.ac.kr
- **Institution**: Korea Development Institute School of Public Policy and Management

## 🙏 Acknowledgments

- KDI School IT Department for infrastructure support
- OpenAI for providing GPT-4o API services
- Python community for excellent libraries and tools

---

**Made with ❤️ for KDI School by the IT Team**