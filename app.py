import streamlit as st
import urllib.request
import urllib.parse
import json
import base64
import re
from datetime import datetime

# ==========================================
# 网页整体设置
# ==========================================
st.set_page_config(page_title="新马汇率哪家好？ | SG/MY Exchange Rates", page_icon="💸", layout="centered")

# ==========================================
# 🧠 记忆中枢初始化
# ==========================================
if 'community_feed' not in st.session_state:
    st.session_state.community_feed = []
if 'lang' not in st.session_state:
    st.session_state.lang = "中文"

# ==========================================
# 🌐 语言字典 (多语种魔法的核心！)
# ==========================================
TEXT = {
    "title": {"中文": "🚀 新马汇率哪家好？", "English": "🚀 Best SG/MY Exchange Rates"},
    "tab1": {"中文": "📱 不需要现金？用app来换汇吧！", "English": "📱 No Cash? Use Apps!"},
    "tab2": {"中文": "🏪 需要现金？ 看看换汇店今日汇率！", "English": "🏪 Need Cash? Check Store Rates!"},
    
    # Tab 1 翻译
    "t1_sub": {"中文": "🌐 App 实时报价精算", "English": "🌐 Live App Rates Calculator"},
    "t1_input": {"中文": "👇 请输入你想汇款的 SGD 金额:", "English": "👇 Enter SGD Amount to transfer:"},
    "t1_btn": {"中文": "⚡ 获取 App 实时报价", "English": "⚡ Get Live Rates"},
    "t1_loading": {"中文": "正在连接大盘...", "English": "Connecting to market..."},
    "t1_success": {"中文": "✅ 国际大盘基准汇率: 1 SGD = {base_rate:.4f} MYR", "English": "✅ Market Base Rate: 1 SGD = {base_rate:.4f} MYR"},
    "t1_err": {"中文": "网络出错了...", "English": "Network error..."},
    
    # Tab 2 翻译
    "t2_sub1": {"中文": "📢 哪家汇率棒选哪家✌🏻", "English": "📢 Pick the Best Rate✌🏻"},
    "t2_empty": {"中文": "暂时还没有人上传今日汇率，快来做第一个爆料的英雄吧！", "English": "No rates uploaded today yet. Be the first to share!"},
    "t2_feed": {"中文": "📅 **{time}** | 📍 **{store}** 现场汇率: **{rate:.4f}**", "English": "📅 **{time}** | 📍 **{store}** Live Rate: **{rate:.4f}**"},
    "t2_sub2": {"中文": "🤝 我要爆料新汇率", "English": "🤝 Share a New Rate"},
    "t2_method": {"中文": "你要如何更新汇率？", "English": "How would you like to update?"},
    "t2_m1": {"中文": "✍️ 手动快速输入", "English": "✍️ Manual Entry"},
    "t2_m2": {"中文": "📸 拍照/上传智能识别", "English": "📸 Upload & AI Scan"},
    "t2_store": {"中文": "这是哪家店？", "English": "Which store is this?"},
    "t2_other": {"中文": "➕ 其他 (自行输入)", "English": "➕ Other (Enter manually)"},
    "t2_custom": {"中文": "🔍 请输入店名或地标:", "English": "🔍 Enter store name or landmark:"},
    
    # 交互与上传翻译
    "manual_input": {"中文": "请输入你看到的汇率 (SGD to MYR):", "English": "Enter the rate you saw (SGD to MYR):"},
    "btn_pub": {"中文": "🚀 极速发布", "English": "🚀 Publish Now"},
    "photo_up": {"中文": "上传现场汇率板照片", "English": "Upload rate board photo"},
    "photo_cap": {"中文": "现场画面", "English": "Live Scene"},
    "ai_btn": {"中文": "🧠 AI 提取汇率", "English": "🧠 AI Extract Rate"},
    "ai_loading": {"中文": "AI 扫描中...", "English": "AI Scanning..."},
    "ai_success": {"中文": "🎉 提取完成！猜测汇率为: {rate}", "English": "🎉 Extraction complete! Guessed rate: {rate}"},
    "ai_err1": {"中文": "图片不清晰。", "English": "Image unclear."},
    "ai_err2": {"中文": "网络连接失败。", "English": "Network connection failed."},
    "verify_sub": {"中文": "### ✍️ 审核与认领", "English": "### ✍️ Verify & Claim"},
    "verify_input": {"中文": "请确认最终汇率:", "English": "Confirm final rate:"},
    "btn_conf": {"中文": "🚀 确认发布", "English": "🚀 Confirm Publish"}
}

# 快捷翻译小助手函数
def t(key):
    return TEXT[key][st.session_state.lang]

