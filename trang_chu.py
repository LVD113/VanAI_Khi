# ==========================================
# FILE: trang_chu.py - FIXED VERSION v2.2
# Cập nhật: Làm đẹp phần Nhận xét & Fix lỗi rò rỉ cấu trúc Prompt (Tags)
# Đã chuẩn hóa lại lỗi khoảng trắng (Indentation)
# ==========================================
import sys
import os
import re
import json
import requests
import pandas as pd
from datetime import datetime

# Ép Python phải nhìn vào đúng thư mục chứa file
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import streamlit as st
from streamlit_option_menu import option_menu
from gtts import gTTS
import google.generativeai as genai

# Try-except cho các module có thể thiếu
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st_lottie = None

try:
    from chatbot import show_floating_chatbot
except ImportError:
    def show_floating_chatbot(): pass

try:
    from style import apply_custom_style
except ImportError:
    def apply_custom_style(): pass

# --- CÁC HÀM HỖ TRỢ (NẰM NGOÀI APP) ---
def load_data(filename):
    if not os.path.exists(filename):
        default_data = [] if "history" in filename else {}
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_data, f)
        return default_data
    with open(filename, "r", encoding="utf-8") as f:
        try: 
            return json.load(f)
        except: 
            return [] if "history" in filename else {}

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_graphviz_code(text):
    pattern = r"```graphviz(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    return None

def text_to_speech(text):
    try:
        tts = gTTS(text=text[:500] + "...", lang='vi')
        filename = "temp_audio.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        st.warning(f"Lỗi TTS: {e}")
        return None

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.warning(f"Lỗi tải Lottie: {e}")
        return None

