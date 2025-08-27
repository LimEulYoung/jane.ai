import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header, decode_header
from email.utils import make_msgid
import re
import html

class EmailSender:
    def __init__(self):
        self.email_address = "jane.ai@kdis.ac.kr"
        self.app_password = "gpzr jhci yflq xyya"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_reply(self, to_email, subject, body, original_email_obj=None, original_subject=None):
        """이메일 답변 보내기 (원본 이메일 스레드 포함)"""
        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.app_password)
            
            # 이메일 메시지 작성
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            
            # 제목 설정 (Re: 접두어 추가)
            if original_subject:
                if not original_subject.startswith('Re:'):
                    reply_subject = f"Re: {original_subject}"
                else:
                    reply_subject = original_subject
            else:
                reply_subject = subject
            
            msg['Subject'] = Header(reply_subject, 'utf-8')
            
            # 이메일 스레드 헤더 설정
            if original_email_obj:
                original_message_id = original_email_obj.get('Message-ID')
                if original_message_id:
                    msg['In-Reply-To'] = original_message_id
                    msg['References'] = original_message_id
            
            # 본문 작성 (원본 이메일 포함)
            email_body = body
            
            if original_email_obj:
                # 원본 이메일 정보 추출 및 디코딩
                original_sender = self.decode_mime_words(original_email_obj.get('From', ''))
                original_date = original_email_obj.get('Date', '')
                original_body = self.extract_email_body(original_email_obj)
                
                # 원본 메시지 포맷으로 추가
                email_body += f"""




-----Original Message-----
From: {original_sender}
To: {self.email_address}
Sent: {original_date}
Subject: {original_subject}

{original_body}"""
            
            # 본문 추가
            msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            
            # 이메일 전송
            server.send_message(msg)
            server.quit()
            
            logging.info(f"답변 이메일을 성공적으로 전송했습니다: {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"이메일 전송 실패: {e}")
            return False
    
    def extract_email_body(self, email_message):
        """이메일 본문 추출"""
        try:
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            
            # HTML 엔터티 디코딩 및 정리
            body = html.unescape(body.strip())
            
            # 추가 정리 (HTML 엔터티만 처리)
            body = re.sub(r'&nbsp;', ' ', body)
            
            # 줄 단위로 처리하여 줄바꿈 보존
            lines = body.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # 각 줄에서만 연속된 공백을 하나로 만들기 (줄바꿈은 보존)
                cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
                cleaned_lines.append(cleaned_line)
            
            # 줄바꿈으로 다시 합치기
            body = '\n'.join(cleaned_lines)
            
            # 연속된 빈 줄을 최대 2개로 제한
            body = re.sub(r'\n{3,}', '\n\n', body)
            
            # 서명 블록 포맷팅 개선
            body = self.format_signature_block(body)
            
            return body.strip()
        except Exception as e:
            logging.error(f"이메일 본문 추출 실패: {e}")
            return "본문을 읽을 수 없습니다."
    
    def format_signature_block(self, body):
        """서명 블록 포맷팅 개선"""
        try:
            # 이메일 주소, 전화번호 패턴 찾아서 줄바꿈 추가
            # Tel, Mobile, Email 앞에 줄바꿈 추가
            body = re.sub(r'(Tel\s+\d)', r'\n\1', body)
            body = re.sub(r'(Mobile\s+\d)', r'\n\1', body) 
            body = re.sub(r'(Email\s+)', r'\n\1', body)
            
            # 부서나 직책 정보 앞에 줄바꿈 추가 (예: "전산2팀")
            body = re.sub(r'([가-힣]+\d*팀)', r'\n\1', body)
            body = re.sub(r'([가-힣]+전문원|[가-힣]+과장|[가-힣]+부장)', r'\n\1', body)
            
            # 연속된 줄바꿈 정리
            body = re.sub(r'\n{3,}', '\n\n', body)
            
            return body
        except Exception as e:
            logging.warning(f"서명 블록 포맷팅 실패: {e}")
            return body
    
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
            logging.warning(f"MIME 디코딩 실패: {e}")
            return str(s)
    
    def generate_simple_reply(self, original_subject, sender_email):
        """간단한 자동 답변 생성 (AI 처리 중 사용)"""
        reply_body = f"""안녕하세요, Jane.ai입니다.

귀하의 메일 "{original_subject}"을 잘 받았습니다.
현재 AI 시스템이 귀하의 문의를 분석하고 있으며, 곧 상세한 답변을 드리겠습니다.

잠시만 기다려주세요.

감사합니다.

---
Jane.ai
한국개발연구원 국제정책대학원 AI 비서
jane.ai@kdis.ac.kr
"""
        return reply_body

if __name__ == "__main__":
    # 테스트용
    sender = EmailSender()
    test_body = sender.generate_simple_reply("테스트 메일", "test@example.com")
    print(test_body)