import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 配置 LangSmith 追踪功能
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING", "true")
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT", "default")

# 设置 Streamlit 应用标题
st.title('🦜🔗 中文小故事生成器')

def get_api_key():
    return os.environ.get("Deepseek_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""

# 创建提示词模板，{topic} 是占位符
prompt = ChatPromptTemplate.from_template("请编写一篇关于{topic}的中文小故事，不超过100字")

# 配置 DeepSeek 模型
model = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=get_api_key(),
    model="deepseek-chat",
    temperature=0.8
)

# 使用 LCEL 构建链：提示词 -> 模型 -> 输出
chain = prompt | model

# 创建 Streamlit 表单
with st.form('my_form'):
    text = st.text_area('输入主题关键词:', '小白兔')
    submitted = st.form_submit_button('提交')
    if submitted:
        st.info(chain.invoke({"topic": text}))