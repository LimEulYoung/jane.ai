# OpenAI Agents SDK 개발 가이드

## 개요

OpenAI Agents SDK는 경량화되고 사용하기 쉬운 패키지로, 최소한의 추상화를 통해 에이전틱 AI 애플리케이션을 구축할 수 있게 해줍니다. 이전 실험 프로젝트인 Swarm의 프로덕션 준비 버전입니다.

## 설치

```bash
pip install openai-agents
```

## 핵심 개념

### 4가지 기본 요소 (Primitives)

1. **Agents** - 지시사항과 도구를 갖춘 LLM
2. **Handoffs** - 특정 작업을 다른 에이전트에게 위임
3. **Guardrails** - 에이전트 입력/출력 검증
4. **Sessions** - 에이전트 실행 간 대화 기록 자동 관리

### 주요 기능

- **Agent Loop**: 도구 호출, LLM 결과 전송, 완료까지 루프 처리
- **Python-first**: 새로운 추상화 대신 내장 언어 기능 사용
- **Function Tools**: Python 함수를 도구로 변환 (자동 스키마 생성, Pydantic 검증)
- **Tracing**: 내장 추적 기능으로 워크플로우 시각화 및 디버깅
- **평가 및 미세조정**: OpenAI 평가, 미세조정, 증류 도구 연동

## 기본 사용법

### Hello World

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# 환경변수 설정 필요
# export OPENAI_API_KEY=sk-...
```

## 주요 패턴들

### 1. Agents-as-Tools 패턴

다른 에이전트들을 도구로 활용하는 오케스트레이션 패턴:

```python
from agents import Agent, Runner

# 전문 번역 에이전트들
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You translate the user's message to Spanish",
    handoff_description="An english to spanish translator"
)

french_agent = Agent(
    name="french_agent", 
    instructions="You translate the user's message to French",
    handoff_description="An english to french translator"
)

# 오케스트레이터 에이전트
orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions="You use the tools to translate. Never translate on your own.",
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate to Spanish"
        ),
        french_agent.as_tool(
            tool_name="translate_to_french", 
            tool_description="Translate to French"
        )
    ]
)
```

### 2. 조건부 도구 활성화

사용자 권한이나 컨텍스트에 따라 도구를 동적으로 활성화/비활성화:

```python
from pydantic import BaseModel
from agents import Agent, RunContextWrapper

class AppContext(BaseModel):
    language_preference: str = "spanish_only"

def french_enabled(ctx: RunContextWrapper[AppContext], agent) -> bool:
    return ctx.context.language_preference in ["french_spanish", "european"]

orchestrator = Agent(
    name="orchestrator",
    tools=[
        spanish_agent.as_tool(is_enabled=True),  # 항상 활성화
        french_agent.as_tool(is_enabled=french_enabled)  # 조건부 활성화
    ]
)
```

### 3. 결정론적 워크플로우

각 단계가 특정 에이전트에 의해 순차적으로 처리되는 패턴:

```python
from pydantic import BaseModel
from agents import Agent, Runner, trace

class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool

story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="Generate a story outline"
)

outline_checker_agent = Agent(
    name="outline_checker_agent", 
    instructions="Judge the quality and determine if it's scifi",
    output_type=OutlineCheckerOutput
)

story_agent = Agent(
    name="story_agent",
    instructions="Write a story based on outline",
    output_type=str
)

async def main():
    with trace("Deterministic story flow"):
        # 1. 개요 생성
        outline_result = await Runner.run(story_outline_agent, input_prompt)
        
        # 2. 개요 검사
        checker_result = await Runner.run(outline_checker_agent, outline_result.final_output)
        
        # 3. 조건부 중단
        if not checker_result.final_output.good_quality:
            print("Outline quality insufficient")
            return
            
        # 4. 스토리 작성
        story_result = await Runner.run(story_agent, outline_result.final_output)
```

### 4. LLM-as-a-Judge 패턴

하나의 에이전트가 다른 에이전트의 출력을 평가하고 피드백을 제공:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]

story_generator = Agent(
    name="story_generator",
    instructions="Generate story outline, use feedback to improve"
)

evaluator = Agent(
    name="evaluator", 
    instructions="Evaluate outline, provide feedback. Never pass on first try.",
    output_type=EvaluationFeedback
)

async def main():
    with trace("LLM as a judge"):
        input_items = [{"content": msg, "role": "user"}]
        
        while True:
            # 스토리 생성
            story_result = await Runner.run(story_generator, input_items)
            input_items = story_result.to_input_list()
            
            # 평가
            eval_result = await Runner.run(evaluator, input_items)
            
            if eval_result.final_output.score == "pass":
                break
                
            # 피드백 추가
            input_items.append({
                "content": f"Feedback: {eval_result.final_output.feedback}", 
                "role": "user"
            })
```

### 5. 병렬화 패턴

여러 에이전트를 병렬로 실행하고 최적 결과 선택:

