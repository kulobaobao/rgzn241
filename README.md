# 🎭 角色扮演AI助手

基于LangChain框架开发的角色扮演AI助手应用，支持多种角色模拟、智能问答等功能。

## ✨ 功能特点

- **角色扮演**：支持模拟不同人物角色进行对话
- **预设角色**：内置孔子、爱因斯坦、客服小美、心理咨询师等角色
- **自定义角色**：支持创建自定义角色，设置姓名、性格、背景和说话风格
- **多种对话模式**：角色扮演、普通聊天、智能助手（支持工具调用）
- **记忆功能**：支持对话历史记忆，保持对话连贯性
- **工具调用**：支持天气查询、数学计算等工具

## 🛠️ 技术栈

- **后端**：LangChain + LangServe + FastAPI
- **前端**：Streamlit
- **大模型**：OpenAI GPT-3.5/4

## 📁 项目结构

```
├── server.py          # 后端LangChain Server
├── frontend.py        # 前端Streamlit应用
├── requirements.txt   # 依赖清单
├── .env.example       # 环境变量示例
└── README.md          # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加您的OpenAI API密钥：

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

### 3. 启动后端服务

```bash
python server.py
```

服务将在 `http://localhost:8000` 启动。

### 4. 启动前端应用

在另一个终端窗口运行：

```bash
streamlit run frontend.py
```

前端应用将在 `http://localhost:8501` 启动。

## 🌐 API接口

### 角色扮演接口

**POST** `/api/roleplay`

请求体：
```json
{
    "character": {
        "name": "角色名称",
        "personality": "性格描述",
        "background": "背景故事",
        "speaking_style": "说话风格"
    },
    "user_input": "用户输入",
    "chat_history": []
}
```

### 普通聊天接口

**POST** `/api/chat`

请求体：
```json
{
    "user_input": "用户输入",
    "chat_history": []
}
```

### 智能助手接口

**POST** `/api/agent`

请求体：
```json
{
    "user_input": "用户输入"
}
```

## 📦 LangChain核心组件

该项目展示了LangChain的核心功能：

1. **LLM调用**：使用ChatOpenAI调用GPT模型
2. **Prompt工程**：自定义System Prompt实现角色模拟
3. **Chain链式调用**：使用ConversationChain管理对话流程
4. **Memory记忆**：使用ConversationBufferMemory保持对话历史
5. **Tool工具使用**：集成天气查询、计算器等工具

## 🔧 工具列表

- `get_weather`：获取指定城市的天气信息
- `calculate`：进行数学计算

## 🚀 部署

### Streamlit Cloud部署

1. 将代码推送到GitHub仓库
2. 登录 [Streamlit Cloud](https://share.streamlit.io/)
3. 连接GitHub仓库
4. 设置环境变量 `OPENAI_API_KEY`
5. 指定 `frontend.py` 为入口文件

### Docker部署

```bash
docker build -t roleplay-ai .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key roleplay-ai
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 参考

本项目基于以下开源项目：

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangServe](https://github.com/langchain-ai/langserve)
- [Streamlit](https://github.com/streamlit/streamlit)