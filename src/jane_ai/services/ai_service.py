"""
AI service for generating email responses
"""
from openai import OpenAI
from ..models.email_models import ProcessingContext
from ..utils.logging_utils import get_logger
from ..utils.email_utils import extract_email_body, separate_current_message_from_thread

logger = get_logger('ai_service')

class AIService:
    """AI service for generating intelligent email responses"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", max_tokens: int = 1000, temperature: float = 0.7):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Jane.ai 시스템 프롬프트
        self.system_prompt = """당신은 Jane.ai, 한국개발연구원 국제정책대학원(KDI School)의 전문 AI 비서입니다.

주요 역할:
1. 휴가기안문, 출장기안문, 대외활동신고서 등 행정 문서 작성 지원
2. 학교 규정 및 정책에 대한 안내
3. 재직증명서 발급 등 행정 업무 지원
4. 일상적인 문의 및 정보 제공

응답 특징:
- 정중하고 전문적인 톤 사용
- 명확하고 구체적인 정보 제공
- 한국어로 응답 (필요시 영어 병기)
- 공공 정보는 적극적으로 제공
- 불확실한 정보는 관련 부서 안내

시작 인사는 "안녕하세요, Jane.ai입니다."로 시작하고,
마무리는 "추가 문의사항이 있으시면 언제든 연락주세요."로 끝내주세요."""
    
    def generate_response(self, context: ProcessingContext) -> str:
        """Generate AI response based on processing context"""
        try:
            # 현재 메시지와 이전 대화 분리
            current_message = context.email_content.current_message
            thread_history = context.email_content.thread_history
            
            # 사용자 메시지 구성
            if thread_history:
                user_message = f"""
발신자 정보: {context.email_info.sender}
이메일 제목: {context.email_info.subject}

=== 현재 메시지 (주요 답변 대상) ===
{current_message}

=== 이전 대화 내역 (참고용) ===
{thread_history}

답변 지침:
- 현재 메시지에서 사용자의 핵심 의도를 파악하여 답변하세요
- 서명, 연락처, 직책 정보 등은 무시하고 실제 질문이나 요청에만 집중하세요
- 이전 대화 내역을 반드시 참고하여 맥락을 파악하세요
- 현재 메시지가 "이것", "그것", "이 내용" 등의 지시어를 사용하거나 구체적인 내용 없이 요청한다면, 반드시 이전 대화를 참고하여 무엇을 가리키는지 파악하세요
- 대화의 연속성을 유지하고, 사용자가 원하는 정보를 정확히 제공하세요
- 맥락이 명확하다면 추가 정보를 요청하지 말고 직접 답변하세요
"""
            else:
                user_message = f"""
발신자 정보: {context.email_info.sender}
이메일 제목: {context.email_info.subject}
이메일 내용:
{current_message}

위 이메일에 대해 적절한 답변을 작성해주세요.
"""
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            logger.info("AI 답변 생성 완료")
            return ai_response
            
        except Exception as e:
            logger.error(f"AI 답변 생성 실패: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
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