```python
import asyncio
from agents import Agent, Runner, trace

translation_agent = Agent(
    name="translator",
    instructions="Translate to Spanish"
)

picker_agent = Agent(
    name="picker", 
    instructions="Pick the best translation"
)

async def main():
    with trace("Parallel translation"):
        # 3개 번역 동시 실행
        res_1, res_2, res_3 = await asyncio.gather(
            Runner.run(translation_agent, msg),
            Runner.run(translation_agent, msg), 
            Runner.run(translation_agent, msg)
        )
        
        # 최적 번역 선택
        best_result = await Runner.run(picker_agent, f"Pick best: {translations}")
```

### 6. 라우팅/핸드오프 패턴

요청의 특성에 따라 적절한 전문 에이전트로 라우팅:

```python
french_agent = Agent(name="french_agent", instructions="You only speak French")
spanish_agent = Agent(name="spanish_agent", instructions="You only speak Spanish")
english_agent = Agent(name="english_agent", instructions="You only speak English")

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to appropriate agent based on language",
    handoffs=[french_agent, spanish_agent, english_agent]
)
```

## Guardrails (가드레일)

### 입력 가드레일

사용자 입력을 사전 검증:

```python
from agents import Agent, input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def math_guardrail(context, agent, input) -> GuardrailFunctionOutput:
    # 수학 숙제 질문인지 검사
    result = await Runner.run(guardrail_agent, input)
    final_output = result.final_output_as(MathHomeworkOutput)
    
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_math_homework
    )

agent = Agent(
    name="support_agent",
    instructions="Help customers with questions",
    input_guardrails=[math_guardrail]
)
```

### 출력 가드레일  

에이전트 응답을 사후 검증:

```python
from agents import Agent, output_guardrail, GuardrailFunctionOutput

@output_guardrail
async def sensitive_data_check(context, agent, output) -> GuardrailFunctionOutput:
    phone_in_response = "650" in output.response
    
    return GuardrailFunctionOutput(
        output_info={"phone_detected": phone_in_response},
        tripwire_triggered=phone_in_response
    )

agent = Agent(
    name="assistant",
    instructions="You are helpful",
    output_guardrails=[sensitive_data_check]
)
```

### 스트리밍 가드레일

실시간으로 출력을 모니터링하여 조기 중단:

```python
async def streaming_with_guardrails():
    result = Runner.run_streamed(agent, question)
    current_text = ""
    
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            current_text += event.data.delta
            
            # N자마다 가드레일 검사
            if len(current_text) >= next_check_len:
                guardrail_result = await check_guardrail(current_text)
                if guardrail_result.is_problematic:
                    break
```

## 도구 사용 강제

특정 상황에서 에이전트가 반드시 도구를 사용하도록 강제:

```python
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> Weather:
    return Weather(city=city, temperature="20C", conditions="Sunny")

agent = Agent(
    name="weather_agent",
    instructions="You are helpful",
    tools=[get_weather],
    tool_use_behavior="stop_on_first_tool",  # 첫 도구 결과로 즉시 완료
    model_settings=ModelSettings(tool_choice="required")  # 도구 사용 강제
)
```

## 세션 관리

자동 대화 기록 관리로 상태 처리 간소화:

```python
from agents import Agent, Runner

agent = Agent(name="assistant", instructions="You are helpful")

# 세션이 자동으로 대화 기록 관리
inputs = [{"content": "Hello", "role": "user"}]
result1 = await Runner.run(agent, inputs)

# 이전 결과를 다음 입력으로 자동 연결
inputs = result1.to_input_list()
inputs.append({"content": "How are you?", "role": "user"})
result2 = await Runner.run(agent, inputs)
```

## 추적 및 디버깅

내장 추적 기능으로 워크플로우 시각화:

```python
from agents import Agent, Runner, trace

async def main():
    # 전체 워크플로우를 단일 추적으로 그룹화
    with trace("Multi-agent workflow"):
        result1 = await Runner.run(agent1, input)
        result2 = await Runner.run(agent2, result1.final_output)
        
    # 대화별 추적 그룹화
    conversation_id = str(uuid.uuid4().hex[:16])
    with trace("User conversation", group_id=conversation_id):
        result = await Runner.run(agent, user_input)
```

## 베스트 프랙티스

1. **단순함 유지**: 복잡한 추상화보다 Python 내장 기능 활용
2. **추적 활용**: 모든 워크플로우에 `trace()` 컨텍스트 사용
3. **가드레일 설정**: 입력/출력 검증으로 안전성 확보
4. **병렬 처리**: `asyncio.gather()`로 독립적 작업 병렬화
5. **에러 핸들링**: 가드레일 예외 적절히 처리
6. **컨텍스트 관리**: 조건부 도구 활성화로 권한 제어

## 환경 설정

```bash
export OPENAI_API_KEY=your_api_key_here
```

이 가이드를 참고하여 OpenAI Agents SDK의 다양한 패턴들을 프로젝트에 적용할 수 있습니다.