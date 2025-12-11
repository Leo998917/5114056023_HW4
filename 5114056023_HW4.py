import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# ==========================================
# ⚠️ 設定區：請在這裡填入你的 Google Gemini API Key
# ==========================================
API_KEY = "AIzaSyBeFmDMw6bDQ68Ofap6qwq2YVFy3xl2Hgc"  # <--- 把你的 Key 貼在這裡，保留雙引號
# ==========================================

# --- 頁面設定 ---
st.set_page_config(page_title="AI 購物比價王", page_icon="🛒", layout="wide")
st.title("🛒 AI 購物比價王 (鎖定電商版)")
st.markdown("這是一個專注於 **購物平台** 的搜尋引擎。我會強制 Gemini 只去 **Momo、蝦皮、PChome** 找資料，過濾掉廣告和廢文！")

# --- 側邊欄 ---
with st.sidebar:
    st.info("✅ 已啟用 Google Search Grounding")
    st.success("🔒 搜尋範圍已鎖定：\n- Momo 購物網\n- 蝦皮購物\n- PChome 24h")

# --- 核心功能 ---
def ask_gemini_shopping_only(user_query, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # 啟用搜尋工具
        model = genai.GenerativeModel('models/gemini-1.5-flash', tools='google_search_retrieval')
        
        # 🌟 關鍵修改：我們不只是傳入使用者的問題，我們還把「搜尋語法」塞進去
        # 這會誘導 Gemini 在搜尋時使用 site: 語法
        search_instruction = f"{user_query} (site:momo.com.tw OR site:shopee.tw OR site:pchome.com.tw)"
        
        prompt = f"""
        你是一位專業的台灣電商導購專家。
        
        請利用 Google 搜尋功能，針對以下關鍵字進行搜尋：
        "{search_instruction}"
        
        ⚠️ 嚴格限制：
        1. 資料來源必須來自 **Momo**、**蝦皮** 或 **PChome** 的商品頁面。
        2. 請忽略新聞、部落格、維基百科或純討論區的結果。
        3. 請找出目前「有現貨」或「價格明確」的 3-5 款產品。

        請輸出結果為 Markdown 表格，欄位包含：
        - 📦 產品名稱
        - 💰 價格 (若搜尋結果有顯示)
        - ✨ 適合理由
        - 🔗 來源平台 (Momo/蝦皮/PChome)
        
        最後請給出一段簡短的購買建議。
        """
        
        # 發送請求
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"發生錯誤: {str(e)}\n(請確認 API Key 是否正確，或是否有啟用 Google Search Grounding 功能)"

# --- 主介面 ---
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_input("你想買什麼？ (例如：輕量化行動電源)", "")
with col2:
    st.write("") # 排版用
    st.write("") 
    search_btn = st.button("開始比價 🔎", use_container_width=True)

if search_btn:
    if "AIza" not in API_KEY:
        st.error("⚠️ 請先在程式碼第 7 行填入正確的 API Key！")
    elif not user_input:
        st.warning("請輸入商品關鍵字！")
    else:
        status_box = st.empty()
        status_box.info(f"正在鎖定各大電商平台搜尋：{user_input} ...")
        
        result = ask_gemini_shopping_only(user_input, API_KEY)
        
        status_box.success("比價完成！")
        st.markdown("### 🏷️ 嚴選商品清單")
        st.markdown(result)