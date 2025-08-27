"""
Test script for the new agent-based Jane.ai system
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from jane_ai.agents.jane_agents import JaneAgents

async def test_vacation_request():
    """Test vacation request processing"""
    print("=== 휴가 요청 테스트 ===")
    
    jane_agents = JaneAgents()
    
    # Test vacation request
    user_message = """안녕하세요. 8월 29일부터 30일까지 연차 휴가를 신청하고 싶습니다. 
    개인 사유로 인한 휴가입니다. 처리 부탁드립니다."""
    
    email_context = {
        'sender': 'test@kdis.ac.kr',
        'subject': '휴가 신청 문의',
        'date': '2025-08-27',
        'thread_history': None
    }
    
    try:
        response = await jane_agents.process_email(user_message, email_context)
        print(f"응답:\n{response}")
    except Exception as e:
        print(f"오류 발생: {e}")

async def test_general_inquiry():
    """Test general information inquiry"""
    print("\n=== 일반 문의 테스트 ===")
    
    jane_agents = JaneAgents()
    
    user_message = """KDI School의 학사 일정에 대해 알고 싶습니다. 
    특히 2025년 1학기 개강일과 종강일이 언제인지 알려주세요."""
    
    email_context = {
        'sender': 'student@kdis.ac.kr',
        'subject': '학사 일정 문의',
        'date': '2025-08-27',
        'thread_history': None
    }
    
    try:
        response = await jane_agents.process_email(user_message, email_context)
        print(f"응답:\n{response}")
    except Exception as e:
        print(f"오류 발생: {e}")

async def main():
    """Main test function"""
    print("Jane.ai 에이전트 시스템 테스트 시작\n")
    
    # Test vacation request
    await test_vacation_request()
    
    # Test general inquiry  
    await test_general_inquiry()
    
    print("\n테스트 완료")

if __name__ == "__main__":
    # Set OpenAI API key for testing (you need to set this)
    if not os.getenv('OPENAI_API_KEY'):
        print("OPENAI_API_KEY 환경변수를 설정해주세요.")
        sys.exit(1)
    
    asyncio.run(main())