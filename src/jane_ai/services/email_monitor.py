"""
Email monitoring service
"""
import imaplib
import email
from email.message import Message
import time
from typing import List, Optional

from ..models.email_models import EmailInfo, EmailContent, ProcessingContext
from ..utils.logging_utils import get_logger
from ..utils.email_utils import decode_mime_words, extract_email_body, extract_sender_email

logger = get_logger('email_monitor')

class EmailMonitor:
    """Service for monitoring incoming emails"""
    
    def __init__(self, email_address: str, app_password: str, imap_server: str, imap_port: int):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.last_seen_uid = None
        self.imap = None
    
    def connect(self) -> bool:
        """Connect to Gmail IMAP server"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.email_address, self.app_password)
            self.imap.select('INBOX')
            logger.info("Gmail IMAP 서버에 성공적으로 연결되었습니다.")
            return True
        except Exception as e:
            logger.error(f"이메일 서버 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                logger.info("IMAP 연결이 해제되었습니다.")
            except Exception as e:
                logger.error(f"연결 해제 중 오류: {e}")
    
    def mark_as_read(self, uid: bytes) -> bool:
        """Mark email as read"""
        try:
            self.imap.uid('store', uid, '+FLAGS', '\\Seen')
            logger.info(f"이메일 UID {uid.decode()}를 읽음으로 처리했습니다.")
            return True
        except Exception as e:
            logger.error(f"읽음 처리 실패 (UID: {uid.decode()}): {e}")
            return False
    
    def get_latest_emails(self) -> List[EmailInfo]:
        """Get latest emails using UID-based tracking"""
        try:
            # INBOX 새로고침 (캐시 방지)
            self.imap.select('INBOX')
            
            # 모든 이메일 UID 검색
            status, messages = self.imap.uid('search', None, 'ALL')
            if status != 'OK':
                return []
            
            all_uids = messages[0].split()
            if not all_uids:
                return []
            
            # 최신 UID 확인
            latest_uid = all_uids[-1]
            
            # 첫 실행시 현재 상태 기록
            if self.last_seen_uid is None:
                self.last_seen_uid = latest_uid
                logger.info(f"모니터링을 시작합니다. 현재 최신 UID: {latest_uid.decode()}")
                return []
            
            # 새로운 이메일 확인
            if latest_uid != self.last_seen_uid:
                # 마지막으로 본 UID 이후의 새 이메일 찾기
                last_seen_index = -1
                for i, uid in enumerate(all_uids):
                    if uid == self.last_seen_uid:
                        last_seen_index = i
                        break
                
                if last_seen_index >= 0:
                    new_uids = all_uids[last_seen_index + 1:]
                else:
                    new_uids = [latest_uid]
                
                new_emails = []
                for uid in new_uids:
                    email_info = self._extract_email_info(uid)
                    if email_info:
                        new_emails.append(email_info)
                
                # 최신 UID 업데이트
                self.last_seen_uid = latest_uid
                return new_emails
            
            return []
        
        except Exception as e:
            logger.error(f"이메일 확인 중 오류: {e}")
            return []
    
    def _extract_email_info(self, uid: bytes) -> Optional[EmailInfo]:
        """Extract email information from UID"""
        try:
            status, msg_data = self.imap.uid('fetch', uid, '(RFC822)')
            if status == 'OK' and msg_data[0] is not None:
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # 이메일 정보 추출
                subject = decode_mime_words(email_message.get('Subject', '제목 없음'))
                sender = decode_mime_words(email_message.get('From', '발신자 없음'))
                date = email_message.get('Date', '날짜 없음')
                message_id = email_message.get('Message-ID')
                in_reply_to = email_message.get('In-Reply-To')
                references = email_message.get('References')
                
                return EmailInfo(
                    uid=uid.decode(),
                    subject=subject,
                    sender=sender,
                    date=date,
                    message_id=message_id,
                    in_reply_to=in_reply_to,
                    references=references
                )
            return None
        except Exception as e:
            logger.error(f"이메일 정보 추출 실패 (UID: {uid.decode()}): {e}")
            return None
    
    def get_original_email(self, uid: str) -> Optional[Message]:
        """Get original email object by UID"""
        try:
            uid_bytes = uid.encode()
            status, msg_data = self.imap.uid('fetch', uid_bytes, '(RFC822)')
            if status == 'OK' and msg_data[0] is not None:
                raw_email = msg_data[0][1]
                return email.message_from_bytes(raw_email)
            return None
        except Exception as e:
            logger.error(f"원본 이메일 가져오기 실패 (UID: {uid}): {e}")
            return None
    
    def create_processing_context(self, email_info: EmailInfo) -> ProcessingContext:
        """Create processing context for email"""
        # 원본 이메일 객체 가져오기
        original_email = self.get_original_email(email_info.uid)
        
        # 이메일 본문 추출
        full_body = ""
        if original_email:
            full_body = extract_email_body(original_email)
        
        # 이메일 콘텐츠 생성
        email_content = EmailContent.from_raw_body(full_body)
        
        # 처리 컨텍스트 생성
        return ProcessingContext(
            email_info=email_info,
            email_content=email_content,
            original_email_obj=original_email
        )