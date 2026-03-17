import streamlit as st
import urllib.request
import urllib.parse
import json
import base64
import re
from datetime import datetime
import pandas as pd

# ==========================================
# 网页整体设置
# ==========================================
st.set_page_config(page_title="新马汇率哪家好？ | SG/MY Exchange Rates", page_icon="💸", layout="centered")

if 'community_feed' not in st.session_state:
    st.session_state.community_feed = []
if 'lang' not in st.session_state:
    st.session_state.lang = "中文"
# 🔥 新增：用于临时储存用户反馈的记忆中枢
if 'user_feedbacks' not in st.session_state:
    st.session_state.user_feedbacks = []

# ==========================================
# 🌐 语言字典
# ==========================================
TEXT = {
    "title": {"中文": "🚀 新马汇率哪家好？", "English": "🚀 Best SG/MY Exchange Rates"},
    "tab1": {"中文": "📱 不需要现金？用app来换汇吧！", "English": "📱 No Cash? Use Apps!"},
    "tab2": {"中文": "🏪 需要现金？ 看看换汇店今日汇率！", "English": "🏪 Need Cash? Check Store Rates!"},
    
    "t1_sub": {"中文": "🌐 App 实时报价精算", "English": "🌐 Live App Rates Calculator"},
    "t1_input": {"中文": "👇 请输入你想汇款的 SGD 金额:", "English": "👇 Enter SGD Amount to transfer:"},
    "t1_btn": {"中文": "⚡ 获取全网 App 报价", "English": "⚡ Get All App Rates"},
    "t1_loading": {"中文": "正在连接大盘...", "English": "Connecting to market..."},
    "t1_success": {"中文": "✅ 国际大盘基准汇率: 1 SGD = {base_rate:.4f} MYR", "English": "✅ Market Base Rate: 1 SGD = {base_rate:.4f} MYR"},
    "t1_disclaimer": {"中文": "⚠️ 免责声明：外汇市场瞬息万变，且各平台实际扣费可能随时调整，以下试算仅供参考，请以 App 内最终显示金额为准。", "English": "⚠️ Disclaimer: Live rates fluctuate constantly. Platform fees may vary. These estimates are for reference only, please check the actual App for final amounts."},
    "t1_full_list": {"中文": "📊 完整到手排行榜", "English": "📊 Full Estimated Payout Ranking"},
    "t1_err": {"中文": "网络出错了...", "English": "Network error..."},
    
    # 走势图专属文案
    "chart_title": {"中文": "📈 新币兑马币 (SGD/MYR) 历史走势", "English": "📈 SGD/MYR Historical Trend"},
    "chart_label": {"中文": "选择时间跨度:", "English": "Select Timeframe:"},
    "chart_loading": {"中文": "正在绘制华尔街走势图...", "English": "Plotting market trends..."},
    
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
    
    "manual_input": {"中文": "请输入你看到的汇率 (SGD to MYR):", "English": "Enter the rate you saw (SGD to MYR):"},
    "btn_pub": {"中文": "🚀 极速发布", "English": "🚀 Publish Now"},
    "photo_up": {"中文": "上传现场汇率板照片", "English": "Upload rate board photo"},
    "photo_cap": {"中文": "现场画面", "English": "Live Scene"},
    "ai_btn": {"中文": "🧠 AI 提取汇率", "English": "🧠 AI Extract Rate"},
    "ai_loading": {"中文": "AI 扫描中...", "English": "AI Scanning..."},
    "ai_success": {"中文": "🎉 提取完成！猜测汇率为: {rate}", "English": "🎉 Extraction complete! Guessed rate: {rate}"},
    "verify_sub": {"中文": "### ✍️ 审核与认领", "English": "### ✍️ Verify & Claim"},
    "verify_input": {"中文": "请确认最终汇率:", "English": "Confirm final rate:"},
    "btn_conf": {"中文": "🚀 确认发布", "English": "🚀 Confirm Publish"},
    
    "fb_title": {"中文": "💡 意见反馈", "English": "💡 Feedback"},
    "fb_prompt": {"中文": "汇率不准？想加新功能？尽管吐槽：", "English": "Found an issue? Want a new feature? Tell us:"},
    "fb_btn": {"中文": "提交反馈", "English": "Submit Feedback"},
    "fb_thanks": {"中文": "💖 收到！感谢你的反馈，我会继续优化的！", "English": "💖 Received! Thanks for helping us improve!"}
}

def t(key):
    return TEXT[key][st.session_state.lang]

# ==========================================
# 顶部语言切换开关
# ==========================================
col1, col2 = st.columns([4, 1])
with col2:
    st.session_state.lang = st.radio("Language / 语言", ["中文", "English"], horizontal=True, label_visibility="collapsed")

st.title(t("title"))

tab1, tab2 = st.tabs([t("tab1"), t("tab2")])

