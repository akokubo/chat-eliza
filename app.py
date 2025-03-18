import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from eliza.eliza import Eliza

# ===============================
# Streamlitページの基本設定
# ===============================
st.set_page_config(
    page_title="ELIZAチャットボット",
    page_icon=":material/psychology:",
    layout="wide"
)
st.title("ELIZAチャットボット")

# ===============================
# ELIZAをRunnable化するクラス定義
# ===============================
class ElizaRunnable(Runnable):
    def __init__(self):
        self.eliza = Eliza()
        self.eliza.load("eliza/doctor.txt")
        self.initial_msg = self.eliza.initial()

    def invoke(self, input, config=None):
        if isinstance(input, dict):
            user_input = input.get('text', '').strip()
        else:
            user_input = str(input).strip()
        return self.eliza.respond(user_input) if user_input else self.initial_msg

# ===============================
# チェインの構築
# ===============================
chain = (
    ElizaRunnable()
    | StrOutputParser()
)

# ===============================
# セッション状態の初期化
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []
    initial_msg = chain.invoke({"text": ""})
    st.session_state.messages.append(AIMessage(content=initial_msg))

# ===============================
# メッセージ履歴の表示
# ===============================
for message in st.session_state.messages:
    role = "assistant" if isinstance(message, AIMessage) else "user"
    avatar = ":material/psychology:" if role == "assistant" else ":material/person:"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.content)

# ===============================
# ユーザー入力の処理
# ===============================
user_input = st.chat_input("ELIZAに話しかけてみましょう", key="user_input")
if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(user_input)

    try:
        response = chain.invoke({"text": user_input})
    except ConnectionError:
        response = "⚠️ネットワークエラーが発生しました。接続を確認してください。"
    except Exception as e:
        response = f"⚠️エラーが発生しました: {str(e)}"

    st.session_state.messages.append(AIMessage(content=response))
    with st.chat_message("assistant", avatar=":material/psychology:"):
        st.markdown(response)
