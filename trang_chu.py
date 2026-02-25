# ==========================================
# FILE: trang_chu.py
# ==========================================
import sys
import os

# Ép Python phải nhìn vào đúng thư mục chứa file web_ai.py này
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
import streamlit as st
from streamlit_option_menu import option_menu
import requests
import os
import re
import json
import pandas as pd
from datetime import datetime
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

# --- CẤU HÌNH DỮ LIỆU ---
KNOWLEDGE_FILE = "brain.json"
HISTORY_FILE = "history.json"

# --- CÁC HÀM HỖ TRỢ (NẰM NGOÀI APP) ---
def load_data(filename):
    if not os.path.exists(filename):
        default_data = [] if filename == HISTORY_FILE else {}
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_data, f)
        return default_data
    with open(filename, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return [] if filename == HISTORY_FILE else {}

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
    except: return None

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ==========================================
# HÀM CHÍNH: CHỈ CHẠY KHI ĐƯỢC GỌI TỪ WEB_AI.PY
# ==========================================
def app():
    apply_custom_style() # Kích hoạt CSS từ file style.py
    
    # --- THÊM MỚI TỪ ĐÂY: CSS TOÀN CỤC CHO NỀN VÀ NÚT BẤM ---
    st.markdown("""
    <style>
    /* 1. Background Ombre tím xuống (Từ Tím nhạt pha trắng xuống Nền sáng #F8F4F9) */
    .stApp {
        background: linear-gradient(to bottom, #E8DEF0 0%, #F8F4F9 100%);
        background-attachment: fixed;
    }
    
    /* 2. Màu nút bấm (Button) - Chủ đạo #7D4698 */
    .stButton > button {
        background-color: #7D4698 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    /* 3. Khi Hover chuột vào nút - Tím đậm #59316B */
    .stButton > button:hover {
        background-color: #59316B !important;
        box-shadow: 0 4px 12px rgba(89, 49, 107, 0.4) !important;
        transform: translateY(-2px);
    }
    
    /* 4. Đổi viền Input/Text Area khi nhập văn bản thành Tím nhạt #A166AB */
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #A166AB !important;
        box-shadow: 0 0 0 1px #A166AB !important;
    }
    </style>
    """, unsafe_allow_html=True)
    # --- KẾT THÚC PHẦN THÊM MỚI ---
    
    # --- MENU ĐIỀU HƯỚNG BÊN TRÁI ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; margin:0;'>ALEXANDER</h2>", unsafe_allow_html=True)
        st.caption("AI Grading System v3.0 Pro")
        
        choice = option_menu(
            menu_title=None,
            options=["Trang chủ", "AI Chấm thi", "Tiến trình học", "Huấn luyện não", "Lịch sử"],
            icons=["house", "pen", "graph-up-arrow", "cpu", "clock-history"],
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                # SỬA MÀU Ở ĐÂY: Icon chính dùng màu Chủ đạo (#7D4698)
                "icon": {"color": "#7D4698", "font-size": "18px"}, 
                
                # SỬA MÀU Ở ĐÂY: Chữ của menu lúc bình thường dùng Tím đậm (#59316B)
                "nav-link": {"font-size": "15px", "margin": "5px", "color": "#59316B"},
                
                # SỬA MÀU Ở ĐÂY: Background khi được chọn dùng màu Chủ đạo (#7D4698)
                "nav-link-selected": {"background-color": "#7D4698", "color": "white"},
            }
        )
        
        st.markdown("---")
        api_key = st.text_input("🔑 API Key:", type="password")
        
        topics = load_data(KNOWLEDGE_FILE)
        st.success(f"🧠 Đã học: {len(topics)} chủ đề")

    # --- LOGIC CÁC TRANG ---
    if choice == "Trang chủ":
        st.markdown("""
        <style>
        /* SỬA MÀU Ở ĐÂY: Gradient tiêu đề dùng Tím đậm (#59316B) -> Tím nhạt (#A166AB) -> Chủ đạo (#7D4698) */
        .title-gradient {
            background: -webkit-linear-gradient(45deg, #59316B, #A166AB, #7D4698);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 3em; font-weight: 800; margin-bottom: 0px; line-height: 1.2;
        }
        
        /* SỬA MÀU Ở ĐÂY: Con trỏ nhấp nháy dùng màu Chủ đạo (#7D4698) */
        .typing-container {
            display: inline-block; overflow: hidden; white-space: nowrap;
            border-right: .15em solid #7D4698; /* Đã đổi màu */
            animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
            font-family: 'Consolas', 'Courier New', monospace; color: #333;
            font-size: 1.2rem; font-weight: 600; margin-bottom: 20px;
        }
        @keyframes typing { from { width: 0 } to { width: 100% } }
        
        /* SỬA MÀU Ở ĐÂY: Hiệu ứng nhấp nháy của con trỏ (Chủ đạo #7D4698) */
        @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #7D4698; } }
        
        /* SỬA MÀU Ở ĐÂY: Viền Card dùng Tím nhạt (#A166AB) dạng trong suốt */
        .feature-card {
            background: rgba(248, 244, 249, 0.8); /* Nền sáng #F8F4F9 */
            backdrop-filter: blur(8px);
            border: 1px solid #A166AB; /* Viền tím nhạt */
            border-radius: 16px;
            padding: 20px; transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* SỬA MÀU Ở ĐÂY: Khi hover chuột vào Card -> Viền dùng Chủ đạo (#7D4698), bóng dùng rgba của Chủ đạo */
        .feature-card:hover {
            transform: translateY(-5px); background: #ffffff;
            box-shadow: 0 10px 15px rgba(125, 70, 152, 0.2); /* Bóng màu tím */
            border-color: #7D4698; /* Viền chủ đạo */
        }
        .card-icon { font-size: 2.2rem; margin-bottom: 12px; display: block; }
        
        /* SỬA MÀU Ở ĐÂY: Tiêu đề Card dùng Tím đậm (#59316B) */
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
            if not api_key: st.error("Thiếu API Key")
            elif not essay_input: st.warning("Chưa nhập nội dung")
            else:
                with st.spinner("Tôi đang đọc và phân tích bài..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel([m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods][0])
                        context = "\n".join([f"- {t}: {topics[t]['content']}" for t in selected_topics])
                        prompt = f"""
                        Vai trò: Bạn là trợ lý AI thông minh. Xưng: 'Tôi' và 'Bạn'.
                        Kiến thức: {context}
                        Nội dung: {essay_input}
                        YÊU CẦU: Trả về ĐÚNG cấu trúc sau:
                        [PHAN_1]
                        (Viết lại văn bản gốc, bọc lỗi sai trong <red>...</red>, ý hay trong <green>...</green>)
                        [/PHAN_1]
                        [PHAN_2]
                        (Giải thích lỗi sai và gợi ý sửa)
                        [/PHAN_2]
                        [PHAN_3]
                        (Code graphviz tóm tắt, mẫu: digraph G {{ rankdir=LR; "A"->"B"; }})
                        [/PHAN_3]
                        """
                        response = model.generate_content(prompt)
                        st.session_state['current_result'] = response.text
                        st.session_state['current_essay'] = essay_input
                        st.rerun()
                    except Exception as e: st.error(f"Lỗi: {e}")

        if 'current_result' in st.session_state:
            full_res = st.session_state['current_result']
            try:
                part1_essay = full_res.split("[PHAN_1]")[1].split("[/PHAN_1]")[0].strip()
                part2_feedback = full_res.split("[PHAN_2]")[1].split("[/PHAN_2]")[0].strip()
                part3_graph = full_res.split("[PHAN_3]")[1].split("[/PHAN_3]")[0].strip()
                part3_graph = part3_graph.replace("```graphviz", "").replace("```", "").strip()
            except:
                part1_essay = st.session_state.get('current_essay', '')
                part2_feedback = full_res
                part3_graph = None

            with st.container():
                st.markdown("##### 🛠️ Bảng điều khiển")
                c_tools = st.columns([1.5, 1, 1, 1], gap="small")
                with c_tools[0]: show_map = st.toggle("🧠 Bật Mindmap", value=False)
                with c_tools[1]:
                    if st.button("🔊 Nghe lỗi", use_container_width=True):
                        audio_file = text_to_speech(part2_feedback[:500])
                        if audio_file: st.audio(audio_file, format='audio/mp3')
                with c_tools[2]: st.download_button("📥 Tải về", data=full_res, file_name="report.txt", use_container_width=True)
                with c_tools[3]:
                    if st.button("💾 Lưu lại", use_container_width=True):
                        h = load_data(HISTORY_FILE)
                        h.append({"date": datetime.now().strftime("%d/%m"), "score": 0, "feedback": "Đã lưu", "essay": st.session_state.get('current_essay', '')})
                        save_data(HISTORY_FILE, h)
                        st.toast("Đã lưu vào bộ nhớ!", icon="✅")

            if show_map and part3_graph:
                st.markdown("---")
                st.graphviz_chart(part3_graph)
                st.markdown("---")

            c_left, c_right = st.columns([1, 1], gap="large")
            with c_left:
                html_essay = part1_essay.replace("<red>", '<span class="highlight-error" title="Lỗi">').replace("</red>", '</span>').replace("<green>", '<span class="highlight-success" title="Hay">').replace("</green>", '</span>').replace("\n", "<br>")
                st.markdown(f'<div class="paper-card"><div class="card-header">📄 BÀI CỦA BẠN</div>{html_essay}</div>', unsafe_allow_html=True)
            with c_right:
                html_feedback = part2_feedback.replace("\n", "<br>")
                # Đổi viền trái sang Chủ đạo #7D4698, nền sang Nền sáng #F8F4F9, màu chữ tiêu đề sang Tím đậm #59316B
                st.markdown(f'<div class="paper-card" style="border-left: 4px solid #7D4698; background-color: #F8F4F9;"><div class="card-header" style="color: #59316B;">🤖 GÓC NHÌN AI</div>{html_feedback}</div>', unsafe_allow_html=True)

    elif choice == "Tiến trình học":
        st.title("📈 Biểu đồ năng lực")
        history = load_data(HISTORY_FILE)
        if len(history) > 0:
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
        else: st.info("Chưa có dữ liệu.")

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
                else: st.warning("Vui lòng nhập đủ thông tin!")
        with tab2:
            topics = load_data(KNOWLEDGE_FILE)
            if not topics: st.info("Bộ nhớ trống.")
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
        if not history: st.info("Chưa có bài nào.")
        for i, item in reversed(list(enumerate(history))):
            score = item.get('score', 'N/A')
            date = item.get('date', 'Không rõ ngày')
            essay_content = item.get('essay', '') 
            with st.expander(f"Điểm: {score} | 📅 {date}"):
                if essay_content: st.write(f"**Đề/Bài làm:** {essay_content[:100]}...")
                st.markdown("---")
                st.write(item.get('feedback', 'Không có nhận xét.'))
                if st.button("Xóa bài này", key=f"del_hist_{i}"):
                    history.pop(i)
                    save_data(HISTORY_FILE, history)
                    st.rerun()
                    
    # Gọi chatbot trôi nổi ở cuối hàm app()
   