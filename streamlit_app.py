import streamlit as st
import os
import dashscope
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.llms.base import LLM
from pydantic import BaseModel

st.set_page_config(page_title="角色扮演AI助手", page_icon="🎭", layout="wide")

st.title("🎭 角色扮演AI助手")

api_key = st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

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

preset_characters = {
    "孔子": {
        "name": "孔子",
        "personality": "温文尔雅、博学多才、循循善诱",
        "background": "春秋时期著名的思想家、教育家，儒家学派创始人",
        "speaking_style": "使用文言文风格，引经据典，语气温和"
    },
    "客服小美": {
        "name": "小美",
        "personality": "热情友好、耐心细致、乐于助人",
        "background": "某大型电商平台的客服代表，拥有丰富的客户服务经验",
        "speaking_style": "亲切自然，使用礼貌用语，善于倾听"
    },
    "科学家爱因斯坦": {
        "name": "阿尔伯特·爱因斯坦",
        "personality": "睿智深沉、富有洞察力、不拘小节",
        "background": "20世纪最伟大的物理学家之一，相对论的创立者",
        "speaking_style": "严谨理性，喜欢用比喻解释复杂概念"
    },
    "心理咨询师": {
        "name": "李医生",
        "personality": "温和耐心、善解人意、专业严谨",
        "background": "资深心理咨询师，擅长倾听和引导",
        "speaking_style": "温和关怀，开放式提问，善于共情"
    }
}

with st.sidebar:
    st.subheader("角色选择")
    character_option = st.selectbox(
        "选择预设角色",
        ["自定义角色"] + list(preset_characters.keys())
    )
    
    if character_option == "自定义角色":
        name = st.text_input("角色名称", "我的角色")
        personality = st.text_area("性格描述", "友好、开朗")
        background = st.text_area("背景故事", "一个有趣的角色")
        speaking_style = st.text_area("说话风格", "自然、亲切")
    else:
        character = preset_characters[character_option]
        name = character["name"]
        personality = character["personality"]
        background = character["background"]
        speaking_style = character["speaking_style"]
        
        st.markdown(f"**性格：** {personality}")
        st.markdown(f"**背景：** {background}")
        st.markdown(f"**说话风格：** {speaking_style}")

    st.subheader("模式选择")
    mode = st.selectbox("选择对话模式", ["角色扮演", "普通聊天", "智能助手"])

    if not llm:
        st.warning("⚠️ DASHSCOPE_API_KEY 未配置，请在 Secrets 中设置")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_character" not in st.session_state:
    st.session_state.current_character = None

if st.session_state.current_character != (name, personality, background, speaking_style):
    st.session_state.chat_history = []
    st.session_state.current_character = (name, personality, background, speaking_style)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("请输入你的消息...")

def get_weather(city: str) -> str:
    return f"查询到{city}的天气：晴朗，温度25°C，湿度60%。"

def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

def roleplay_chat(name: str, personality: str, background: str, speaking_style: str, user_input: str, chat_history: list = None):
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

def normal_chat(user_input: str, chat_history: list = None):
    messages = []
    
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

def agent_chat(user_input: str):
    prompt = f"""你是一个智能助手，可以使用工具来回答问题。
如果需要获取天气或进行计算，请使用相应的工具。
如果不需要工具，可以直接回答。

问题：{user_input}

可用工具：
1. get_weather(city) - 获取指定城市的天气信息
2. calculate(expression) - 进行数学计算，支持加减乘除等基本运算

请直接给出答案或使用工具。
"""
    
    result = llm(prompt)
    return result

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                if not llm:
                    raise Exception("DASHSCOPE_API_KEY 未配置，请在 Streamlit Secrets 中设置")
                
                if mode == "角色扮演":
                    result = roleplay_chat(
                        name=name,
                        personality=personality,
                        background=background,
                        speaking_style=speaking_style,
                        user_input=user_input,
                        chat_history=st.session_state.chat_history[:-1]
                    )
                elif mode == "普通聊天":
                    result = normal_chat(
                        user_input=user_input,
                        chat_history=st.session_state.chat_history[:-1]
                    )
                else:
                    result = agent_chat(user_input=user_input)
                
                st.markdown(result)
                st.session_state.chat_history.append({"role": "assistant", "content": result})
                
            except Exception as e:
                st.error(f"错误：{str(e)}")
                st.markdown("请确保已在 Streamlit Secrets 中配置 DASHSCOPE_API_KEY")