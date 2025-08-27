"""
Email utility functions
"""
import re
import html
import logging
from email.header import decode_header
from email.message import Message
from typing import Tuple, Optional

def decode_mime_words(s: str) -> str:
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

def extract_email_body(email_message: Message) -> str:
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
        body = format_signature_block(body)
        
        return body.strip()
    except Exception as e:
        logging.error(f"이메일 본문 추출 실패: {e}")
        return "본문을 읽을 수 없습니다."

def format_signature_block(body: str) -> str:
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

def separate_current_message_from_thread(full_email_body: str) -> Tuple[str, str]:
    """이메일 본문에서 현재 메시지와 이전 대화 스레드 분리"""
    try:
        # -----Original Message----- 패턴을 찾아서 분리
        original_message_pattern = r'-----Original Message-----'
        
        if re.search(original_message_pattern, full_email_body):
            # Original Message 이전 부분이 현재 메시지
            parts = re.split(original_message_pattern, full_email_body, 1)
            current_message = parts[0].strip()
            thread_history = f"-----Original Message-----{parts[1]}" if len(parts) > 1 else ""
            
            logging.debug("현재 메시지와 스레드 히스토리를 분리했습니다.")
            return current_message, thread_history.strip()
        else:
            # Original Message가 없으면 전체가 현재 메시지
            return full_email_body.strip(), ""
            
    except Exception as e:
        logging.warning(f"메시지 분리 중 오류: {e}")
        # 오류 시 전체를 현재 메시지로 처리
        return full_email_body.strip(), ""

def extract_sender_email(sender_string: str) -> str:
    """발신자 문자열에서 이메일 주소 추출"""
    if '<' in sender_string and '>' in sender_string:
        return sender_string.split('<')[1].split('>')[0]
    return sender_string