# ==========================================
# FILE: trang_chu.py - FIXED VERSION v2.6 (THÊM THƯ VIỆN MẪU CHẤM)
# ==========================================
import sys
import os
import re
import json
import requests
import pandas as pd
from datetime import datetime
import io

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

# --- THƯ VIỆN ĐỌC FILE ---
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

# --- CÁC HÀM HỖ TRỢ ---
def read_file_content(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            if not PyPDF2: return "⚠️ Thiếu thư viện PyPDF2. Hãy mở terminal gõ: pip install PyPDF2"
            pdf = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        elif uploaded_file.name.endswith('.docx'):
            if not docx: return "⚠️ Thiếu thư viện python-docx. Hãy mở terminal gõ: pip install python-docx"
            doc = docx.Document(uploaded_file)
            return "\n".join(para.text for para in doc.paragraphs)
        elif uploaded_file.name.endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"⚠️ Lỗi đọc file: {e}"
    return ""

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
    apply_custom_style() 
    
    # Lấy API KEY từ Secrets để không bị Google khóa mã
    try:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        MY_API_KEY = ""
    
    current_user = st.session_state.get('user_name', 'Khach')
    
    if not os.path.exists("data_users"):
        os.makedirs("data_users")
        
    user_folder = f"data_users/{current_user}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    KNOWLEDGE_FILE = f"{user_folder}/brain.json"
    HISTORY_FILE = f"{user_folder}/history.json"
    CONFIG_FILE = f"{user_folder}/config.json"
    
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #E8DEF0 0%, #F8F4F9 100%); background-attachment: fixed; }
    .stButton > button { background-color: #7D4698 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { background-color: #59316B !important; box-shadow: 0 4px 12px rgba(89, 49, 107, 0.4) !important; transform: translateY(-2px); }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { border-color: #A166AB !important; box-shadow: 0 0 0 1px #A166AB !important; }
    .paper-card { background: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); line-height: 1.6; font-size: 0.95rem; color: #333; }
    .card-header { font-weight: 700; font-size: 1.05rem; color: #59316B; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #A166AB; }
    .highlight-error { background-color: #ffebee; color: #c62828; padding: 2px 4px; border-radius: 3px; font-weight: 600; }
    .highlight-success { background-color: #e8f5e9; color: #1b5e20; padding: 2px 4px; border-radius: 3px; font-weight: 600; }
    /* Fix bảng table trong markdown */
    table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; color: #59316B; }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; margin:0;'>HỌC GIỎI VĂN</h2>", unsafe_allow_html=True)
        st.caption("AI Grading System v3.0 Pro")
        st.markdown("---")
        st.write(f"👤 Xin chào: **{current_user}**")
        st.markdown("---")
        
        # --- [ĐÃ SỬA]: THÊM MENU "Thư viện mẫu chấm" VÀ ICON TƯƠNG ỨNG ---
        choice = option_menu(
            menu_title=None,
            options=["Trang chủ", "AI Chấm văn", "Tiến trình học", "Huấn luyện não", "Thư viện mẫu chấm", "Lịch sử"],
            icons=["house", "pen", "graph-up-arrow", "cpu", "journal-bookmark", "clock-history"],
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#7D4698", "font-size": "18px"}, 
                "nav-link": {"font-size": "15px", "margin": "5px", "color": "#59316B"},
                "nav-link-selected": {"background-color": "#7D4698", "color": "white"},
            }
        )
        
        st.markdown("---")
        topics = load_data(KNOWLEDGE_FILE)
        st.success(f"🧠 Đã học: {len(topics)} chủ đề")
        st.markdown("---")
        if st.button("🔴 Đăng xuất", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['logged_in'] = False
            st.session_state['user_name'] = ""
            st.session_state['onboarding_step'] = 'intro'
            st.rerun()

    if choice == "Trang chủ":
        st.markdown("""
        <style>
        .title-gradient { background: -webkit-linear-gradient(45deg, #59316B, #A166AB, #7D4698); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3em; font-weight: 800; margin-bottom: 0px; line-height: 1.2; }
        .typing-container { display: inline-block; overflow: hidden; white-space: nowrap; border-right: .15em solid #7D4698; animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite; font-family: 'Consolas', 'Courier New', monospace; color: #333; font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; }
        @keyframes typing { from { width: 0 } to { width: 100% } }
        @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #7D4698; } }
        .feature-card { background: rgba(248, 244, 249, 0.8); backdrop-filter: blur(8px); border: 1px solid #A166AB; border-radius: 16px; padding: 20px; transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .feature-card:hover { transform: translateY(-5px); background: #ffffff; box-shadow: 0 10px 15px rgba(125, 70, 152, 0.2); border-color: #7D4698; }
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

    elif choice == "AI Chấm văn":
        st.title("📝 Phân tích văn bản")
        topics = load_data(KNOWLEDGE_FILE)
        selected_topics = st.multiselect("📚 Kiến thức áp dụng (Lấy từ Huấn luyện não):", list(topics.keys()))
        
        if 'current_result' not in st.session_state:
            uploaded_files = st.file_uploader("📂 Tải 1 hoặc NHIỀU bài làm lên (PDF, DOCX, TXT):", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
            
            default_text = ""
            if uploaded_files:
                combined_texts = []
                for idx, file in enumerate(uploaded_files):
                    extracted_text = read_file_content(file)
                    if extracted_text.startswith("⚠️"):
                        st.error(f"Lỗi đọc file {file.name}: {extracted_text}")
                    else:
                        combined_texts.append(f"--- BÀI LÀM {idx+1} ({file.name}) ---\n{extracted_text}\n")
                
                default_text = "\n".join(combined_texts)
                
                if len(uploaded_files) == 1:
                    st.success(f"✅ Đã đọc thành công file: {uploaded_files[0].name}")
                else:
                    st.success(f"✅ Đã gộp thành công {len(uploaded_files)} file. Hệ thống sẽ bật chế độ SO SÁNH ĐỐI CHIẾU!")

            essay_input = st.text_area("Nhập văn bản của bạn (nếu chọn file, nội dung sẽ tự điền):", value=default_text, height=300)
            
            c_act1, c_act2, c_act3 = st.columns([1, 2, 1])
            with c_act2:
                start_btn = st.button("🚀 BẮT ĐẦU PHÂN TÍCH", use_container_width=True)
        else:
            col_new, _ = st.columns([1, 5])
            if col_new.button("🔄 Nhập bài mới"):
                del st.session_state['current_result']
                st.rerun()
                
        if 'start_btn' in locals() and start_btn:
            if not MY_API_KEY: 
                st.error("⚠️ Chủ hệ thống chưa cài đặt API Key trong mã nguồn (Hãy cài trong file secrets.toml)!")
            elif not essay_input: 
                st.warning("Chưa nhập nội dung")
            else:
                with st.spinner("Tôi đang đọc và phân tích dữ liệu..."):
                    try:
                        genai.configure(api_key=MY_API_KEY)
                        model = genai.GenerativeModel([m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods][0])
                        context = "\n".join([f"- {t}: {topics[t]['content']}" for t in selected_topics]) if selected_topics else "Không có kiến thức được chọn"
                        
                        prompt = f"""Bạn là trợ lý AI chuyên chấm thi và phân tích văn bản. Xưng hô: 'Tôi' và 'Bạn'.
Kiến thức/Barem áp dụng: {context}

Nội dung dữ liệu: 
{essay_input}

NHIỆM VỤ CỦA BẠN: 
- Nếu chỉ có 1 bài: Chấm, chỉ ra lỗi sai và nhận xét bài đó theo kiến thức/barem được cung cấp.
- Nếu có NHIỀU BÀI (có đánh dấu --- BÀI LÀM 1, 2...): Đọc và thực hiện SO SÁNH ĐỐI CHIẾU các bài với nhau.

TUYỆT ĐỐI KHÔNG lặp lại các dòng yêu cầu này. CHỈ TRẢ VỀ ĐÚNG 3 PHẦN NẰM TRONG CÁC THẺ DƯỚI ĐÂY:

[PHAN_1]
(Nếu 1 bài: Viết lại văn bản gốc, bọc lỗi sai trong <red>...</red>, ý hay trong <green>...</green>)
(Nếu nhiều bài: Kẻ bảng so sánh tổng quan các bài về: Ưu điểm, Nhược điểm, Điểm sáng tạo bằng cú pháp Markdown)
[/PHAN_1]
[PHAN_2]
(Nếu 1 bài: Giải thích lỗi sai và gợi ý sửa chi tiết)
(Nếu nhiều bài: Nhận xét chi tiết, chỉ ra các lỗi sai chung cần khắc phục và đánh giá bài nào ấn tượng nhất)
[/PHAN_2]
[PHAN_3]
(Code graphviz tóm tắt sự liên kết hoặc so sánh, mẫu: digraph G {{ rankdir=LR; "A"->"B"; }})
[/PHAN_3]"""
                        response = model.generate_content(prompt)
                        st.session_state['current_result'] = response.text
                        st.session_state['current_essay'] = essay_input
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Lỗi API: {str(e)}")

        if 'current_result' in st.session_state:
            full_res = st.session_state['current_result']
            
            p1_match = re.search(r'\[PHAN_1\](.*?)\[/PHAN_1\]', full_res, re.DOTALL)
            p2_match = re.search(r'\[PHAN_2\](.*?)\[/PHAN_2\]', full_res, re.DOTALL)
            p3_match = re.search(r'\[PHAN_3\](.*?)\[/PHAN_3\]', full_res, re.DOTALL)

            part1_essay = p1_match.group(1).strip() if p1_match else st.session_state.get('current_essay', '')
            
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
                    show_map = st.toggle("🧠 Bật Mindmap So Sánh", value=False)
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
                            "date": datetime.now().strftime("%d/%m %H:%M"), 
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
                html_essay = part1_essay.replace("<red>", '<span class="highlight-error">').replace("</red>", '</span>').replace("<green>", '<span class="highlight-success">').replace("</green>", '</span>')
                st.markdown(f'<div class="paper-card"><div class="card-header">📄 BẢN GỐC / SO SÁNH</div>\n\n{html_essay}\n\n</div>', unsafe_allow_html=True)
            with c_right:
                html_feedback = re.sub(r'\*\*(.*?)\*\*', r'<b style="color: #59316B;">\1</b>', part2_feedback)
                html_feedback = re.sub(r'(?m)^\s*[\*\-]\s+', '&#8226; ', html_feedback)
                html_feedback = html_feedback.replace('*', '')
                html_feedback = html_feedback.replace("\n", "<br>")
                
                st.markdown(f'<div class="paper-card" style="border-left: 4px solid #7D4698;"><div class="card-header" style="color: #59316B;">🤖 GÓC NHÌN AI</div>{html_feedback}</div>', unsafe_allow_html=True)

    # ==========================================
    # [TÍNH NĂNG MỚI] TAB: THƯ VIỆN MẪU CHẤM
    # ==========================================
    elif choice == "Thư viện mẫu chấm":
        st.title("📚 Thư viện Barem / Mẫu chấm điểm")
        st.write("Bấm vào từng mẫu để xem chi tiết. Nếu ưng ý, bạn chỉ cần bấm nút nạp để đưa thẳng vào bộ nhớ của AI.")
        st.markdown("---")
        
        # -----------------------------------------------------
        # KHOẢNG TRỐNG ĐỂ BẠN TỰ THÊM/CẬP NHẬT MẪU CHẤM
        # -----------------------------------------------------
        RUBRIC_TEMPLATES = {
            "Nghị luận xã hội 600 chữ": {
                "Mô tả": "Barem tiêu chuẩn dành cho các đoạn/bài văn nghị luận xã hội ngắn.",
                "Tiêu chí": """1. Mở bài/Mở đoạn: Giới thiệu đúng vấn đề nghị luận (1.0đ)
2. Giải thích vấn đề: Ngắn gọn, súc tích (1.5đ)
3. Phân tích - Bàn luận: Lập luận chặt chẽ, đa chiều (3.0đ)
4. Dẫn chứng: Sát thực tế, tiêu biểu (2.0đ)
5. Liên hệ bản thân & Rút ra bài học (1.5đ)
6. Điểm diễn đạt, chính tả, sáng tạo (1.0đ)""",
                "Phương thức AI chấm": "Hãy chấm điểm cực kỳ khắt khe ở phần 'Phân tích - Bàn luận' và 'Dẫn chứng'. Yêu cầu học sinh không dùng những dẫn chứng quá cũ. Kiểm tra tính logic giữa các câu văn."
            },
            
            "Phân tích tác phẩm văn học (Cơ bản)": {
                "Mô tả": "Barem chấm bài làm văn phân tích nhân vật hoặc đoạn trích thơ/văn xuôi.",
                "Tiêu chí": """1. Đảm bảo cấu trúc (Mở - Thân - Kết) (0.5đ)
2. Xác định đúng yêu cầu đề bài (0.5đ)
3. Triển khai nội dung sâu sắc, chia luận điểm rõ ràng (6.0đ)
4. Phân tích được nét đặc sắc Nghệ thuật (1.5đ)
5. Chính tả, ngữ pháp, chữ viết (0.5đ)
6. Sáng tạo, cảm nhận riêng (1.0đ)""",
                "Phương thức AI chấm": "Đọc kỹ phần phân tích nghệ thuật (các biện pháp tu từ, nhịp điệu, giọng văn). Nếu học sinh chỉ phân tích nội dung mà bỏ quên nghệ thuật, trừ thẳng 1.5đ. Chỉ ra các câu văn diễn đạt lủng củng."
            },

            "Đoạn văn NLXH 200 chữ": {
                "Mô tả": "Barem chấm đoạn văn nghị luận xã hội 200 chữ đánh giá theo các mức độ: Nhận biết, Thông hiểu, Vận dụng và Sáng tạo.",
                "Tiêu chí": """- Nhận biết: Xác định đúng vấn đề cần nghị luận, cách thức trình bày đoạn văn.
- Thông hiểu: Biết cách nêu quan điểm cá nhân; phối hợp các thao tác lập luận để phân tích, làm sáng tỏ vấn đề.
- Vận dụng: Đề xuất được hệ thống ý phù hợp; vận dụng tốt kĩ năng tạo lập văn bản (dùng từ, viết câu, liên kết, biểu đạt).
- Sáng tạo: Có sáng tạo trong diễn đạt, có giọng điệu cá nhân riêng biệt.""",
                "Phương thức AI chấm": "Hãy chấm sát theo 4 mức độ (Nhận biết, Thông hiểu, Vận dụng, Sáng tạo). Đánh giá kĩ sự mạch lạc trong lập luận, khả năng nêu quan điểm cá nhân và nhận xét về sự sáng tạo, giọng điệu riêng của người viết."
            },
            
            "Đoạn văn NLVH 200 chữ (Nhân vật)": {
                "Mô tả": "Barem chấm đoạn văn 200 chữ nghị luận về một nhân vật trong tác phẩm văn học.",
                "Tiêu chí": """1. Hình thức (0.25đ): Đúng cấu trúc đoạn văn (không xuống dòng), dung lượng khoảng 200 chữ (cho phép sai số 10-20%).
2. Xác định vấn đề (0.25đ): Nêu đúng tên nhân vật và đặc điểm/khía cạnh cần nghị luận ngay từ câu mở đoạn.
3. Triển khai nội dung (1.0đ): Phân tích chi tiết nghệ thuật (hành động, tâm trạng, ngôn ngữ), làm rõ ý nghĩa/thông điệp, dẫn chứng xác thực và có nhận xét nghệ thuật.
4. Sáng tạo & Cảm xúc (0.25đ): Có liên tưởng, so sánh, ngôn từ biểu cảm, góc nhìn riêng.
5. Chính tả & Ngữ pháp (0.25đ): Mạch lạc, không mắc lỗi diễn đạt cơ bản.""",
                "Phương thức AI chấm": "Bắt lỗi cực gắt ở phần hình thức: NẾU HỌC SINH XUỐNG DÒNG, trừ thẳng điểm hình thức (đoạn văn không được xuống dòng). Yêu cầu AI kiểm tra kĩ việc học sinh có trích dẫn từ văn bản hay không và đánh giá mức độ biểu cảm trong ngôn từ."
            },

            "Bài văn NLVH 600 chữ (Thang 4.0)": {
                "Mô tả": "Barem chấm bài văn 600 chữ phân tích tác phẩm văn học/thơ. Đi kèm yêu cầu AI viết đoạn văn 'Nâng tầm' làm mẫu.",
                "Tiêu chí": """1. Kiến thức nội dung & Đặc trưng thể loại (1.5đ):
- Mức 4: Phân tích sâu sắc nghệ thuật, sự vận động cảm xúc. Không bị 'diễn xuôi thơ'.
- Mức 3: Hiểu nội dung, có phân tích nghệ thuật nhưng chưa thực sự sắc sảo.
- Mức 2: Chủ yếu diễn xuôi, nghệ thuật hời hợt. Mức 1: Lạc đề/sai ý nghĩa.
2. Cấu trúc & Dung lượng (0.5đ):
- Mức 4: Đủ Mở-Thân-Kết, liên kết chặt chẽ, xấp xỉ 600 chữ.
- Mức 2: Thiếu phần, bố cục không rõ, bài quá ngắn/dài.
3. Tư duy sáng tạo & Liên hệ (1.0đ):
- Mức 4: Góc nhìn độc đáo, có liên hệ/so sánh tác phẩm khác.
- Mức 2: Liên hệ khiên cưỡng. Mức 1: Không mở rộng.
4. Kỹ năng diễn đạt & Chính tả (1.0đ):
- Mức 4: Văn phong cảm xúc, chuẩn thuật ngữ, không lỗi. Mức 2: Lỗi diễn đạt, lủng củng.""",
                "Phương thức AI chấm": """BẮT BUỘC TRẢ VỀ KẾT QUẢ THEO FORMAT SAU:
1. Bảng điểm tóm tắt: (STT Tiêu chí | Điểm đạt được | Nhận xét nhanh).
2. Tổng điểm: .../4.0.
3. Phân tích lỗi sai cụ thể: Trích dẫn lại ít nhất 2 câu văn bị lỗi của học sinh và chỉ ra cách sửa.
4. Đoạn văn 'Nâng tầm': Hãy chọn 1 đoạn trong bài và viết lại nó theo phong cách xuất sắc, sâu sắc hơn để làm mẫu cho học sinh."""
            },

            "Bài văn NLXH 600 chữ (Thang 4.0)": {
                "Mô tả": "Barem chấm bài văn 600 chữ nghị luận xã hội, chú trọng khả năng tư duy phản biện và tính thực tiễn của dẫn chứng.",
                "Tiêu chí": """1. Giải quyết vấn đề & Lập luận (1.5đ):
- Mức 4: Lý lẽ sắc sảo, logic, giải quyết triệt để. Mức 3: Lập luận đúng nhưng chưa sâu. Mức 2: Chung chung, giáo điều. Mức 1: Lạc đề.
2. Dẫn chứng & Tính thực tiễn (1.0đ):
- Mức 4: Dẫn chứng tiêu biểu, mới mẻ, mang tính thời sự, phân tích khéo léo. Mức 2: Lối mòn, hời hợt. Mức 1: Không có dẫn chứng.
3. Tư duy phản biện & Mở rộng (0.75đ):
- Mức 4: Lật ngược vấn đề, nhìn nhận nhiều chiều, giải pháp độc đáo. Mức 2: Phản biện yếu, lặp lại quan điểm cũ.
4. Hình thức, Ngôn ngữ & Dung lượng (0.75đ):
- Mức 4: Bố cục 3 phần, ngôn từ đanh thép, truyền cảm hứng, khoảng 600 chữ. Mức 2: Lỗi diễn đạt, sai dung lượng.""",
                "Phương thức AI chấm": """BẮT BUỘC TRẢ VỀ KẾT QUẢ THEO FORMAT SAU:
1. Bảng điểm tóm tắt: Tiêu chí | Điểm đạt được | Nhận xét nhanh. Tổng điểm: .../4.0.
2. Phân tích chi tiết: 
- Điểm sáng: Trích dẫn 1 câu văn hoặc 1 ý tưởng xuất sắc nhất của học sinh.
- Lỗ hổng tư duy: Chỉ ra điểm yếu trong lập luận hoặc dẫn chứng cần thay thế.
3. Đoạn văn 'Nâng cấp': Chọn một đoạn viết 'non' nhất của học sinh và viết lại theo phong cách nghị luận sắc sảo, chuyên sâu hơn.
4. Lời khuyên chiến thuật: Đưa ra 1 hành động cụ thể học sinh cần làm để tiến bộ ở bài sau."""
            }
        }
        # -----------------------------------------------------
        
        if not RUBRIC_TEMPLATES:
            st.info("Hiện chưa có mẫu chấm nào.")
        else:
            for template_name, data in RUBRIC_TEMPLATES.items():
                with st.expander(f"📌 Mẫu chấm: {template_name}"):
                    st.markdown(f"**Mô tả:** {data['Mô tả']}")
                    
                    st.markdown("**📋 Tiêu chí & Thang điểm:**")
                    st.write(data["Tiêu chí"])
                    
                    st.markdown("**🤖 Hướng dẫn AI cách chấm:**")
                    st.write(data["Phương thức AI chấm"])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Nút nạp trực tiếp vào KNOWLEDGE_FILE (Brain)
                    if st.button(f"🚀 Nạp '{template_name}' vào bộ nhớ AI", key=f"add_{template_name}", use_container_width=True):
                        topics = load_data(KNOWLEDGE_FILE)
                        # Gộp cả tiêu chí và phương thức chấm lại thành nội dung học cho AI
                        combined_content = f"TIÊU CHÍ CHẤM ĐIỂM:\n{data['Tiêu chí']}\n\nPHƯƠNG THỨC CHẤM (QUAN TRỌNG):\n{data['Phương thức AI chấm']}"
                        
                        topics[template_name] = {
                            "content": combined_content, 
                            "date": datetime.now().strftime("%d/%m/%Y")
                        }
                        save_data(KNOWLEDGE_FILE, topics)
                        
                        st.success(f"✅ Đã nạp thành công '{template_name}' vào hệ thống! Bạn có thể sang tab **AI Chấm văn** để sử dụng ngay.")

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
        st.caption("Mẹo: Dán các Tiêu chí từ 'Thư viện mẫu chấm' vào đây để hệ thống học cách chấm bài nhé!")
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
                    
                    p1_hist = re.search(r'\[PHAN_1\](.*?)\[/PHAN_1\]', feedback_content, re.DOTALL)
                    p2_hist = re.search(r'\[PHAN_2\](.*?)\[/PHAN_2\]', feedback_content, re.DOTALL)

                    if p1_hist and p2_hist:
                        part1 = p1_hist.group(1).strip()
                        part2 = p2_hist.group(1).strip()
                        
                        html_essay_hist = part1.replace("<red>", '<span class="highlight-error">').replace("</red>", '</span>').replace("<green>", '<span class="highlight-success">').replace("</green>", '</span>')
                        
                        formatted_part2 = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#59316B;">\1</b>', part2)
                        formatted_part2 = re.sub(r'(?m)^\s*[\*\-]\s+', '&#8226; ', formatted_part2)
                        formatted_part2 = formatted_part2.replace('*', '')
                        formatted_part2 = formatted_part2.replace('\n', '<br>')

                        col_hist1, col_hist2 = st.columns([1, 1], gap="medium")
                        with col_hist1:
                            st.markdown(f'<div class="paper-card"><div class="card-header">Sửa trên bài / Bảng So sánh</div>\n\n{html_essay_hist}\n\n</div>', unsafe_allow_html=True)
                        with col_hist2:
                            st.markdown(f'<div class="paper-card" style="border-left: 4px solid #7D4698;"><div class="card-header">Nhận xét</div>{formatted_part2}</div>', unsafe_allow_html=True)
                    else:
                        clean_fb = re.sub(r'\[/?PHAN_\d\]', '', feedback_content).strip()
                        st.write(clean_fb)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Xóa bài này", key=f"del_hist_{i}"):
                        history.pop(i)
                        save_data(HISTORY_FILE, history)
                        st.rerun()