# ==========================================
# HÀM CHÍNH: CHỈ CHẠY KHI ĐƯỢC GỌI TỪ WEB_AI.PY
# ==========================================
def app():
    apply_custom_style() # Kích hoạt CSS từ file style.py
    
    # --- XỬ LÝ DỮ LIỆU CÁ NHÂN HÓA ---
    current_user = st.session_state.get('user_name', 'Khach')
    
    # 1. Tạo thư mục data_users nếu chưa có
    if not os.path.exists("data_users"):
        os.makedirs("data_users")
        
    # 2. Tạo thư mục riêng cho user hiện tại
    user_folder = f"data_users/{current_user}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    # 3. Gán file dữ liệu vào đúng thư mục user
    KNOWLEDGE_FILE = f"{user_folder}/brain.json"
    HISTORY_FILE = f"{user_folder}/history.json"
    CONFIG_FILE = f"{user_folder}/config.json" # File lưu cấu hình & API Key
    
    # Đọc config (chứa trạng thái onboarding và api_key nếu có)
    user_config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                user_config = json.load(f)
            except:
                user_config = {}
    saved_api_key = user_config.get("api_key", "") # Lấy API Key đã lưu (nếu có)
    
    # --- CSS TOÀN CỤC CHO NỀN VÀ NÚT BẤM ---
    st.markdown("""
    <style>
    /* 1. Background Ombre tím xuống */
    .stApp {
        background: linear-gradient(to bottom, #E8DEF0 0%, #F8F4F9 100%);
        background-attachment: fixed;
    }
    
    /* 2. Màu nút bấm (Button) */
    .stButton > button {
        background-color: #7D4698 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    /* 3. Khi Hover chuột vào nút */
    .stButton > button:hover {
        background-color: #59316B !important;
        box-shadow: 0 4px 12px rgba(89, 49, 107, 0.4) !important;
        transform: translateY(-2px);
    }
    
    /* 4. Đổi viền Input/Text Area */
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #A166AB !important;
        box-shadow: 0 0 0 1px #A166AB !important;
    }
    
    /* 5. Paper Card Style */
    .paper-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        line-height: 1.6;
        font-size: 0.95rem;
        color: #333;
    }
    
    .card-header {
        font-weight: 700;
        font-size: 1.05rem;
        color: #59316B;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #A166AB;
    }
    
    /* 6. Highlight styles */
    .highlight-error {
        background-color: #ffebee;
        color: #c62828;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 600;
    }
    
    .highlight-success {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- MENU ĐIỀU HƯỚNG BÊN TRÁI ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; margin:0;'>ALEXANDER</h2>", unsafe_allow_html=True)
        st.caption("AI Grading System v3.0 Pro")
        
        # --- THÔNG TIN USER ---
        st.markdown("---")
        st.write(f"👤 Xin chào: **{current_user}**")
        
        # --- CẤU HÌNH API KEY ---
        api_key = st.text_input("🔑 API Key:", type="password", value=saved_api_key)
        
        # Nếu nhập key mới thì tự động lưu vào config.json
        if api_key and api_key != saved_api_key:
            user_config["api_key"] = api_key
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(user_config, f)
        
        # Hướng dẫn lấy API Key
        with st.expander("❓ Trợ giúp: Cách lấy API Key"):
            st.markdown('''
                <ol style="font-size: 13px; padding-left: 20px;">
                    <li>Vào <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #7D4698;"><b>Google AI Studio</b></a></li>
                    <li>Đăng nhập bằng Gmail</li>
                    <li>Bấm nút <b>Create API key</b></li>
                    <li>Copy mã và dán vào ô bên trên</li>
                </ol>
            ''', unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- MENU TÍNH NĂNG ---
        choice = option_menu(
            menu_title=None,
            options=["Trang chủ", "AI Chấm thi", "Tiến trình học", "Huấn luyện não", "Lịch sử"],
            icons=["house", "pen", "graph-up-arrow", "cpu", "clock-history"],
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#7D4698", "font-size": "18px"}, 
                "nav-link": {"font-size": "15px", "margin": "5px", "color": "#59316B"},
                "nav-link-selected": {"background-color": "#7D4698", "color": "white"},
            }
        )
        
        st.markdown("---")
        
        # --- TIẾN TRÌNH / THỐNG KÊ NHANH ---
        topics = load_data(KNOWLEDGE_FILE)
        st.success(f"🧠 Đã học: {len(topics)} chủ đề")
        
        # --- NÚT ĐĂNG XUẤT ---
        st.markdown("---")
        if st.button("🔴 Đăng xuất", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['logged_in'] = False
            st.session_state['user_name'] = ""
            st.session_state['onboarding_step'] = 'intro'
            st.rerun()

    # --- LOGIC CÁC TRANG ---
    if choice == "Trang chủ":
        st.markdown("""
        <style>
        .title-gradient {
            background: -webkit-linear-gradient(45deg, #59316B, #A166AB, #7D4698);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 3em; font-weight: 800; margin-bottom: 0px; line-height: 1.2;
        }
        
        .typing-container {
            display: inline-block; overflow: hidden; white-space: nowrap;
            border-right: .15em solid #7D4698; 
            animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
            font-family: 'Consolas', 'Courier New', monospace; color: #333;
            font-size: 1.2rem; font-weight: 600; margin-bottom: 20px;
        }
        @keyframes typing { from { width: 0 } to { width: 100% } }
        
        @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #7D4698; } }
        
        .feature-card {
            background: rgba(248, 244, 249, 0.8); 
            backdrop-filter: blur(8px);
            border: 1px solid #A166AB; 
            border-radius: 16px;
            padding: 20px; transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .feature-card:hover {
            transform: translateY(-5px); background: #ffffff;
            box-shadow: 0 10px 15px rgba(125, 70, 152, 0.2); 
            border-color: #7D4698; 
        }
        .card-icon { font-size: 2.2rem; margin-bottom: 12px; display: block; }
        
        .card-title { font-weight: 700; font-size: 1.1rem; color: #59316B; margin-bottom: 5px; }
        .card-desc { font-size: 0.95rem; color: #4b5563; line-height: 1.5; }
        </style>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1.6, 1], gap="large")
        with c1:
            st.markdown('<h1 class="title-gradient">Hệ thống Alexander</h1>', unsafe_allow_html=True)
            st.markdown('<div class="typing-container">Trợ lý AI chấm thi & Phân tích thông minh</div>', unsafe_allow_html=True)
            st.write("Chào mừng trở lại! Dưới đây là các tính năng chính:")
            st.write("---")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                st.markdown("""<div class="feature-card"><span class="card-icon">📝</span><div class="card-title">AI Chấm thi</div><div class="card-desc">Phân tích bài làm tự động dựa trên barem chuẩn xác.</div></div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""<div class="feature-card"><span class="card-icon">🧠</span><div class="card-title">Bộ nhớ đệm</div><div class="card-desc">Quản lý và cập nhật kiến thức liên tục cho AI.</div></div>""", unsafe_allow_html=True)
            with col_sub2:
                st.markdown("""<div class="feature-card"><span class="card-icon">📊</span><div class="card-title">Tiến trình</div><div class="card-desc">Theo dõi biểu đồ tăng trưởng điểm số trực quan.</div></div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""<div class="feature-card"><span class="card-icon">⚡</span><div class="card-title">Tốc độ cao</div><div class="card-desc">Xử lý hàng nghìn từ vựng chỉ trong vài giây.</div></div>""", unsafe_allow_html=True)

    elif choice == "AI Chấm thi":
        st.title("📝 Phân tích văn bản")
        topics = load_data(KNOWLEDGE_FILE)
        selected_topics = st.multiselect("📚 Kiến thức áp dụng:", list(topics.keys()))
        
        if 'current_result' not in st.session_state:
            essay_input = st.text_area("Nhập văn bản của bạn:", height=300, placeholder="Gõ hoặc dán nội dung vào đây...")
            c_act1, c_act2, c_act3 = st.columns([1, 2, 1])
            with c_act2:
                start_btn = st.button("🚀 BẮT ĐẦU PHÂN TÍCH", use_container_width=True)
        else:
            col_new, _ = st.columns([1, 5])
            if col_new.button("🔄 Nhập bài mới"):
                del st.session_state['current_result']
                st.rerun()
                
        if 'start_btn' in locals() and start_btn:
            if not api_key: 
                st.error("⚠️ Bạn chưa nhập API Key ở thanh menu bên trái!")
            elif not essay_input: 
                st.warning("Chưa nhập nội dung")
            else:
                with st.spinner("Tôi đang đọc và phân tích bài..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel([m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods][0])
                        context = "\n".join([f"- {t}: {topics[t]['content']}" for t in selected_topics]) if selected_topics else "Không có kiến thức được chọn"
                        
                        # ĐÃ FIX: Rào lại prompt cực chặt, cấm nhại lời
                        prompt = f"""Bạn là trợ lý AI chuyên chấm thi. Xưng hô: 'Tôi' và 'Bạn'.
Kiến thức áp dụng: {context}

Bài làm của học viên: 
{essay_input}

NHIỆM VỤ: Phân tích bài làm. TUYỆT ĐỐI KHÔNG lặp lại các dòng yêu cầu này. CHỈ TRẢ VỀ ĐÚNG 3 PHẦN NẰM TRONG CÁC THẺ SAU:

[PHAN_1]
(Viết lại văn bản gốc, bọc lỗi sai trong <red>...</red>, ý hay trong <green>...</green>)
[/PHAN_1]
[PHAN_2]
(Giải thích lỗi sai và gợi ý sửa chi tiết)
[/PHAN_2]
[PHAN_3]
(Code graphviz tóm tắt, mẫu: digraph G {{ rankdir=LR; "A"->"B"; }})
[/PHAN_3]"""
                        response = model.generate_content(prompt)
                        st.session_state['current_result'] = response.text
                        st.session_state['current_essay'] = essay_input
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Lỗi: {str(e)}")

        if 'current_result' in st.session_state:
            full_res = st.session_state['current_result']
            
            p1_match = re.search(r'\[PHAN_1\](.*?)\[/PHAN_1\]', full_res, re.DOTALL)
            p2_match = re.search(r'\[PHAN_2\](.*?)\[/PHAN_2\]', full_res, re.DOTALL)
            p3_match = re.search(r'\[PHAN_3\](.*?)\[/PHAN_3\]', full_res, re.DOTALL)

            part1_essay = p1_match.group(1).strip() if p1_match else st.session_state.get('current_essay', '')
            
            # ĐÃ FIX: Nếu AI bị ngáo không trả về đúng định dạng -> Không in raw response ra để tránh lộ prompt
            if p2_match:
                part2_feedback = p2_match.group(1).strip()
            else:
                part2_feedback = "⚠️ **Lỗi hệ thống:** AI phản hồi sai cấu trúc định dạng. Vui lòng bấm '🔄 Nhập bài mới' và phân tích lại!"
                
            part3_graph = p3_match.group(1).strip() if p3_match else None
            if part3_graph:
                part3_graph = part3_graph.replace("```graphviz", "").replace("```", "").strip()

            with st.container():
                st.markdown("##### 🛠️ Bảng điều khiển")
                c_tools = st.columns([1.5, 1, 1, 1], gap="small")
                with c_tools[0]: 
                    show_map = st.toggle("🧠 Bật Mindmap", value=False)
                with c_tools[1]:
                    if st.button("🔊 Nghe lỗi", use_container_width=True):
                        audio_file = text_to_speech(part2_feedback[:500])
                        if audio_file: 
                            st.audio(audio_file, format='audio/mp3')
                with c_tools[2]: 
                    st.download_button("📥 Tải về", data=full_res, file_name="report.txt", use_container_width=True)
                with c_tools[3]:
                    if st.button("💾 Lưu lại", use_container_width=True):
                        h = load_data(HISTORY_FILE)
                        h.append({
                            "date": datetime.now().strftime("%d/%m"), 
                            "score": 0, 
                            "feedback": full_res, 
                            "essay": st.session_state.get('current_essay', '')
                        })
                        save_data(HISTORY_FILE, h)
                        st.toast("Đã lưu vào bộ nhớ!", icon="✅")

            if show_map and part3_graph:
                st.markdown("---")
                try:
                    st.graphviz_chart(part3_graph)
                except Exception as e:
                    st.warning(f"Lỗi hiển thị sơ đồ: {e}")
                st.markdown("---")

            c_left, c_right = st.columns([1, 1], gap="large")
            with c_left:
                html_essay = part1_essay.replace("<red>", '<span class="highlight-error">').replace("</red>", '</span>').replace("<green>", '<span class="highlight-success">').replace("</green>", '</span>').replace("\n", "<br>")
                st.markdown(f'<div class="paper-card"><div class="card-header">📄 BÀI CỦA BẠN</div>{html_essay}</div>', unsafe_allow_html=True)
            with c_right:
                # --- CHUYỂN ĐỔI MARKDOWN SANG HTML TRỰC QUAN ---
                html_feedback = re.sub(r'\*\*(.*?)\*\*', r'<b style="color: #59316B;">\1</b>', part2_feedback)
                html_feedback = re.sub(r'(?m)^\s*[\*\-]\s+', '&#8226; ', html_feedback)
                html_feedback = html_feedback.replace('*', '')
                html_feedback = html_feedback.replace("\n", "<br>")
                
                st.markdown(f'<div class="paper-card" style="border-left: 4px solid #7D4698;"><div class="card-header" style="color: #59316B;">🤖 GÓC NHÌN AI</div>{html_feedback}</div>', unsafe_allow_html=True)

    elif choice == "Tiến trình học":
        st.title("📈 Biểu đồ năng lực")
        history = load_data(HISTORY_FILE)
        if len(history) > 0:
            try:
                df = pd.DataFrame(history)
                chart_data = df[['date', 'score']]
                avg = df['score'].mean()
                last = df['score'].iloc[-1]
                best = df['score'].max()
                m1, m2, m3 = st.columns(3)
                m1.metric("Điểm trung bình", f"{avg:.2f}")
                m2.metric("Điểm cao nhất", f"{best}")
                m3.metric("Bài mới nhất", f"{last}", delta=f"{last - avg:.1f} so với TB")
                st.markdown("### Xu hướng điểm số")
                st.line_chart(chart_data.set_index('date'))
            except Exception as e:
                st.error(f"Lỗi xử lý dữ liệu: {e}")
        else: 
            st.info("Chưa có dữ liệu.")

    elif choice == "Huấn luyện não":
        st.title("🎓 Quản lý Kiến thức (Brain)")
        tab1, tab2 = st.tabs(["➕ Thêm kiến thức mới", "📋 Danh sách đã học"])
        with tab1:
            t_name = st.text_input("Tên chủ đề:")
            t_content = st.text_area("Nội dung:", height=200)
            if st.button("Nạp vào bộ nhớ"):
                if t_name and t_content:
                    topics = load_data(KNOWLEDGE_FILE)
                    topics[t_name] = {"content": t_content, "date": datetime.now().strftime("%d/%m/%Y")}
                    save_data(KNOWLEDGE_FILE, topics)
                    st.success(f"Đã học: {t_name}")
                    st.rerun()
                else: 
                    st.warning("Vui lòng nhập đủ thông tin!")
        with tab2:
            topics = load_data(KNOWLEDGE_FILE)
            if not topics: 
                st.info("Bộ nhớ trống.")
            else:
                for name, data in topics.items():
                    with st.expander(f"📚 {name}"):
                        st.code(data['content'])
                        if st.button("Quên (Xóa)", key=f"del_{name}"):
                            del topics[name]
                            save_data(KNOWLEDGE_FILE, topics)
                            st.rerun()

    elif choice == "Lịch sử":
        st.title("Nhật ký học tập")
        history = load_data(HISTORY_FILE)
        
        if not history: 
            st.info("Chưa có bài nào.")
        else:
            for i, item in reversed(list(enumerate(history))):
                score = item.get('score', 'N/A')
                date = item.get('date', 'Không rõ ngày')
                essay_content = item.get('essay', '') 
                feedback_content = item.get('feedback', 'Không có nhận xét.')
                
                with st.expander(f"Mục ngày 📅 {date}"):
                    if essay_content: 
                        st.markdown("**📄 BÀI LÀM GỐC CỦA BẠN:**")
                        st.info(essay_content)
                        
                    st.markdown("---")
                    st.markdown("**🤖 PHẦN ĐÃ SỬA VÀ NHẬN XÉT:**")
                    
                    # CHỖ NÀY CŨNG ĐÃ ĐƯỢC SỬA Regex cho phần lịch sử
                    p1_hist = re.search(r'\[PHAN_1\](.*?)\[/PHAN_1\]', feedback_content, re.DOTALL)
                    p2_hist = re.search(r'\[PHAN_2\](.*?)\[/PHAN_2\]', feedback_content, re.DOTALL)

                    if p1_hist and p2_hist:
                        part1 = p1_hist.group(1).strip()
                        part2 = p2_hist.group(1).strip()
                        
                        html_essay_hist = part1.replace("<red>", '<span class="highlight-error">').replace("</red>", '</span>').replace("<green>", '<span class="highlight-success">').replace("</green>", '</span>').replace("\n", "<br>")
                        
                        formatted_part2 = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#59316B;">\1</b>', part2)
                        formatted_part2 = re.sub(r'(?m)^\s*[\*\-]\s+', '&#8226; ', formatted_part2)
                        formatted_part2 = formatted_part2.replace('*', '')
                        formatted_part2 = formatted_part2.replace('\n', '<br>')

                        col_hist1, col_hist2 = st.columns([1, 1], gap="medium")
                        with col_hist1:
                            st.markdown(f'<div class="paper-card"><div class="card-header">Sửa trên bài</div>{html_essay_hist}</div>', unsafe_allow_html=True)
                        with col_hist2:
                            st.markdown(f'<div class="paper-card" style="border-left: 4px solid #7D4698;"><div class="card-header">Nhận xét</div>{formatted_part2}</div>', unsafe_allow_html=True)
                    else:
                        # Làm sạch các tag nếu AI trả lỗi cấu trúc để không bị lộ
                        clean_fb = re.sub(r'\[/?PHAN_\d\]', '', feedback_content).strip()
                        st.write(clean_fb)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Xóa bài này", key=f"del_hist_{i}"):
                        history.pop(i)
                        save_data(HISTORY_FILE, history)
                        st.rerun()
