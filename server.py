from fastapi import FastAPI, HTTPException, Body
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import dashscope

load_dotenv()

app = FastAPI(title="角色扮演AI助手", version="1.0")

api_key = os.getenv("DASHSCOPE_API_KEY")

class DashScopeLLM(LLM):
    model_name: str = "qwen-plus"
    
    @property
    def _llm_type(self) -> str:
        return "dashscope"
    
    def _call(self, prompt: str, stop=None) -> str:
        dashscope.api_key = api_key
        response = dashscope.Generation.call(
            model=self.model_name,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.7
        )
        if response.status_code == 200:
            if response.output is not None and hasattr(response.output, 'text') and response.output.text is not None:
                return response.output.text.strip()
            else:
                raise Exception(f"API response has no text: {response}")
        else:
            raise Exception(f"API call failed: {response.message}")

llm = None
if api_key and api_key != "your_dashscope_api_key_here":
    llm = DashScopeLLM()

class CharacterInfo(BaseModel):
    name: str = Field(description="角色名称")
    personality: str = Field(description="角色性格描述")
    background: str = Field(description="角色背景故事")
    speaking_style: str = Field(description="说话风格")

class RoleplayRequest(BaseModel):
    character: CharacterInfo
    user_input: str
    chat_history: list = None

class ChatRequest(BaseModel):
    user_input: str
    chat_history: list = None

class AgentRequest(BaseModel):
    user_input: str

def get_weather(city: str) -> str:
    return f"查询到{city}的天气：晴朗，温度25°C，湿度60%。"

def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="获取指定城市的天气信息"
)

calculator_tool = Tool(
    name="calculate",
    func=calculate,
    description="进行数学计算，支持加减乘除等基本运算"
)

tools = [weather_tool, calculator_tool]

def roleplay_chat(name: str, personality: str, background: str, speaking_style: str, user_input: str, chat_history: list = None):
    if not llm:
        raise HTTPException(status_code=500, detail="DashScope API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量")
    
    system_prompt = f"""你是一个角色扮演AI助手。

当前角色信息：
姓名：{name}
性格：{personality}
背景：{background}
说话风格：{speaking_style}

请严格按照上述角色设定进行对话，保持角色一致性。
"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=user_input))
    
    prompt = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    result = llm(prompt)
    return result

@app.get("/")
async def root():
    if llm:
        return {"message": "角色扮演AI助手服务已启动", "status": "ready"}
    else:
        return {"message": "角色扮演AI助手服务已启动", "status": "waiting", "info": "请配置 DASHSCOPE_API_KEY 环境变量"}

@app.post("/api/roleplay")
async def api_roleplay(request: RoleplayRequest = Body(...)):
    if not llm:
        raise HTTPException(status_code=500, detail="DashScope API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量")
    
    result = roleplay_chat(
        name=request.character.name,
        personality=request.character.personality,
        background=request.character.background,
        speaking_style=request.character.speaking_style,
        user_input=request.user_input,
        chat_history=request.chat_history
    )
    return {"response": result}

@app.post("/api/chat")
async def api_chat(request: ChatRequest = Body(...)):
    if not llm:
        raise HTTPException(status_code=500, detail="DashScope API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量")
    
    messages = []
    
    if request.chat_history:
        for msg in request.chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=request.user_input))
    
    prompt = "\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    result = llm(prompt)
    return {"response": result}

@app.post("/api/agent")
async def api_agent(request: AgentRequest = Body(...)):
    if not llm:
        raise HTTPException(status_code=500, detail="DashScope API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量")
    
    prompt = f"""你是一个智能助手，可以使用工具来回答问题。
如果需要获取天气或进行计算，请使用相应的工具。
如果不需要工具，可以直接回答。

问题：{request.user_input}

可用工具：
1. get_weather(city) - 获取指定城市的天气信息
2. calculate(expression) - 进行数学计算，支持加减乘除等基本运算

请直接给出答案或使用工具。
"""
    
    result = llm(prompt)
    return {"response": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
