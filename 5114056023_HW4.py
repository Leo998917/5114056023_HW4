import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI

# --- 頁面設定 ---
st.set_page_config(page_title="AI 電商搜尋助手", page_icon="🔍", layout="wide")
st.title("🔍 AI 電商搜尋助手 (聯網版)")
st.markdown("告訴我你想買什麼，我幫你上網搜 **Momo** 和 **蝦皮**，並整理懶人包給你！")

# --- 側邊欄設定 ---
with st.sidebar:
    api_key = st.text_input("請輸入 OpenAI API Key", type="password")
    st.info("💡 本系統使用 DuckDuckGo 進行即時聯網搜尋。")
    target_site = st.radio("你想搜尋哪個平台？", ["Momo 購物網", "蝦皮購物 (Shopee)", "全網搜尋"])

# --- 核心功能：聯網搜尋 ---
def search_web(query, site_choice):
    # 根據選擇鎖定特定網站，增加準確度
    site_syntax = ""
    if site_choice == "Momo 購物網":
        site_syntax = "site:momo.com.tw"
    elif site_choice == "蝦皮購物 (Shopee)":
        site_syntax = "site:shopee.tw"
    
    # 組合搜尋關鍵字
    search_term = f"{site_syntax} {query}"
    
    results = []
    try:
        # 使用 DuckDuckGo 搜尋 (max_results 設為 8 筆，避免讀太多雜訊)
        with DDGS() as ddgs:
            # ddgs.text 回傳的是一個 generator，我們把它轉成 list
            search_gen = ddgs.text(search_term, max_results=8)
            for r in search_gen:
                results.append(r)
    except Exception as e:
        st.error(f"搜尋連線錯誤: {e}")
    
    return results

# --- 核心功能：AI 整理 ---
def ai_summarize(user_query, search_results, api_key):
    if not search_results:
        return "找不到相關資料，請嘗試更換關鍵字。"

    client = OpenAI(api_key=api_key)
    
    # 1. 把搜尋結果變成文字檔給 AI 看
    context = ""
    for i, res in enumerate(search_results):
        context += f"""
        [結果 {i+1}]
        標題: {res.get('title')}
        連結: {res.get('href')}
        摘要: {res.get('body')}
        ----------------
        """

    # 2. 下 Prompt (提示詞)
    prompt = f"""
    使用者想找："{user_query}"
    
    我剛剛上網搜尋到了以下產品資訊（來自 DuckDuckGo）：
    {context}
    
    任務：
    1. 請從搜尋結果中，挑選 **3-4 款最相關** 的產品。
    2. 如果搜尋結果是廣告或與產品無關，請忽略。
    3. 請製作一個 Markdown 表格，欄位包括：【產品名稱】、【價格(若摘要有提到)】、【特色分析】、【購買連結】。
    4. 在表格下方，給出一段 150 字的「AI 購買建議」，比較這幾款的差異。
    
    請注意：連結必須保留原始網址，不要隨意修改。
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini", # 使用 mini 版比較省錢且速度快
        messages=[
            {"role": "system", "content": "你是一個專業的網購導購 AI。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --- 主介面 ---
user_input = st.text_input("你想找什麼？ (例如：羅技靜音滑鼠、適合小坪數的除濕機)", "")

if st.button("開始搜尋"):
    if not api_key:
        st.warning("請先輸入 API Key！")
    elif not user_input:
        st.warning("請輸入關鍵字！")
    else:
        # 第一步：顯示搜尋狀態
        status_box = st.empty()
        status_box.info("正在連線 DuckDuckGo 搜尋中...")
        
        # 執行搜尋
        raw_results = search_web(user_input, target_site)
        
        if raw_results:
            # 顯示原始結果 (除錯用，也可以讓使用者看到你真的有搜)
            with st.expander("查看原始搜尋結果 (Raw Data)"):
                st.write(raw_results)
            
            # 第二步：AI 思考
            status_box.info("搜尋完成！AI 正在閱讀並撰寫比較報告...")
            ai_response = ai_summarize(user_input, raw_results, api_key)
            
            # 第三步：顯示結果
            status_box.success("分析完成！")
            st.markdown("### AI 推薦結果")
            st.markdown(ai_response)
            
        else:
            status_box.error("搜尋不到任何資料，可能是網路問題或關鍵字太冷門。")