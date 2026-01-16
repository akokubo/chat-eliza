import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
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
# 1. ELIZAインスタンスの永続化
# ===============================
# ページがリロードされても「同じELIZA」と話せるようにsession_stateに保存
if "eliza_core" not in st.session_state:
    bot = Eliza()
    bot.load("eliza/doctor.txt") # パスは環境に合わせて調整してください
    st.session_state.eliza_core = bot

# ===============================
# ELIZAをRunnable化するクラス定義
# ===============================
class ElizaRunnable(Runnable):
    def __init__(self, eliza_instance):
        # 毎回newするのではなく、渡された既存のインスタンスを使う
        self.eliza = eliza_instance
        # initialは毎回呼ぶとランダムで変わる可能性があるため固定したい場合は注意
        # ここでは便宜上、インスタンスのinitialメソッドを使います
        self.initial_msg = "How do you do. Please tell me your problem." 

    def invoke(self, input, config=None):
        if isinstance(input, dict):
            user_input = input.get('text', '').strip()
        else:
            user_input = str(input).strip()
        
        # 入力が空の場合は初期メッセージを返す(セッション初期化時用)
        if not user_input:
            return self.eliza.initial()
            
        return self.eliza.respond(user_input)

# ===============================
# チェインの構築
# ===============================
# session_stateにある「記憶を持ったELIZA」を渡す
chain = (
    ElizaRunnable(st.session_state.eliza_core)
    | StrOutputParser()
)

# ===============================
# セッション状態の初期化
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 初回メッセージの取得
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
        # ここでinvokeすると、session_state内のeliza_coreが更新（記憶）される
        response = chain.invoke({"text": user_input})
    except ConnectionError:
        response = "⚠️ネットワークエラーが発生しました。接続を確認してください。"
    except Exception as e:
        response = f"⚠️エラーが発生しました: {str(e)}"

    st.session_state.messages.append(AIMessage(content=response))
    with st.chat_message("assistant", avatar=":material/psychology:"):
        st.markdown(response)