import imaplib
import email
import time
import logging
from email.header import decode_header
from email_sender import EmailSender
from jane_ai_agent import JaneAIAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EmailMonitor:
    def __init__(self):
        self.email_address = "jane.ai@kdis.ac.kr"
        self.app_password = "gpzr jhci yflq xyya"
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.last_seen_uid = None
        self.imap = None
        self.email_sender = EmailSender()
        self.jane_ai = JaneAIAgent()
    
    def connect(self):
        """Gmail IMAP 서버에 연결"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.email_address, self.app_password)
            self.imap.select('INBOX')
            logging.info("Gmail IMAP 서버에 성공적으로 연결되었습니다.")
            return True
        except Exception as e:
            logging.error(f"이메일 서버 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """IMAP 연결 해제"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                logging.info("IMAP 연결이 해제되었습니다.")
            except Exception as e:
                logging.error(f"연결 해제 중 오류: {e}")
    
    def decode_mime_words(self, s):
        """MIME 인코딩된 문자열 디코딩"""
        try:
            decoded_fragments = decode_header(s)
            decoded_string = ''
            for fragment, charset in decoded_fragments:
                if isinstance(fragment, bytes):
                    if charset:
                        decoded_string += fragment.decode(charset)
                    else:
                        decoded_string += fragment.decode('utf-8')
                else:
                    decoded_string += fragment
            return decoded_string
        except Exception as e:
            logging.warning(f"문자열 디코딩 실패: {e}")
            return str(s)
    
    def mark_as_read(self, uid):
        """이메일을 읽음으로 표시"""
        try:
            self.imap.uid('store', uid, '+FLAGS', '\\Seen')
            logging.info(f"이메일 UID {uid.decode()}를 읽음으로 처리했습니다.")
            return True
        except Exception as e:
            logging.error(f"읽음 처리 실패 (UID: {uid.decode()}): {e}")
            return False
    
    def process_new_email(self, email_info):
        """새 이메일 처리 (읽음 처리 + AI 답변)"""
        try:
            # 이메일을 읽음으로 처리
            uid_bytes = email_info['uid'].encode()
            if self.mark_as_read(uid_bytes):
                # 발신자 이메일 주소 추출
                sender_email = email_info['sender']
                if '<' in sender_email and '>' in sender_email:
                    sender_email = sender_email.split('<')[1].split('>')[0]
                
                logging.info("AI 답변 생성 중...")
                
                # 원본 이메일 객체 가져오기
                original_email = self.get_original_email(email_info['uid'])
                full_email_body = ""
                if original_email:
                    full_email_body = self.jane_ai.extract_email_body(original_email)
                
                # Jane.ai로 AI 답변 생성 (전체 이메일 내용 포함)
                ai_response = self.jane_ai.generate_response(
                    email_info['subject'],
                    full_email_body,
                    email_info['sender'],
                    full_email_body
                )
                
                # AI 답변 전송 (원본 이메일 객체 포함)
                if self.email_sender.send_reply(
                    sender_email, 
                    email_info['subject'], 
                    ai_response,
                    original_email,
                    email_info['subject']
                ):
                    logging.info(f"AI 답변을 전송했습니다: {sender_email}")
                else:
                    logging.error(f"AI 답변 전송 실패: {sender_email}")
        
        except Exception as e:
            logging.error(f"이메일 처리 중 오류: {e}")
    
    def get_original_email(self, uid):
        """UID로 원본 이메일 객체 가져오기"""
        try:
            uid_bytes = uid.encode()
            status, msg_data = self.imap.uid('fetch', uid_bytes, '(RFC822)')
            if status == 'OK' and msg_data[0] is not None:
                raw_email = msg_data[0][1]
                return email.message_from_bytes(raw_email)
            return None
        except Exception as e:
            logging.error(f"원본 이메일 가져오기 실패 (UID: {uid}): {e}")
            return None
    
    def get_latest_emails(self):
        """최신 이메일 확인 (UID 기반)"""
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
                logging.info(f"모니터링을 시작합니다. 현재 최신 UID: {latest_uid.decode()}")
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
                    status, msg_data = self.imap.uid('fetch', uid, '(RFC822)')
                    if status == 'OK' and msg_data[0] is not None:
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # 이메일 정보 추출
                        subject = self.decode_mime_words(email_message.get('Subject', '제목 없음'))
                        sender = self.decode_mime_words(email_message.get('From', '발신자 없음'))
                        date = email_message.get('Date', '날짜 없음')
                        
                        new_emails.append({
                            'uid': uid.decode(),
                            'subject': subject,
                            'sender': sender,
                            'date': date
                        })
                
                # 최신 UID 업데이트
                self.last_seen_uid = latest_uid
                return new_emails
            
            return []
        
        except Exception as e:
            logging.error(f"이메일 확인 중 오류: {e}")
            return []
    
    def start_monitoring(self):
        """이메일 모니터링 시작"""
        logging.info("이메일 모니터링을 시작합니다...")
        logging.info("10초마다 새 이메일을 확인합니다.")
        logging.info("종료하려면 Ctrl+C를 누르세요.")
        
        if not self.connect():
            return
        
        try:
            while True:
                new_emails = self.get_latest_emails()
                
                if new_emails:
                    logging.info(f"새 이메일 {len(new_emails)}개가 도착했습니다!")
                    for email_info in new_emails:
                        logging.info(f"- 제목: {email_info['subject']}")
                        logging.info(f"  발신자: {email_info['sender']}")
                        logging.info(f"  날짜: {email_info['date']}")
                        logging.info("-" * 50)
                        
                        # 이메일 처리 (읽음 처리 + 자동 답변)
                        self.process_new_email(email_info)
                else:
                    logging.info("새 이메일이 없습니다.")
                
                time.sleep(10)
                
        except KeyboardInterrupt:
            logging.info("사용자가 모니터링을 중단했습니다.")
        except Exception as e:
            logging.error(f"모니터링 중 오류 발생: {e}")
        finally:
            self.disconnect()

if __name__ == "__main__":
    monitor = EmailMonitor()
    monitor.start_monitoring()