# ==========================================
# 标签页 1：不需要现金 (线上 App & 走势图)
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
                
                st.caption(t("t1_disclaimer"))
                
                wise_myr = (amount - (0.50 + amount * 0.0045)) * base_rate
                youtrip_myr = amount * (base_rate * (1 - 0.0015))
                panda_myr = ((amount - 4.0) * (base_rate * (1 - 0.002))) if amount > 4 else 0
                cimb_maybank_myr = amount * (base_rate * (1 - 0.01))
                dbs_uob_myr = amount * (base_rate * (1 - 0.015))
                
                results = {
                    "YouTrip 🟪": youtrip_myr,
                    "Wise 🟦": wise_myr,
                    "PandaRemit 🐼": panda_myr,
                    "CIMB / Maybank 🔴🟡": cimb_maybank_myr,
                    "DBS / UOB ⬛🔵": dbs_uob_myr
                }
                sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric(f"🥇 {sorted_results[0][0]}", f"{sorted_results[0][1]:.2f} MYR")
                c2.metric(f"🥈 {sorted_results[1][0]}", f"{sorted_results[1][1]:.2f} MYR")
                c3.metric(f"🥉 {sorted_results[2][0]}", f"{sorted_results[2][1]:.2f} MYR")
                
                st.markdown("---")
                with st.expander(t("t1_full_list")):
                    for i, (name, val) in enumerate(sorted_results, start=1):
                        display_val = f"{val:.2f} MYR" if val > 0 else "N/A (金额太小)"
                        st.write(f"第 {i} 名: **{name}** 👉 预计到手: **{display_val}**")
                        
            except Exception as e:
                st.error(t("t1_err"))

    # 🔥 雅虎财经走势图模块
    st.markdown("---")
    st.subheader(t("chart_title"))
    
    # 时间维度选择器
    time_options = {
        "当日 (Today)": ("1d", "15m"),
        "当周 (This Week)": ("5d", "1h"),
        "当月 (This Month)": ("1mo", "1d"),
        "3个月 (3 Months)": ("3mo", "1d"),
        "半年 (6 Months)": ("6mo", "1d"),
        "一年 (1 Year)": ("1y", "1d")
    }
    selected_range = st.selectbox(t("chart_label"), list(time_options.keys()))
    
    with st.spinner(t("chart_loading")):
        try:
            # 悄悄呼叫雅虎财经的底层 API
            range_val, interval_val = time_options[selected_range]
            yahoo_url = f"https://query1.finance.yahoo.com/v8/finance/chart/SGDMYR=X?range={range_val}&interval={interval_val}"
            req_yahoo = urllib.request.Request(yahoo_url, headers={'User-Agent': 'Mozilla/5.0'})
            yahoo_data = json.loads(urllib.request.urlopen(req_yahoo).read())
            
            # 解析数据并用 Pandas 整理成表格
            timestamps = yahoo_data['chart']['result'][0]['timestamp']
            closes = yahoo_data['chart']['result'][0]['indicators']['quote'][0]['close']
            
            dates = [datetime.fromtimestamp(ts) for ts in timestamps]
            df = pd.DataFrame({'SGD to MYR': closes}, index=dates)
            df = df.dropna() # 剔除空数据
            
            # 用 Streamlit 自带的折线图一键渲染！
            st.line_chart(df, use_container_width=True, color="#2ECC71")
        except Exception as e:
            st.warning("⚠️ 暂时无法获取历史走势图，请稍后再试。")

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

    if upload_method == t("t2_m1"):
        final_rate_manual = st.number_input(t("manual_input"), value=3.4500, step=0.0010, format="%.4f")
        confirmed_store_manual = select_and_verify_store()
        
        if confirmed_store_manual:
            if st.button(t("btn_pub")):
                now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.community_feed.append({"store": confirmed_store_manual, "rate": final_rate_manual, "time": now_time})
                st.rerun()

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
                    except Exception:
                        pass
            
            st.markdown(t("verify_sub"))
            final_rate = st.number_input(t("verify_input"), value=ai_predicted_rate, step=0.0010, format="%.4f")
            confirmed_store = select_and_verify_store()
            
            if confirmed_store:
                if st.button(t("btn_conf")):
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.community_feed.append({"store": confirmed_store, "rate": final_rate, "time": now_time})
                    st.rerun()

# ==========================================
# 💡 全局意见反馈窗口 (带隐藏后门版)
# ==========================================
st.markdown("---")
st.subheader(t("fb_title"))
feedback_text = st.text_area(t("fb_prompt"), placeholder="例如：能不能加入汇率走势图？...")

if st.button(t("fb_btn")):
    # 🕵️‍♂️ 隐藏的超级管理员后门！
    if feedback_text.strip() == "admin888":
        st.warning("⚠️ 警告：已进入管理员模式，正在调取后台用户反馈日志...")
        if len(st.session_state.user_feedbacks) == 0:
            st.write("目前还没有人提交反馈哦。")
        else:
            for fb in reversed(st.session_state.user_feedbacks):
                st.code(f"时间: {fb['time']} \n内容: {fb['msg']}")
    elif feedback_text:
        # 正常用户提交逻辑
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.user_feedbacks.append({"time": now_time, "msg": feedback_text})
        st.success(t("fb_thanks"))
        st.balloons()
