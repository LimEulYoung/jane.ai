"""
AI service for generating email responses using Agent system
"""
from openai import OpenAI
from ..models.email_models import ProcessingContext
from ..utils.logging_utils import get_logger
from ..utils.email_utils import extract_email_body, separate_current_message_from_thread
from ..agents.jane_agents import JaneAgents
import asyncio

logger = get_logger('ai_service')

class AIService:
    """AI service for generating intelligent email responses using Agent system"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", max_tokens: int = 1000, temperature: float = 0.7):
        # Keep OpenAI client for fallback
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Agent system
        try:
            self.jane_agents = JaneAgents()
            logger.info("에이전트 시스템 초기화 완료")
        except Exception as e:
            logger.error(f"에이전트 시스템 초기화 실패: {e}")
            self.jane_agents = None
        
        # Jane.ai 시스템 프롬프트
        self.system_prompt = """당신은 Jane.ai, 한국개발연구원 국제정책대학원(KDI School)의 전문 이메일 응답 AI입니다.

## 핵심 원칙
1. **사용자 중심**: 현재 사용자의 요청과 의도를 정확히 파악하여 직접적으로 응답
2. **가치 제공**: 사용자에게 실질적으로 도움이 되는 정보와 서비스 제공
3. **맥락 통합**: 이메일 스레드의 전체 맥락을 이해하고 활용하여 일관성 있고 연속성 있는 응답 제공
4. **전문성**: KDI School 구성원에게 적합한 수준의 전문적이고 정확한 정보 제공

## 응답 방식
- **직접성**: 사용자의 질문이나 요청에 바로 답변하고, 불필요한 전치나 과거 언급 최소화
- **완전성**: 사용자가 추가 질문 없이도 만족할 수 있는 충분한 정보 제공
- **명료성**: 복잡한 내용도 이해하기 쉽게 구조화하여 설명
- **적응성**: 사용자의 요청 유형(정보 요청, 문서 작성, 해석, 설명 등)에 맞는 응답 스타일 적용

## 서비스 영역
- 행정 업무 지원 (휴가기안문, 출장기안문, 대외활동신고서 등)
- 학사 및 규정 안내
- 일반 정보 제공 (공공 지식, 문화, 언어, 역사 등)
- 문서 해석 및 번역
- 업무 관련 조언 및 가이드

## 커뮤니케이션 스타일
- 정중하면서도 친근한 전문적 톤
- 한국어 기본, 필요시 영어 또는 다국어 지원
- 불확실한 정보는 솔직히 인정하고 대안 제시
- 이메일 형식에 맞는 적절한 인사와 마무리

모든 응답은 "안녕하세요, Jane.ai입니다."로 시작하고, "추가 문의사항이 있으시면 언제든 연락주세요."로 마무리해주세요."""
    
    def generate_response(self, context: ProcessingContext) -> str:
        """Generate AI response based on processing context using Agent system"""
        try:
            # Use Agent system if available
            if self.jane_agents:
                return self._generate_agent_response(context)
            else:
                # Fallback to original OpenAI approach
                return self._generate_openai_response(context)
                
        except Exception as e:
            logger.error(f"AI 답변 생성 실패: {e}")
            return self._get_fallback_response()
    
    def _generate_agent_response(self, context: ProcessingContext) -> str:
        """Generate response using Agent system"""
        try:
            current_message = context.email_content.current_message
            
            # Email context for agents
            email_context = {
                'sender': context.email_info.sender,
                'subject': context.email_info.subject,
                'date': context.email_info.date,
                'thread_history': context.email_content.thread_history
            }
            
            # Run agent processing (synchronous wrapper for async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self.jane_agents.process_email(current_message, email_context)
                )
                return response
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"에이전트 응답 생성 실패: {e}")
            return self._generate_openai_response(context)
    
    def _generate_openai_response(self, context: ProcessingContext) -> str:
        """Fallback OpenAI response generation"""
        try:
            # 현재 메시지와 이전 대화 분리
            current_message = context.email_content.current_message
            thread_history = context.email_content.thread_history
            
            # 사용자 메시지 구성
            if thread_history:
                user_message = f"""
## 이메일 정보
발신자: {context.email_info.sender}
제목: {context.email_info.subject}

## 현재 사용자 요청
{current_message}

## 대화 맥락 (참고용)
{thread_history}

## 응답 가이드라인
1. 현재 사용자의 요청을 정확히 파악하고 그에 직접 응답
2. 서명, 연락처 등 메타 정보는 무시하고 핵심 내용에만 집중
3. 대화 맥락을 종합적으로 고려하여 사용자 의도를 정확히 파악
4. 이메일 스레드의 연속성을 인식하되, 현재 요청에 집중하여 응답
5. 구체적 요청이 있으면 과거 답변을 언급하지 말고 요청된 내용을 직접 제공
6. 사용자가 만족할 수 있는 완전하고 유용한 답변 작성
7. 이메일 응답에 적합한 정중하고 전문적인 톤 유지
"""
            else:
                user_message = f"""
## 이메일 정보
발신자: {context.email_info.sender}
제목: {context.email_info.subject}

## 사용자 요청
{current_message}

## 응답 요청
위 사용자의 요청에 대해 도움이 되고 완전한 답변을 제공해주세요. 서명이나 연락처 정보는 무시하고 실제 질문이나 요청에만 집중하여 응답하세요.
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
            
            logger.info("OpenAI 답변 생성 완료")
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI 답변 생성 실패: {e}")
            raise e
    
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