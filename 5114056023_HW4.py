import streamlit as st
import google.generativeai as genai

# ==========================================
# ⚠️ 請填入你的 API Key
# ==========================================
API_KEY = "AIzaSyBeFmDMw6bDQ68Ofap6qwq2YVFy3xl2Hgc" # <--- 記得填回你的 Key
# ==========================================

st.set_page_config(page_title="AI 購物比價王", page_icon="🛒", layout="wide")
st.title("🛒 AI 購物比價王 (鎖定電商版)")
st.markdown("這是一個專注於 **購物平台** 的搜尋引擎。我會強制 Gemini 只去 **Momo、蝦皮、PChome** 找資料！")

# --- 側邊欄 ---
with st.sidebar:
    st.info("✅ 已啟用 Google Search Grounding")

# --- 核心功能 ---
def ask_gemini_shopping_only(user_query, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # ✅ 關鍵：現在環境已經更新了，這個寫法絕對可以跑！
        model = genai.GenerativeModel('models/gemini-1.5-flash-002', tools='google_search_retrieval')
        
        search_instruction = f"{user_query} (site:momo.com.tw OR site:shopee.tw OR site:pchome.com.tw)"
        
        prompt = f"""
        你是一位電商導購專家。請利用 Google 搜尋功能，針對以下關鍵字搜尋："{search_instruction}"
        
        ⚠️ 嚴格限制：
        1. 資料來源必須來自 **Momo**、**蝦皮** 或 **PChome**。
        2. 請找出現貨且價格明確的 3-5 款產品。

        請輸出 Markdown 表格 (產品名稱/價格/理由/來源)，並給出購買建議。
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"發生錯誤: {str(e)}"

# --- 主介面 ---
user_input = st.text_input("你想買什麼？", "")

if st.button("開始比價 🔎"):
    if "AIza" not in API_KEY:
        st.error("⚠️ 請填入 API Key")
    elif not user_input:
        st.warning("請輸入關鍵字")
    else:
        st.info(f"🔍 搜尋中：{user_input} ...")
        result = ask_gemini_shopping_only(user_input, API_KEY)
        st.markdown(result)