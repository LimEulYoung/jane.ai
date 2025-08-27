"""
Jane.ai Agent-based system using OpenAI Agents SDK
"""
from agents import Agent, Runner, function_tool, trace
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timedelta
import asyncio
import json

from ..services.vacation_service import VacationService, VacationRequest
from ..utils.logging_utils import get_logger

logger = get_logger('jane_agents')

# Pydantic models for structured outputs
class VacationRequestAnalysis(BaseModel):
    """Analysis result for vacation request"""
    is_vacation_request: bool
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None    # YYYY-MM-DD format
    vacation_type: Optional[str] = "01"  # 01: 연가
    reason: Optional[str] = None
    missing_info: list[str] = []

class EmailIntent(BaseModel):
    """Analysis of email intent"""
    intent_type: Literal["vacation", "document", "information", "general"]
    confidence: float
    requires_action: bool
    action_description: str

# Function tools
@function_tool
def submit_vacation_request(
    start_date: str,
    end_date: str, 
    vacation_type: str = "01",
    reason: str = "개인 사유"
) -> dict:
    """
    Submit a vacation request to KDI portal
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format  
        vacation_type: Type of vacation (01: 연가, 02: 병가, etc.)
        reason: Reason for vacation request
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Calculate days count
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days_count = (end - start).days + 1
        
        vacation_request = VacationRequest(
            start_date=start_date,
            end_date=end_date,
            vacation_type=vacation_type,
            days_count=days_count,
            reason=reason
        )
        
        vacation_service = VacationService()
        result = vacation_service.submit_vacation_request(vacation_request)
        
        logger.info(f"휴가 신청 결과: {result}")
        return result
        
    except Exception as e:
        logger.error(f"휴가 신청 도구 실행 중 오류: {e}")
        return {"success": False, "message": f"휴가 신청 처리 중 오류: {str(e)}"}

@function_tool
def analyze_vacation_request(user_message: str) -> VacationRequestAnalysis:
    """
    Analyze user message for vacation request information
    
    Args:
        user_message: User's message content
        
    Returns:
        VacationRequestAnalysis: Analysis result with extracted information
    """
    # This would typically use AI to extract vacation details
    # For now, simple keyword-based analysis
    analysis = VacationRequestAnalysis(is_vacation_request=False)
    
    vacation_keywords = ['휴가', '연차', '병가', '외출', '반차', 'vacation', 'leave']
    if any(keyword in user_message.lower() for keyword in vacation_keywords):
        analysis.is_vacation_request = True
        
        # Extract dates (simplified - in practice would use more sophisticated parsing)
        missing_info = []
        if not analysis.start_date:
            missing_info.append("시작 날짜")
        if not analysis.end_date:
            missing_info.append("종료 날짜")
        if not analysis.reason:
            missing_info.append("휴가 사유")
            
        analysis.missing_info = missing_info
    
    return analysis

# Specialized Agents
class JaneAgents:
    """Jane.ai Agent system"""
    
    def __init__(self):
        self.setup_agents()
    
    def setup_agents(self):
        """Initialize all specialized agents"""
        
        # Intent Analysis Agent
        self.intent_agent = Agent(
            name="intent_analyzer",
            instructions="""
            사용자의 이메일 내용을 분석하여 의도를 파악하는 전문가입니다.
            
            다음 카테고리로 분류하세요:
            - vacation: 휴가, 연차, 병가, 외출 등 관련 요청
            - document: 문서 작성, 해석, 번역 요청
            - information: 정보 제공, 규정 안내, 질문 답변
            - general: 일반적인 대화나 인사
            
            의도 분석 시 고려사항:
            1. 사용자가 명시적으로 요청한 내용
            2. 문맥상 암시된 요구사항
            3. 실행 가능한 액션이 필요한지 여부
            """,
            output_type=EmailIntent
        )
        
        # Vacation Request Agent
        self.vacation_agent = Agent(
            name="vacation_specialist",
            instructions="""
            휴가 신청 전문 에이전트입니다. 사용자의 휴가 요청을 처리합니다.
            
            주요 업무:
            1. 휴가 관련 정보 추출 (날짜, 기간, 사유 등)
            2. 부족한 정보 식별 및 추가 정보 요청
            3. 휴가 신청 도구 실행
            4. 휴가 관련 문의 답변
            
            휴가 종류:
            - 01: 연가 (기본값)
            - 02: 병가
            - 03: 경조휴가
            - 04: 특별휴가
            
            필수 정보:
            - 시작 날짜 (YYYY-MM-DD 형식)
            - 종료 날짜 (YYYY-MM-DD 형식)  
            - 휴가 사유
            
            사용자에게 부족한 정보가 있으면 정중하게 추가 정보를 요청하세요.
            """,
            tools=[submit_vacation_request, analyze_vacation_request]
        )
        
        # Document Agent
        self.document_agent = Agent(
            name="document_specialist", 
            instructions="""
            문서 작성 및 해석 전문 에이전트입니다.
            
            주요 업무:
            1. 각종 공문서 작성 (출장기안문, 대외활동신고서 등)
            2. 문서 해석 및 번역
            3. 양식 및 템플릿 제공
            4. 문서 작성 가이드라인 안내
            
            KDI School의 공식 문서 형식과 절차를 준수하여 작성합니다.
            """
        )
        
        # Information Agent  
        self.information_agent = Agent(
            name="information_specialist",
            instructions="""
            정보 제공 및 규정 안내 전문 에이전트입니다.
            
            주요 업무:
            1. KDI School 규정 및 절차 안내
            2. 학사 일정 및 행정 정보 제공  
            3. 일반 지식 및 공공 정보 제공
            4. 질문 답변 및 문의 처리
            
            정확하고 최신의 정보를 제공하며, 불확실한 경우 솔직히 안내합니다.
            """
        )
        
        # Main Orchestrator Agent
        self.main_agent = Agent(
            name="jane_ai_orchestrator",
            instructions="""
            Jane.ai의 메인 오케스트레이터 에이전트입니다.
            사용자 요청을 분석하고 적절한 전문 에이전트에게 작업을 위임합니다.
            
            작업 흐름:
            1. 사용자 의도 분석
            2. 적절한 전문 에이전트 선택
            3. 작업 위임 및 결과 통합
            4. 사용자에게 최종 응답 제공
            
            각 전문 에이전트의 역할:
            - vacation_specialist: 휴가 관련 업무
            - document_specialist: 문서 작성/해석 
            - information_specialist: 정보 제공/안내
            
            항상 사용자 중심의 도움이 되는 응답을 제공하세요.
            """,
            tools=[
                self.vacation_agent.as_tool(
                    tool_name="handle_vacation_request",
                    tool_description="휴가 관련 요청 처리"
                ),
                self.document_agent.as_tool(
                    tool_name="handle_document_request", 
                    tool_description="문서 작성/해석 요청 처리"
                ),
                self.information_agent.as_tool(
                    tool_name="provide_information",
                    tool_description="정보 제공 및 질문 답변"
                )
            ]
        )
    
    async def process_email(self, user_message: str, email_context: dict) -> str:
        """
        Process email using agent system
        
        Args:
            user_message: User's message content
            email_context: Email metadata and context
            
        Returns:
            str: Generated response
        """
        try:
            with trace("Jane.ai Email Processing"):
                # Step 1: Intent Analysis
                logger.info("사용자 의도 분석 시작...")
                intent_result = await Runner.run(
                    self.intent_agent, 
                    f"다음 이메일 내용의 의도를 분석하세요:\n\n{user_message}"
                )
                
                intent = intent_result.final_output
                logger.info(f"의도 분석 결과: {intent.intent_type} (신뢰도: {intent.confidence})")
                
                # Step 2: Route to appropriate agent
                agent_input = f"""
                이메일 정보:
                - 발신자: {email_context.get('sender', 'Unknown')}
                - 제목: {email_context.get('subject', 'No Subject')}
                - 의도 분류: {intent.intent_type}
                
                사용자 메시지:
                {user_message}
                
                위 요청을 처리해주세요.
                """
                
                # Route based on intent
                if intent.intent_type == "vacation":
                    logger.info("휴가 전문 에이전트로 라우팅...")
                    result = await Runner.run(self.vacation_agent, agent_input)
                elif intent.intent_type == "document":
                    logger.info("문서 전문 에이전트로 라우팅...")
                    result = await Runner.run(self.document_agent, agent_input)
                elif intent.intent_type == "information":
                    logger.info("정보 제공 에이전트로 라우팅...")
                    result = await Runner.run(self.information_agent, agent_input)
                else:
                    logger.info("메인 오케스트레이터로 처리...")
                    result = await Runner.run(self.main_agent, agent_input)
                
                response = result.final_output
                logger.info("에이전트 처리 완료")
                
                return response
                
        except Exception as e:
            logger.error(f"에이전트 처리 중 오류: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response in case of errors"""
        return """안녕하세요, Jane.ai입니다.

죄송합니다. 현재 일시적인 시스템 오류로 인해 상세한 답변을 제공드리지 못하고 있습니다.

귀하의 문의사항은 정상적으로 접수되었으며, 관련 담당자가 확인 후 빠른 시일 내에 답변드리겠습니다.

불편을 드려 죄송합니다.

감사합니다.

---
Jane.ai
한국개발연구원 국제정책대학원 AI 비서
jane.ai@kdis.ac.kr"""