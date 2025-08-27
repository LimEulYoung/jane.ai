from openai import OpenAI
import logging
import os
import html
import re

class JaneAIAgent:
    def __init__(self):
        # OpenAI API 키 설정
        self.api_key = os.getenv('OPENAI_API_KEY', "")
        self.client = OpenAI(api_key=self.api_key)
        
        # Jane.ai 시스템 프롬프트
        self.system_prompt = """당신은 Jane.ai, 한국개발연구원 국제정책대학원(KDI School)의 전문 AI 비서입니다.

주요 역할:
1. 휴가기안문, 출장기안문, 대외활동신고서 등 행정 문서 작성 지원
2. 학교 규정 및 정책에 대한 안내
3. 재직증명서 발급 등 행정 업무 지원
4. 기타 학교 관련 문의 응답

응답 특징:
- 정중하고 전문적인 톤 사용
- 명확하고 구체적인 정보 제공
- 한국어로 응답 (필요시 영어 병기)
- 불확실한 정보는 관련 부서 안내

시작 인사는 "안녕하세요, Jane.ai입니다."로 시작하고,
마무리는 "추가 문의사항이 있으시면 언제든 연락주세요."로 끝내주세요."""
    
    def generate_response(self, email_subject, email_body, sender_info, full_email_body=None):
        """OpenAI GPT-4o를 사용하여 이메일 답변 생성"""
        try:
            # 현재 메시지와 이전 대화 분리
            current_message, thread_history = self.separate_current_message_from_thread(full_email_body if full_email_body else email_body)
            
            # 사용자 메시지 구성
            if thread_history:
                user_message = f"""
발신자 정보: {sender_info}
이메일 제목: {email_subject}

=== 현재 메시지 (주요 답변 대상) ===
{current_message}

=== 이전 대화 내역 (참고용) ===
{thread_history}

답변 지침:
- 현재 메시지에서 사용자의 핵심 의도를 파악하여 답변하세요
- 서명, 연락처, 직책 정보 등은 무시하고 실제 질문이나 요청에만 집중하세요
- 이전 대화 내역을 참고하여 맥락을 파악하고, 현재 메시지와 연관성이 있다면 이를 고려하세요
- 사용자가 실제로 원하는 것이 무엇인지 종합적으로 판단하여 유용한 답변을 제공하세요
"""
            else:
                user_message = f"""
발신자 정보: {sender_info}
이메일 제목: {email_subject}
이메일 내용:
{current_message}

위 이메일에 대해 적절한 답변을 작성해주세요.
"""
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            logging.info("AI 답변 생성 완료")
            return ai_response
            
        except Exception as e:
            logging.error(f"AI 답변 생성 실패: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self):
        """API 오류 시 기본 답변"""
        return """안녕하세요, Jane.ai입니다.

죄송합니다. 현재 일시적인 시스템 오류로 인해 상세한 답변을 제공드리지 못하고 있습니다.

귀하의 문의사항은 정상적으로 접수되었으며, 관련 담당자가 확인 후 빠른 시일 내에 답변드리겠습니다.

불편을 드려 죄송합니다.

감사합니다.

---
Jane.ai
한국개발연구원 국제정책대학원 AI 비서
jane.ai@kdis.ac.kr"""
    
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
            
            return body.strip()
        except Exception as e:
            logging.error(f"이메일 본문 추출 실패: {e}")
            return "본문을 읽을 수 없습니다."
    
    def separate_current_message_from_thread(self, full_email_body):
        """이메일 본문에서 현재 메시지와 이전 대화 스레드 분리"""
        try:
            # -----Original Message----- 패턴을 찾아서 분리
            original_message_pattern = r'-----Original Message-----'
            
            if re.search(original_message_pattern, full_email_body):
                # Original Message 이전 부분이 현재 메시지
                parts = re.split(original_message_pattern, full_email_body, 1)
                current_message = parts[0].strip()
                thread_history = f"-----Original Message-----{parts[1]}" if len(parts) > 1 else ""
                
                logging.info("현재 메시지와 스레드 히스토리를 분리했습니다.")
                return current_message, thread_history.strip()
            else:
                # Original Message가 없으면 전체가 현재 메시지
                return full_email_body.strip(), ""
                
        except Exception as e:
            logging.warning(f"메시지 분리 중 오류: {e}")
            # 오류 시 전체를 현재 메시지로 처리
            return full_email_body.strip(), ""

if __name__ == "__main__":
    # 테스트용
    agent = JaneAIAgent()
    test_response = agent.generate_response(
        "휴가 신청 문의",
        "안녕하세요. 다음 주에 휴가를 신청하고 싶은데 어떤 절차를 거쳐야 하나요?",
        "홍길동 <hong@example.com>"
    )
    print(test_response)