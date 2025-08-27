"""
Email sending service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import make_msgid
from email.message import Message

from ..models.email_models import ProcessingContext
from ..utils.logging_utils import get_logger
from ..utils.email_utils import decode_mime_words, extract_email_body

logger = get_logger('email_sender')

class EmailSender:
    """Service for sending email responses"""
    
    def __init__(self, email_address: str, app_password: str, smtp_server: str, smtp_port: int):
        self.email_address = email_address
        self.app_password = app_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send_reply(self, context: ProcessingContext, response_body: str) -> bool:
        """Send email reply with thread history"""
        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.app_password)
            
            # 이메일 메시지 작성
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = context.sender_email
            
            # 제목 설정 (Re: 접두어 추가)
            subject = context.email_info.subject
            if not subject.startswith('Re:'):
                reply_subject = f"Re: {subject}"
            else:
                reply_subject = subject
            
            msg['Subject'] = Header(reply_subject, 'utf-8')
            
            # 이메일 스레드 헤더 설정
            if context.original_email_obj and context.email_info.message_id:
                msg['In-Reply-To'] = context.email_info.message_id
                msg['References'] = context.email_info.message_id
            
            # 본문 작성 (원본 이메일 포함)
            email_body = response_body
            
            if context.original_email_obj:
                # 원본 이메일 정보 추출 및 디코딩
                original_sender = decode_mime_words(context.original_email_obj.get('From', ''))
                original_date = context.original_email_obj.get('Date', '')
                original_body = extract_email_body(context.original_email_obj)
                
                # 원본 메시지 포맷으로 추가
                email_body += f"""




-----Original Message-----
From: {original_sender}
To: {self.email_address}
Sent: {original_date}
Subject: {subject}

{original_body}"""
            
            # 본문 추가
            msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            
            # 이메일 전송
            server.send_message(msg)
            server.quit()
            
            logger.info(f"답변 이메일을 성공적으로 전송했습니다: {context.sender_email}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            return False