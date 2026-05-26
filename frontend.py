import streamlit as st
import requests
import json

st.set_page_config(page_title="角色扮演AI助手", page_icon="🎭", layout="wide")

st.title("🎭 角色扮演AI助手")

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

    api_url = st.text_input("后端API地址", "http://localhost:8000")

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

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                if mode == "角色扮演":
                    payload = {
                        "character": {
                            "name": name,
                            "personality": personality,
                            "background": background,
                            "speaking_style": speaking_style
                        },
                        "user_input": user_input,
                        "chat_history": st.session_state.chat_history[:-1]
                    }
                    response = requests.post(f"{api_url}/api/roleplay", json=payload)
                elif mode == "普通聊天":
                    payload = {
                        "user_input": user_input,
                        "chat_history": st.session_state.chat_history[:-1]
                    }
                    response = requests.post(f"{api_url}/api/chat", json=payload)
                else:
                    payload = {"user_input": user_input}
                    response = requests.post(f"{api_url}/api/agent", json=payload)
                
                response.raise_for_status()
                result = response.json()
                
                ai_response = result.get("response", "抱歉，我无法回答这个问题。")
                st.markdown(ai_response)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
            except requests.exceptions.RequestException as e:
                st.error(f"连接错误：{str(e)}")
                st.markdown("当前后端服务未启动，请先运行 `python server.py` 启动服务。")