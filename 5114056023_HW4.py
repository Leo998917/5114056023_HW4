import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai

# ==========================================
# ⚠️ 設定區：請在這裡填入你的 Google Gemini API Key
# ==========================================
API_KEY = "AIzaSyBeFmDMw6bDQ68Ofap6qwq2YVFy3xl2Hgc"  # <--- 把你的 Key 貼在這裡，保留雙引號
# ==========================================

# --- 頁面設定 ---
st.set_page_config(page_title="Gemini 電商搜尋助手", page_icon="💎", layout="wide")
st.title("💎 Gemini 電商搜尋助手 (Hardcode Key 版)")
st.markdown("告訴我你想買什麼，我幫你上網搜 **Momo** 和 **蝦皮**，並用 **Gemini** 整理懶人包！")

# --- 側邊欄設定 ---
with st.sidebar:
    st.success("✅ 目前已使用內建的 API Key")
    st.info("💡 本系統使用 Gemini 1.5 Flash 模型進行分析。")
    target_site = st.radio("你想搜尋哪個平台？", ["Momo 購物網", "蝦皮購物 (Shopee)", "全網搜尋"])

# --- 核心功能：聯網搜尋 ---
def search_web(query, site_choice):
    site_syntax = ""
    if site_choice == "Momo 購物網":
        site_syntax = "site:momo.com.tw"
    elif site_choice == "蝦皮購物 (Shopee)":
        site_syntax = "site:shopee.tw"
    
    search_term = f"{site_syntax} {query}"
    results = []
    try:
        with DDGS() as ddgs:
            # max_results 可以自己調整，抓太多會變慢
            search_gen = ddgs.text(search_term, max_results=6)
            for r in search_gen:
                results.append(r)
    except Exception as e:
        st.error(f"搜尋連線錯誤: {e}")
    return results

# --- 核心功能：Gemini 分析 ---
def ai_summarize(user_query, search_results, api_key):
    if not search_results:
        return "找不到相關資料。"

    # 設定 Google API
    try:
        genai.configure(api_key=api_key)
        # 使用 Gemini 1.5 Flash (速度快且免費額度高)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return f"API 設定錯誤: {str(e)}"
    
    # 整理搜尋資料
    context = ""
    for i, res in enumerate(search_results):
        context += f"""
        [結果 {i+1}]
        標題: {res.get('title')}
        連結: {res.get('href')}
        摘要: {res.get('body')}
        ----------------
        """

    # 提示詞 (Prompt)
    prompt = f"""
    使用者想找："{user_query}"
    
    我剛剛上網搜尋到了以下產品資訊：
    {context}
    
    任務：
    1. 請從搜尋結果中，挑選 **3 款最相關** 的產品。
    2. 請製作一個 Markdown 表格，欄位包括：【產品名稱】、【價格(若有)】、【特色分析】、【購買連結】。
    3. 在表格下方，給出一段 100 字的「購買建議」。
    4. 若搜尋結果與產品無關，請說明找不到。
    
    請直接輸出分析結果。
    """

    try:
        # 呼叫 Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini 分析失敗: {str(e)}"

# --- 主介面互動 ---
user_input = st.text_input("你想找什麼？ (例如：羅技靜音滑鼠)", "")

if st.button("開始搜尋 🚀"):
    if "AIza" not in API_KEY:
        st.error("⚠️ 請先在程式碼第 7 行填入正確的 API Key！")
    elif not user_input:
        st.warning("請輸入關鍵字！")
    else:
        status_box = st.empty()
        status_box.info("正在連線 DuckDuckGo 搜尋中...")
        
        # 1. 搜尋
        raw_results = search_web(user_input, target_site)
        
        if raw_results:
            with st.expander("查看原始搜尋結果"):
                st.write(raw_results)
            
            # 2. Gemini 分析
            status_box.info("搜尋完成！正在呼叫 Gemini 大腦...")
            ai_response = ai_summarize(user_input, raw_results, API_KEY)
            
            status_box.success("分析完成！")
            st.markdown("### 💎 Gemini 推薦結果")
            st.markdown(ai_response)
        else:
            status_box.error("搜尋不到資料。")