# ==========================================
# 顶部语言切换开关
# ==========================================
col1, col2 = st.columns([4, 1]) # 让开关靠右
with col2:
    st.session_state.lang = st.radio("Language / 语言", ["中文", "English"], horizontal=True, label_visibility="collapsed")

# 大标题
st.title(t("title"))

tab1, tab2 = st.tabs([t("tab1"), t("tab2")])

# ==========================================
# 标签页 1：不需要现金 (线上 App)
# ==========================================
with tab1:
    st.subheader(t("t1_sub"))
    amount = st.number_input(t("t1_input"), min_value=1.0, value=1000.0, step=100.0)
    
    if st.button(t("t1_btn")):
        with st.spinner(t("t1_loading")):
            try:
                url = "https://api.exchangerate-api.com/v4/latest/SGD"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                base_rate = json.loads(urllib.request.urlopen(req).read())['rates']['MYR']
                st.success(t("t1_success").format(base_rate=base_rate))
                
                c1, c2, c3 = st.columns(3)
                c1.metric("🥇 YouTrip", f"{amount * (base_rate * (1 - 0.0015)):.2f} MYR")
                c2.metric("🥈 Wise", f"{(amount - (0.50 + amount * 0.0045)) * base_rate:.2f} MYR")
                c3.metric("🥉 CIMB / Maybank", f"{amount * (base_rate * (1 - 0.01)):.2f} MYR")
            except Exception as e:
                st.error(t("t1_err"))

# ==========================================
# 标签页 2：需要现金 (实体店社区)
# ==========================================
with tab2:
    st.subheader(t("t2_sub1"))
    
    if len(st.session_state.community_feed) == 0:
        st.info(t("t2_empty"))
    else:
        for item in reversed(st.session_state.community_feed):
            st.success(t("t2_feed").format(time=item['time'], store=item['store'], rate=item['rate']))
            
    st.markdown("---")
    st.subheader(t("t2_sub2"))
    
    upload_method = st.radio(t("t2_method"), [t("t2_m1"), t("t2_m2")], horizontal=True)
    
    store_list = [
        "Johor Bahru City Square - MaxMoney",
        "KSL City Mall - L.S. Money Changer",
        "牛车水 珍珠坊 - Crante",
        "莱佛士坊 The Arcade - Arcade Money Changers",
        t("t2_other")
    ]

    def select_and_verify_store():
        selected = st.selectbox(t("t2_store"), store_list)
        if selected == t("t2_other"):
            custom_store = st.text_input(t("t2_custom"))
            return custom_store if custom_store else None
        return selected

    # ----------------------------------------
    # 路线 A：手动流 
    # ----------------------------------------
    if upload_method == t("t2_m1"):
        final_rate_manual = st.number_input(t("manual_input"), value=3.4500, step=0.0010, format="%.4f")
        confirmed_store_manual = select_and_verify_store()
        
        if confirmed_store_manual:
            if st.button(t("btn_pub")):
                now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.community_feed.append({
                    "store": confirmed_store_manual,
                    "rate": final_rate_manual,
                    "time": now_time
                })
                st.rerun()

    # ----------------------------------------
    # 路线 B：拍照流 
    # ----------------------------------------
    else:
        uploaded_file = st.file_uploader(t("photo_up"), type=["jpg", "jpeg", "png"])
        ai_predicted_rate = 3.4500 
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption=t("photo_cap"), use_container_width=True)
            if st.button(t("ai_btn")):
                with st.spinner(t("ai_loading")):
                    try:
                        bytes_data = uploaded_file.getvalue()
                        base64_img = "data:image/jpeg;base64," + base64.b64encode(bytes_data).decode('utf-8')
                        ocr_url = "https://api.ocr.space/parse/image"
                        req_ocr = urllib.request.Request(ocr_url, data=urllib.parse.urlencode({'apikey': 'helloworld', 'base64Image': base64_img, 'language': 'eng'}).encode('utf-8'))
                        result = json.loads(urllib.request.urlopen(req_ocr).read())
                        if not result.get('IsErroredOnProcessing'):
                            parsed_text = result['ParsedResults'][0]['ParsedText']
                            match = re.search(r'(3\.\d{2,4})', parsed_text)
                            if match: ai_predicted_rate = float(match.group(1))
                            st.success(t("ai_success").format(rate=ai_predicted_rate))
                        else:
                            st.error(t("ai_err1"))
                    except Exception:
                        st.error(t("ai_err2"))
            
            st.markdown(t("verify_sub"))
            final_rate = st.number_input(t("verify_input"), value=ai_predicted_rate, step=0.0010, format="%.4f")
            confirmed_store = select_and_verify_store()
            
            if confirmed_store:
                if st.button(t("btn_conf")):
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.community_feed.append({
                        "store": confirmed_store,
                        "rate": final_rate,
                        "time": now_time
                    })
                    st.rerun()