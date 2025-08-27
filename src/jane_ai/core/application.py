"""
Main Jane.ai application
"""
import time
from typing import List

from ..models.email_models import EmailInfo, ProcessingContext
from ..services.email_monitor import EmailMonitor
from ..services.email_sender import EmailSender
from ..services.ai_service import AIService
from ..utils.logging_utils import get_logger
from config.config import AppConfig

logger = get_logger('application')

class JaneAIApplication:
    """Main Jane.ai application class"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        
        # Initialize services
        self.email_monitor = EmailMonitor(
            email_address=config.email.address,
            app_password=config.email.app_password,
            imap_server=config.email.imap_server,
            imap_port=config.email.imap_port
        )
        
        self.email_sender = EmailSender(
            email_address=config.email.address,
            app_password=config.email.app_password,
            smtp_server=config.email.smtp_server,
            smtp_port=config.email.smtp_port
        )
        
        self.ai_service = AIService(
            api_key=config.ai.openai_api_key,
            model=config.ai.model,
            max_tokens=config.ai.max_tokens,
            temperature=config.ai.temperature
        )
    
    def start(self):
        """Start the Jane.ai email monitoring application"""
        logger.info("Jane.ai 이메일 모니터링을 시작합니다...")
        logger.info(f"{self.config.check_interval}초마다 새 이메일을 확인합니다.")
        logger.info("종료하려면 Ctrl+C를 누르세요.")
        
        if not self.email_monitor.connect():
            logger.error("이메일 서버 연결에 실패했습니다.")
            return
        
        try:
            while True:
                self._process_new_emails()
                time.sleep(self.config.check_interval)
                
        except KeyboardInterrupt:
            logger.info("사용자가 모니터링을 중단했습니다.")
        except Exception as e:
            logger.error(f"애플리케이션 실행 중 오류 발생: {e}")
        finally:
            self.email_monitor.disconnect()
    
    def _process_new_emails(self):
        """Process new emails"""
        try:
            new_emails = self.email_monitor.get_latest_emails()
            
            if new_emails:
                logger.info(f"새 이메일 {len(new_emails)}개가 도착했습니다!")
                for email_info in new_emails:
                    self._process_single_email(email_info)
            else:
                logger.info("새 이메일이 없습니다.")
        
        except Exception as e:
            logger.error(f"이메일 처리 중 오류: {e}")
    
    def _process_single_email(self, email_info: EmailInfo):
        """Process a single email"""
        try:
            logger.info(f"- 제목: {email_info.subject}")
            logger.info(f"  발신자: {email_info.sender}")
            logger.info(f"  날짜: {email_info.date}")
            logger.info("-" * 50)
            
            # 이메일을 읽음으로 처리
            uid_bytes = email_info.uid.encode()
            if not self.email_monitor.mark_as_read(uid_bytes):
                logger.warning(f"이메일 읽음 처리 실패: {email_info.uid}")
                return
            
            # 처리 컨텍스트 생성
            context = self.email_monitor.create_processing_context(email_info)
            
            logger.info("AI 답변 생성 중...")
            
            # AI 답변 생성
            ai_response = self.ai_service.generate_response(context)
            
            # AI 답변 전송
            if self.email_sender.send_reply(context, ai_response):
                logger.info(f"AI 답변을 전송했습니다: {context.sender_email}")
            else:
                logger.error(f"AI 답변 전송 실패: {context.sender_email}")
        
        except Exception as e:
            logger.error(f"개별 이메일 처리 중 오류: {e}")